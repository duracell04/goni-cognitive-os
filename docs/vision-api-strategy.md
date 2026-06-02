# Vision API Strategy

GONI Cognitive OS should pair a local perception engine with a cloud or local vision/reasoning model. The first executable backend starts with a local stub brain so the perception/cognition boundary, API contract, and SQLite logging can be tested before any provider is added. Codex in VS Code can help build the project, but runtime API use is separate from a ChatGPT Pro/Codex subscription; OpenAI documents ChatGPT and API platform billing as separate systems. ([OpenAI Help Center][1])

The practical architecture is:

```text
local screen capture
→ OCR / UI parsing
→ structured context
→ stub brain first, then one selected LLM provider
→ answer / highlight / canvas update
```

## Copilot Vision API Position

Do not assume there is a public, reusable “Copilot Vision API” for this project.

Microsoft Copilot Vision is best treated as a Microsoft product feature rather than a general API that can be plugged into a custom desktop app. Microsoft describes it as an opt-in assistant that can view a shared screen, app, browser, or mobile camera feed and answer through Copilot Voice/text. It can highlight relevant screen areas, but Microsoft states that it does not click, type, or scroll on the user's behalf. ([Microsoft Support][2])

Microsoft also offers Copilot Studio Computer Use for enterprise agents that interact with websites and desktop apps, but that belongs to the Power Platform / enterprise agent ecosystem. It is not the same as a public consumer Copilot Vision API for a local desktop application. ([The Verge][3])

For GONI Cognitive OS, build the Copilot Vision-style layer directly:

```text
local perception engine
→ structured screen context
→ VLM / LLM reasoning API
→ explanation, highlight, canvas update, or approved tool call
```

## Local Perception Engine

The visual engine should start local. It does not need an external API for every frame.

Core local components:

```text
1. Screen capture
   mss or DXcam

2. Change detection
   OpenCV frame diff

3. OCR
   PaddleOCR / Tesseract / Google Cloud Vision OCR if cloud OCR is needed

4. UI structure
   OmniParser spike, Windows UI Automation, pywinauto

5. Context cache
   SQLite

6. Backend
   FastAPI

7. Interface
   Tauri/Electron + React overlay/canvas

8. AI brain
   local stub first, then one selected provider
```

The system should not send the user's full screen to an AI model every second. It should capture locally, detect meaningful changes, run local OCR/UI parsing where possible, and send only relevant screenshots and structured context when the user asks a question or starts a workflow.

OmniParser is worth evaluating because a local parser that returns bounding boxes and element types would let the orchestrator send compact JSON instead of raw pixels. Treat it as a spike before dependency commitment: verify local installation, hardware requirements, latency, and output quality on real desktop screenshots.

## Current V1 Skeleton

The current scaffold is deliberately smaller than the full target stack:

```text
mss placeholder
→ OpenCV diff placeholder
→ OCR placeholder
→ structured JSON
→ FastAPI orchestrator
→ local stub brain
→ SQLite action log
```

The implemented API boundary is:

* `GET /health`
* `GET /context`
* `POST /command` with `{ "message": "...", "provider": "stub" }`

This keeps V1 testable without API keys, screenshots, OCR models, or OmniParser runtime dependencies.

## API Options

### OpenAI Responses API

OpenAI Responses API is a strong first cloud-provider candidate for GONI Cognitive OS because it supports the vision, reasoning, and tool-calling workflow the project needs. The executable V1 scaffold does not wire OpenAI yet; it uses the local stub brain until the local pipeline is stable. OpenAI's vision docs describe image inputs for multimodal applications, including image analysis through the Responses API. ([OpenAI Platform][4])

Use OpenAI for:

* screenshot understanding;
* “what am I looking at?” answers;
* code-line explanation;
* visual tutoring;
* structured JSON tool calls;
* mind-map and canvas instruction generation;
* later computer-use actions.

The local app should:

```text
GONI local app:
  - captures screen
  - extracts OCR/UI context
  - sends screenshot + context to OpenAI
  - receives answer or tool call
  - updates overlay/canvas
  - asks approval before action
```

OpenAI's computer-use docs describe a loop where the model receives screenshots, returns actions such as clicks, typing, or scrolling, the harness executes them, and updated screenshots are sent back until the model stops requesting actions. ([OpenAI Platform][5])

For actual computer use, keep strict safety controls: sandboxing, allowlisted actions/domains, and human confirmation for purchases, authenticated workflows, destructive operations, or anything hard to reverse.

### Anthropic Claude Computer Use

Claude Computer Use is the strongest alternative for desktop-agent experiments. Anthropic documents screenshot, mouse, keyboard, and desktop automation capabilities for computer-use workflows. ([Claude API Docs][6])

Use Claude when comparing agentic desktop-control performance. For the first GONI version, keep provider work out of the skeleton until the local API and memory loop are reliable.

Claude-style computer use needs the same safety posture: virtual machines or containers, minimal privileges, domain allowlists, and human confirmation for consequential actions.

### Google Gemini API

Gemini is a useful multimodal alternative for image understanding. Google's Gemini docs describe multimodal models that handle image captioning, classification, and visual question answering without training specialized ML models. The API supports images inline or through the File API. ([Google AI for Developers][7])

Use Gemini as a second model for comparison or as a fallback if pricing, latency, or quality is better for repeated image-understanding tasks.

### Google Cloud Vision / Azure AI Vision

OCR and object-detection APIs are useful helper services, not the main “brain” for GONI Cognitive OS. They can extract text, labels, handwriting, and bounding boxes, but they do not reason over user intent like a VLM/LLM.

Example helper flow:

```text
Google Cloud Vision OCR:
screenshot → text + bounding boxes

OpenAI:
screenshot + OCR + user question → explanation / action plan
```

Google Cloud Vision OCR supports text detection, dense document text detection, and handwriting extraction. ([Google Cloud][8])

## Recommended GONI Stack

Use this stack for the first implementation:

```text
Local:
- mss or DXcam
- OpenCV
- PaddleOCR first, Google Cloud Vision OCR optional later
- OmniParser spike / Windows UI Automation
- FastAPI
- SQLite
- Tauri/Electron overlay
- React Flow canvas

API:
- local stub brain for the current scaffold
- one selected LLM provider after the local loop is stable
- OpenAI Responses API as a strong candidate for vision + reasoning + tool calling
- OpenAI Realtime API later for voice
- Optional Claude Computer Use for benchmarking
- Optional Gemini API for model comparison
```

The first build should be vision-only assistance, not autonomous computer use:

```text
capture screen
→ run OCR/UI parse
→ user asks question
→ send screenshot + context to OpenAI
→ answer + optional highlight region
→ save explanation to canvas
```

That gives the project the Copilot Vision-style experience without prematurely adding high-risk desktop control.

## Minimum API Set

### Required

No API key is required for the current skeleton.

After the local loop is stable, use one selected provider key for:

```text
vision understanding
chat
structured JSON output
canvas instruction generation
```

### Optional Later

Use OpenAI Realtime API for low-latency speech-to-speech and voice-agent interaction. ([OpenAI Platform][9])

Use Google Cloud Vision API if local OCR is weak or slow.

Use Anthropic API to benchmark Claude's computer-use loop.

Use Gemini API as a second vision model or cheaper/faster fallback.

## V1 Build Flow

The build-it-yourself “Copilot Vision” loop is:

```text
1. Local screen watcher
   - captures screenshot every 500ms or 1s
   - compares with previous frame
   - stores latest changed frame

2. OCR/UI parser
   - extracts visible text
   - detects boxes/buttons/menus
   - maps text to screen coordinates

3. Context object
   {
     active_app,
     visible_text,
     ui_elements,
     screenshot_path,
     cursor_position,
     last_user_question
   }

4. AI call
   Send:
   - user question
   - screenshot
   - OCR text
   - UI elements
   - current mode: tutor / builder / guide

5. Response
   AI returns:
   - explanation
   - highlight region
   - canvas node
   - optional tool call

6. UI output
   - answer in chat
   - speak aloud later
   - highlight screen area
   - add node to mind map
```

## Final Recommendation

Build the Copilot Vision-style engine locally first and keep the brain swappable. Do not wait for a Microsoft Copilot Vision API.

The V1 target is:

```text
GONI Vision Engine
= mss/DXcam + OpenCV + PaddleOCR + evaluated UI parser + FastAPI + selected LLM provider
```

Then add:

```text
GONI Voice
= OpenAI Realtime API or whisper.cpp

GONI Canvas
= React Flow

GONI Actions
= PyAutoGUI / Playwright / PowerShell with approval gates
```

The first demo should answer:

> “What am I looking at?”
> “Explain this line.”
> “Highlight the important part.”
> “Add this to my mind map.”

That is the realistic path to a GONI Copilot Vision-style assistant.

[1]: https://help.openai.com/en/articles/9039756-managing-billing-settings-on-chatgpt-web-and-platform "Managing Billing Settings on ChatGPT Web and Platform | OpenAI Help Center"
[2]: https://support.microsoft.com/en-us/topic/using-copilot-vision-with-microsoft-copilot-3c67686f-fa97-40f6-8a3e-0e45265d425f "Using Copilot Vision with Microsoft Copilot | Microsoft Support"
[3]: https://www.theverge.com/news/649574/microsoft-copilot-studio-computer-use-ai?utm_source=chatgpt.com "Microsoft lets Copilot Studio use a computer on its own"
[4]: https://platform.openai.com/docs/guides/images-vision "Images and vision | OpenAI API"
[5]: https://platform.openai.com/docs/guides/tools-computer-use "Computer use | OpenAI API"
[6]: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool "Computer use tool - Claude API Docs"
[7]: https://ai.google.dev/gemini-api/docs/vision "Gemini API | Google AI for Developers"
[8]: https://cloud.google.com/vision/docs/ocr "Detect and extract text from images | Cloud Vision API | Google Cloud Documentation"
[9]: https://platform.openai.com/docs/guides/realtime "Realtime and audio | OpenAI API"
