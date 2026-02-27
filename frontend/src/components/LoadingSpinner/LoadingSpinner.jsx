import React from "react";


function LoadingSpinner({ size = "medium" }) {
  return (
    <div className={`loading-spinner-container ${size}`}>
      <div className="spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </div>
      <span className="loading-text">Analyzing...</span>
    </div>
  );
}

export default LoadingSpinner;
