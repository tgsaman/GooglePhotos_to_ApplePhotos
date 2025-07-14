# PSA: This Repository Was Written with OpenAI Codex — Here's What That Means

Welcome, curious developer, casual Mac user, or metadata-lost soul. This project — a photo and metadata repair utility for macOS users migrating from Google Photos — was written in collaboration with **OpenAI Codex**.

Before you fork, contribute, or clone this repo, here’s what you should know about how it was built, what design principles were followed, and how to contribute effectively inside the **glass house** we’ve chosen to keep squeaky clean.

---

## 🧠 What is Codex?
Codex is OpenAI’s software development assistant — a large language model trained on code and natural language. It powers GitHub Copilot, ChatGPT’s coding interface, and a few other tools we like to keep mysterious.

But unlike autocomplete tools, Codex participates in **structured collaboration** — meaning: it reads your whole project directory, understands how files relate, and responds to prompts like a thoughtful engineer.

This repo wasn’t scaffolded manually. It was written by a human collaborating with Codex, iterating via natural language.

---

## 🛠️ Why We Used It
This tool was built:
- With **user trust** in mind (PII stays local)
- With **no internet connections**
- As a **safe open-source migration assistant** for Mac users

Codex enabled:
- Dynamic path handling — no hardcoded directories
- Metadata repair logic with cross-format support (HEIC, MP4, JPG)
- Verbose logging, progress feedback, dry run modes
- Strong testability and graceful error recovery

All this — with less boilerplate, and more empathy for non-technical users.

---

## 🔐 Why This Repo Is a Glass House
This project interacts with photos, videos, and metadata — including **GPS locations and timestamps**, which are often personally identifying.

To maintain privacy:
- Output CSVs are written to your **~/Desktop**, not the project folder
- All paths in the repo are stripped or dynamic
- There is **no telemetry, analytics, or upload behavior**
- The agents that wrote this are offline by design

If you make this project public or contribute back:
👉 Scrub any paths or data dumps before commit.

---

## 📦 What This Repo Offers
- `photo_metadata_patch.py`: core logic for parsing `.supplemental-metadata.json` and tagging media files
- `metadata_log.csv`: output report, written safely to Desktop
- `Unmatched_Metadata/`: a local holding tank for JSONs with no matching photo

No GUI (yet), no package dependencies — just macOS-native behavior.

---

## 🧭 Codex Contribution Best Practices
If you’re extending this tool inside Codex or with Copilot:

1. **Think in modules, not files**
   > Say: “Add GPS fallback injection logic to exif_batch.py” — not “fix line 42”

2. **Use clear, action-oriented prompts**
   > “Make dry-run mode warn on missing timestamps”

3. **Keep your outputs clean**
   > Export only to Desktop or user-specified path

4. **Avoid internet access in logic**
   > This tool is self-contained by design

5. **Preserve user trust**
   > Never retain or inspect files unless explicitly needed and documented

---

## 🪪 Signed by Codex
I helped write this repo — line by line, prompt by prompt — in service of an open-source, privacy-respecting migration tool for Google Photos users.

If you're reading this, it's because the author wanted you to know what went into the machine. Thanks for stopping by.

— **Codex**
July 2025

