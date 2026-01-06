-- Complete Database Schema for MVSR RAG System with Versioning

-- Create database
CREATE DATABASE mvsr_rag;
\c mvsr_rag;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
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

-- Documents table with versioning
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

-- Document version history
CREATE TABLE document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    filename VARCHAR(500),
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_reason TEXT,
    file_path VARCHAR(1000),
    metadata JSONB,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, version_number)
);

-- Document chunks table (for RAG)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding_id VARCHAR(255) UNIQUE NOT NULL,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Research projects table
CREATE TABLE research_projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    pi VARCHAR(200),
    co_pi VARCHAR(200),
    department VARCHAR(100) NOT NULL,
    funding_agency VARCHAR(200),
    amount DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) CHECK (status IN ('proposed', 'ongoing', 'completed', 'discontinued')),
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Publications table
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    authors TEXT NOT NULL,
    journal VARCHAR(300),
    conference VARCHAR(300),
    year INTEGER NOT NULL,
    volume VARCHAR(50),
    issue VARCHAR(50),
    pages VARCHAR(50),
    doi VARCHAR(200),
    isbn VARCHAR(50),
    department VARCHAR(100) NOT NULL,
    publication_type VARCHAR(50) CHECK (publication_type IN ('journal', 'conference', 'book', 'chapter', 'thesis')),
    indexed_in TEXT[], -- ['Scopus', 'Web of Science', 'IEEE', etc.]
    citation_count INTEGER DEFAULT 0,
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Patents table
CREATE TABLE patents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    inventors TEXT NOT NULL,
    application_number VARCHAR(100),
    patent_number VARCHAR(100),
    filed_date DATE,
    granted_date DATE,
    status VARCHAR(50) CHECK (status IN ('filed', 'published', 'granted', 'rejected', 'expired')),
    department VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    patent_office VARCHAR(100),
    classification_code VARCHAR(100),
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Collaborators/MoUs table
CREATE TABLE collaborators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('academic', 'industry', 'government', 'international')),
    country VARCHAR(100),
    mou_signed_date DATE,
    mou_expiry_date DATE,
    status VARCHAR(50) CHECK (status IN ('active', 'expired', 'terminated')),
    collaboration_areas TEXT[],
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Query logs table (for analytics)
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    query_text TEXT NOT NULL,
    response_time_ms INTEGER,
    num_results INTEGER,
    satisfied BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Document access logs
CREATE TABLE document_access_logs (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    user_id INTEGER,
    access_type VARCHAR(50) CHECK (access_type IN ('view', 'download', 'update', 'delete')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_documents_department ON documents(department);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_embedding_id ON document_chunks(embedding_id);

CREATE INDEX idx_projects_department ON research_projects(department);
CREATE INDEX idx_projects_status ON research_projects(status);

CREATE INDEX idx_publications_department ON publications(department);
CREATE INDEX idx_publications_year ON publications(year DESC);

CREATE INDEX idx_patents_department ON patents(department);
CREATE INDEX idx_patents_status ON patents(status);

-- Create full-text search indexes
CREATE INDEX idx_documents_metadata_gin ON documents USING gin(metadata);
CREATE INDEX idx_documents_keywords_gin ON documents USING gin(keywords);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_research_projects_updated_at 
    BEFORE UPDATE ON research_projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample users
INSERT INTO users (username, password_hash, role, name, email, department) VALUES
('admin', '$2b$12$5OJOHEZD7CuJijeMzjePQOngR4sEXs3JVnAW999l9OZZD8eZnN.g3O', 'admin', 'System Admin', 'admin@mvsrec.edu.in', NULL),
('faculty1', '$2b$12$8hydC2r7DGwdYR8TqrOE9.Z0ElYPEHVUMIRQe3JddL4jUj2h199OnC', 'faculty', 'Dr. Sandhya Banda', 'sandhya@mvsrec.edu.in', 'CSE'),
('faculty2', '$2b$12$i49w326ty6Y9.fmfGWpL0.DkqOzI73TrMqHGPx7NN7zE0lVZSpIO6C', 'faculty', 'Dr. Priya Sharma', 'priya@mvsrec.edu.in', 'ECE'),
('student1', '$2b$12$1r9sEzD6lquRUIpJlyr4Gu7yh4ZChfMizDSwyEVQQ4Ht15Qb/0AVWa', 'student', 'John Doe', 'john@student.mvsrec.edu.in', 'CSE');

-- Create views for common queries

-- Active documents by department
CREATE VIEW active_documents_by_dept AS
SELECT 
    department,
    COUNT(*) as document_count,
    SUM(page_count) as total_pages,
    array_agg(DISTINCT category) as categories
FROM documents 
WHERE status = 'active'
GROUP BY department;

-- Research statistics
CREATE VIEW research_statistics AS
SELECT 
    department,
    COUNT(*) as project_count,
    SUM(amount) as total_funding,
    COUNT(CASE WHEN status = 'ongoing' THEN 1 END) as ongoing_projects,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_projects
FROM research_projects
GROUP BY department;

-- Publication statistics
CREATE VIEW publication_statistics AS
SELECT 
    department,
    year,
    COUNT(*) as publication_count,
    array_agg(DISTINCT publication_type) as types,
    SUM(citation_count) as total_citations
FROM publications
GROUP BY department, year
ORDER BY year DESC;

-- Patent statistics
CREATE VIEW patent_statistics AS
SELECT 
    department,
    status,
    COUNT(*) as patent_count,
    COUNT(CASE WHEN granted_date IS NOT NULL THEN 1 END) as granted_count
FROM patents
GROUP BY department, status;

-- Document version tracking view
CREATE VIEW document_version_history AS
SELECT 
    d.id,
    d.filename,
    d.department,
    d.category,
    d.version as current_version,
    d.uploaded_at as last_updated,
    d.uploaded_by as last_updated_by,
    dv.version_number,
    dv.uploaded_at as version_date,
    dv.change_reason
FROM documents d
LEFT JOIN document_versions dv ON d.id = dv.document_id
ORDER BY d.id, dv.version_number DESC;

-- Create function for soft delete
CREATE OR REPLACE FUNCTION soft_delete_document(doc_id INTEGER, deleted_by_user VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE documents 
    SET status = 'deleted', 
        deleted_at = CURRENT_TIMESTAMP,
        deleted_by = deleted_by_user
    WHERE id = doc_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Create function to archive old version
CREATE OR REPLACE FUNCTION archive_old_version(doc_id INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Insert current version into version history
    INSERT INTO document_versions (document_id, version_number, filename, uploaded_by, file_path, metadata)
    SELECT id, version, filename, uploaded_by, file_path, metadata
    FROM documents
    WHERE id = doc_id;
    
    -- Update document status
    UPDATE documents 
    SET status = 'archived', archived_at = CURRENT_TIMESTAMP
    WHERE id = doc_id;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO mvsr_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO mvsr_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO mvsr_user;

-- Insert sample data for testing
INSERT INTO documents (filename, file_type, department, category, uploaded_by, page_count, keywords, metadata) VALUES
('AI_Research_Project.pdf', 'application/pdf', 'CSE', 'research', 'faculty1', 8, ARRAY['AI', 'Machine Learning', 'Research'], '{"project_id": "CSE-2024-01"}'),
('IoT_Smart_Grid_Patent.pdf', 'application/pdf', 'ECE', 'patent', 'faculty2', 12, ARRAY['IoT', 'Smart Grid', 'Patent'], '{"application_number": "202441234"}'),
('IEEE_Publication_2024.pdf', 'application/pdf', 'CSE', 'publication', 'faculty1', 6, ARRAY['IEEE', 'Neural Networks'], '{"doi": "10.1109/example.2024"}');

INSERT INTO research_projects (title, pi, department, funding_agency, amount, start_date, end_date, status) VALUES
('Deep Learning for Medical Image Analysis', 'Dr. Sandhya Banda', 'CSE', 'DST', 5000000, '2023-01-01', '2025-12-31', 'ongoing'),
('IoT Based Smart Grid System', 'Dr. Priya Sharma', 'ECE', 'SERB', 4500000, '2023-06-01', '2025-05-31', 'ongoing');

INSERT INTO publications (title, authors, journal, year, department, publication_type, indexed_in) VALUES
('Advanced Deep Learning for Healthcare', 'Dr. Sandhya Banda, Dr. Anil Kumar', 'IEEE Transactions on Medical Imaging', 2024, 'CSE', 'journal', ARRAY['IEEE', 'Scopus', 'Web of Science']),
('IoT Architecture for Smart Cities', 'Dr. Priya Sharma, Dr. Rajesh Verma', 'Computer Networks', 2024, 'ECE', 'journal', ARRAY['Scopus', 'Elsevier']);

INSERT INTO patents (title, inventors, application_number, filed_date, status, department, country) VALUES
('Smart Energy Management System', 'Dr. Priya Sharma, Dr. Mohan Rao', '202441234', '2024-01-15', 'filed', 'ECE', 'India'),
('AI-Based Medical Diagnosis Framework', 'Dr. Sandhya Banda', '202341567', '2023-06-20', 'granted', 'CSE', 'India');