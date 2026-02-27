import React from "react";
import "../css/DocumentationPanel.css";

function DocumentationPanel({ documentation }) {
  const formatMarkdown = (text) => {
    if (!text) return null;

    const lines = text.split('\n');
    const elements = [];
    let inCodeBlock = false;
    let codeContent = [];
    let codeLanguage = '';
    let listItems = [];
    let inList = false;

    lines.forEach((line, index) => {
      // Code blocks
      if (line.startsWith('```')) {
        if (!inCodeBlock) {
          inCodeBlock = true;
          codeLanguage = line.slice(3).trim();
          codeContent = [];
        } else {
          elements.push(
            <pre key={`code-${index}`} className="doc-code-block">
              <code>{codeContent.join('\n')}</code>
            </pre>
          );
          inCodeBlock = false;
          codeContent = [];
        }
        return;
      }

      if (inCodeBlock) {
        codeContent.push(line);
        return;
      }

      // Headers
      if (line.startsWith('## ')) {
        if (inList) {
          elements.push(<ul key={`list-${index}`}>{listItems}</ul>);
          listItems = [];
          inList = false;
        }
        elements.push(<h3 key={index} className="doc-h3">{line.slice(3)}</h3>);
        return;
      }

      if (line.startsWith('### ')) {
        if (inList) {
          elements.push(<ul key={`list-${index}`}>{listItems}</ul>);
          listItems = [];
          inList = false;
        }
        elements.push(<h4 key={index} className="doc-h4">{line.slice(4)}</h4>);
        return;
      }

      // List items
      if (line.startsWith('- ') || line.match(/^\d+\.\s/)) {
        inList = true;
        listItems.push(<li key={index} className="doc-li">{formatInlineCode(line.replace(/^[-\d.]+\s/, ''))}</li>);
        return;
      }

      // Empty line
      if (line.trim() === '') {
        if (inList) {
          elements.push(<ul key={`list-${index}`}>{listItems}</ul>);
          listItems = [];
          inList = false;
        }
        return;
      }

      // Regular text
      if (inList) {
        elements.push(<ul key={`list-${index}`}>{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<p key={index} className="doc-p">{formatInlineCode(line)}</p>);
    });

    if (inList) {
      elements.push(<ul key="list-end">{listItems}</ul>);
    }

    return elements;
  };

  const formatInlineCode = (text) => {
    const parts = text.split(/(`[^`]+`)/g);
    return parts.map((part, index) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={index} className="doc-inline-code">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return (
    <div className="documentation-panel">
      <div className="doc-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
        <span>Documentation</span>
      </div>
      <div className="doc-content">
        {documentation ? (
          formatMarkdown(documentation)
        ) : (
          <p className="doc-placeholder">
            Documentation will appear here after you ask a question or paste code.
          </p>
        )}
      </div>
    </div>
  );
}

export default DocumentationPanel;
