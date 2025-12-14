<h1 align="center">🧠 Cerina Protocol Foundry</h1>

<h3 align="center">
Multi-Agent Clinical Protocol Generation System<br/>
LangGraph · Human-in-the-Loop · Model Context Protocol (MCP)
</h3>

<p align="center">
  <strong>⚠️ This is NOT a chatbot.</strong><br/>
  A production-style, multi-agent clinical workflow with explicit human authority.
</p>

<hr/>

<h2>📌 Project Overview</h2>

<p>
Cerina Protocol Foundry is a multi-agent AI workflow system designed to generate
<strong>safe, structured Cognitive Behavioral Therapy (CBT) protocols</strong>
with explicit human control.
</p>

<p>
The system behaves like a <strong>clinical protocol foundry</strong>,
not a conversational assistant.
</p>

<ul>
  <li>Multiple AI agents collaborate</li>
  <li>Every step is checkpointed and persisted</li>
  <li>Humans can approve, decline, halt, or request revisions</li>
  <li>The same workflow is exposed via UI and MCP (machine-to-machine)</li>
</ul>

<hr/>

<h2>🎯 Core Goals</h2>

<ul>
  <li>Generate clinically structured CBT protocols</li>
  <li>Enforce explicit human-in-the-loop authority</li>
  <li>Prevent unsafe or autonomous retries</li>
  <li>Enable AI-to-AI interoperability via MCP</li>
  <li>Provide auditability, persistence, and crash recovery</li>
</ul>

<hr/>

<h2>🧰 Tech Stack</h2>

<h3>Backend</h3>
<ul>
  <li>Python</li>
  <li><strong>FastAPI</strong> — API layer</li>
  <li><strong>LangGraph</strong> — Multi-agent orchestration</li>
  <li><strong>SQLAlchemy + SQLite</strong> — Persistent blackboard & audit trail</li>
  <li><strong>Ollama (Llama-3 8B)</strong> — Local LLM inference</li>
</ul>

<h3>Frontend</h3>
<ul>
  <li>React</li>
  <li>TypeScript</li>
  <li><strong>Server-Sent Events (SSE)</strong> — Real-time agent streaming</li>
  <li>Tailwind CSS</li>
</ul>

<h3>Interoperability</h3>
<ul>
  <li><strong>Model Context Protocol (MCP)</strong> — Expose workflow as a reusable AI tool</li>
</ul>

<hr/>

<h2>🧩 System Architecture (High Level)</h2>

<p>
The system follows a <strong>Supervisor-style multi-agent architecture</strong>.
</p>

<table border="1" cellpadding="8" cellspacing="0">
  <tr>
    <th>Agent</th>
    <th>Responsibility</th>
  </tr>
  <tr>
    <td>Drafter Agent</td>
    <td>Generates or revises CBT protocol drafts</td>
  </tr>
  <tr>
    <td>Safety Agent</td>
    <td>Evaluates content for safety risks</td>
  </tr>
  <tr>
    <td>Clinical Critic Agent</td>
    <td>Reviews tone, empathy, and structure</td>
  </tr>
  <tr>
    <td>Supervisor Logic</td>
    <td>Decides whether to revise, halt, or finalize</td>
  </tr>
</table>

<p>
All agents operate on a <strong>shared, versioned blackboard state</strong>.
</p>

<p>
📌 <strong>Architecture Diagram:</strong><br/>
👉 <code>docs/architecture.mmd</code>
</p>

<hr/>

<h2>🗂️ Shared Blackboard (State Management)</h2>

<ul>
  <li>Draft text</li>
  <li>Safety score</li>
  <li>Empathy score</li>
  <li>Iteration count</li>
  <li>Agent notes</li>
  <li>Human decisions</li>
  <li>Finalization status</li>
</ul>

<h3>🔒 Key Rule</h3>

<p>
<strong>No agent output is ephemeral.</strong> Every step is persisted.
</p>

<ul>
  <li>Crash recovery</li>
  <li>Full audit trails</li>
  <li>Transparent human review</li>
</ul>

<hr/>

<h2>👤 Human-in-the-Loop Control (Critical)</h2>

<table border="1" cellpadding="8" cellspacing="0">
  <tr>
    <th>Action</th>
    <th>Behavior</th>
  </tr>
  <tr>
    <td>Start</td>
    <td>Begin protocol generation</td>
  </tr>
  <tr>
    <td>Approve</td>
    <td>Finalize permanently (terminal)</td>
  </tr>
  <tr>
    <td>Decline</td>
    <td>Pause system (no auto-retry)</td>
  </tr>
  <tr>
    <td>Request Revision</td>
    <td>Explicit re-run using human feedback</td>
  </tr>
  <tr>
    <td>Halt</td>
    <td>Stop execution immediately</td>
  </tr>
</table>

<h3>🔐 Safety Guarantee</h3>

<p>Once a human approves:</p>
<ul>
  <li>❌ No loop back to drafter</li>
  <li>❌ No safety re-run</li>
  <li>❌ No critic re-run</li>
</ul>

<p><strong>Human approval is final authority.</strong></p>

<hr/>

<h2>🔁 Decline vs Request Revision (Intentional Design)</h2>

<h3>Decline</h3>
<ul>
  <li>Records human decision</li>
  <li>Persists feedback</li>
  <li>Pauses execution</li>
  <li>No automatic retry</li>
</ul>

<h3>Request Revision</h3>
<ul>
  <li>Explicit human intent</li>
  <li>Pipeline resumes once</li>
  <li>Human feedback injected into state</li>
</ul>

<p>
This prevents silent retries, assumed intent, and unsafe autonomy.
</p>

<hr/>

<h2>⚡ Streaming & Performance</h2>

<ul>
  <li>LLM output is streamed token-by-token from Ollama</li>
  <li>UI displays partial drafts immediately</li>
  <li>Low perceived latency even for long generations</li>
</ul>

<hr/>

<h2>🔌 Model Context Protocol (MCP) Integration</h2>

<p>
The entire Foundry is exposed as a single MCP tool.
</p>

<p><strong>Tool Name:</strong> <code>cerina_protocol_generator</code></p>

<h3>Key Principle</h3>
<p><strong>MCP wraps a workflow, not an LLM.</strong></p>

<p>The same LangGraph pipeline is used by:</p>
<ul>
  <li>React UI</li>
  <li>MCP clients</li>
</ul>

<hr/>

<h2>🧪 Practical MCP Usage</h2>

<pre>
{
  "tool": "cerina_protocol_generator",
  "arguments": {
    "prompt": "Create a CBT thought record for social anxiety"
  }
}
</pre>

<p>
The client receives a clinically reviewed artifact without knowing internal agent logic.
</p>

<hr/>

<h2>🔗 Backend API Overview</h2>

<table border="1" cellpadding="8" cellspacing="0">
  <tr>
    <th>Endpoint</th>
    <th>Purpose</th>
  </tr>
  <tr><td>POST /start</td><td>Start protocol generation</td></tr>
  <tr><td>GET /stream/{id}</td><td>Stream agent updates</td></tr>
  <tr><td>GET /state/{id}</td><td>Fetch latest state</td></tr>
  <tr><td>POST /approve/{id}</td><td>Finalize protocol</td></tr>
  <tr><td>POST /decline/{id}</td><td>Decline and pause</td></tr>
  <tr><td>POST /rerun/{id}</td><td>Request revision</td></tr>
</table>

<hr/>

<h2>▶️ Running the Project Locally</h2>

<pre>
Backend:
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend:
cd frontend
npm install
npm run dev

Ollama:
ollama run llama3:8b
</pre>

<hr/>

<h2>🏁 Final Note</h2>

<p>
Cerina Protocol Foundry demonstrates how agentic AI systems can be:
</p>

<ul>
  <li>Autonomous without being unsafe</li>
  <li>Transparent without being complex</li>
  <li>Interoperable without duplicating logic</li>
</ul>

<p>
This project focuses on <strong>system design, control boundaries, and real-world AI workflows</strong> — not just model outputs.
</p>
