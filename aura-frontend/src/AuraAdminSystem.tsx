import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, Sparkles, BookOpen, Upload, Trash2, Edit, BarChart3, Users, Shield, FileText, LogIn, X } from 'lucide-react';

type Role = 'student' | 'admin' | 'faculty';

interface User {
  role: Role;
  name: string;
  department?: string;
}

interface Source {
  filename?: string;
  version?: number | string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface DocumentItem {
  id: string | number;
  filename: string;
  department: string;
  category: string;
  version: number | string;
  uploaded_by: string;
  uploaded_at: string;
  chunks?: number;
  pages?: number;
  status?: string;
  keywords?: string[];
}

const tokenize = (text: string) =>
  text
    .toLowerCase()
    .split(/[^a-z0-9]+/g)
    .filter(Boolean);

const synonymMap: Record<string, string[]> = {
  cnn: ['cnn', 'convnet', 'convolutional', 'convolution', 'neural', 'network', 'convolutional neural network', 'deep', 'learning'],
  rnn: ['rnn', 'recurrent', 'neural', 'network'],
  svm: ['svm', 'support', 'vector', 'machine'],
  mlp: ['mlp', 'multilayer', 'perceptron'],
  nlp: ['nlp', 'natural', 'language', 'processing'],
  ai: ['ai', 'artificial', 'intelligence'],
  dl: ['dl', 'deep', 'learning'],
};

  const expandTokens = (tokens: string[]) => {
    const out = new Set<string>(tokens);
    tokens.forEach(t => {
      const syns = synonymMap[t];
      if (syns) syns.forEach(s => out.add(s));
    });
    return Array.from(out);
  };

  const deriveKeywords = (d: { filename?: string; category?: string; department?: string }) => {
    const base = [
      ...(d.filename ? tokenize(d.filename) : []),
      ...(d.category ? tokenize(d.category) : []),
      ...(d.department ? tokenize(d.department) : []),
    ];
    return expandTokens(base);
  };

  const knowledgeBase: Record<string, string> = {
    cnn: 'A convolutional neural network (CNN) is a deep learning model that uses convolutional layers to automatically learn spatial hierarchies of features from data, commonly used in image and video tasks.',
    rnn: 'A recurrent neural network (RNN) is a neural architecture designed for sequential data, maintaining hidden state to capture temporal dependencies.',
    svm: 'Support Vector Machine (SVM) is a supervised learning algorithm that finds the optimal separating hyperplane maximizing margin between classes.',
    mlp: 'A multilayer perceptron (MLP) is a feedforward neural network with one or more hidden layers, using nonlinear activations to model complex functions.',
    nlp: 'Natural Language Processing (NLP) is a field focused on enabling computers to understand and generate human language.',
  };

const AURACompleteSystem = () => {
  const [currentUser, setCurrentUser] = useState<User>({ role: 'student', name: 'Student' });
  const [view, setView] = useState<'chat' | 'login' | 'admin'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDept, setSelectedDept] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState<boolean>(false);
  const [selectedDocForUpdate, setSelectedDocForUpdate] = useState<DocumentItem | null>(null);
  const [updateReason, setUpdateReason] = useState<string>('');
  const [updateFile, setUpdateFile] = useState<File | null>(null);
  const [uploadKeywords, setUploadKeywords] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const backendUrl: string = import.meta.env?.VITE_BACKEND_URL ?? 'http://localhost:8000';
  const [localMode, setLocalMode] = useState<boolean>(false);
  const LOCAL_DOCS_KEY = 'aura_local_docs_v1';
  const [backendOnline, setBackendOnline] = useState<boolean>(false);

  const loadLocalDocs = (): DocumentItem[] => {
    try {
      const raw = localStorage.getItem(LOCAL_DOCS_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw) as DocumentItem[];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  };

  const saveLocalDocs = (docs: DocumentItem[]) => {
    try {
      localStorage.setItem(LOCAL_DOCS_KEY, JSON.stringify(docs));
    } catch {
      // ignore storage errors
    }
  };

  const departments = ['CSE', 'ECE', 'EEE', 'MECH', 'CIVIL', 'IT', 'AUTO', 'MBA'];
  const categories = ['research', 'patent', 'publication', 'project', 'proposal'];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const stored = loadLocalDocs();
    if (stored.length > 0) {
      setDocuments(stored);
      setLocalMode(true);
    }
  }, []);

  const checkBackend = useCallback(async () => {
    try {
      const token = sessionStorage.getItem('aura_token');
      await fetch(`${backendUrl}/api/documents`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
      });
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    checkBackend();
  }, [checkBackend]);

  const handleLogin = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch(`${backendUrl}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (!response.ok) {
        const msg = `Login failed (status ${response.status}).`;
        throw new Error(msg);
      }

      const data = await response.json() as { access_token?: string; user?: Partial<User> };
      sessionStorage.setItem('aura_token', data.access_token ?? '');
      setCurrentUser({
        role: (data.user?.role as Role) ?? 'admin',
        name: data.user?.name ?? 'Admin',
        department: data.user?.department,
      });
      setView('admin');
      setBackendOnline(true);
    } catch {
      const isDemoAdmin = username === 'admin' && password === 'admin123';
      const isDemoFaculty = username === 'faculty1' && password === 'fac123';
      if (isDemoAdmin || isDemoFaculty) {
        const mockUser: User = isDemoAdmin
          ? { role: 'admin', name: 'Admin' }
          : { role: 'faculty', name: 'Faculty', department: 'CSE' };
        sessionStorage.setItem('aura_token', 'demo-token');
        setCurrentUser(mockUser);
        setView('admin');
        setLocalMode(true);
        return;
      }
      alert(`Login failed. Ensure the backend is running at ${backendUrl}.`);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('aura_token');
    setCurrentUser({ role: 'student', name: 'Student' });
    setView('chat');
    setMessages([]);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const uploadDept = currentUser.role === 'admin'
      ? (selectedDept === 'all' ? 'GENERAL' : selectedDept)
      : currentUser.department ?? '';
    const uploadCategory = selectedCategory === 'all' ? 'research' : selectedCategory;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('department', uploadDept);
    formData.append('category', uploadCategory);

    try {
      const token = sessionStorage.getItem('aura_token');
      const response = await fetch(`${backendUrl}/api/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      alert(`Document uploaded successfully: ${result.doc_id}`);
      // Refresh documents list after upload
      fetchDocuments();
    } catch {
      const userKw = uploadKeywords ? expandTokens(tokenize(uploadKeywords)) : [];
      const baseKw = deriveKeywords({ filename: file.name, category: uploadCategory, department: uploadDept });
      const newDoc: DocumentItem = {
        id: `local-${Date.now()}`,
        filename: file.name,
        department: uploadDept,
        category: uploadCategory,
        version: 1,
        uploaded_by: currentUser.name,
        uploaded_at: new Date().toISOString(),
        chunks: 0,
        pages: 0,
        status: 'active',
        keywords: Array.from(new Set([...baseKw, ...userKw])),
      };
      setDocuments(prev => {
        const next = [newDoc, ...prev];
        saveLocalDocs(next);
        return next;
      });
      setLocalMode(true);
      alert('Document saved locally for demo. Backend upload unavailable.');
    }
  };
  
  const handleUpdateDocument = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedDocForUpdate || !updateFile) {
        alert("Please select a file to update.");
        return;
    }

    const formData = new FormData();
    formData.append('file', updateFile);
    formData.append('reason', updateReason);

    try {
        const token = sessionStorage.getItem('aura_token');
        const response = await fetch(`${backendUrl}/api/documents/${selectedDocForUpdate.id}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Update failed');
        }

        alert('Document updated successfully!');
        closeUpdateModal();
        fetchDocuments();
    } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Update failed';
        const localDoc = selectedDocForUpdate;
        if (localDoc) {
          const updated: DocumentItem = {
            ...localDoc,
            version: typeof localDoc.version === 'number' ? localDoc.version + 1 : 2,
            uploaded_at: new Date().toISOString(),
          };
          setDocuments(prev => {
            const next = prev.map(d => (d.id === localDoc.id ? updated : d));
            saveLocalDocs(next);
            return next;
          });
          closeUpdateModal();
          setLocalMode(true);
          alert('Local document updated. Backend update unavailable.');
          return;
        }
        alert(`Failed to update document: ${msg}`);
    }
  };


  const fetchDocuments = useCallback(async () => {
    try {
      const token = sessionStorage.getItem('aura_token');
      const response = await fetch(`${backendUrl}/api/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      const docs = ((data.documents ?? []) as DocumentItem[]).map(d => ({
        ...d,
        keywords: deriveKeywords({ filename: d.filename, category: d.category, department: d.department }),
      }));
      setDocuments(docs);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  }, [backendUrl]);

  // Fetch documents when admin view is shown
  useEffect(() => {
    if (view === 'admin') {
      fetchDocuments();
    }
  }, [view, fetchDocuments]);

  const handleDeleteDocument = async (docId: string | number) => {
    if (window.confirm('Are you sure you want to delete this document? This will remove all associated embeddings.')) {
        try {
            const token = sessionStorage.getItem('aura_token');
            await fetch(`${backendUrl}/api/documents/${docId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
            });
            alert('Document deleted successfully!');
            fetchDocuments();
        } catch {
            setDocuments(prev => {
              const next = prev.filter(d => d.id !== docId);
              saveLocalDocs(next);
              return next;
            });
            setLocalMode(true);
            alert('Local document removed. Backend delete unavailable.');
        }
    }
  };
  
  const openUpdateModal = (doc: DocumentItem) => {
    setSelectedDocForUpdate(doc);
    setUpdateReason(`Updating ${doc.filename} for clarity.`);
    setIsUpdateModalOpen(true);
  };

  const closeUpdateModal = () => {
    setSelectedDocForUpdate(null);
    setUpdateFile(null);
    setUpdateReason('');
    setIsUpdateModalOpen(false);
  };


  const processQuery = async (query: string) => {
    setLoading(true);
    try {
      const token = sessionStorage.getItem('aura_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      // Public users (students) won't have a token, but the endpoint should handle it
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${backendUrl}/api/query`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ query: query, top_k: 5 }),
      });

      if (!response.ok) {
        throw new Error('Query failed');
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch {
      const tokens = expandTokens(tokenize(query));
      const scored = documents
        .map(d => {
          const kws = d.keywords ?? deriveKeywords({ filename: d.filename, category: d.category, department: d.department });
          const set = new Set(kws);
          const name = d.filename.toLowerCase();
          const scoreKeywords = tokens.reduce((s, t) => s + (set.has(t) ? 1 : 0), 0);
          const scoreName = tokens.reduce((s, t) => s + (name.includes(t) ? 1 : 0), 0);
          const score = scoreKeywords + scoreName;
          return { d, score };
        })
        .filter(x => x.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map(x => x.d);
      const sources: Source[] = scored.map(s => ({ filename: s.filename, version: s.version }));
      const names = scored.map(s => s.filename).join(', ');
      if (scored.length > 0) {
        const topic = tokens.find(t => knowledgeBase[t]);
        const answer = topic ? knowledgeBase[topic] : `The query matches your uploaded documents: ${names}.`;
        const response = `${answer}\nSources: ${names}`;
        setLoading(false);
        setLocalMode(true);
        return { response, sources };
      }
      const response = `I couldn't find any documents in the local knowledge base that match your query "${query}". This could be because:\n\n• No documents have been uploaded yet\n• The query terms don't match the document content\n• The documents are stored in the backend database\n\nTry uploading some documents first, or check if the backend is running properly.`;
      setLoading(false);
      setLocalMode(true);
      return { response, sources };
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    const data = await processQuery(input);
    const assistantMessage: Message = { role: 'assistant', content: data.response, sources: data.sources };
    setMessages(prev => [...prev, assistantMessage]);
  };
  
  // The rest of the component's JSX remains largely the same...
  // I will only show the changed parts for brevity.
  // The full code will be replaced in the file.

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
              AURA Staff Login
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
          </div>

          <button
            onClick={() => setView('chat')}
            className="w-full mt-6 p-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
          >
            Back to Chat
          </button>

          <div className="mt-4 text-sm text-gray-500 text-center">
            <p>Demo Credentials:</p>
            <p>Admin: admin / admin123</p>
            <p>Faculty: faculty1 / fac123</p>
          </div>
        </div>
      </div>
    );
  }

  // Admin/Faculty Dashboard
  if (view === 'admin') {
    const filteredDocs = documents.filter((doc: DocumentItem) => {
      // This logic seems to be missing from the original file, I'm keeping it simple
      if (doc.status === 'deleted') return false;
      if (currentUser.role === 'faculty' && doc.department !== (currentUser.department ?? '')) return false;
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
                {localMode && (
                  <span className="mt-1 inline-block text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-800">
                    Demo Mode
                  </span>
                )}
                <span className={`mt-1 ml-2 inline-block text-xs px-2 py-1 rounded ${backendOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {backendOnline ? 'Backend Connected' : 'Backend Offline'}
                </span>
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
                {filteredDocs.reduce((sum, doc) => sum + (doc.chunks || 0), 0)}
              </p>
              <p className="text-gray-600 text-sm">Total Chunks</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <BookOpen className="w-8 h-8 text-purple-600 mb-2" />
              <p className="text-2xl font-bold text-gray-800">
                {filteredDocs.reduce((sum, doc) => sum + (doc.pages || 0), 0)}
              </p>
              <p className="text-gray-600 text-sm">Total Pages</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <Users className="w-8 h-8 text-indigo-600 mb-2" />
              <p className="text-2xl font-bold text-gray-800">
                {new Set(filteredDocs.map(d => d.uploaded_by)).size}
              </p>
              <p className="text-gray-600 text-sm">Contributors</p>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-4">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Actions</h2>
            <div className="flex flex-wrap gap-4 items-end">
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
                  <input
                    type="text"
                    value={uploadKeywords}
                    onChange={(e) => setUploadKeywords(e.target.value)}
                    placeholder="Keywords (comma-separated)"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  <label className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg cursor-pointer hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center gap-2">
                    <Upload className="w-4 h-4" />
                    Browse
                    <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} className="hidden" />
                  </label>
                </div>
              </div>
              {/* <button
                onClick={() => alert("Generating report...")}
                className="px-6 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition-all flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Generate Report
              </button> */}
              <button
                onClick={() => fetchDocuments()}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Refresh Documents
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
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredDocs.map(doc => (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-800">{doc.filename}</p>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{doc.department}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-700">
                          {doc.category}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">v{doc.version}</td>
                      <td className="px-4 py-3">
                        <div className="text-sm">
                          <p className="text-gray-800">{doc.uploaded_by}</p>
                          <p className="text-gray-500">{new Date(doc.uploaded_at).toLocaleDateString()}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                            <button onClick={() => openUpdateModal(doc)} className="p-2 text-indigo-600 hover:bg-indigo-50 rounded">
                                <Edit className="w-4 h-4" />
                            </button>
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
        
        {isUpdateModalOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div className="bg-white rounded-xl shadow-2xl p-8 max-w-lg w-full">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-2xl font-bold text-gray-800">Update Document</h2>
                        <button onClick={closeUpdateModal} className="p-2 text-gray-500 hover:bg-gray-100 rounded-full">
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                    <form onSubmit={handleUpdateDocument}>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">New Document File</label>
                                <input 
                                    type="file" 
                                    accept=".pdf,.docx" 
                                    onChange={(e) => {
                                      const file = e.target.files?.[0] ?? null;
                                      setUpdateFile(file);
                                    }} 
                                    className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                                />
                            </div>
                            <div>
                                <label htmlFor="updateReason" className="block text-sm font-medium text-gray-700">Reason for Update</label>
                                <textarea 
                                    id="updateReason"
                                    value={updateReason}
                                    onChange={(e) => setUpdateReason(e.target.value)}
                                    rows={3}
                                    className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                ></textarea>
                            </div>
                        </div>
                        <div className="mt-6 flex justify-end gap-4">
                            <button type="button" onClick={closeUpdateModal} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">
                                Cancel
                            </button>
                            <button type="submit" className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700">
                                Submit Update
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        )}
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
              {currentUser.role === 'student' ? (
                 <button
                  onClick={() => setView('login')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all flex items-center gap-2"
                >
                  <LogIn className="w-4 h-4" />
                  Staff Login
                </button>
              ) : (
                <>
                  <button
                    onClick={() => setView('admin')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all"
                  >
                    Dashboard
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all"
                  >
                    Logout
                  </button>
                </>
              )}
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
                    Ask me anything about the documents in the knowledge base.
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
                                {src.filename} (v{src.version})
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
