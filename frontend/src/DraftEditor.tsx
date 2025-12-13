import React from "react";

type Props = {
  text: string;
  onChange: (t: string) => void;
};

export function DraftEditor({ text, onChange }: Props) {
  return (
    <div>
      <h3>Draft</h3>
      <textarea
        rows={10}
        cols={80}
        value={text}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
