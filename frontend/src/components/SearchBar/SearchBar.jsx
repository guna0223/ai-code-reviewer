import React from "react";
import "../css/SearchBar.css";

function SearchBar({ value, onChange, onSubmit, loading }) {
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      onSubmit();
    }
  };

  return (
    <div className="search-bar-container">
      <div className="search-input-wrapper">
        <svg
          className="search-icon"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          className="search-input"
          placeholder="Ask a question or paste Python code..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <button
          className="search-button"
          onClick={onSubmit}
          disabled={loading || !value.trim()}
        >
          {loading ? (
            <span className="loading-spinner"></span>
          ) : (
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

export default SearchBar;
