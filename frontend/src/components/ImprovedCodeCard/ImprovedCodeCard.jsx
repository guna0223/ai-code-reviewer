import React from "react";
import "./ImprovedCodeCard.css";

function ImprovedCodeCard({ version, code, explanation, isBest, onCopy, copied }) {
  return (
    <div className={`improved-code-card ${isBest ? "best-version" : ""}`}>
      <div className="card-header">
        <span className="version-badge">Version {version}</span>
        {isBest && <span className="best-badge">⭐ Best</span>}
        {onCopy && (
          <button className="copy-btn" onClick={onCopy} title="Copy code">
            {copied ? (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
              </svg>
            )}
          </button>
        )}
      </div>
      <pre className="code-block">
        <code>{code}</code>
      </pre>
      <div className="explanation">
        <strong>Explanation:</strong> {explanation}
      </div>
    </div>
  );
}

export default ImprovedCodeCard;
