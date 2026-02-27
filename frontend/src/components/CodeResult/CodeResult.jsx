import React, { useState } from "react";
import ImprovedCodeCard from "../ImprovedCodeCard/ImprovedCodeCard";
import "./CodeResult.css";

function CodeResult({ result }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const handleCopy = async (code, index) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="code-result">
      {result.error && (
        <div className="error-box">
          <div className="error-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </div>
          <div className="error-content">
            <strong>Error Detected:</strong>
            <pre>{result.error}</pre>
          </div>
        </div>
      )}

      {result.corrected_code && (
        <div className="corrected-code-section">
          <h4>Corrected Code</h4>
          <div className="corrected-code-card">
            <pre><code>{result.corrected_code}</code></pre>
            <button 
              className="copy-button"
              onClick={() => handleCopy(result.corrected_code, 'corrected')}
            >
              {copiedIndex === 'corrected' ? (
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
        <div className="improved-versions-section">
          <h4>Improved Versions</h4>
          <div className="improved-versions-grid">
            {result.improved_versions.map((version) => (
              <div key={version.version} className="improved-version-wrapper">
                <ImprovedCodeCard
                  version={version.version}
                  code={version.code}
                  explanation={version.explanation}
                  isBest={version.version === result.best_version}
                  onCopy={() => handleCopy(version.code, version.version)}
                  copied={copiedIndex === version.version}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CodeResult;
