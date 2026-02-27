import React, { useState } from "react";
import SearchBar from "../components/SearchBar/SearchBar";
import ChatMessage from "../components/ChatMessage/ChatMessage";
import CodeResult from "../components/CodeResult/CodeResult";
import DocumentationPanel from "../components/DocumentationPanel/DocumentationPanel";
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

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      { type: "user", content: userMessage },
    ]);

    try {
      const response = await analyzeInput(userMessage);
      const result = response.data;
      
      setCurrentResult(result);
      
      // Add AI response to chat
      if (result.type === "code") {
        let aiContent = "";
        if (result.error) {
          aiContent = `I detected an error in your code: ${result.error}\n\nHere's the corrected version:\n${result.corrected_code}`;
        } else {
          aiContent = `I've analyzed your code and generated 3 improved versions. The best version is Version ${result.best_version}.`;
        }
        setMessages((prev) => [
          ...prev,
          { type: "ai", content: aiContent, isCode: true },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { type: "ai", content: "Here's the explanation and documentation:" },
        ]);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to process your request. Please try again.");
      setMessages((prev) => [
        ...prev,
        { type: "ai", content: "Sorry, I encountered an error processing your request." },
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
          Ask questions or paste Python code for AI-powered analysis
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
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                </div>
                <h2>Welcome to AI Code Review</h2>
                <p>Ask me anything about Python programming or paste your code for analysis.</p>
                <div className="example-queries">
                  <p>Try these examples:</p>
                  <ul>
                    <li>"Explain Python decorators"</li>
                    <li>"What is list comprehension?"</li>
                    <li>Paste Python code for improvement</li>
                  </ul>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                type={message.isCode ? "code" : "text"}
                content={message.content}
                isUser={message.type === "user"}
              />
            ))}

            {loading && (
              <div className="loading-indicator">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}

            {currentResult && currentResult.type === "code" && (
              <CodeResult result={currentResult} />
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
          padding: 24px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .home-header {
          text-align: center;
          margin-bottom: 24px;
        }

        .home-header h1 {
          color: #f1f5f9;
          font-size: 36px;
          font-weight: 700;
          margin: 0 0 8px;
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .subtitle {
          color: #94a3b8;
          font-size: 16px;
          margin: 0;
        }

        .search-container {
          max-width: 800px;
          margin: 0 auto 24px;
        }

        .main-content {
          display: grid;
          grid-template-columns: 1fr 400px;
          gap: 24px;
          max-width: 1400px;
          margin: 0 auto;
          height: calc(100vh - 200px);
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
          padding: 60px 20px;
          color: #94a3b8;
        }

        .welcome-icon {
          color: #6366f1;
          margin-bottom: 20px;
        }

        .welcome-message h2 {
          color: #f1f5f9;
          font-size: 24px;
          margin: 0 0 12px;
        }

        .welcome-message p {
          font-size: 16px;
          margin: 0 0 24px;
        }

        .example-queries {
          text-align: left;
          max-width: 300px;
          margin: 0 auto;
          background: #0f172a;
          border-radius: 12px;
          padding: 20px;
        }

        .example-queries p {
          margin: 0 0 12px;
          font-weight: 600;
          color: #f1f5f9;
        }

        .example-queries ul {
          margin: 0;
          padding-left: 20px;
        }

        .example-queries li {
          margin-bottom: 8px;
          font-size: 14px;
        }

        .loading-indicator {
          display: flex;
          gap: 8px;
          padding: 16px;
          justify-content: center;
        }

        .loading-dot {
          width: 10px;
          height: 10px;
          background: #6366f1;
          border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out both;
        }

        .loading-dot:nth-child(1) { animation-delay: -0.32s; }
        .loading-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        .error-message {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid #ef4444;
          color: #fca5a5;
          padding: 12px 20px;
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
            min-height: 500px;
          }
        }
      `}</style>
    </div>
  );
}

export default Home;
