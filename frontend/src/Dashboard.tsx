import React, { useState } from "react";
import { startProtocol, streamProtocol, approveProtocol } from "./api";
import { AgentStream } from "./AgentStream";
import { DraftEditor } from "./DraftEditor";

export default function Dashboard() {
  const [intent, setIntent] = useState("");
  const [requestId, setRequestId] = useState<number | null>(null);
  const [updates, setUpdates] = useState<any[]>([]);
  const [draft, setDraft] = useState("");

  const start = async () => {
    const res = await startProtocol(intent);
    setRequestId(res.request_id);

    streamProtocol(res.request_id, (data) => {
      setUpdates((u) => [...u, data]);
      setDraft(data.draft_text);
    });
  };

  const approve = async () => {
    if (!requestId) return;
    await approveProtocol(requestId, draft);
    alert("Approved");
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Cerina Protocol Foundry</h2>

      <input
        value={intent}
        onChange={(e) => setIntent(e.target.value)}
        placeholder="Enter protocol intent"
      />
      <button onClick={start}>Start</button>

      <DraftEditor text={draft} onChange={setDraft} />
      <button onClick={approve}>Approve</button>

      <AgentStream updates={updates} />
    </div>
  );
}
