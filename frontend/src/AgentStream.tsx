import React from "react";

type Props = {
  updates: any[];
};

export function AgentStream({ updates }: Props) {
  return (
    <div>
      <h3>Agent Stream</h3>
      {updates.map((u, i) => (
        <pre key={i}>{JSON.stringify(u.notes, null, 2)}</pre>
      ))}
    </div>
  );
}
