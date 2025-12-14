import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  content: string;
};

export default function MarkdownRenderer({ content }: Props) {
  return (
    <div
      style={{
        lineHeight: 1.6,
        fontSize: 15,
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 style={{ fontSize: 22, marginBottom: 12 }}>{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 style={{ fontSize: 18, marginTop: 20 }}>{children}</h2>
          ),
          strong: ({ children }) => (
            <strong style={{ fontWeight: 600 }}>{children}</strong>
          ),
          ul: ({ children }) => (
            <ul style={{ paddingLeft: 20 }}>{children}</ul>
          ),
          li: ({ children }) => (
            <li style={{ marginBottom: 6 }}>{children}</li>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
