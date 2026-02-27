import React from "react";

function SubmitButton({ onSubmit }) {
  return (
    <button onClick={onSubmit} style={{ marginTop: "10px" }}>
      Review Code
    </button>
  );
}

export default SubmitButton;