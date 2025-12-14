# main.py - Complete FastAPI Backend with Authentication & Document Versioning

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document as DocxDocument
import jwt
import json
import google.generativeai as genai
from passlib.context import CryptContext

# Configuration
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt (truncate to 72 bytes for bcrypt limit)"""
    # bcrypt has a 72 byte limit, truncate if necessary
    truncated_password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt"""
    # bcrypt has a 72 byte limit, truncate if necessary
    truncated_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)

# Toggle heavy embedding/vector operations for local debugging
SKIP_EMBEDDINGS = os.environ.get("SKIP_EMBEDDINGS", "1") == "1"

# Configure the Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock document storage for demo (in case PostgreSQL is not available)
mock_documents = {
    1: {
        'id': 1,
        'filename': 'AI_Research_Project.pdf',
        'department': 'CSE',
        'category': 'research',
        'uploaded_by': 'admin',
        'uploaded_at': datetime.now(),
        'version': 1,
        'status': 'active',
        'metadata': {'keywords': ['AI', 'ML']}
    }
}
doc_counter = 1

# Mock users for demo
mock_users = {
    'admin': {
        'username': 'admin',
        'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lWZQXyzO',  # bcrypt hash
        'role': 'admin',
        'name': 'Admin',
        'department': None,
        'is_active': True
    },
    'faculty1': {
        'username': 'faculty1',
        'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lWZQXyzO',  # bcrypt hash
        'role': 'faculty',
        'name': 'Faculty',
        'department': 'CSE',
        'is_active': True
    }
}

# Database connections
def get_db():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="mvsr_rag",
            user="mvsr_user",
            password="Aura2451",
            host="localhost"
        )
        yield conn
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}. Using mock data.")
        yield None
    finally:
        if conn is not None:
            conn.close()

def get_cursor(conn: psycopg2.extensions.connection = Depends(get_db)):
    if conn is None:
        yield None
    else:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()

def get_vector_db():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="mvsr_documents",
        metadata={"hnsw:space": "cosine"}
    )
    return collection

# Initialize embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Models
class User(BaseModel):
    username: str
    role: str
    department: Optional[str] = None
    name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class DocumentUpload(BaseModel):
    department: str
    category: str
    metadata: Optional[dict] = {}

class DocumentUpdate(BaseModel):
    doc_id: int
    reason: Optional[str] = "Document updated"

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")



@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        print(f"Login attempt: {form_data.username}")

        # Try database first
        try:
            conn = psycopg2.connect(
                dbname="mvsr_rag",
                user="mvsr_user",
                password="Aura2451",
                host="localhost"
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (form_data.username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and verify_password(form_data.password, user['password_hash']):
                print(f"Database user authenticated: {form_data.username}")
                access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
                user_data = User(
                    username=user['username'],
                    role=user['role'],
                    name=user['name'],
                    department=user['department']
                )
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": user_data
                }
        except Exception as db_error:
            print(f"Database error: {db_error}. Falling back to mock users.")

        # Fall back to mock users
        if form_data.username in mock_users:
            user = mock_users[form_data.username]
            if verify_password(form_data.password, user['password_hash']):
                print(f"Mock user authenticated: {form_data.username}")
                access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
                user_data = User(
                    username=user['username'],
                    role=user['role'],
                    name=user['name'],
                    department=user['department']
                )
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": user_data
                }

        raise HTTPException(status_code=401, detail="Incorrect username or password")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Document Processing Functions
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# API Endpoints

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    category: str = Form(...),
    current_user: dict = Depends(verify_token),
    cursor: psycopg2.extensions.cursor = Depends(get_cursor)
):
    """Upload and process a new document"""
    print("--- UPLOAD START ---")
    
    # Check permissions
    if current_user["role"] == "student":
        raise HTTPException(status_code=403, detail="Students cannot upload documents")
    
    if current_user["role"] == "faculty" and department != current_user.get("department"):
        raise HTTPException(status_code=403, detail="Faculty can only upload to their department")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text
    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Chunk text
    chunks = chunk_text(text)
    # Ensure at least one chunk to avoid downstream errors
    if not chunks:
        if text:
            chunks = [text]
        else:
            chunks = [""]
    
    # Store in database
    global doc_counter
    
    try:
        if cursor is None:
            # Use mock storage
            doc_counter += 1
            doc_id = doc_counter
            mock_documents[doc_id] = {
                'id': doc_id,
                'filename': file.filename,
                'file_type': file.content_type,
                'department': department,
                'category': category,
                'uploaded_by': current_user["sub"],
                'uploaded_at': datetime.now(),
                'version': 1,
                'status': 'active',
                'metadata': {'keywords': ['mvsr', category]},
                'chunks': len(chunks),
                'pages': len(text) // 2000
            }
            print(f"--- DOCUMENT STORED IN MOCK DB, DOC_ID: {doc_id} ---")
        else:
            cursor.execute("""
                INSERT INTO documents (filename, file_type, department, category, uploaded_by, metadata, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                file.filename,
                file.content_type,
                department,
                category,
                current_user["sub"],
                json.dumps({"keywords": ["mvsr", category]}),
                1
            ))
            
            doc_id = cursor.fetchone()['id']
            cursor.connection.commit()
            print(f"--- DOCUMENT INSERTED, DOC_ID: {doc_id} ---")
        
        # Generate embeddings and store in vector DB (guarded)
        ids = []
        if not SKIP_EMBEDDINGS:
            try:
                vector_db = get_vector_db()
                embeddings = embedding_model.encode(chunks)

                ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [{
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "department": department,
                    "category": category,
                    "filename": file.filename
                } for i in range(len(chunks))]

                try:
                    vector_db.add(
                        documents=chunks,
                        embeddings=embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings,
                        ids=ids,
                        metadatas=metadatas
                    )
                    print(f"--- EMBEDDINGS ADDED TO VECTOR DB ---")
                except Exception as inner_e:
                    print(f"--- VECTOR DB ADD FAILED: {inner_e} ---")
                    ids = []
            except Exception as e:
                print(f"--- EMBEDDING/VECTOR DB GENERATION FAILED: {e} ---")
                ids = []
        else:
            print("--- SKIPPING EMBEDDINGS AND VECTOR DB (debug mode) ---")
        
        # Store chunk references in database
        if cursor is not None and ids:
            for i, chunk in enumerate(chunks):
                cursor.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding_id)
                    VALUES (%s, %s, %s, %s)
                """, (doc_id, chunk, i, ids[i]))
            
            cursor.connection.commit()
        
        print("--- UPLOAD END ---")
        
        return {
            "message": "Document uploaded successfully",
            "doc_id": doc_id,
            "chunks": len(chunks),
            "pages": len(text) // 2000  # Approximate
        }
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # attempt rollback if possible
        try:
            if cursor is not None:
                cursor.connection.rollback()
        except:
            pass
        # write traceback to log for debugging
        try:
            with open('backend_error.log', 'a', encoding='utf-8') as f:
                f.write(f"--- UPLOAD FAILED at {datetime.now().isoformat()} ---\n")
                f.write(tb + "\n")
        except Exception:
            print("Failed to write backend_error.log")
        print(f"--- UPLOAD FAILED, TRANSACTION ROLLED BACK: {e} ---")
        raise HTTPException(status_code=500, detail="Failed to process document.")


async def _archive_document(cursor: psycopg2.extensions.cursor, doc_id: int, reason: str, updated_by: str):
    """Helper to archive a single document version."""
    cursor.execute("SELECT * FROM documents WHERE id = %s AND status = 'active'", (doc_id,))
    doc = cursor.fetchone()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Active document with id {doc_id} not found.")

    # Move to document_versions table
    cursor.execute("""
        INSERT INTO document_versions (document_id, filename, file_type, department, category, uploaded_by, uploaded_at, version, metadata, reason, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        doc['id'], doc['filename'], doc['file_type'], doc['department'], doc['category'],
        doc['uploaded_by'], doc['uploaded_at'], doc['version'], json.dumps(doc['metadata']),
        reason, updated_by
    ))

    # Soft delete the original document record
    cursor.execute("""
        UPDATE documents 
        SET status = 'archived', archived_at = NOW() 
        WHERE id = %s
    """, (doc_id,))

    # Clean up associated chunks and embeddings
    vector_db = get_vector_db()
    cursor.execute("SELECT embedding_id FROM document_chunks WHERE document_id = %s", (doc_id,))
    embedding_ids = [row['embedding_id'] for row in cursor.fetchall() if row['embedding_id']]
    if embedding_ids:
        vector_db.delete(ids=embedding_ids)
    
    cursor.execute("DELETE FROM document_chunks WHERE document_id = %s", (doc_id,))
    
@app.put("/api/documents/{doc_id}")
async def update_document(
    doc_id: int,
    file: UploadFile = File(...),
    reason: str = Form("Document updated"),
    current_user: dict = Depends(verify_token),
    cursor: psycopg2.extensions.cursor = Depends(get_cursor)
):
    """Update an existing document (creates a new version by archiving the old one)."""
    if cursor is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")

    if current_user["role"] == "student":
        raise HTTPException(status_code=403, detail="Students cannot update documents")

    try:
        # 1. Get existing document metadata
        cursor.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
        existing_doc = cursor.fetchone()
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # 2. Check permissions
        if current_user["role"] == "faculty" and existing_doc['department'] != current_user.get("department"):
            raise HTTPException(status_code=403, detail="Cannot update documents from other departments")

        # 3. Archive the old document
        await _archive_document(cursor, doc_id, reason, current_user["sub"])

        # 4. Process the new file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        chunks = chunk_text(text)
        if not chunks: chunks = [""]

        # 5. Create the new document record
        new_version = existing_doc['version'] + 1
        cursor.execute("""
            UPDATE documents
            SET filename = %s, file_type = %s, uploaded_by = %s, uploaded_at = NOW(), 
                version = %s, status = 'active', metadata = %s,
                archived_at = NULL, deleted_at = NULL, deleted_by = NULL
            WHERE id = %s
        """, (
            file.filename, file.content_type, current_user["sub"], new_version,
            json.dumps({"update_reason": reason}),
            doc_id
        ))
        
        # 6. Add new embeddings (if not skipped)
        if not SKIP_EMBEDDINGS:
            vector_db = get_vector_db()
            embeddings = embedding_model.encode(chunks)
            ids = [f"doc_{doc_id}_v{new_version}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{
                "doc_id": doc_id, "chunk_index": i, 
                "department": existing_doc['department'], "category": existing_doc['category'],
                "filename": file.filename, "version": new_version
            } for i in range(len(chunks))]
            vector_db.add(documents=chunks, embeddings=embeddings.tolist(), ids=ids, metadatas=metadatas)
            
            # Store new chunk references
            for i, chunk in enumerate(chunks):
                cursor.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding_id)
                    VALUES (%s, %s, %s, %s)
                """, (doc_id, chunk, i, ids[i]))

        # 7. Commit transaction
        cursor.connection.commit()

        return {
            "message": "Document updated successfully",
            "doc_id": doc_id,
            "new_version": new_version
        }
    except Exception as e:
        if cursor and cursor.connection:
            cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

@app.delete("/api/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: dict = Depends(verify_token),
    cursor: psycopg2.extensions.cursor = Depends(get_cursor)
):
    """Soft delete a document"""
    if cursor is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")

    if current_user["role"] not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        cursor.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
        doc = cursor.fetchone()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if current_user["role"] == "faculty" and doc['department'] != current_user.get("department"):
            raise HTTPException(status_code=403, detail="Cannot delete documents from other departments")
        
        cursor.execute("""
            UPDATE documents 
            SET status = 'deleted', deleted_at = NOW(), deleted_by = %s
            WHERE id = %s
        """, (current_user["sub"], doc_id))
        
        cursor.execute("SELECT embedding_id FROM document_chunks WHERE document_id = %s", (doc_id,))
        embedding_ids = [row['embedding_id'] for row in cursor.fetchall() if row['embedding_id']]
        
        if embedding_ids:
            vector_db = get_vector_db()
            vector_db.delete(ids=embedding_ids)
        
        cursor.connection.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        if cursor and cursor.connection:
            cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/api/documents")
async def list_documents(
    department: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(verify_token),
    cursor: psycopg2.extensions.cursor = Depends(get_cursor)
):
    """List documents with filtering"""
    if cursor is None:
        # Use mock data if DB is not available
        documents = [doc for doc in mock_documents.values() if doc['status'] == 'active']
        if current_user["role"] == "faculty":
            documents = [d for d in documents if d['department'] == current_user.get("department")]
        elif department:
            documents = [d for d in documents if d['department'] == department]
        if category:
            documents = [d for d in documents if d['category'] == category]
        return {"documents": documents}

    query = "SELECT * FROM documents WHERE status = 'active'"
    params = []
    
    # Department filtering based on role
    if current_user["role"] == "faculty":
        query += " AND department = %s"
        params.append(current_user.get("department"))
    elif department:
        query += " AND department = %s"
        params.append(department)
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    query += " ORDER BY uploaded_at DESC"
    
    cursor.execute(query, tuple(params))
    documents = cursor.fetchall()
    
    return {"documents": documents}

@app.post("/api/query")
async def query_rag(
    request: QueryRequest,
    current_user: dict = Depends(verify_token)
):
    """Query the RAG system"""
    
    # Generate query embedding
    query_embedding = embedding_model.encode([request.query])[0]
    
    # Search vector DB
    vector_db = get_vector_db()
    results = vector_db.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=request.top_k
    )
    
    if not results['documents'][0]:
        return {
            "response": "I couldn't find relevant information in the knowledge base.",
            "sources": []
        }
    
    # Combine context
    context = "\n\n".join(results['documents'][0])
    sources = results['metadatas'][0]
    
    # Generate response (integrate your LLM here)
    prompt = f"""Based on the following context from MVSR Engineering College documents, 
answer the question accurately.

Context:
{context}

Question: {request.query}

Answer:"""
    
    # Generate response using Gemini
    if not GEMINI_API_KEY:
        response = "LLM generation is not configured. Please set the GEMINI_API_KEY environment variable."
    else:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            llm_response = model.generate_content(prompt)
            response = llm_response.text
        except Exception as e:
            print(f"Error generating response from LLM: {e}")
            response = "I'm experiencing technical difficulties generating a response right now. The knowledge base search was successful, but the AI assistant is temporarily unavailable. Please try again later or contact support."
            
    return {
        "response": response,
        "sources": sources,
        "num_sources": len(sources)
    }

@app.get("/api/reports/generate")
async def generate_report(
    department: Optional[str] = None,
    current_user: dict = Depends(verify_token),
    cursor: psycopg2.extensions.cursor = Depends(get_cursor)
):
    """Generate aggregated report"""
    if cursor is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")

    if current_user["role"] == "student":
        raise HTTPException(status_code=403, detail="Students cannot generate reports")
    
    try:
        query = "SELECT * FROM documents WHERE status = 'active'"
        params = []
        
        if current_user["role"] == "faculty":
            query += " AND department = %s"
            params.append(current_user.get("department"))
        elif department:
            query += " AND department = %s"
            params.append(department)
        
        cursor.execute(query, tuple(params))
        documents = cursor.fetchall()
        
        stats = {
            "total_documents": len(documents),
            "by_department": {},
            "by_category": {},
            "by_year": {},
            "total_versions": sum(doc['version'] for doc in documents) if documents else 0
        }
        
        for doc in documents:
            stats['by_department'][doc['department']] = stats['by_department'].get(doc['department'], 0) + 1
            stats['by_category'][doc['category']] = stats['by_category'].get(doc['category'], 0) + 1
            year = doc['uploaded_at'].year
            stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
        
        return {
            "report": stats,
            "documents": documents,
            "generated_at": datetime.now().isoformat(),
            "generated_by": current_user["sub"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
