from backend_complete import extract_text_from_xlsx

text = extract_text_from_xlsx("uploads/Journals-Conferences-Books-Book Chapters 2024-25 (1).xlsx")
print("Extracted text:")
print(text[:1000])  # First 1000 chars
