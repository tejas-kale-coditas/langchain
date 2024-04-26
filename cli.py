import argparse

from app import (
    add_text_to_collection, 
    get_answer, 
    verify_pdf_path, 
    collection_clear
)

def main():
    # Create a command-line argument parser with a description
    parser = argparse.ArgumentParser(description="PDF Processing CLI Tool")
    
    # Define command-line arguments
    parser.add_argument("-f", "--file", help="Path to the input PDF file")
    
    parser.add_argument(
        "-c", "--count",
        default=200, 
        type=int, 
        help="Optional integer value for the number of words in a single chunk"
    )
    
    parser.add_argument(
        "-q", "--question", 
        type=str,
        help="Ask a question"
    )
    
    parser.add_argument(
        "-cl", "--clear", 
        type=bool, 
        help="Clear existing collection data"
    )
    
    parser.add_argument(
        "-n", "--number", 
        type=int, 
        default=1, 
        help="Number of results to be fetched from the collection"
    )

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Check if the '--file' argument is provided
    if args.file is not None:
        # Verify the PDF file path and add its text to the collection
        verify_pdf_path(args.file)
        confirmation = add_text_to_collection(file=args.file, word=args.count)
        print(f" This is confirmation: {confirmation}")

    # Check if the '--question' argument is provided
    if args.question is not None:
        n = args.number if args.number else 1  # Set 'n' to the specified number or default to 1
        answer = get_answer(args.question, n=n)
        print("Answer:", answer)

    # Check if the '--clear' argument is provided
    if args.clear:
        collection_clear()
        print("Current collection cleared successfully")

if __name__ == "__main__":
    main()
