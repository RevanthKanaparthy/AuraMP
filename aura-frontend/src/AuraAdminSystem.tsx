import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Send, Loader2, Sparkles, BookOpen, Upload, Trash2, 
  Shield, FileText, LogIn, Lock, User as UserIcon,
  ChevronRight, BarChart3, Database
} from 'lucide-react';

// --- TYPES ---
type Role = 'student' | 'admin' | 'faculty';

interface User {
  role: Role;
  name: string;
  department: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

interface DocumentItem {
  id: string | number;
  filename: string;
  department: string;
  category: string;
  status: string;
  uploaded_at: string;
}

const AURACompleteSystem = () => {
  // --- STATE ---
  const [currentUser, setCurrentUser] = useState<User>({ role: 'student', name: 'Student', department: 'all' });
  const [view, setView] = useState<'chat' | 'login' | 'admin'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  
  // Login Form
  const [loginUser, setLoginUser] = useState('');
  const [loginPass, setLoginPass] = useState('');
  
  // Admin Upload Selection
  const [uploadDept, setUploadDept] = useState('CSE');
  const [uploadCat, setUploadCat] = useState('research');

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const backendUrl = "http://localhost:8000";

  // --- UTILS ---
  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(() => { scrollToBottom(); }, [messages]);

  const fetchDocuments = useCallback(async () => {
    const token = sessionStorage.getItem('aura_token');
    if (!token) return;
    try {
      const res = await fetch(`${backendUrl}/api/documents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) {
        throw new Error(`Server returned ${res.status} ${res.statusText}`);
      }
      try {
        const data = await res.json();
        if (Array.isArray(data)) {
          setDocuments(data);
        } else {
          setDocuments([]);
          console.error("Fetched documents data is not an array:", data);
        }
      } catch (jsonError: any) {
        setDocuments([]);
        console.error("Failed to parse documents JSON:", jsonError.message);
        // Try to get text response for more context
        const textResponse = await res.text();
        console.error("Non-JSON response from server:", textResponse);
        alert("Failed to parse server response. Check console for details.");
      }
    } catch (err: any) {
      console.error("Failed to fetch documents", err);
      alert(`Failed to fetch documents: ${err.message}`);
    }
  }, [backendUrl]);

  useEffect(() => {
    if (view === 'admin') {
      fetchDocuments();
    }
  }, [view, fetchDocuments]);

  // --- API CALLS ---

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', loginUser);
    formData.append('password', loginPass);

    try {
      const res = await fetch(`${backendUrl}/token`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Unauthorized");
      const data = await res.json();
      
      sessionStorage.setItem('aura_token', data.access_token);
      setCurrentUser({ role: 'admin', name: loginUser.toUpperCase(), department: 'all' });
      setView('admin');
      setLoginUser('');
      setLoginPass('');
    } catch (err) {
      alert("Invalid credentials. Please try admin / admin123");
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const token = sessionStorage.getItem('aura_token');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('department', uploadDept);
    formData.append('category', uploadCat);

    try {
      setLoading(true);
      const res = await fetch(`${backendUrl}/api/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        alert("Document indexed successfully!");
        fetchDocuments();
      } else {
        alert(`Upload failed: ${data.detail || res.statusText}`);
      }
    } catch (err) {
      alert(`Upload failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string | number) => {
    if (!window.confirm("Permanent delete? This removes vector embeddings too.")) return;
    const token = sessionStorage.getItem('aura_token');
    try {
      const res = await fetch(`${backendUrl}/api/documents/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        fetchDocuments();
      } else {
        alert("Delete failed.");
      }
    } catch (err) {
      alert("Delete failed.");
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const queryText = input;
    setInput('');
    setLoading(true);

    try {
      const token = sessionStorage.getItem('aura_token');
      const res = await fetch(`${backendUrl}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: queryText,
          department: currentUser.department,
          history: messages // Send previous messages
        })
      });

      if (!res.ok) {
        if (res.status === 401) {
          throw new Error("Unauthorized: Your session may have expired. Please log in again.");
        }
        throw new Error(`API error: ${res.statusText} (${res.status})`);
      }

      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }]);
    } catch (err: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message || "Could not connect to the backend."}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  // --- RENDER VIEWS ---

  if (view === 'login') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="bg-white p-8 rounded-3xl shadow-2xl w-full max-w-md border border-slate-100">
          <div className="text-center mb-8">
            <div className="bg-indigo-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Shield className="text-white w-8 h-8" />
            </div>
            <h2 className="text-3xl font-bold text-slate-800">Staff Portal</h2>
            <p className="text-slate-500">Access the research indexing engine</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-600 ml-1">Username</label>
              <input 
                type="text" required value={loginUser} onChange={e => setLoginUser(e.target.value)}
                className="w-full p-4 bg-slate-50 border rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="admin"
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-600 ml-1">Password</label>
              <input 
                type="password" required value={loginPass} onChange={e => setLoginPass(e.target.value)}
                className="w-full p-4 bg-slate-50 border rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="••••••••"
              />
            </div>
            <button className="w-full bg-indigo-600 text-white p-4 rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100">
              Sign In
            </button>
          </form>
          <button onClick={() => setView('chat')} className="w-full mt-6 text-slate-400 font-medium hover:text-slate-600">
            Back to Chat
          </button>
        </div>
      </div>
    );
  }

  if (view === 'admin') {
    return (
      <div className="min-h-screen bg-slate-50 p-4 md:p-10">
        <div className="max-w-6xl mx-auto space-y-8">
          <header className="flex flex-wrap justify-between items-center bg-white p-6 rounded-3xl shadow-sm border border-slate-100 gap-4">
            <div className="flex items-center gap-3">
              <Database className="text-indigo-600 w-8 h-8" />
              <div>
                <h1 className="text-2xl font-bold text-slate-800">Research Management</h1>
                <p className="text-sm text-slate-500">Managing embeddings for {currentUser.name}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setView('chat')} className="px-6 py-2 border rounded-xl font-semibold hover:bg-slate-50">Interface</button>
              <button onClick={() => { sessionStorage.clear(); setView('chat'); }} className="px-6 py-2 bg-slate-800 text-white rounded-xl font-semibold">Logout</button>
            </div>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 bg-white p-8 rounded-3xl shadow-sm border border-slate-100 space-y-6">
              <h3 className="text-lg font-bold flex items-center gap-2"><Upload size={20} className="text-indigo-600" /> Index New Material</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Department</label>
                  <select className="w-full mt-1 p-3 bg-slate-50 border rounded-xl outline-none" value={uploadDept} onChange={e => setUploadDept(e.target.value)}>
                    <option value="CSE">CSE</option><option value="ECE">ECE</option><option value="EEE">EEE</option><option value="MECH">MECH</option><option value="CIVIL">CIVIL</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Category</label>
                  <select className="w-full mt-1 p-3 bg-slate-50 border rounded-xl outline-none" value={uploadCat} onChange={e => setUploadCat(e.target.value)}>
                    <option value="research">Research Paper</option><option value="patent">Patent</option><option value="project">Project Report</option>
                  </select>
                </div>
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-200 rounded-3xl cursor-pointer hover:bg-slate-50 transition-all">
                  <FileText className="text-slate-300 w-10 h-10 mb-2" />
                  <span className="text-sm font-bold text-slate-500">Click to Select PDF</span>
                  <input type="file" className="hidden" accept=".pdf,.docx,.xlsx" onChange={handleFileUpload} />
                </label>
              </div>
            </div>

            <div className="lg:col-span-2 bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
              <div className="p-6 border-b bg-slate-50/50 flex justify-between items-center">
                <h3 className="font-bold text-slate-700">Indexed Documents</h3>
                <BarChart3 size={18} className="text-slate-400" />
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="text-xs font-bold text-slate-400 uppercase bg-slate-50">
                    <tr>
                      <th className="p-4">Filename</th>
                      <th className="p-4">Dept</th>
                      <th className="p-4">Category</th>
                      <th className="p-4 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {documents.map(d => (
                      <tr key={d.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="p-4 font-medium text-slate-700">{d.filename}</td>
                        <td className="p-4"><span className="text-xs font-bold px-2 py-1 bg-slate-100 rounded text-slate-500">{d.department}</span></td>
                        <td className="p-4 text-sm text-slate-500">{d.category}</td>
                        <td className="p-4 text-center">
                          <button onClick={() => handleDelete(d.id)} className="text-red-400 hover:text-red-600 transition-colors"><Trash2 size={18}/></button>
                        </td>
                      </tr>
                    ))}
                    {documents.length === 0 && (
                      <tr><td colSpan={4} className="p-20 text-center text-slate-300 italic">No research documents indexed in this session.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center p-4">
      <div className="w-full max-w-4xl flex flex-col h-[92vh] space-y-4">
        <header className="flex justify-between items-center bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-4">
            <div className="bg-indigo-600 p-3 rounded-2xl shadow-lg shadow-indigo-100">
              <Sparkles className="text-white w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-800 tracking-tight">AURA AI</h1>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Research Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex bg-slate-100 p-1 rounded-xl">
              {['all', 'CSE', 'ECE'].map(dept => (
                <button 
                  key={dept} onClick={() => setCurrentUser({...currentUser, department: dept})}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${currentUser.department === dept ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-400'}`}
                >
                  {dept.toUpperCase()}
                </button>
              ))}
            </div>
            <button onClick={() => setView('login')} className="p-2.5 bg-slate-50 rounded-xl hover:bg-slate-100 transition-all border border-slate-100">
              <UserIcon size={20} className="text-slate-600" />
            </button>
          </div>
        </header>

        <div className="flex-1 bg-white rounded-[2rem] shadow-sm border border-slate-100 flex flex-col overflow-hidden relative">
          <div className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-10 opacity-30">
                <BookOpen size={48} className="mb-4" />
                <h3 className="text-xl font-bold">Research Knowledge Base</h3>
                <p className="max-w-xs mt-2">Ask questions about MVSR publications, patents, and faculty projects.</p>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-5 rounded-3xl shadow-sm ${
                  m.role === 'user' 
                  ? 'bg-indigo-600 text-white rounded-tr-none' 
                  : 'bg-slate-50 text-slate-800 rounded-tl-none border border-slate-100'
                }`}>
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">{m.content}</div>
                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-slate-200/50 flex flex-wrap gap-2">
                      <span className="w-full text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Citations Found:</span>
                      {m.sources.map((s, idx) => (
                        <span key={idx} className="flex items-center gap-1 text-[10px] bg-white/50 backdrop-blur border px-2 py-1 rounded-full font-bold text-slate-500">
                          <FileText size={10} /> {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-50 p-4 rounded-3xl border border-slate-100 flex items-center gap-3">
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">AURA is thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 bg-slate-50/50 border-t border-slate-100">
            <div className="relative max-w-3xl mx-auto flex items-center">
              <input 
                type="text" className="w-full p-5 pr-16 bg-white border border-slate-200 rounded-[1.5rem] outline-none shadow-sm focus:ring-4 focus:ring-indigo-500/5 transition-all"
                placeholder="Ex: What are the recent CNN publications in CSE?" value={input} 
                onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSend()}
              />
              <button 
                onClick={handleSend} disabled={!input.trim() || loading}
                className="absolute right-2 p-3 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-700 disabled:opacity-30 transition-all shadow-lg shadow-indigo-200"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AURACompleteSystem;