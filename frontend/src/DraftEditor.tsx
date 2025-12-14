import React from "react";
import ReactMarkdown from "react-markdown";

type Props = {
  text: string;
  editable?: boolean;
  onChange?: (t: string) => void;
};

export function DraftEditor({ text, editable = false, onChange }: Props) {
  return (
    <div>
      <h3>Draft</h3>

      {editable ? (
        <textarea
          style={{ width: "100%", height: 400 }}
          value={text}
          onChange={(e) => onChange?.(e.target.value)}
        />
      ) : (
        <div
          style={{
            padding: 16,
            border: "1px solid #ccc",
            borderRadius: 6,
            background: "#fafafa",
            maxHeight: 400,
            overflowY: "auto",
          }}
        >
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
