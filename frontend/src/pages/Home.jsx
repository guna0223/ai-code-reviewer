import React, { useState } from "react";
import SearchBar from "../components/SearchBar/SearchBar";
import LoadingSpinner from "../components/LoadingSpinner/LoadingSpinner";
import { analyzeInput } from "../services/api";

function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeInput(query);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to connect. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <header className="header">
          <h1 className="logo">
            <span className="logo-icon">⚡</span>
            AI Code Assistant
          </h1>
          <p className="tagline">Powered by Gemini AI</p>
        </header>

        {/* Search Bar */}
        <div className="search-section">
          <SearchBar
            value={query}
            onChange={setQuery}
            onSubmit={handleSubmit}
            loading={loading}
          />
        </div>

        {/* Loading */}
        {loading && <LoadingSpinner />}

        {/* Error */}
        {error && (
          <div className="error-card">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="main-layout">
            {/* Left Panel - Results */}
            <div className="left-panel">
              {/* Question Answer */}
              {result.type === "question" && (
                <div className="result-card">
                  <div className="result-header">
                    <span className="result-icon">💡</span>
                    <h3>Answer</h3>
                  </div>
                  <p className="answer-text">{result.answer}</p>
                  {result.example_code && (
                    <div className="code-box">
                      <pre><code>{result.example_code}</code></pre>
                    </div>
                  )}
                </div>
              )}

              {/* Code Analysis */}
              {result.type === "code" && (
                <div className="code-analysis">
                  {/* Status */}
                  <div className={`status-badge ${result.is_valid ? "valid" : "invalid"}`}>
                    {result.is_valid ? "✅ Code is Correct" : "❌ Code has Errors"}
                  </div>

                  {/* Error Details */}
                  {!result.is_valid && result.error && (
                    <div className="error-details">
                      <h4>🚫 Error Found</h4>
                      <div className="error-info">
                        <p><strong>Message:</strong> {result.error.message}</p>
                        {result.error.line && <p><strong>Line:</strong> {result.error.line}</p>}
                        {result.error.fixed && <p className="fixed-msg">✨ {result.error.fix_message}</p>}
                      </div>
                    </div>
                  )}

                  {/* Corrected Code */}
                  {result.corrected_code && (
                    <div className="corrected-section">
                      <h4>🔧 Corrected Code</h4>
                      <div className="code-box corrected">
                        <pre><code>{result.corrected_code}</code></pre>
                      </div>
                    </div>
                  )}

                  {/* Improved Versions */}
                  {result.improved_versions && result.improved_versions.length > 0 && (
                    <div className="improvements">
                      <h4>🚀 Improved Versions</h4>
                      <div className="versions-grid">
                        {result.improved_versions.map((v) => (
                          <div key={v.version} className={`version-card ${v.version === result.best_version ? "best" : ""}`}>
                            <div className="version-header">
                              <span className="version-num">Version {v.version}</span>
                              {v.version === result.best_version && <span className="best-tag">⭐ Best</span>}
                            </div>
                            <div className="code-box">
                              <pre><code>{v.code}</code></pre>
                            </div>
                            <p className="version-exp">{v.explanation}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.is_valid && result.improved_versions && (
                    <div className="success-msg">
                      ✅ Your code works! Here are optimized versions.
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Right Panel - Documentation */}
            <div className="right-panel">
              <div className="doc-card">
                <div className="doc-header">
                  <span>📚</span>
                  <h3>Documentation</h3>
                </div>
                <div className="doc-content">
                  {result.documentation ? (
                    <pre className="doc-text">{result.documentation}</pre>
                  ) : (
                    <p className="doc-placeholder">Documentation will appear here...</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Welcome / How it Works */}
        {!result && !loading && (
          <div className="welcome-section">
            <div className="info-card">
              <h3>🔄 How It Works</h3>
              <div className="flow">
                <span>User Input</span> → <span>React Frontend</span> → <span>Django API</span> → <span>Gemini AI</span> → <span>Response</span>
              </div>
            </div>

            <div className="features">
              <div className="feature">
                <span className="feature-icon">💬</span>
                <h4>Ask Questions</h4>
                <p>Get explanations for any programming concept</p>
              </div>
              <div className="feature">
                <span className="feature-icon">🔍</span>
                <h4>Analyze Code</h4>
                <p>Paste code to check for errors</p>
              </div>
              <div className="feature">
                <span className="feature-icon">✨</span>
                <h4>Get Improvements</h4>
                <p>Receive optimized versions</p>
              </div>
            </div>

            <div className="examples">
              <p>Try these examples:</p>
              <div className="example-tags">
                <span onClick={() => setQuery("How to reverse a list?")}>How to reverse a list?</span>
                <span onClick={() => setQuery("for i in range(10) print(i)")}>for i in range(10) print(i)</span>
                <span onClick={() => setQuery("Explain decorators")}>Explain decorators</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        .app {
          min-height: 100vh;
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          padding: 20px;
          font-family: 'Inter', -apple-system, sans-serif;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        .header { text-align: center; margin-bottom: 24px; }
        
        .logo {
          font-size: 2rem;
          font-weight: 800;
          color: #f8fafc;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
        }
        
        .logo-icon {
          font-size: 1.5rem;
        }
        
        .tagline { color: #94a3b8; font-size: 0.9rem; }

        .search-section { margin-bottom: 24px; }

        .error-card {
          background: rgba(239,68,68,0.15);
          border: 1px solid #ef4444;
          border-radius: 12px;
          padding: 14px 18px;
          color: #fca5a5;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .main-layout {
          display: grid;
          grid-template-columns: 1fr 350px;
          gap: 20px;
        }

        .left-panel, .right-panel { display: flex; flex-direction: column; gap: 16px; }

        .result-card, .doc-card, .error-details, .corrected-section, .improvements {
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 16px;
          padding: 20px;
        }

        .result-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
        .result-header h3 { color: #f8fafc; font-size: 1.1rem; }
        .result-icon { font-size: 1.3rem; }
        
        .answer-text { color: #e2e8f0; line-height: 1.7; white-space: pre-line; }

        .code-box {
          background: #0f172a;
          border-radius: 10px;
          padding: 14px;
          overflow-x: auto;
          margin-top: 12px;
        }
        
        .code-box code {
          color: #10b981;
          font-family: 'Fira Code', monospace;
          font-size: 0.85rem;
          line-height: 1.5;
        }

        .status-badge {
          text-align: center;
          padding: 14px;
          border-radius: 12px;
          font-size: 1.1rem;
          font-weight: 600;
        }
        
        .status-badge.valid { background: rgba(16,185,129,0.15); border: 1px solid #10b981; color: #34d399; }
        .status-badge.invalid { background: rgba(239,68,68,0.15); border: 1px solid #ef4444; color: #fca5a5; }

        .error-details h4, .corrected-section h4, .improvements h4 {
          color: #f8fafc;
          font-size: 1rem;
          margin-bottom: 12px;
        }

        .error-info p { color: #fca5a5; margin-bottom: 6px; font-size: 0.9rem; }
        .fixed-msg { color: #34d399 !important; }

        .versions-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        
        .version-card {
          background: #0f172a;
          border: 2px solid #334155;
          border-radius: 12px;
          padding: 14px;
        }
        
        .version-card.best { border-color: #6366f1; }
        
        .version-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .version-num { background: #334155; color: #f8fafc; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; }
        .best-tag { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; }
        
        .version-card .code-box { margin-bottom: 10px; padding: 10px; }
        .version-card .code-box code { font-size: 0.75rem; }
        
        .version-exp { color: #94a3b8; font-size: 0.8rem; line-height: 1.4; }

        .success-msg {
          background: rgba(16,185,129,0.15);
          border: 1px solid #10b981;
          border-radius: 12px;
          padding: 14px;
          color: #34d399;
          text-align: center;
        }

        .doc-card { height: 100%; }
        .doc-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
        .doc-header h3 { color: #f8fafc; font-size: 1rem; }
        .doc-content { max-height: 500px; overflow-y: auto; }
        .doc-text { color: #94a3b8; font-size: 0.85rem; white-space: pre-wrap; line-height: 1.6; }
        .doc-placeholder { color: #64748b; font-style: italic; }

        .welcome-section { text-align: center; padding: 30px 0; }
        
        .info-card {
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 16px;
          padding: 24px;
          margin-bottom: 30px;
          display: inline-block;
        }
        
        .info-card h3 { color: #f8fafc; margin-bottom: 14px; }
        
        .flow {
          color: #94a3b8;
          font-size: 0.9rem;
        }
        
        .flow span { color: #6366f1; font-weight: 500; }

        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 30px; }
        
        .feature {
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 14px;
          padding: 20px;
        }
        
        .feature-icon { font-size: 1.8rem; display: block; margin-bottom: 10px; }
        .feature h4 { color: #f8fafc; font-size: 1rem; margin-bottom: 6px; }
        .feature p { color: #94a3b8; font-size: 0.85rem; }

        .examples p { color: #94a3b8; margin-bottom: 14px; }
        
        .example-tags { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
        
        .example-tags span {
          background: #1e293b;
          border: 1px solid #334155;
          color: #e2e8f0;
          padding: 10px 16px;
          border-radius: 20px;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.2s;
        }
        
        .example-tags span:hover { background: #334155; border-color: #6366f1; }

        @media (max-width: 900px) {
          .main-layout { grid-template-columns: 1fr; }
          .versions-grid { grid-template-columns: 1fr; }
          .features { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
}

export default Home;
