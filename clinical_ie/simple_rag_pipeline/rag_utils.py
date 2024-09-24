from sentence_transformers import CrossEncoder

from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import (SemanticSplitterNodeParser, SentenceSplitter)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings

from clinical_ie.simple_rag_pipeline.document_processor import DocumentProcessor


EMBEDDING_MODEL_PATH = "mixedbread-ai/mxbai-embed-large-v1"
RERANKER_MODEL_PATH = "mixedbread-ai/mxbai-rerank-base-v1"


def get_node_parser(embed_model, parsing_method: str = "semantic", **kwargs):
    """Returns a node parser based on the specified parsing method."""
    if parsing_method == "semantic":
        return SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model)
    elif parsing_method == "simple":
        chunk_size = kwargs.get("chunk_size")
        chunk_overlap = kwargs.get("chunk_overlap")
        if chunk_size is None or chunk_overlap is None:
            raise ValueError("chunk_size and chunk_overlap must be provided for 'simple' parsing method")
        return SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        raise ValueError(f'Invalid Parsing Method: {parsing_method}, choose one of "semantic", "simple"')


def get_embedding_model (embedding_provider="huggingface",DEBUG=False):
        if embedding_provider=="huggingface":
            embed_model_name = EMBEDDING_MODEL_PATH
            embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_PATH)
        else:
            raise ValueError (f"Embedding provider : {embedding_provider} not supported. Pick 'huggingface")
        
        print(f'{"==="*10} Embedding {embed_model_name} is loaded successfully using the provider {embedding_provider}')
        if DEBUG:
            print('Testing the Embedding output for query: Hellow World"')
            embeddings = embed_model.get_text_embedding("Hello World!")
            print(len(embeddings))
            print(embeddings[:5])
        return embed_model


def load_reranker_model() -> CrossEncoder:
    return CrossEncoder(RERANKER_MODEL_PATH)


def get_retriever_(pdf_file, node_parser_type,Settings,top_k, **kwargs):
        """
        Sets up the entire RAG pipeline, from document preparation to indexing.

        Args:
            pdf_paths (str): Path to the directory containing PDF files.
            node_parser_type (str): Method to use for parsing documents ('semantic', 'simple', etc.).
            **kwargs: Additional arguments for specific parsers and retrievers.

        Returns:
            VectorIndex: A configured query pipeline ready to run queries.
        """

        document_processor = DocumentProcessor()

        # Step 1: Prepare documents
        documents = document_processor.prepare_single_document(pdf_file=pdf_file)

        # Step 2: Run ingestion pipeline
        node_parser = get_node_parser(Settings.embed_model, parsing_method=node_parser_type, **kwargs)
        nodes = node_parser.get_nodes_from_documents(documents)

        # Step 3: prepare vector index
        return VectorStoreIndex(nodes).as_retriever(similarity_top_k=top_k)

def get_retriever(pdf_file, embed_model, node_parsing_method,top_k):
    Settings.embed_model = embed_model

    if node_parsing_method == "semantic":
        retriever = get_retriever_(pdf_file, node_parsing_method, Settings,top_k)
    elif node_parsing_method == "simple":
        retriever = get_retriever_(pdf_file, node_parsing_method, Settings,top_k, chunk_size = 376, chunk_overlap=128)
    
    return retriever

    

