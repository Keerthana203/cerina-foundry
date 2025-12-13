const API_BASE = "http://127.0.0.1:8000";

export function startProtocol(intent: string) {
  return fetch(`${API_BASE}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ intent }),
  }).then(res => res.json());
}

export function streamProtocol(
  requestId: number,
  onMessage: (data: any) => void
) {
  const eventSource = new EventSource(`${API_BASE}/stream/${requestId}`);
  eventSource.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };
  return eventSource;
}

export function approveProtocol(requestId: number, finalText: string) {
  return fetch(`${API_BASE}/approve/${requestId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ final_text: finalText }),
  });
}
