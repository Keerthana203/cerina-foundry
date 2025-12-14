import React from "react";
import { useState } from "react";

export default function AgentTimeline({ updates }: { updates: any[] }) {
  const [open, setOpen] = useState(true);

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <button
        onClick={() => setOpen(!open)}
        className="font-semibold text-sm mb-2"
      >
        Agent Activity {open ? "▼" : "▶"}
      </button>

      {open && (
        <div className="space-y-3 text-sm">
          {updates.flatMap((u) =>
            u.notes?.map((n: any, i: number) => (
              <div
                key={i}
                className="border-l-4 border-indigo-500 pl-3"
              >
                <div className="font-medium uppercase text-xs">
                  {n.agent}
                </div>
                <div className="text-gray-700">{n.message}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
