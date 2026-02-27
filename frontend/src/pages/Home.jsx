import React, { useState } from "react";
import SearchBar from "../components/SearchBar/SearchBar";
import ChatMessage from "../components/ChatMessage/ChatMessage";
import CodeImprovement from "../components/CodeImprovement/CodeImprovement";
import DocumentationPanel from "../components/DocumentationPanel/DocumentationPanel";
import LoadingSpinner from "../components/LoadingSpinner/LoadingSpinner";
import { analyzeInput } from "../services/api";

function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [currentResult, setCurrentResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    const userMessage = query;
    setQuery("");
    setLoading(true);
    setError(null);

    setMessages((prev) => [
      ...prev,
      { type: "user", content: userMessage },
    ]);

    try {
      const response = await analyzeInput(userMessage);
      const result = response.data;
      
      setCurrentResult(result);
      
      if (result.type === "code") {
        let aiContent = result.error 
          ? `Error detected: ${result.error}\n\nI've generated corrected and improved versions.`
          : "I've analyzed your code and generated 3 improved versions with detailed explanations.";
        
        setMessages((prev) => [
          ...prev,
          { type: "ai", content: aiContent, isCode: true },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { type: "ai", content: result.answer, exampleCode: result.example_code },
        ]);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to process your request. Please try again.");
      setMessages((prev) => [
        ...prev,
        { type: "ai", content: "I apologize, but I encountered an error processing your request. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>AI Code Review</h1>
        <p className="subtitle">
          Ask questions or paste code for intelligent analysis
        </p>
      </header>

      <div className="search-container">
        <SearchBar
          value={query}
          onChange={setQuery}
          onSubmit={handleSubmit}
          loading={loading}
        />
      </div>

      <div className="main-content">
        <div className="left-panel">
          <div className="chat-container">
            {messages.length === 0 && (
              <div className="welcome-message">
                <div className="welcome-icon">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                </div>
                <h2>Welcome to AI Code Review</h2>
                <p>Your intelligent programming assistant</p>
                <div className="example-queries">
                  <p>Try asking:</p>
                  <ul>
                    <li>"How to reverse a list in Python?"</li>
                    <li>"Explain Python decorators"</li>
                    <li>"What is list comprehension?"</li>
                    <li>Or paste any Python code</li>
                  </ul>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div key={index}>
                <ChatMessage
                  type={message.isCode ? "code" : "text"}
                  content={message.content}
                  isUser={message.type === "user"}
                />
                {message.exampleCode && (
                  <div className="example-code-block">
                    <pre><code>{message.exampleCode}</code></pre>
                  </div>
                )}
              </div>
            ))}

            {loading && <LoadingSpinner />}

            {error && <div className="error-message">{error}</div>}

            {currentResult && currentResult.type === "code" && (
              <CodeImprovement result={currentResult} />
            )}
          </div>
        </div>

        <div className="right-panel">
          <DocumentationPanel
            documentation={currentResult?.documentation || ""}
          />
        </div>
      </div>

      <style>{`
        .home-container {
          min-height: 100vh;
          background: #0f172a;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .home-header {
          text-align: center;
          margin-bottom: 20px;
        }

        .home-header h1 {
          color: #f1f5f9;
          font-size: 32px;
          font-weight: 700;
          margin: 0 0 8px;
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .subtitle {
          color: #94a3b8;
          font-size: 15px;
          margin: 0;
        }

        .search-container {
          max-width: 800px;
          margin: 0 auto 20px;
        }

        .main-content {
          display: grid;
          grid-template-columns: 1fr 380px;
          gap: 20px;
          max-width: 1400px;
          margin: 0 auto;
          height: calc(100vh - 180px);
        }

        .left-panel {
          background: #1e293b;
          border-radius: 16px;
          border: 1px solid #334155;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .chat-container {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
        }

        .welcome-message {
          text-align: center;
          padding: 50px 20px;
          color: #94a3b8;
        }

        .welcome-icon {
          color: #6366f1;
          margin-bottom: 16px;
        }

        .welcome-message h2 {
          color: #f1f5f9;
          font-size: 22px;
          margin: 0 0 8px;
        }

        .welcome-message p {
          font-size: 15px;
          margin: 0 0 20px;
        }

        .example-queries {
          text-align: left;
          max-width: 280px;
          margin: 0 auto;
          background: #0f172a;
          border-radius: 12px;
          padding: 16px;
        }

        .example-queries p {
          margin: 0 0 10px;
          font-weight: 600;
          color: #f1f5f9;
        }

        .example-queries ul {
          margin: 0;
          padding-left: 18px;
        }

        .example-queries li {
          margin-bottom: 8px;
          font-size: 13px;
        }

        .example-code-block {
          background: #0f172a;
          border-radius: 8px;
          margin: -8px 16px 16px;
          overflow-x: auto;
        }

        .example-code-block pre {
          margin: 0;
          padding: 14px;
        }

        .example-code-block code {
          font-family: 'Fira Code', 'Consolas', monospace;
          font-size: 12px;
          color: #10b981;
        }

        .error-message {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid #ef4444;
          color: #fca5a5;
          padding: 12px 16px;
          border-radius: 8px;
          margin: 12px 0;
        }

        .right-panel {
          height: 100%;
        }

        @media (max-width: 1024px) {
          .main-content {
            grid-template-columns: 1fr;
            height: auto;
          }

          .right-panel {
            height: 400px;
          }

          .left-panel {
            min-height: 450px;
          }
        }
      `}</style>
    </div>
  );
}

export default Home;
