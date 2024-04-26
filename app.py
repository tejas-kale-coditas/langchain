groq_key = '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'

from groq import Groq
import PyPDF2
import re
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from typing import List, Dict

groq_client = Groq(
    api_key=groq_key,
)

ef = embedding_functions.ONNXMiniLM_L6_V2()
client = Client(settings = Settings(persist_directory="./", is_persistent=True))
collection_ = None
collection_ = client.get_or_create_collection(name="test2", embedding_function=ef)

def verify_pdf_path(file_path):
    try:
        # Attempt to open the PDF file in binary read mode
        with open(file_path, "rb") as pdf_file:
            # Create a PDF reader object using PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if the PDF has at least one page
            if len(pdf_reader.pages) > 0:
                # If it has pages, the PDF is not empty, so do nothing (pass)
                pass
            else:
                # If it has no pages, raise an exception indicating that the PDF is empty
                raise ValueError("PDF file is empty")
    except PyPDF2.errors.PdfReadError:
        # Handle the case where the PDF cannot be read (e.g., it's corrupted or not a valid PDF)
        raise PyPDF2.errors.PdfReadError("Invalid PDF file")
    except FileNotFoundError:
        # Handle the case where the specified file doesn't exist
        raise FileNotFoundError("File not found, check file address again")
    except Exception as e:
        # Handle other unexpected exceptions and display the error message
        raise Exception(f"Error: {e}")

def load_pdf(file: str, word: int) -> Dict[int, List[str]]:
    # Create a PdfReader object from the specified PDF file
    reader = PdfReader(file)
    
    # Initialize an empty dictionary to store the extracted text chunks
    documents = {}
    
    # Iterate through each page in the PDF
    for page_no in range(len(reader.pages)):
        # Get the current page
        page = reader.pages[page_no]
        
        # Extract text from the current page
        texts = page.extract_text()
        
        # Use the get_text_chunks function to split the extracted text into chunks of 'word' length
        text_chunks = get_text_chunks(texts, word)
        
        # Store the text chunks in the documents dictionary with the page number as the key
        documents[page_no] = text_chunks
    
    # Return the dictionary containing page numbers as keys and text chunks as values
    return documents

def get_text_chunks(text: str, word_limit: int) -> List[str]:
    """
    Divide a text into chunks with a specified word limit 
    while ensuring each chunk contains complete sentences.
    
    Parameters:
        text (str): The entire text to be divided into chunks.
        word_limit (int): The desired word limit for each chunk.
    
    Returns:
        List[str]: A list containing the chunks of text with 
        the specified word limit and complete sentences.
    """
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        words = sentence.split()
        if len(" ".join(current_chunk + words)) <= word_limit:
            current_chunk.extend(words)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = words

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
    

def add_text_to_collection(file: str, word: int = 200) -> None:
    # Load the PDF file and extract text chunks
    docs = load_pdf(file, word)
    
    # Initialize empty lists to store data
    docs_strings = []  # List to store text chunks
    ids = []  # List to store unique IDs
    metadatas = []  # List to store metadata for each text chunk
    id = 0  # Initialize ID
    
    # Iterate through each page and text chunk in the loaded PDF
    for page_no in docs.keys():
        for doc in docs[page_no]:
            # Append the text chunk to the docs_strings list
            docs_strings.append(doc)
            
            # Append metadata for the text chunk, including the page number
            metadatas.append({'page_no': page_no})
            
            # Append a unique ID for the text chunk
            ids.append(id)
            
            # Increment the ID
            id += 1

    # Add the collected data to a collection
    collection_.add(
        ids=[str(id) for id in ids],  # Convert IDs to strings
        documents=docs_strings,  # Text chunks
        metadatas=metadatas,  # Metadata
    )
    
    # Return a success message
    return "PDF embeddings successfully added to collection"

def get_response(queried_texts: List[str],) -> List[Dict]:
    global messages
    
    # for qt in queried_texts:
    #     print(qt)

    messages = [
                    {"role": "system", "content": "You are a helpful assistant.\
                    And will always answer the question asked in 'ques:' and \
                    will quote the page number while answering any questions,\
                    It is always at the start of the prompt in the format 'page n'."},
                    {"role": "user", "content": ''.join(queried_texts)}
            ]
    # messages = [
    #             {
    #                 "role": "system", 
    #              "content": "You are a helpful assistant.\
    #              And will always answer the question asked in 'ques:' and \
    #              will quote the page number while answering any questions,\
    #              It is always at the start of the prompt in the format 'page n'."
    #              },
    #             {
    #                 "role": "user", 
    #                 "content": ''.join(queried_texts)
    #             }
    #       ]

    response = groq_client.chat.completions.create(
        messages= messages,
        model="llama3-70b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    print(f" groq response: {response.choices[0].message.content}")

    response_msg = response.choices[0].message.content
    messages = messages + [{"role":'assistant', 'content': response_msg}]
    return response_msg

def query_collection(texts: str, n: int) -> List[str]:
    result = collection_.query(
                  query_texts = texts,
                  n_results = n,
                 )
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    # distances = result["distances"][0]
    # print(f"distances: {distances}")
    resulting_strings = []
    for page_no, text_chunk in zip(metadatas, documents):
        resulting_strings.append(f"Page {page_no['page_no']}: {text_chunk}")
    return resulting_strings

def get_answer(query: str, n: int):
    queried_texts = query_collection(texts = query, n = n)
    queried_string = [''.join(text) for text in queried_texts]
    queried_string = queried_string[0] + f"ques: {query}"
    answer = get_response(queried_texts = queried_string,)
    return answer

def collection_clear():
    print("reached collection clear")
    collection_ = None


    
    