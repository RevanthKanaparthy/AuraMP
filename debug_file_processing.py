import sys
import os
from backend_complete import extract_text_from_pdf, extract_text_from_docx, extract_text_from_xlsx
from chunking_utils import create_semantic_chunks

def debug_file(file_path):
    """
    Extracts text and creates semantic chunks from a given file for debugging purposes.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    print(f"--- Debugging file: {os.path.basename(file_path)} ---\n")

    # 1. Extract Text
    text = ""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith(".xlsx"):
        text = extract_text_from_xlsx(file_path)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print(f"Error: Unsupported file type for file: {file_path}")
        return

    if not text.strip():
        print("--- Extracted Text (Failed or Empty) ---")
        print("No text could be extracted from the document.")
        print("---------------------------------------\n")
        return
        
    print("--- Extracted Text (First 500 characters) ---")
    print(text[:500])
    print("-------------------------------------------\n")

    # 2. Create Chunks
    print("--- Semantic Chunks ---")
    try:
        chunks = create_semantic_chunks(text, document_id=os.path.basename(file_path))
        if not chunks:
            print("No chunks were created. The text might be too short or lack semantic content.")
        else:
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"\n[Chunk {i+1}]")
                print(f"  - Text: '{chunk['chunk_text'][:150]}...'")
                print(f"  - Quality Score: {chunk['quality_score']:.2f}")
                print(f"  - Keywords: {chunk['keywords']}")
        print("\n-----------------------\n")
        
    except Exception as e:
        print(f"An error occurred during chunk creation: {e}")

    print("--- Debugging Complete ---")
    print("What to look for:")
    print("1. Extracted Text: Does the text look garbled or incomplete? If so, the issue is with text extraction.")
    print("2. Semantic Chunks: Are the chunks coherent sentences or paragraphs? Are the keywords relevant?")
    print("If both look good, the issue may be in the embedding, retrieval, or LLM response generation stages.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_file_processing.py <path_to_file>")
        sys.exit(1)
    
    file_to_debug = sys.argv[1]
    debug_file(file_to_debug)
