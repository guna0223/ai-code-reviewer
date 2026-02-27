import React from "react";

function ReviewResult({ review }) {
  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Review Result</h3>
      <p>{review}</p>
    </div>
  );
}

export default ReviewResult;