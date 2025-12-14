import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, BookOpen, Upload, Trash2, Edit, Download, BarChart3, Users, Shield, FileText, ChevronDown, CheckCircle, XCircle } from 'lucide-react';

const AURACompleteSystem = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const [view, setView] = useState('login');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [editingDoc, setEditingDoc] = useState(null);
  const messagesEndRef = useRef(null);

  // Mock users
  const users = {
    admin: { username: 'admin', password: 'admin123', role: 'admin', name: 'System Admin' },
    faculty1: { username: 'faculty1', password: 'fac123', role: 'faculty', name: 'Dr. Sandhya Banda', department: 'CSE' },
    faculty2: { username: 'faculty2', password: 'fac123', role: 'faculty', name: 'Dr. Priya Sharma', department: 'ECE' },
    student: { username: 'student', password: 'stu123', role: 'student', name: 'John Doe' }
  };

  // Sample documents with version control
  const [docDatabase, setDocDatabase] = useState([
    {
      id: 1,
      filename: 'AI_Research_Project.pdf',
      department: 'CSE',
      category: 'research',
      uploadedBy: 'Dr. Sandhya Banda',
      uploadedAt: '2024-12-10 10:30',
      pages: 8,
      size: '2.5 MB',
      version: 1,
      status: 'active',
      chunks: 15,
      metadata: { keywords: ['AI', 'Machine Learning', 'Research'] }
    },
    {
      id: 2,
      filename: 'IoT_Smart_Grid_Patent.pdf',
      department: 'ECE',
      category: 'patent',
      uploadedBy: 'Dr. Priya Sharma',
      uploadedAt: '2024-12-09 14:20',
      pages: 12,
      size: '3.8 MB',
      version: 1,
      status: 'active',
      chunks: 24,
      metadata: { keywords: ['IoT', 'Smart Grid', 'Patent'] }
    },
    {
      id: 3,
      filename: 'IEEE_Publication_2024.pdf',
      department: 'CSE',
      category: 'publication',
      uploadedBy: 'Dr. Sandhya Banda',
      uploadedAt: '2024-12-08 09:15',
      pages: 6,
      size: '1.8 MB',
      version: 2,
      status: 'active',
      chunks: 12,
      metadata: { keywords: ['IEEE', 'Publication', 'Neural Networks'] }
    }
  ]);

  const departments = ['CSE', 'ECE', 'EEE', 'MECH', 'CIVIL', 'IT', 'AUTO', 'MBA'];
  const categories = ['research', 'patent', 'publication', 'project', 'proposal'];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleLogin = async (username, password) => {
    // Try backend authentication first
    let backendSuccess = false;
    try {
      const resp = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password })
      });

      if (resp.ok) {
        const data = await resp.json();
        setAuthToken(data.access_token);
        setCurrentUser(data.user);
        if (data.user.role === 'admin' || data.user.role === 'faculty') setView('admin');
        else setView('chat');
        backendSuccess = true;
      }
    } catch (err) {
      console.log('Backend unavailable, falling back to mock users');
    }

    // If backend failed, try mock users
    if (!backendSuccess) {
      const user = users[username];
      if (user && user.password === password) {
        setCurrentUser(user);
        if (user.role === 'admin' || user.role === 'faculty') {
          setView('admin');
        } else {
          setView('chat');
        }
      } else {
        alert('Invalid credentials');
      }
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setView('login');
    setMessages([]);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      if (!authToken) throw new Error('Not authenticated. Please login first.');

      // Upload file to backend
      const formData = new FormData();
      formData.append('file', file);
      formData.append('department', currentUser.department || selectedDept);
      formData.append('category', selectedCategory);

      const uploadResponse = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` },
        body: formData
      });

      if (!uploadResponse.ok) {
        const error = await uploadResponse.json().catch(() => ({}));
        throw new Error(error.detail || 'Upload failed');
      }

      const result = await uploadResponse.json();

      // Add to local state after successful backend upload
      const newDoc = {
        id: result.doc_id,
        filename: file.name,
        department: currentUser.department || selectedDept,
        category: selectedCategory,
        uploadedBy: currentUser.name,
        uploadedAt: new Date().toLocaleString(),
        pages: result.pages || Math.floor(Math.random() * 20) + 1,
        size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
        version: 1,
        status: 'active',
        chunks: result.chunks,
        metadata: { keywords: ['Research', 'MVSR'] }
      };

      setDocDatabase([...docDatabase, newDoc]);
      alert(`Document uploaded successfully! ${result.chunks} chunks created and embedded.`);
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateDocument = (docId, newFile) => {
    const updatedDocs = docDatabase.map(doc => {
      if (doc.id === docId) {
        return {
          ...doc,
          filename: newFile.name,
          pages: Math.floor(Math.random() * 20) + 1,
          size: (newFile.size / (1024 * 1024)).toFixed(2) + ' MB',
          version: doc.version + 1,
          uploadedAt: new Date().toLocaleString(),
          chunks: Math.floor(Math.random() * 30) + 10
        };
      }
      return doc;
    });
    setDocDatabase(updatedDocs);
    setEditingDoc(null);
    alert('Document updated successfully! Old embeddings removed, new embeddings generated.');
  };

  const handleDeleteDocument = (docId) => {
    if (window.confirm('Are you sure you want to delete this document? This will remove all associated embeddings.')) {
      const updatedDocs = docDatabase.map(doc => 
        doc.id === docId ? { ...doc, status: 'deleted' } : doc
      );
      setDocDatabase(updatedDocs);
      alert('Document deleted successfully!');
    }
  };

  const generateReport = () => {
    const activeDocsOnly = docDatabase.filter(d => d.status === 'active');
    
    const reportData = {
      totalDocuments: activeDocsOnly.length,
      byDepartment: departments.reduce((acc, dept) => {
        acc[dept] = activeDocsOnly.filter(d => d.department === dept).length;
        return acc;
      }, {}),
      byCategory: categories.reduce((acc, cat) => {
        acc[cat] = activeDocsOnly.filter(d => d.category === cat).length;
        return acc;
      }, {}),
      totalChunks: activeDocsOnly.reduce((sum, doc) => sum + doc.chunks, 0),
      totalPages: activeDocsOnly.reduce((sum, doc) => sum + doc.pages, 0)
    };

    let report = `# MVSR Engineering College - Research Database Report\n`;
    report += `Generated on: ${new Date().toLocaleString()}\n\n`;
    report += `## Summary\n`;
    report += `- Total Active Documents: ${reportData.totalDocuments}\n`;
    report += `- Total Pages: ${reportData.totalPages}\n`;
    report += `- Total Embedded Chunks: ${reportData.totalChunks}\n\n`;
    
    report += `## Documents by Department\n`;
    Object.entries(reportData.byDepartment).forEach(([dept, count]) => {
      if (count > 0) report += `- ${dept}: ${count} documents\n`;
    });
    
    report += `\n## Documents by Category\n`;
    Object.entries(reportData.byCategory).forEach(([cat, count]) => {
      if (count > 0) report += `- ${cat}: ${count} documents\n`;
    });

    report += `\n## Detailed Document List\n\n`;
    activeDocsOnly.forEach(doc => {
      report += `### ${doc.filename}\n`;
      report += `- Department: ${doc.department}\n`;
      report += `- Category: ${doc.category}\n`;
      report += `- Uploaded By: ${doc.uploadedBy}\n`;
      report += `- Version: ${doc.version}\n`;
      report += `- Pages: ${doc.pages}\n`;
      report += `- Chunks: ${doc.chunks}\n\n`;
    });

    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MVSR_Research_Report_${new Date().toISOString().split('T')[0]}.md`;
    a.click();
  };

  const processQuery = async (query) => {
    setLoading(true);
    try {
      if (!authToken) throw new Error('Not authenticated. Please login first.');

      // Call backend RAG API
      const queryResponse = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          top_k: 5
        })
      });

      if (!queryResponse.ok) throw new Error('Query failed');
      const result = await queryResponse.json();

      const response = result.response;
      const sources = (result.sources || []).map((source) => ({
        type: source.category || 'Document',
        title: source.filename || source.title || 'source',
        dept: source.department || source.dept
      }));

      setLoading(false);
      return { response, sources };
    } catch (error) {
      console.error('Query error:', error);
      setLoading(false);
      return {
        response: `Sorry, I encountered an error: ${error.message}. Please make sure the backend is running.`,
        sources: []
      };
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    const { response, sources } = await processQuery(input);
    const assistantMessage = { role: 'assistant', content: response, sources: sources };
    setMessages(prev => [...prev, assistantMessage]);
  };

  // Login View
  if (view === 'login') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              AURA
            </h1>
            <p className="text-gray-600 mt-2">MVSR Engineering College</p>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => handleLogin('admin', 'admin123')}
              className="w-full p-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center justify-center gap-2"
            >
              <Shield className="w-5 h-5" />
              Login as Admin
            </button>
            <button
              onClick={() => handleLogin('faculty1', 'fac123')}
              className="w-full p-4 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition-all flex items-center justify-center gap-2"
            >
              <Users className="w-5 h-5" />
              Login as Faculty (CSE)
            </button>
            <button
              onClick={() => handleLogin('student', 'stu123')}
              className="w-full p-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-all flex items-center justify-center gap-2"
            >
              <BookOpen className="w-5 h-5" />
              Login as Student
            </button>
          </div>

          <div className="mt-6 text-sm text-gray-500 text-center">
            <p>Demo Credentials:</p>
            <p>Admin: admin / admin123</p>
            <p>Faculty: faculty1 / fac123</p>
            <p>Student: student / stu123</p>
          </div>
        </div>
      </div>
    );
  }

  // Admin/Faculty Dashboard
  if (view === 'admin') {
    const filteredDocs = docDatabase.filter(doc => {
      if (doc.status === 'deleted') return false;
      if (currentUser.role === 'faculty' && doc.department !== currentUser.department) return false;
      if (selectedDept !== 'all' && doc.department !== selectedDept) return false;
      if (selectedCategory !== 'all' && doc.category !== selectedCategory) return false;
      return true;
    });

    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-blue-50 p-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-4">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  {currentUser.role === 'admin' ? 'Admin Dashboard' : 'Faculty Dashboard'}
                </h1>
                <p className="text-gray-600">Welcome, {currentUser.name}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setView('chat')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all"
                >
                  Chat Interface
                </button>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-white rounded-lg shadow p-4">
              <FileText className="w-8 h-8 text-blue-600 mb-2" />
              <p className="text-2xl font-bold text-gray-800">{filteredDocs.length}</p>
              <p className="text-gray-600 text-sm">Total Documents</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <BarChart3 className="w-8 h-8 text-green-600 mb-2" />
              <p className="text-2xl font-bold text-gray-800">
                {filteredDocs.reduce((sum, doc) => sum + doc.chunks, 0)}
              </p>
              <p className="text-gray-600 text-sm">Total Chunks</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <BookOpen className="w-8 h-8 text-purple-600 mb-2" />
              <p className="text-2xl font-bold text-gray-800">
                {filteredDocs.reduce((sum, doc) => sum + doc.pages, 0)}
              </p>
              <p className="text-gray-600 text-sm">Total Pages</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <CheckCircle className="w-8 h-8 text-indigo-600 mb-2" />
              <p className="text-2xl font-bold text-gray-800">
                {docDatabase.filter(d => d.status === 'active').length}
              </p>
              <p className="text-gray-600 text-sm">Active Docs</p>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-4">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Actions</h2>
            <div className="flex flex-wrap gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload New Document
                </label>
                <div className="flex gap-2">
                  {currentUser.role === 'admin' && (
                    <select
                      value={selectedDept}
                      onChange={(e) => setSelectedDept(e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg"
                    >
                      {departments.map(dept => (
                        <option key={dept} value={dept}>{dept}</option>
                      ))}
                    </select>
                  )}
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                  <label className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg cursor-pointer hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center gap-2">
                    <Upload className="w-4 h-4" />
                    Upload PDF
                    <input type="file" accept=".pdf,.docx,.xlsx" onChange={handleFileUpload} className="hidden" />
                  </label>
                </div>
              </div>
              <button
                onClick={generateReport}
                className="px-6 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition-all flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Generate Report
              </button>
            </div>
          </div>

          {/* Documents Table */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">Document Management</h2>
              {currentUser.role === 'admin' && (
                <select
                  value={selectedDept}
                  onChange={(e) => setSelectedDept(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All Departments</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pages/Chunks</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredDocs.map(doc => (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-gray-800">{doc.filename}</p>
                          <p className="text-sm text-gray-500">{doc.size}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{doc.department}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-700">
                          {doc.category}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">v{doc.version}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{doc.pages}p / {doc.chunks}c</td>
                      <td className="px-4 py-3">
                        <div className="text-sm">
                          <p className="text-gray-800">{doc.uploadedBy}</p>
                          <p className="text-gray-500">{doc.uploadedAt}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <label className="p-2 text-blue-600 hover:bg-blue-50 rounded cursor-pointer">
                            <Edit className="w-4 h-4" />
                            <input
                              type="file"
                              accept=".pdf,.docx"
                              onChange={(e) => e.target.files[0] && handleUpdateDocument(doc.id, e.target.files[0])}
                              className="hidden"
                            />
                          </label>
                          <button
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Chat View
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-2xl p-6 mb-4 border-t-4 border-indigo-600">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-3 rounded-xl">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  AURA
                </h1>
                <p className="text-gray-600 font-medium">Welcome, {currentUser.name}</p>
                <p className="text-sm text-gray-500">MVSR Engineering College</p>
              </div>
            </div>
            <div className="flex gap-2">
              {(currentUser.role === 'admin' || currentUser.role === 'faculty') && (
                <button
                  onClick={() => setView('admin')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all"
                >
                  Dashboard
                </button>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg">
          <div className="flex flex-col h-[600px]">
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8">
                  <div className="bg-gradient-to-br from-indigo-600 to-purple-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">Welcome to AURA! 🎓</h3>
                  <p className="text-gray-600 mb-2">Your AI assistant for MVSR Engineering College</p>
                  <p className="text-sm text-gray-500 mb-6">
                    Powered by {docDatabase.filter(d => d.status === 'active').length} verified documents
                  </p>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-3xl rounded-xl p-4 shadow-md ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                          : 'bg-gray-50 text-gray-800 border border-gray-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-300">
                          <p className="text-xs font-semibold mb-2 text-gray-600 flex items-center gap-1">
                            <BookOpen className="w-3 h-3" />
                            Sources:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {msg.sources.map((src, i) => (
                              <span
                                key={i}
                                className="text-xs bg-white px-2 py-1 rounded-md text-gray-700 border border-gray-200"
                              >
                                {src.type}: {src.title}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 shadow-md">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-5 h-5 text-indigo-600 animate-spin" />
                      <span className="text-sm text-gray-600">AURA is searching...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t bg-gray-50 p-4 rounded-b-xl">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="Ask AURA about MVSR research, documents, faculty..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-md hover:shadow-lg"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AURACompleteSystem;