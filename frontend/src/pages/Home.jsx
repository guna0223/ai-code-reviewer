import React, { useState } from "react";
import SearchBar from "../components/SearchBar/SearchBar";
import LoadingSpinner from "../components/LoadingSpinner/LoadingSpinner";
import { analyzeInput } from "../services/api";
import "../components/css/Home.css";

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
      setError("Connection failed. Please check your API key.");
    } finally {
      setLoading(false);
    }
  };

  // Render greeting type
  const renderGreeting = () => (
    <div className="greeting-card">
      <div className="greeting-icon">👋</div>
      <p className="greeting-text">{result.answer}</p>
    </div>
  );

  // Render general knowledge type
  const renderGeneral = () => (
    <div className="general-card">
      <div className="section-title">
        <span className="icon">💭</span>
        <h2>Answer</h2>
      </div>
      <div className="content-card">
        <p className="explanation">{result.answer}</p>
      </div>
    </div>
  );

  // Render programming question type
  const renderProgramming = () => (
    <div className="programming-card">
      <div className="section-title">
        <span className="icon">💡</span>
        <h2>Explanation</h2>
      </div>
      <div className="content-card">
        <p className="explanation">{result.answer}</p>
      </div>
      {result.example_code && (
        <div className="code-section">
          <div className="section-title">
            <span className="icon">📝</span>
            <h3>Example Code</h3>
          </div>
          <div className="code-card">
            <pre><code>{result.example_code}</code></pre>
          </div>
        </div>
      )}
    </div>
  );

  // Render code analysis type
  const renderCode = () => (
    <div className="code-analysis">
      <div className={`status-pill ${result.is_valid ? "valid" : "invalid"}`}>
        {result.is_valid ? (result.answer ? "✨ Generated Code" : "✅ Code is Correct") : "❌ Code has Errors"}
      </div>

      {result.answer && (
        <div className="answer-section">
          <div className="content-card">
            <p className="explanation">{result.answer}</p>
          </div>
        </div>
      )}

      {!result.is_valid && result.error && (
        <div className="error-card">
          <div className="error-title">
            <span>🚫</span> Error Detected
          </div>
          <div className="error-body">
            <div className="error-item">
              <span className="label">Message:</span>
              <span className="value error-text">{result.error.message}</span>
            </div>
            {result.error.line && (
              <div className="error-item">
                <span className="label">Line:</span>
                <span className="value">{result.error.line}</span>
              </div>
            )}
            {result.error.fixed && (
              <div className="fix-badge">✨ {result.error.fix_message}</div>
            )}
          </div>
        </div>
      )}

      {result.corrected_code && (
        <div className="corrected-section">
          <div className="section-title">
            <span className="icon">🔧</span>
            <h3>Corrected Code</h3>
          </div>
          <div className="code-card corrected">
            <pre><code>{result.corrected_code}</code></pre>
          </div>
        </div>
      )}

      {result.output && (
        <div className="output-section">
          <div className="section-title">
            <span className="icon">📤</span>
            <h3>Output</h3>
          </div>
          <div className="output-card">
            <pre><code>{result.output}</code></pre>
          </div>
        </div>
      )}

      {result.improved_versions && result.improved_versions.length > 0 && (
        <div className="improvements-section">
          <div className="section-title">
            <span className="icon">🚀</span>
            <h3>Improved Versions</h3>
          </div>
          <div className="versions-stack">
            {result.improved_versions.map((v) => (
              <div key={v.version} className={`version-card ${v.version === result.best_version ? "best" : ""}`}>
                <div className="version-bar">
                  <span className="version-label">Version {v.version}</span>
                  {v.version === result.best_version && <span className="best-badge">⭐ Best</span>}
                </div>
                <div className="version-code">
                  <pre><code>{v.code}</code></pre>
                </div>
                <div className="version-expl">{v.explanation}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.is_valid && result.improved_versions && (
        <div className="success-note">
          ✅ Your code works! Check out the optimized versions above.
        </div>
      )}
    </div>
  );

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="logo-area">
            <div className="logo-icon">⚡</div>
            <div className="logo-text">
              <h1>AI Code Assistant</h1>
              <p>Powered by Gemini AI</p>
            </div>
          </div>
        </header>

        {/* Search */}
        <div className="search-wrapper">
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
          <div className="error-toast">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="results-wrapper">
            {/* Left Panel */}
            <div className="left-col">
              {result.type === "greeting" && renderGreeting()}
              {result.type === "general" && renderGeneral()}
              {result.type === "programming" && renderProgramming()}
              {result.type === "code" && renderCode()}
            </div>

            {/* Right Panel - Documentation */}
            <div className="right-col">
              {result.documentation && (
                <div className="documentation-panel">
                  <div className="doc-header">
                    <span className="doc-icon">📚</span>
                    <h3>Documentation</h3>
                  </div>
                  <div className="doc-content">
                    <div 
                      className="markdown-body"
                      dangerouslySetInnerHTML={{ 
                        __html: result.documentation
                          .replace(/```python\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                          .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                          .replace(/## (.*)/g, '<h2>$1</h2>')
                          .replace(/### (.*)/g, '<h3>$1</h3>')
                          .replace(/\n\n/g, '</p><p>')
                          .replace(/- (.*)/g, '<li>$1</li>')
                          .replace(/^(.*)$/g, (match) => {
                            if (match.startsWith('<')) return match;
                            return `<p>${match}</p>`;
                          })
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
