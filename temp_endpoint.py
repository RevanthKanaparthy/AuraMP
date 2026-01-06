
@app.get("/api/documents", response_model=List[Dict[str, Any]])
async def get_documents(
    current_user: dict = Depends(get_current_user), 
    db: psycopg.AsyncConnection = Depends(get_db)
):
    if not db:
        # Return mock data if DB is not available
        return [
            {"id": 1, "filename": "mock_paper.pdf", "department": "CSE", "category": "research", "uploaded_at": "2023-10-27T10:00:00Z"},
            {"id": 2, "filename": "mock_patent.docx", "department": "ECE", "category": "patent", "uploaded_at": "2023-10-26T12:00:00Z"},
        ]

    async with db.cursor(row_factory=dict_row) as acur:
        await acur.execute("SELECT id, filename, department, category, uploaded_at FROM documents ORDER BY uploaded_at DESC")
        documents = await acur.fetchall()
    return documents
