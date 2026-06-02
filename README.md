# GONI Cognitive OS

**GONI Cognitive OS** is an experimental multimodal desktop-agent architecture: a local-first cognitive workspace layer that can perceive screen context, reason over user intent, build visual artifacts, and execute bounded software actions through explicit approval gates.

The project explores a practical path toward a **Copilot Vision-style assistant** combined with a lightweight agentic execution loop.

> **See. Understand. Build. Operate.**

---

## Concept

Modern AI assistants are usually separated from the operating environment. They can answer questions, but they do not naturally know what the user is looking at, what file is open, what error is visible, or how the current task is evolving across applications.

GONI Cognitive OS is designed as a user-space cognitive layer above the desktop:

```text
screen / files / browser / code / voice
        ↓
perception engine
        ↓
semantic context model
        ↓
agentic reasoning layer
        ↓
canvas + memory + safe tool execution
```

The system is not intended to replace the operating system. It is an AI-native coordination layer that observes the current work context and helps the user learn, build, explain, structure, and operate software.

---

## Core Architecture

The first implementation follows a strict **PERCEIVE → DECIDE → ACT → VERIFY → REMEMBER** loop.

```text
USER
  ↓
PERCEIVE
screen capture • OCR • UI parsing • active-window context
  ↓
DECIDE
intent detection • ambiguity handling • planning • tool-call selection
  ↓
ACT
canvas updates • browser automation • file operations • controlled shell commands
  ↓
VERIFY
screenshot diff • state check • semantic output validation
  ↓
REMEMBER
action log • project memory • learned facts • user preferences
```

---

## Technical Goals

1. **Screen-aware assistance**
   Understand the current screen, visible text, UI elements, code, errors, documents, and browser state.

2. **Contextual dialogue**
   Let the user ask questions like “What does this line do?”, “Why is this error happening?”, or “Turn this page into a mind map” without manually copying context.

3. **Canvas-based cognition**
   Externalize reasoning into a visible workspace: mind maps, flowcharts, study notes, diagrams, architecture maps, and task plans.

4. **Safe bounded execution**
   Operate through allowlisted tools, approval gates, action logs, and reversible workflows.

5. **Incremental agentic behavior**
   Gradually support clarification, replanning, semantic verification, long-term memory, and skill learning.

---

## Planned Open-Source Stack

### Perception Layer

| Capability     | Candidate Tools                  |
| -------------- | -------------------------------- |
| Screen capture | `mss`, `DXcam`                   |
| Image diffing  | `OpenCV`                         |
| OCR            | `PaddleOCR`, `Tesseract`         |
| UI parsing     | `OmniParser`, accessibility APIs |
| Voice input    | `whisper.cpp`                    |
| Gesture input  | `MediaPipe`, `OpenCV`            |

### Reasoning Layer

| Capability                      | Candidate Tools                             |
| ------------------------------- | ------------------------------------------- |
| LLM / VLM brain                 | OpenAI Responses API, local VLMs via Ollama |
| Tool calling                    | JSON tool calls, function calling           |
| Local orchestration             | `FastAPI`, async Python state machine       |
| Optional advanced orchestration | LangGraph, MCP                              |

### Execution Layer

| Capability      | Candidate Tools                               |
| --------------- | --------------------------------------------- |
| Browser control | Playwright, browser-use                       |
| Desktop control | PyAutoGUI, pywinauto                          |
| Shell execution | PowerShell with allowlists                    |
| File generation | `python-docx`, `python-pptx`, Markdown export |
| Code workspace  | VS Code / file-system integration             |

### Memory Layer

| Capability                | Candidate Tools         |
| ------------------------- | ----------------------- |
| Action log                | SQLite                  |
| Project facts             | SQLite key-value table  |
| Long-term semantic memory | Qdrant, Chroma, LanceDB |
| Screen/audio memory       | screenpipe              |

### Interface Layer

| Capability                | Candidate Tools                   |
| ------------------------- | --------------------------------- |
| Desktop shell             | Tauri or Electron                 |
| Canvas                    | React Flow, Mermaid               |
| API bridge                | FastAPI + WebSockets              |
| Overlay / highlight layer | Tauri/Electron transparent window |

---

## Vision API Strategy

GONI Cognitive OS should build its Copilot Vision-style capability as a local perception engine plus an AI vision/reasoning API. The default runtime direction is `mss`/`DXcam`, OpenCV, PaddleOCR, OmniParser or Windows UI Automation, FastAPI, SQLite, and OpenAI Responses API for vision, reasoning, and structured tool calls.

See [Vision API Strategy](docs/vision-api-strategy.md) for the API decision notes, alternatives, safety posture, and V1 vision-only workflow.

---

## MVP Scope

The first build should stay intentionally small.

### Version 0.1

```text
screen capture
→ frame diff
→ OCR on meaningful changes
→ visible context string
→ chat command
→ LLM response
→ canvas node creation
→ SQLite action log
```

Initial target features:

* Capture the current screen.
* Detect meaningful screen changes.
* Extract visible text from the screen.
* Answer questions about the current screen.
* Add explanations, concepts, or summaries to a visual canvas.
* Log all user commands, tool calls, and results.

### Version 0.2

* Highlight relevant screen regions.
* Explain selected code lines.
* Summarize browser pages and PDFs.
* Generate mind maps from visible content.
* Export canvas content as Markdown or PPTX.

### Version 0.3

* Add browser automation via Playwright.
* Add safe file operations inside a scoped workspace.
* Add approval gates for clicks, typing, shell commands, and file writes.
* Add screenshot-before/screenshot-after verification.

### Version 0.4

* Add episodic memory.
* Add tutoring mode.
* Add quiz generation from observed context.
* Add user preference memory.
* Add workflow templates / learned skills.

---

## Suggested Repository Structure

```text
goni-cognitive-os/
├── perceive/
│   ├── screen.py
│   ├── ocr.py
│   ├── ui_parse.py
│   └── voice.py
│
├── decide/
│   ├── orchestrator.py
│   ├── planner.py
│   ├── prompts.py
│   └── policy.py
│
├── act/
│   ├── canvas.py
│   ├── browser.py
│   ├── desktop.py
│   ├── files.py
│   └── shell.py
│
├── verify/
│   ├── screenshot_diff.py
│   └── semantic_check.py
│
├── memory/
│   ├── sqlite_mem.py
│   └── schema.sql
│
├── canvas/
│   └── frontend/
│
├── config.py
├── main.py
└── README.md
```

---

## Minimal SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    user_input TEXT,
    screen_context TEXT,
    planned_tool TEXT,
    planned_params TEXT,
    approved INTEGER,
    result TEXT,
    screenshot_before TEXT,
    screenshot_after TEXT
);

CREATE TABLE IF NOT EXISTS facts (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
```

---

## Tool Safety Model

GONI Cognitive OS should treat all actions as capability-bound tool calls.

```text
safe:
  - canvas.add_node
  - canvas.add_edge
  - memory.save_fact

approval_required:
  - mouse.click
  - keyboard.type
  - browser.submit_form
  - files.write

dangerous:
  - shell.run
  - files.delete
  - git.push
  - email.send
```

Execution principles:

* Every action is logged.
* Risky tools require explicit user approval.
* Shell commands are allowlisted.
* File operations are scoped to a project workspace.
* Before/after screenshots are captured for UI actions.
* The system prefers previews, drafts, and branches over destructive edits.

---

## Example Interaction

```text
User: What am I looking at?

Agent:
You are viewing a C source file in VS Code. The visible function allocates memory,
passes a pointer into a helper function, and then frees it. The terminal shows a
segmentation fault, likely caused by dereferencing an invalid pointer.

User: Explain the highlighted line and add it to the map.

Agent:
The highlighted line dereferences the pointer and writes into the memory location
it points to. I added a canvas node under “Pointers → Dereferencing”.
```

---

## Project Philosophy

GONI Cognitive OS follows a solo-founder-friendly engineering philosophy:

```text
Start with perception.
Add reasoning.
Act only through bounded tools.
Verify everything.
Persist useful memory.
Promote abstractions only when the pain is real.
```

The project deliberately starts with a simple architecture:

* FastAPI instead of a complex graph runtime.
* SQLite instead of a vector database.
* Hardcoded tool calls before MCP.
* Canvas updates before full desktop automation.
* Screen understanding before autonomous control.

The long-term system can grow into a full agentic workspace, but the first milestone is a reliable local assistant that sees the screen and helps structure understanding.

---

## Roadmap

### Phase 1 — Perception Engine

* [ ] Implement screen capture.
* [ ] Add frame-diff detection.
* [ ] Add OCR on meaningful changes.
* [ ] Expose `/context` API endpoint.

### Phase 2 — Contextual Chat

* [ ] Add `/command` endpoint.
* [ ] Send screen context to an LLM.
* [ ] Return structured responses.
* [ ] Log commands and results to SQLite.

### Phase 3 — Canvas Agent

* [ ] Add React Flow canvas.
* [ ] Add `canvas.add_node` tool.
* [ ] Add `canvas.add_edge` tool.
* [ ] Generate mind maps from visible content.

### Phase 4 — Safe Execution

* [ ] Add approval gates.
* [ ] Add PyAutoGUI wrapper.
* [ ] Add Playwright wrapper.
* [ ] Add scoped file operations.
* [ ] Add before/after verification.

### Phase 5 — Cognitive Layer

* [ ] Add user preference memory.
* [ ] Add episodic task memory.
* [ ] Add tutoring mode.
* [ ] Add skill templates.
* [ ] Add semantic verification of generated artifacts.

---

## Status

Early experimental repository. Architecture and implementation are evolving.

---

## License

License to be defined.
