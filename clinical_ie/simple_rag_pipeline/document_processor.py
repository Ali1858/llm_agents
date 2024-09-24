import os
import re
from typing import List
from functools import partial

from llama_index.core import SimpleDirectoryReader, Document
from clinical_ie.simple_rag_pipeline.text_cleaning_helpers import clean as advanced_clean

def is_int(s: str) -> bool:
    "Check if the input string can be converted to an integer."
    try:
        int(s)
        return True
    except ValueError:
        return False


class DocumentProcessor:
    """Handles document preparation and cleaning."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.cleaning_func = partial(advanced_clean,
                                     extra_whitespace=True,
                                     broken_paragraphs=True,
                                     bullets=True,
                                     ascii=True,
                                     lowercase=False,
                                     citations=True,
                                     merge_split_words=True)

    def basic_clean(self, txt: str) -> str:
        """Applies basic cleaning operations to the provided text."""
        txt = txt.replace('-\n', '')  # remove line hyphenated words
        txt = re.sub(r'(?<!\n)\n(?!\n|[A-Z0-9])', ' ', txt)  # remove unnecessary line break
        txt = '\n\n'.join([line for line in txt.split('\n') if not is_int(line)])  # remove lines that only have numbers
        return txt
        

    def extract_reference_section_text(self, page_text):
        found_references = False
        pattern = r'(?:References|Reference|Reference:|References:|Bibliography|Bibliographical References)\s*\n'
        
        if re.search(pattern, page_text, flags=re.IGNORECASE):
            found_references = True
            modified_text = re.sub(pattern + r'.*', '', page_text, flags=re.IGNORECASE | re.DOTALL)
        else:
            modified_text = page_text  # No change if no reference section is found
        
        return modified_text, found_references    


    def prepare_single_document(self, pdf_file: str, method: str = "simple") -> List[Document]:
        """Prepares a single document from a PDF file located at the specified path."""
        if not os.path.isfile(pdf_file) or not pdf_file.endswith('.pdf'):
            raise ValueError(f"The file {pdf_file} is not a valid PDF file")

        documents = []
        if method == "simple":
            documents = SimpleDirectoryReader(input_files=[pdf_file]).load_data()
            cleaned_docs = []
            found_references = None
            for doc in documents:
                if found_references:
                    break
                doc.text = self.basic_clean(doc.text)
                doc.text, found_references = self.extract_reference_section_text(doc.text)
                doc.text = self.cleaning_func(doc.text)
                cleaned_docs.append(doc)

        else:
            raise ValueError(f"Invalid Method: {method} not supported. Pick 'simple' or 'manual_parsing'")
    
        print(f'Found {len(documents)} total number of pages from the document {pdf_file}, after cleaning {len(cleaned_docs)} left')
        return cleaned_docs