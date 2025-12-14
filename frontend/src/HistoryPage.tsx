import { useEffect, useState } from "react";
import MarkdownRenderer from "./MarkdownRenderer";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [activeDraft, setActiveDraft] = useState<any | null>(null);

  useEffect(() => {
    // Load completed history
    const stored = localStorage.getItem("cerina-history");
    if (stored) {
      setHistory(JSON.parse(stored));
    }

    // Load active (in-progress) session
    const active = localStorage.getItem("cerina-active-session");
    if (active) {
      try {
        setActiveDraft(JSON.parse(active));
      } catch {
        setActiveDraft(null);
      }
    }
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <h2 className="text-2xl font-semibold">Protocol History</h2>

      {/* 🔥 ACTIVE DRAFT */}
      {activeDraft && activeDraft.draft && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-xl shadow-sm space-y-2">
          <div className="text-sm font-semibold text-yellow-800">
            Active Draft (In Progress)
          </div>

          <div className="text-xs text-yellow-700">
            Request #{activeDraft.requestId}
          </div>

          <MarkdownRenderer content={activeDraft.draft} />
        </div>
      )}

      {/* EMPTY STATE */}
      {history.length === 0 && !activeDraft && (
        <div className="text-gray-500">
          No protocols generated yet.
        </div>
      )}

      {/* COMPLETED HISTORY */}
      {history.map((h, i) => (
        <div
          key={i}
          className="bg-white p-6 rounded-xl shadow space-y-2"
        >
          <div className="text-sm text-gray-500">
            Request #{h.requestId} •{" "}
            {new Date(h.timestamp).toLocaleString()}
          </div>

          <MarkdownRenderer content={h.draft} />
        </div>
      ))}
    </div>
  );
}
