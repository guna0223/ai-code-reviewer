import React from "react";

function CodeEditor({ code, setCode }) {
  return (
    <div>
      <textarea
        rows="12"
        cols="70"
        placeholder="Write Python code here..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
    </div>
  );
}

export default CodeEditor;