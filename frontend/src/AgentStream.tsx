import React from "react";

type Props = {
  updates: any[];
};

export function AgentStream({ updates }: Props) {
  return (
    <div style={{ background: "#f9f9f9", padding: 16, borderRadius: 8 }}>
      <h3>Agent Activity</h3>

      {updates.map((u, i) =>
        u.notes?.map((n: any, j: number) => (
          <div
            key={`${i}-${j}`}
            style={{
              padding: "6px 0",
              borderBottom: "1px solid #eee",
              fontSize: 14,
            }}
          >
            <strong>{n.agent.toUpperCase()}</strong>: {n.message}
          </div>
        ))
      )}
    </div>
  );
}
