
@app.delete("/api/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: psycopg.AsyncConnection = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    # First, get the filename from the database
    async with db.cursor(row_factory=dict_row) as acur:
        await acur.execute("SELECT filename FROM documents WHERE id = %s", (document_id,))
        doc = await acur.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        filename = doc['filename']

    # Delete from PostgreSQL
    async with db.cursor() as acur:
        await acur.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        await db.commit()

    # Delete from ChromaDB
    if collection:
        # Find all chunks associated with the file
        results = collection.get(where={"source": filename})
        if results and results['ids']:
            collection.delete(ids=results['ids'])

    return
