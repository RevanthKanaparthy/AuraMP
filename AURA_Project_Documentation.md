# AURA - AI-Powered Unified Repository Application

## Project Documentation

### Version 1.0.0
### Date: December 2024
### Developed for: MVSR Research Intelligence Platform

---

## 1. Executive Summary

AURA (AI-Powered Unified Repository Application) is a comprehensive full-stack web application designed to serve as an intelligent research knowledge base for educational institutions. The system combines advanced document management, AI-powered semantic search, and administrative controls to facilitate efficient access to academic resources including research papers, patents, project reports, and faculty publications.

The application achieved a successful implementation with core functionality operational, including document upload processing, AI-powered querying with 77.5% accuracy on evaluation metrics, and secure user authentication. The system demonstrates strong capabilities in semantic search and fact retrieval, making it a valuable tool for research intelligence and knowledge management.

---

## 2. System Architecture

### 2.1 Technology Stack

#### Backend (FastAPI - Python)
- **Framework**: FastAPI for high-performance REST API development
  - Asynchronous request handling with async/await
  - Automatic OpenAPI/Swagger documentation generation
  - Built-in dependency injection system
  - Pydantic models for data validation and serialization
- **Database**: PostgreSQL with connection pooling for metadata storage
  - psycopg2 with RealDictCursor for efficient data retrieval
  - Connection pooling with configurable parameters
  - Transaction management and rollback capabilities
- **Vector Database**: ChromaDB for semantic search and document embeddings
  - Persistent storage with local file system
  - Cosine similarity search algorithms
  - Metadata filtering and collection management
- **AI Integration**: Ollama with Llama3.2:3b model for local LLM processing
  - RESTful API communication with Ollama server
  - Streaming response handling for real-time output
  - Model parameter configuration and optimization
- **Authentication**: JWT-based token authentication system
  - PyJWT library for token encoding/decoding
  - Configurable token expiration (60 minutes default)
  - Bearer token authentication middleware
- **File Processing**: Multi-format support (PDF, DOCX, XLSX) with intelligent text extraction
  - PyPDF2 for PDF text and metadata extraction
  - python-docx for Word document processing
  - openpyxl for Excel spreadsheet parsing
  - Intelligent chunking strategies (sentence-based, paragraph-based)

#### Frontend (React - TypeScript)
- **Framework**: React with TypeScript for type safety and maintainability
  - Functional components with hooks architecture
  - TypeScript interfaces for API response typing
  - Error boundary components for graceful error handling
- **Styling**: Tailwind CSS for modern, responsive UI design
  - Utility-first CSS framework
  - Responsive design patterns (mobile-first approach)
  - Dark/light theme capability (extensible)
- **State Management**: React hooks for efficient component state handling
  - useState for local component state
  - useEffect for side effects and API calls
  - useRef for DOM manipulation and persistent references
- **API Communication**: Fetch API for seamless backend integration
  - Native browser Fetch API with Promise-based handling
  - JSON request/response processing
  - Error handling and retry logic
  - Session storage for authentication tokens

### 2.2 Database Schema

The system utilizes a comprehensive PostgreSQL schema with 11+ tables designed for academic research management:

#### Core Tables
- **Users Table**: Authentication and role-based access control
  - Fields: id, username, password_hash, role, name, email, department, created_at, last_login, is_active
  - Roles: admin, faculty, student with hierarchical permissions
  - Unique constraints on username and email

- **Documents Table**: File metadata with versioning and soft delete capabilities
  - Fields: id, filename, file_type, file_path, file_size_bytes, department, category, uploaded_by, uploaded_at, version, status, archived_at, deleted_at, deleted_by, metadata (JSONB), keywords (TEXT[]), page_count
  - Categories: research, patent, publication, project, proposal, test
  - Status tracking: active, archived, deleted

#### Research Management Tables
- **Research Projects**: Funding, duration, and status tracking
  - Fields: id, title, pi, co_pi, department, funding_agency, amount, currency, start_date, end_date, status, document_id, created_at, updated_at, metadata
  - Status options: proposed, ongoing, completed, discontinued

- **Publications**: Academic paper management with indexing information
  - Fields: id, title, authors, journal, conference, year, volume, issue, pages, doi, isbn, department, publication_type, indexed_in (TEXT[]), citation_count, document_id, created_at, metadata
  - Publication types: journal, conference, book, chapter, thesis

- **Patents**: Intellectual property tracking and status monitoring
  - Fields: id, title, inventors, application_number, patent_number, filed_date, granted_date, status, department, country, patent_office, classification_code, document_id, created_at, metadata
  - Status options: filed, published, granted, rejected, expired

#### Supporting Tables
- **Document Versions**: Version history tracking
- **Document Chunks**: RAG processing data
- **Collaborators**: MoU and partnership management
- **Query Logs**: System usage analytics and performance metrics
  - Fields: id, user_id, query_text, response_time_ms, num_results, satisfied, timestamp, metadata

### 2.3 System Components Architecture

#### Document Processing Pipeline
1. **File Upload**: Multi-format file reception with validation
2. **Text Extraction**: Format-specific parsing (PDF/DOCX/XLSX)
3. **Chunking Strategy**: Intelligent text segmentation for embeddings
4. **Vector Generation**: Sentence-transformer model processing
5. **Storage**: ChromaDB persistence with metadata indexing
6. **Search Indexing**: PostgreSQL metadata cataloging

#### Query Processing Flow
1. **Natural Language Input**: User query reception
2. **Semantic Search**: Vector similarity matching
3. **Context Retrieval**: Relevant document chunks extraction
4. **AI Generation**: LLM response synthesis with citations
5. **Response Formatting**: Structured output with source attribution

#### Authentication Flow
1. **Credential Validation**: Username/password verification
2. **JWT Generation**: Secure token creation with expiration
3. **Middleware Verification**: Request authentication checking
4. **Role-based Access**: Permission validation per endpoint
5. **Session Management**: Token refresh and invalidation

---

## 3. Core Features & Functionality

### 3.1 User Authentication System
- **Multi-role Support**: Admin, faculty, and student access levels
- **Secure Login**: JWT token-based session management
- **Default Credentials**:
  - Administrator: `admin` / `admin123`
  - Faculty: `faculty1` / `fac123`, `faculty2` / `fac123`
  - Student: `student1` / `stu123`

### 3.2 Document Management System
- **Multi-format Upload**: PDF, DOCX, and XLSX file processing
- **Intelligent Processing**:
  - PDF: Page-by-page text extraction and chunking
  - DOCX: Paragraph-based content processing
  - XLSX: Row-by-row data conversion with header mapping
- **Metadata Tracking**: Department, category, upload timestamps, file statistics
- **Soft Delete**: Document archival with vector embedding preservation

### 3.3 AI-Powered Query Interface
- **Natural Language Processing**: Chat-based interface for research queries
- **Retrieval-Augmented Generation (RAG)**:
  - Semantic search across vectorized document chunks
  - AI-generated responses with source citations
  - Department-specific filtering capabilities
- **Performance Metrics**:
  - Response latency: <2 seconds
  - Semantic recall: Strong (77.5% evaluation pass rate)
  - Context window: Optimized for research document analysis

### 3.4 Administrative Dashboard
- **Document Oversight**: Upload management and status monitoring
- **User Management**: Role-based access control administration
- **Analytics**: Query logs and system usage statistics
- **Maintenance**: Document deletion with vector cleanup

---

## 4. Performance Evaluation

### 4.1 System Metrics

| Metric | Result | Analysis |
|--------|--------|----------|
| Query Accuracy | 31/40 (77.5%) | High performance for local AI system |
| Response Latency | <2 seconds | Near real-time responses |
| Semantic Recall | Strong | Effective concept linking and context understanding |
| Document Processing | Reliable | Multi-format support with accurate text extraction |

### 4.2 Evaluation Methodology

The system was tested against a comprehensive suite of 40 diverse queries covering:
- Author lookup and faculty identification
- Departmental filtering and resource isolation
- Semantic search without exact keyword matches
- Strict formatting requirements and output constraints
- Fact verification and metadata accuracy

### 4.3 Current Capabilities

**Strengths**:
- Robust semantic search and concept mapping
- Low-latency local processing
- Multi-format document handling
- Secure authentication and access control

**Areas for Enhancement**:
- Complex date filtering logic
- Strict formatting constraints
- Advanced metadata extraction

---

## 5. Deployment & Setup

### 5.1 Prerequisites
- Python 3.7+ with pip package manager
- Node.js with npm for frontend dependencies
- PostgreSQL database server
- Ollama with Llama3.2:3b model for AI processing

### 5.2 Installation Steps

#### Backend Setup
```bash
# Navigate to project root
cd /path/to/aura

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
psql -U postgres -d mvsr_rag -f database_schema.sql
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd aura-frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

#### AI Model Setup
```bash
# Ensure Ollama is running
ollama serve

# Pull required model
ollama pull llama3.2:3b
```

### 5.3 Environment Configuration

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT token signing key
- `OLLAMA_URL`: Local Ollama API endpoint (default: http://localhost:11434)

### 5.4 System Startup

```bash
# Terminal 1: Start backend
python backend_complete.py

# Terminal 2: Start frontend
cd aura-frontend && npm run dev
```

Access the application at `http://localhost:5173`

---

## 6. API Reference

### Authentication Endpoints
- `POST /token`: User login with username/password
- Returns: `{"access_token": "jwt_token", "token_type": "bearer"}`

### Document Management
- `GET /api/documents`: List all documents (authenticated)
- `POST /api/upload`: Upload new document with metadata
- `DELETE /api/documents/{id}`: Soft delete document

### Query Interface
- `POST /api/query`: Submit natural language query
- Request: `{"query": "search text", "department": "CSE"}`
- Response: `{"response": "AI answer", "sources": ["doc1.pdf", "doc2.pdf"]}`

### System Health
- `GET /api/health`: System status check
- Returns: `{"status": "online", "llm": "Ollama Running"}`

---

## 7. Security & Access Control

### Authentication Mechanisms
- JWT token-based session management
- Role-based access control (RBAC)
- Secure password handling with bcrypt (currently disabled for development)

### Data Protection
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Secure file upload with type checking

### Privacy Considerations
- Local AI processing (no external data transmission)
- On-premise document storage
- User activity logging for audit trails

---

## 8. Future Enhancements

### 8.1 AI Model Integration
- **Recommended**: Gemini 1.5 Flash for production deployment
- **Alternative**: Llama 3 8B for fully offline operation
- **Benefits**: Improved reasoning for complex queries and formatting

### 8.2 Feature Roadmap
- Advanced metadata extraction and tagging
- Collaborative document annotation
- Real-time notification system
- Advanced analytics dashboard
- Mobile application development

### 8.3 Performance Optimizations
- Distributed vector database scaling
- Caching layer implementation
- Query optimization and indexing improvements

---

## 9. Troubleshooting

### Common Issues

**Login Failures**:
- Verify database connection and user credentials
- Check JWT token expiration (60-minute timeout)
- Ensure bcrypt library compatibility (currently using plain text for development)

**Document Upload Errors**:
- Confirm file format support (PDF, DOCX, XLSX)
- Check file size limits and disk space
- Verify ChromaDB vector storage availability

**Query Response Issues**:
- Ensure Ollama service is running
- Check model loading status
- Verify document chunking and embedding generation

**Database Connection Problems**:
- Confirm PostgreSQL service status
- Validate connection string and credentials
- Check database schema initialization

---

## 10. Conclusion

AURA represents a significant advancement in research intelligence platforms, successfully combining modern web technologies with AI-powered knowledge discovery. The system demonstrates strong performance in semantic search and document processing while maintaining security and usability standards appropriate for academic environments.

With a 77.5% accuracy rate on comprehensive evaluation metrics and sub-2-second response times, AURA provides a solid foundation for research knowledge management. Future enhancements focusing on advanced AI model integration and feature expansion will further improve its capabilities for complex academic workflows.

The application successfully bridges the gap between traditional document repositories and intelligent knowledge systems, offering researchers and administrators powerful tools for information discovery and management.

---

## Appendices

### Appendix A: Database Schema Details

#### Complete Table Structures

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'faculty', 'student')),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

**documents**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100),
    file_path VARCHAR(1000),
    file_size_bytes BIGINT,
    department VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN ('research', 'patent', 'publication', 'project', 'proposal', 'test')),
    uploaded_by VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    archived_at TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    keywords TEXT[],
    page_count INTEGER,
    FOREIGN KEY (uploaded_by) REFERENCES users(username) ON DELETE SET NULL
);
```

**research_projects**
```sql
CREATE TABLE research_projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    pi VARCHAR(200),
    co_pi VARCHAR(200),
    department VARCHAR(100),
    funding_agency VARCHAR(200),
    amount DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'INR',
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'proposed' CHECK (status IN ('proposed', 'ongoing', 'completed', 'discontinued')),
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);
```

**publications**
```sql
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    authors TEXT NOT NULL,
    journal VARCHAR(300),
    conference VARCHAR(300),
    year INTEGER,
    volume VARCHAR(50),
    issue VARCHAR(50),
    pages VARCHAR(50),
    doi VARCHAR(200),
    isbn VARCHAR(20),
    department VARCHAR(100),
    publication_type VARCHAR(50) CHECK (publication_type IN ('journal', 'conference', 'book', 'chapter', 'thesis')),
    indexed_in TEXT[],
    citation_count INTEGER DEFAULT 0,
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);
```

**patents**
```sql
CREATE TABLE patents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    inventors TEXT NOT NULL,
    application_number VARCHAR(100) UNIQUE,
    patent_number VARCHAR(100),
    filed_date DATE,
    granted_date DATE,
    status VARCHAR(20) DEFAULT 'filed' CHECK (status IN ('filed', 'published', 'granted', 'rejected', 'expired')),
    department VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    patent_office VARCHAR(200),
    classification_code VARCHAR(50),
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);
```

#### Index Definitions for Performance Optimization

```sql
-- Users table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_active ON users(is_active);

-- Documents table indexes
CREATE INDEX idx_documents_department ON documents(department);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_documents_keywords ON documents USING GIN(keywords);
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);

-- Research projects indexes
CREATE INDEX idx_projects_department ON research_projects(department);
CREATE INDEX idx_projects_status ON research_projects(status);
CREATE INDEX idx_projects_pi ON research_projects(pi);
CREATE INDEX idx_projects_dates ON research_projects(start_date, end_date);

-- Publications indexes
CREATE INDEX idx_publications_department ON publications(department);
CREATE INDEX idx_publications_year ON publications(year);
CREATE INDEX idx_publications_type ON publications(publication_type);
CREATE INDEX idx_publications_indexed_in ON publications USING GIN(indexed_in);
CREATE INDEX idx_publications_authors ON publications(authors);

-- Patents indexes
CREATE INDEX idx_patents_department ON patents(department);
CREATE INDEX idx_patents_status ON patents(status);
CREATE INDEX idx_patents_filed_date ON patents(filed_date);
CREATE INDEX idx_patents_application_number ON patents(application_number);
```

#### Foreign Key Constraints and Data Integrity Rules

- **Referential Integrity**: All foreign key relationships maintain CASCADE or SET NULL delete actions
- **Check Constraints**: Enforce valid values for status fields, roles, and categories
- **Unique Constraints**: Prevent duplicate usernames, emails, and patent application numbers
- **Not Null Constraints**: Ensure required fields are populated
- **Default Values**: Provide sensible defaults for timestamps and status fields

### Appendix B: API Response Examples

#### Authentication Endpoints

**POST /token**
```json
// Request
{
  "username": "admin",
  "password": "admin123"
}

// Success Response (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

// Error Response (401)
{
  "detail": "Invalid credentials"
}
```

#### Document Management Endpoints

**GET /api/documents**
```json
// Success Response (200)
[
  {
    "id": 1,
    "filename": "AI_Research_Project.pdf",
    "department": "CSE",
    "category": "research",
    "uploaded_by": "faculty1",
    "uploaded_at": "2024-12-01T10:30:00Z",
    "status": "active",
    "file_size_bytes": 2048576,
    "page_count": 8
  },
  {
    "id": 2,
    "filename": "IoT_Smart_Grid_Patent.pdf",
    "department": "ECE",
    "category": "patent",
    "uploaded_by": "faculty2",
    "uploaded_at": "2024-12-02T14:20:00Z",
    "status": "active",
    "file_size_bytes": 1572864,
    "page_count": 12
  }
]

// Error Response (401)
{
  "detail": "Not authenticated"
}
```

**POST /api/upload**
```json
// Request (multipart/form-data)
{
  "file": "<PDF/DOCX/XLSX file>",
  "department": "CSE",
  "category": "research"
}

// Success Response (200)
{
  "message": "Document uploaded successfully",
  "document_id": 3,
  "filename": "uploaded_document.pdf",
  "chunks_processed": 45,
  "processing_time_seconds": 2.3
}

// Error Response (400)
{
  "detail": "Unsupported file format. Supported formats: PDF, DOCX, XLSX"
}
```

#### Query Interface Endpoints

**POST /api/query**
```json
// Request
{
  "query": "What are the recent publications in machine learning?",
  "department": "CSE"
}

// Success Response (200)
{
  "response": "Based on the uploaded documents, recent machine learning publications in the CSE department include:\n\n1. 'Deep Learning for Medical Image Analysis' by Dr. Sandhya Banda (2024)\n2. 'Advanced Neural Network Architectures' by faculty researchers (2023)\n\nThese works focus on healthcare applications and novel network designs.",
  "sources": [
    "AI_Research_Project.pdf",
    "Medical_Imaging_Paper.pdf"
  ],
  "processing_time_ms": 1250,
  "confidence_score": 0.87
}

// Error Response (503)
{
  "detail": "AI service unavailable. Please try again later."
}
```

#### Error Handling and Status Codes

**Common HTTP Status Codes:**
- `200 OK`: Successful request
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: External service (Ollama) unavailable

**Validation Error Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "department"],
      "msg": "Department must be one of: CSE, ECE, EEE, MECH, CIVIL",
      "type": "value_error.const"
    }
  ]
}
```

### Appendix C: Development Environment Setup

#### Detailed Dependency Installation

**Python Backend Dependencies:**
```bash
# Core web framework
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0

# Database and ORM
pip install psycopg2-binary==2.9.9
pip install sqlalchemy==2.0.23

# Authentication and security
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4

# AI and ML
pip install chromadb==0.4.18
pip install sentence-transformers==2.2.2
pip install httpx==0.25.2

# Document processing
pip install PyPDF2==3.0.1
pip install python-docx==1.1.0
pip install openpyxl==3.1.2

# Utilities
pip install python-multipart==0.0.6
pip install aiofiles==23.2.1
```

**Node.js Frontend Dependencies:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "lucide-react": "^0.294.0",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  },
  "devDependencies": {
    "@types/node": "^20.9.0",
    "@typescript-eslint/eslint-plugin": "^6.11.0",
    "@typescript-eslint/parser": "^6.11.0",
    "eslint": "^8.54.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.4",
    "vite": "^5.0.0"
  }
}
```

#### Development Tools and IDE Configuration

**VS Code Extensions:**
- Python (Microsoft)
- Pylance
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- GitLens
- REST Client

**IDE Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

#### Testing Framework Setup and Usage

**Backend Testing:**
```bash
# Install testing dependencies
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install httpx==0.25.2
pip install pytest-cov==4.1.0

# Run tests
pytest tests/ -v --cov=app --cov-report=html
```

**Frontend Testing:**
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event
npm install --save-dev jsdom

# Run tests
npm test
```

**Sample Test Structure:**
```
tests/
├── __init__.py
├── conftest.py
├── test_auth.py
├── test_documents.py
├── test_query.py
└── integration/
    ├── test_full_workflow.py
    └── test_admin_functions.py
```

### Appendix D: Evaluation Test Cases

#### Complete List of 40 Evaluation Queries

**Author Lookup Queries (8 queries):**
1. "Who published on Deep Learning?"
2. "Find papers by Dr. Sandhya Banda"
3. "List faculty working on IoT"
4. "Who are the researchers in CSE department?"
5. "Find publications by faculty1"
6. "Who works on Smart Grid technology?"
7. "List authors of patent applications"
8. "Find researchers in Medical Imaging"

**Departmental Filtering (6 queries):**
9. "Show all CSE publications"
10. "What research is happening in ECE?"
11. "List MECH department projects"
12. "Find EEE patents"
13. "What documents are in CIVIL department?"
14. "Show research across all departments"

**Semantic Search (10 queries):**
15. "Tell me about CNN" (should find Deep Learning content)
16. "What is Alzheimer's research?" (should find MRI context)
17. "Explain Smart Grid technology"
18. "What are recent AI developments?"
19. "Find information about Neural Networks"
20. "What IoT applications exist?"
21. "Describe Medical Image Analysis work"
22. "What renewable energy research is there?"
23. "Find cloud computing papers"
24. "What cybersecurity work is being done?"

**Strict Formatting (8 queries):**
25. "List exactly 3 research projects"
26. "Give me 5 faculty names in bullet points"
27. "Show publications from 2023 only"
28. "List patents in numbered format"
29. "Find documents uploaded in December"
30. "Show projects with budget over 5 lakhs"
31. "List publications with DOI numbers"
32. "Find papers with more than 5 citations"

**Fact Verification (8 queries):**
33. "When was the AI research project uploaded?"
34. "What is the DOI of the IEEE publication?"
35. "How many pages in the Smart Grid patent?"
36. "What funding does the Medical Imaging project have?"
37. "When was the IoT patent filed?"
38. "How many CSE publications are there?"
39. "What is the file size of the research document?"
40. "When was faculty1's last login?"

#### Performance Metrics Breakdown

**Query Category Performance:**
- Author Lookup: 7/8 (87.5%) - Strong performance
- Departmental Filtering: 6/6 (100%) - Perfect accuracy
- Semantic Search: 8/10 (80%) - Good concept mapping
- Strict Formatting: 5/8 (62.5%) - Needs improvement
- Fact Verification: 5/8 (62.5%) - Mixed results

**Error Analysis:**
- Formatting issues: Complex constraints (exact counts, date ranges)
- Fact verification: Metadata extraction limitations
- Semantic search: Some context linking failures

#### Improvement Recommendations

**Immediate Improvements:**
1. Enhance date parsing and filtering logic
2. Implement strict counting mechanisms for list responses
3. Improve metadata extraction from documents
4. Add citation counting and DOI validation

**Medium-term Enhancements:**
1. Integrate more advanced AI models (Gemini 1.5 Flash)
2. Implement query expansion and refinement
3. Add document summarization capabilities
4. Enhance multi-document synthesis

**Long-term Goals:**
1. Implement conversational memory
2. Add document recommendation system
3. Create collaborative annotation features
4. Develop advanced analytics dashboard

---

**Document Version Control**
- v1.0.0: Initial release documentation
- Created: December 2024
- Last Updated: December 2024
- Author: AURA Development Team
