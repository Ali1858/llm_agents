from typing import Dict, List, Tuple
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser



class ChunkManager:
    def __init__(self):
        self.chunks = {}

    def save_chunks(self, chunks_dict: List[Tuple[str,str]]) -> bool:
        """
        Save relevant chunks if it's unique. Returns appropriate message according to uniqueness of the chunks.
        Args chunks_dict List[Tuple[str,str]], where first item of the  tuple is id and second item is chunk text.
        """

        non_unique_ids = []
        for id, chunk in chunks_dict:
            if id not in self.chunks:
                self.chunks[id] = chunk
            else:
                non_unique_ids.append(id)
        
        if len(non_unique_ids) > 0:
            return f"chunk ids {non_unique_ids} already exists." 
        else:
            return "All chunks saved."


    def get_chunks(self) -> Dict[str, str]:
        "Get all saved chunks"
        return self.chunks
    
    def get_chunk(self, id:str) -> Dict[str, str]:
        "Get individual chunk by its id"
        if id in self.chunks:
            return self.chunks[id]
        return "Chunk id don't exits, try different id"


class RetrieverManager:
    def __init__(self, retriever, reranker_model, top_k=3) -> None:
        self.retriever = retriever
        self.reranker_model = reranker_model
        self.top_k = top_k
        
    def retrieve_chunks(self, query: str) -> str:
        "Given a query retrieves top k chunks from the vector db and concatanate them together along with their id before returning. Useful for querying the case study vector database."
        
        reranker_query = query
        query = f"Represent this sentence for searching relevant passages: {query}"

        chunk_id_mapper = {node.node.text : node.node.id_ for node in self.retriever.retrieve(query)}
        relevant_chunks = list(chunk_id_mapper.keys())
        ranked_result = self.reranker_model.rank(reranker_query, relevant_chunks, return_documents=True, top_k=self.top_k)
        
        concat_result = "Relevant Chunks:"

        for r in ranked_result:
            corpus_id = r['corpus_id']
            chunk_text = relevant_chunks[corpus_id]
            id = chunk_id_mapper[chunk_text]
            concat_result += f"\n{id} --> {chunk_text}"
        return concat_result


class MetadataManager:
    def __init__(self, categories: List[str]):
        self.categories = categories
        self.metadata_store = {category: [] for category in categories}


    def add_metadatas(self, metadata: List[Tuple[str,str]]) -> bool:
        """Add a piece of metadata to a specific category. 
        Args: metadata List[Tuple[str,str]], expects List of Tuples where first element of the tuple is category name and second element is metadata text.
        If a category have multiple metadata seperate it by delimeter ';'.
        Returns True if successful, return False if category doesnt exist"""

        unknow_cats = []
        for category, data in metadata:
            if category in self.categories:
                self.metadata_store[category].extend(data.split(';'))
            else:
                unknow_cats.append(category)
        if len(unknow_cats) > 0 :
            return f"Categories: {unknow_cats} are unknown, use know category names: {self.categories}"
        return "succesfully added metadata"


    def get_all_metadata(self) -> Dict[str, List[str]]:
        "Get all metadata for all categories. Returns a dictionary with categories as keys and lists of metadata as values."
        return self.metadata_store
    

class ClinicalMetadata(BaseModel):
    Life_Style: List[str]
    Family_History: List[str]
    Social_History: List[str]
    Medical_Surgical_History: List[str]
    Signs_and_Symptoms: List[str]
    Comorbidities: List[str]
    Diagnostic_Techniques_and_Procedures: List[str]
    Diagnosis: List[str]
    Laboratory_Values: List[str]
    Pathology: List[str]
    Pharmacological_Therapy: List[str]
    Interventional_Therapy: List[str]
    Patient_Outcome_Assessment: List[str]
    Age: int
    Gender: str

    class Config:
        populate_by_name = True


class OutputValidator:

    def __init__(self, pydantic_model) -> None:
        self.parser = PydanticOutputParser(pydantic_model)

    def validate_generated_metadata(self, text: str) -> ClinicalMetadata:
        """
        Validate generated structured clinical metadata from the given text.
        """
        try:
            parsed_output = self.parser.parse(text)
        except Exception as e:
            return f'Error during parsing the generated text: {e}'
        return parsed_output
