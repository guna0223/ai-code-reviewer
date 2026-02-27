import React, { useState } from "react";
import CodeEditor from "../components/CodeEditor/CodeEditor.jsx";
import SubmitButton from "../components/SubmitButton/SubmitButton.jsx";
import ReviewResult from "../components/ReviewResult/ReviewResult.jsx";
import { submitCode } from "../services/api";

function Home() {
  const [code, setCode] = useState("");
  const [review, setReview] = useState("");

  const handleSubmit = async () => {
    try {
      const response = await submitCode(code);
      setReview(response.data.review);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>AI Code Review</h1>

      <CodeEditor code={code} setCode={setCode} />

      <SubmitButton onSubmit={handleSubmit} />

      <ReviewResult review={review} />
    </div>
  );
}

export default Home;