import React, { useState } from "react";
import "../css/CodeImprovement.css";

function CodeImprovement({ result }) {
  const [copied, setCopied] = useState(null);

  const handleCopy = async (code, index) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(index);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  if (!result || result.type !== "code") return null;

  return (
    <div className="code-improvement">
      {result.error && (
        <div className="error-section">
          <div className="section-header error">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <span>Error Detected</span>
          </div>
          <div className="error-message">
            <code>{result.error}</code>
          </div>
        </div>
      )}

      {result.corrected_code && (
        <div className="corrected-section">
          <div className="section-header success">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span>Corrected Code</span>
          </div>
          <div className="code-card">
            <pre><code>{result.corrected_code}</code></pre>
            <button 
              className="copy-btn"
              onClick={() => handleCopy(result.corrected_code, 'corrected')}
            >
              {copied === 'corrected' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                </svg>
              )}
            </button>
          </div>
        </div>
      )}

      {result.improved_versions && result.improved_versions.length > 0 && (
        <div className="improvements-section">
          <div className="section-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
            </svg>
            <span>Improved Versions</span>
          </div>
          <p className="improvement-intro">
            {result.explanation}
          </p>
          <div className="improvements-grid">
            {result.improved_versions.map((version) => (
              <div 
                key={version.version} 
                className={`improvement-card ${version.version === result.best_version ? 'best' : ''}`}
              >
                <div className="card-top">
                  <span className="version-label">Version {version.version}</span>
                  {version.version === result.best_version && (
                    <span className="best-badge">Recommended</span>
                  )}
                </div>
                <pre className="code-preview"><code>{version.code}</code></pre>
                <div className="explanation">
                  <strong>Why this version:</strong> {version.explanation}
                </div>
                <button 
                  className="copy-btn-small"
                  onClick={() => handleCopy(version.code, version.version)}
                >
                  {copied === version.version ? 'Copied!' : 'Copy'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CodeImprovement;
