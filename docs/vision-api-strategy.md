# Vision API Strategy

GONI Cognitive OS pairs a local perception engine with on-demand vision and reasoning models. The always-on layer stays local: screen capture, diffing, OCR, Windows UI Automation, SQLite context, and FastAPI. Model calls happen only when the user asks a screen question.

The V1 routing decision is:

```text
local screen capture
-> OCR / UI parsing
-> structured context
-> Gemini Flash-Lite by default
-> Grok fallback for stronger reasoning
-> Qwen later for offline/private mode
```

## Copilot Vision API Position

Do not assume there is a public, reusable "Copilot Vision API" for this project.

Microsoft Copilot Vision is best treated as a Microsoft product feature rather than a general API that can be plugged into a custom desktop app. Microsoft describes it as an opt-in assistant that can view a shared screen, app, browser, or mobile camera feed and answer through Copilot Voice/text. It can highlight relevant screen areas, but Microsoft states that it does not click, type, or scroll on the user's behalf. ([Microsoft Support][2])

For GONI Cognitive OS, build the Copilot Vision-style layer directly:

```text
local perception engine
-> structured screen context
-> on-demand VLM / LLM reasoning API
-> explanation, highlight, canvas update, or approved tool call
```

## Local Perception Engine

The visual engine starts local and should not send the user's full screen to an AI model every second.

Core local components:

```text
1. Screen capture
   mss or DXcam

2. Change detection
   OpenCV frame diff

3. OCR
   PaddleOCR / Tesseract

4. UI structure
   Windows UI Automation, pywinauto, OmniParser spike later

5. Context cache
   SQLite

6. Backend
   FastAPI

7. AI brain
   Gemini Flash-Lite default, Grok fallback, Qwen later/offline
```

OmniParser is worth evaluating because a local parser that returns bounding boxes and element types would let the orchestrator send compact JSON instead of raw pixels. Treat it as a spike before dependency commitment: verify local installation, hardware requirements, latency, and output quality on real desktop screenshots.

## Current V1 Perception Kernel

The current scaffold is deliberately smaller than the full target stack:

```text
screen capture
-> OpenCV diff gate
-> PaddleOCR
-> Windows UI Automation foreground map
-> SQLite perception log
-> FastAPI /context
-> /command Gemini-first router
```

Implemented API boundary:

* `GET /health`
* `GET /context`
* `POST /command` with `{ "text": "...", "provider": "auto" }`
* `POST /act/desktop` as a blocked placeholder

This keeps V1 testable without API keys, LM Studio, cloud accounts, or OmniParser runtime dependencies. Real provider calls only happen from `/command` when keys are configured. The perception runner is available separately as `python -m goni.perceive.perceive` after installing `requirements.txt`.

## Provider Strategy

### Gemini Flash-Lite

Gemini is the default V1 vision brain for speed and low cost. Google's pricing page currently lists `gemini-2.5-flash-lite` as Flash-Lite and describes it as the smallest, most cost-effective model for at-scale usage. The live perception loop must not stream frames to Gemini; `/command` sends only the current screenshot/context when the user asks. ([Google AI for Developers][7])

Use Gemini for:

* "What am I looking at?"
* "Explain this error."
* "What should I click?"
* "Summarize this screen."
* "Turn this into a mind map node."

### xAI Grok API

Grok is the V1 reasoning fallback, not the default screenshot explainer. xAI documents `grok-4.3` with text and image modalities, a 1M context window, function calling, structured outputs, and configurable reasoning. xAI's image-understanding docs show image input through an OpenAI-compatible API base URL. ([xAI Grok 4.3][10], [xAI Image Understanding][11])

Use Grok for stronger agentic reasoning, workflow critique, or when Gemini returns a weak/error result.

### Qwen Local

Qwen is not the always-on eye. Keep Qwen as a later local/offline/private mode. The continuous loop remains OCR/UIA/diff/SQLite; local Qwen should only be called on user request after explicit configuration.

### OpenAI and Claude

OpenAI and Claude are not used in V1. OpenAI remains a possible later tool-calling provider. Claude remains useful later for planning-heavy or computer-use benchmarking, with the same sandboxing and approval posture.

## Recommended GONI Stack

```text
PERCEIVE:
- mss/DXcam
- OpenCV
- PaddleOCR
- Windows UI Automation
- OmniParser spike later

DECIDE:
- Gemini Flash-Lite default
- Grok reasoning fallback
- Qwen later for offline/private mode

MEMORY:
- SQLite

ORCHESTRATOR:
- FastAPI + WebSockets later

VOICE:
- whisper.cpp + edge-tts later
- Gemini Live later only if low-latency voice becomes worth the cost

ACTIONS:
- PyAutoGUI / Playwright later, approval-gated
```

## Minimum API Set

No API key is required to run the perception loop and tests.

For the Gemini-first V1 router:

```text
GEMINI_API_KEY
```

Optional fallback:

```text
XAI_API_KEY
```

## V1 Build Flow

```text
1. Local screen watcher
   - captures screenshot every 500ms or 1s
   - compares with previous frame
   - stores latest changed frame

2. OCR/UI parser
   - extracts visible text
   - reads foreground UI elements
   - maps text/elements to screen coordinates

3. Context object
   {
     active_window,
     ocr_text,
     ui_elements,
     screenshot_path
   }

4. User asks a question
   - send current screenshot or compressed image
   - send OCR text
   - send UI elements
   - send active window

5. Router
   - Gemini by default
   - Grok if explicitly requested or Gemini is weak/error
   - local Qwen only if offline/private mode is enabled later
```

## Final Recommendation

Build the Copilot Vision-style engine locally first and keep model calls on-demand. Do not wait for a Microsoft Copilot Vision API.

The V1 target is:

```text
GONI Vision Engine
= mss/DXcam + OpenCV + PaddleOCR + Windows UIA + FastAPI + Gemini Flash-Lite
```

Cost control rule:

```text
Never stream the screen continuously. Send only on question.
```

[1]: https://help.openai.com/en/articles/9039756-managing-billing-settings-on-chatgpt-web-and-platform "Managing Billing Settings on ChatGPT Web and Platform | OpenAI Help Center"
[2]: https://support.microsoft.com/en-us/topic/using-copilot-vision-with-microsoft-copilot-3c67686f-fa97-40f6-8a3e-0e45265d425f "Using Copilot Vision with Microsoft Copilot | Microsoft Support"
[7]: https://ai.google.dev/gemini-api/docs/pricing "Gemini Developer API pricing | Gemini API | Google AI for Developers"
[10]: https://docs.x.ai/developers/models/grok-4.3 "Grok 4.3 | xAI Docs"
[11]: https://docs.x.ai/developers/model-capabilities/images/understanding "Image Understanding | xAI Docs"
