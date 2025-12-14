import { useEffect, useRef, useState } from "react";
import {
  startProtocol,
  streamProtocol,
  approveProtocol,
  declineProtocol,
  rerunProtocol,
} from "./api";
import AgentTimeline from "./AgentTimeline";

type ActiveSession = {
  requestId: number;
  intent: string;
  draft: string;
  updates: any[];
};

export default function SubmitPage() {
  const [intent, setIntent] = useState("");
  const [requestId, setRequestId] = useState<number | null>(null);
  const [updates, setUpdates] = useState<any[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [reviewNote, setReviewNote] = useState("");

  const eventSourceRef = useRef<EventSource | null>(null);

  // ---------------- RESTORE ACTIVE SESSION ----------------
  useEffect(() => {
    const saved = localStorage.getItem("cerina-active-session");
    if (saved) {
      const parsed: ActiveSession = JSON.parse(saved);
      setRequestId(parsed.requestId);
      setIntent(parsed.intent);
      setDraft(parsed.draft);
      setUpdates(parsed.updates || []);
    }
  }, []);

  // ---------------- PERSIST ACTIVE SESSION ----------------
  const persistSession = (
    next: Partial<ActiveSession> & { requestId: number }
  ) => {
    const payload: ActiveSession = {
      requestId: next.requestId,
      intent: next.intent ?? intent,
      draft: next.draft ?? draft,
      updates: next.updates ?? updates,
    };
    localStorage.setItem("cerina-active-session", JSON.stringify(payload));
  };

  // ---------------- START ----------------
  const start = async () => {
    if (!intent.trim() || loading) return;

    setLoading(true);
    setDraft("");
    setUpdates([]);
    setReviewNote("");

    eventSourceRef.current?.close();
    eventSourceRef.current = null;

    const res = await startProtocol(intent);
    setRequestId(res.request_id);

    persistSession({
      requestId: res.request_id,
      intent,
      draft: "",
      updates: [],
    });

    const es = streamProtocol(res.request_id, (data) => {
      setDraft(data.draft_text);
      setUpdates((prev) => {
        const next = [...prev, data];
        persistSession({
          requestId: res.request_id,
          draft: data.draft_text,
          updates: next,
        });
        return next;
      });

      setLoading(false);

      if (data.finalized) {
        es.close();
        eventSourceRef.current = null;

        const history = JSON.parse(
          localStorage.getItem("cerina-history") || "[]"
        );

        localStorage.setItem(
          "cerina-history",
          JSON.stringify([
            {
              requestId: res.request_id,
              draft: data.draft_text,
              timestamp: new Date().toISOString(),
            },
            ...history,
          ])
        );
      }
    });

    eventSourceRef.current = es;
  };

  // ---------------- APPROVE ----------------
  const approve = async () => {
    if (!requestId) return;

    await approveProtocol(requestId, draft);

    cleanupTerminal();
    alert("Protocol approved");
  };

  // ---------------- DECLINE ----------------
  const decline = async () => {
    if (!requestId || !reviewNote.trim()) return;

    await declineProtocol(requestId, reviewNote);

    cleanupTerminal();
    alert("Protocol declined");
  };

  // ---------------- RERUN ----------------
  const rerun = async () => {
    if (!requestId || !reviewNote.trim()) return;

    eventSourceRef.current?.close();
    eventSourceRef.current = null;

    setLoading(true);
    setDraft("");
    setUpdates([]);

    await rerunProtocol(requestId, reviewNote);
    setReviewNote("");

    const es = streamProtocol(requestId, (data) => {
      setDraft(data.draft_text);
      setUpdates((prev) => {
        const next = [...prev, data];
        persistSession({
          requestId,
          draft: data.draft_text,
          updates: next,
        });
        return next;
      });

      setLoading(false);

      if (data.finalized) {
        es.close();
        eventSourceRef.current = null;
      }
    });

    eventSourceRef.current = es;
  };

  // ---------------- TERMINAL CLEANUP ----------------
  const cleanupTerminal = () => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;

    localStorage.removeItem("cerina-active-session");

    setIntent("");
    setRequestId(null);
    setDraft("");
    setUpdates([]);
    setReviewNote("");
    setLoading(false);
  };

  // ---------------- UI ----------------
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h1 className="text-2xl font-semibold mb-1">
          Cerina Protocol Foundry
        </h1>
        <p className="text-gray-600 text-sm">
          Multi-agent CBT protocol generation with human-in-the-loop control
        </p>
      </div>

      {/* Intent Input */}
      <div className="bg-white p-6 rounded-xl shadow space-y-3">
        <label className="font-medium">Protocol Intent</label>
        <div className="flex gap-2">
          <input
            disabled={!!requestId}
            className="flex-1 border rounded-lg px-4 py-2 disabled:bg-gray-100"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="Create an exposure hierarchy for agoraphobia…"
          />
          <button
            onClick={start}
            disabled={loading || !!requestId}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          >
            Start
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="animate-pulse bg-white p-6 rounded-xl shadow">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
          <div className="h-3 bg-gray-200 rounded mb-2" />
          <div className="h-3 bg-gray-200 rounded mb-2" />
          <div className="h-3 bg-gray-200 rounded w-2/3" />
        </div>
      )}

      {/* Main Content */}
      {draft && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <AgentTimeline updates={updates} />
          </div>

          <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow">
            <h3 className="font-semibold mb-4">Draft (Editable)</h3>
            <textarea
              value={draft}
              onChange={(e) => {
                setDraft(e.target.value);
                if (requestId) {
                  persistSession({
                    requestId,
                    draft: e.target.value,
                  });
                }
              }}
              className="w-full min-h-[400px] border rounded-lg p-4 font-mono text-sm"
            />
          </div>
        </div>
      )}

      {/* Human Review */}
      {requestId && !loading && (
        <div className="bg-white p-6 rounded-xl shadow space-y-4">
          <h3 className="font-semibold">Human Review</h3>

          <textarea
            rows={3}
            className="w-full border rounded-lg p-3"
            placeholder="Required for Decline / Request Revision"
            value={reviewNote}
            onChange={(e) => setReviewNote(e.target.value)}
          />

          <div className="flex gap-3">
            <button
              onClick={approve}
              className="bg-green-600 text-white px-4 py-2 rounded-lg"
            >
              Approve
            </button>

            <button
              onClick={decline}
              disabled={!reviewNote}
              className="bg-red-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
            >
              Decline
            </button>

            <button
              onClick={rerun}
              disabled={!reviewNote}
              className="bg-yellow-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
            >
              Request Revision
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
