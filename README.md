# ⚡ CompText Codex (V4.0)
### The Semantic Compression Protocol for LLMs

![Version](https://img.shields.io/badge/release-v4.0.0-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/status-production_ready-success?style=for-the-badge)
![System](https://img.shields.io/badge/protocol-CompText-orange?style=for-the-badge)

> **"Speak the language of the Latent Space."**
> CompText is a strict Domain Specific Language (DSL) designed to reduce token usage by up to 80% while increasing prompt precision for AI models like GPT-4, Claude 3.5, and GitHub Copilot.

---

## 🚀 Why CompText?

| Feature | Standard Prompting | CompText V4.0 |
| :--- | :--- | :--- |
| **Token Cost** | 💸 Expensive (Verbose) | 📉 **Ultra-Low** (Compressed) |
| **Precision** | 🤷‍♂️ Variable (Hallucinations) | 🎯 **Pinpoint** (Strict Syntax) |
| **Speed** | 🐢 Slower generation | ⚡ **Instant** (Less to process) |
| **Workflow** | Linear (One by one) | 📦 **Batch Processing** (Parallel) |

---

## 📚 The Protocol (Quick Reference)

### 1. Core Syntax
Structure: `KEY:VALUE; KEY:VALUE`

| Command | Description | Example |
| :--- | :--- | :--- |
| `CMD:` | Action | `CODE`, `FIX`, `MOD`, `DOC`, `TEST` |
| `LNG:` | Language | `PY`, `TS`, `GO`, `SQL`, `HTM` |
| `FRM:` | Framework | `RCT` (React), `PND` (Pandas), `NS` (NextJS) |
| `STY:` | Output Style | `PRO` (Pro), `CONCISE`, `ROBUST` |
| `SKL:` | Skill Level | `MST` (Master), `EXP` (Expert), `BEG` (Beginner) |

### 2. Batch Processing (New in V4.0)
Execute multiple distinct tasks in a single token stream using the `||` separator.

```text
BATCH: [CMD:FIX; TSK:AUTH_BUG] || [CMD:DOC; FMT:MD] || [CMD:TEST; FRM:JEST]
```

### 3. Context & Skills
Anchor the AI to a specific persona or project context instantly.

```text
SKL:MST; PRF:NO_COM; CTX:Caspar-Web
```

(Translation: "Act as a Master Architect, write code with no comments, use 'Caspar-Web' project context.")

---

## 🛠️ Installation & Auto-Sync

This repository features a **Self-Healing Architecture**.

* **The Source:** All rules are defined in the `/spec` directory.
* **The Brain:** GitHub Actions automatically compiles these specs into `.github/copilot-instructions.md`.
* **The Agent:** GitHub Copilot reads these instructions automatically.

To use in your own Copilot:

Simply copy the content of `.github/copilot-instructions.md` into your Custom Instructions, or fork this repo to use the agent directly.

---

## 📂 Project Structure

```
├── .github/
│   ├── workflows/      # Auto-update automation
│   └── copilot-...     # The compiled "Brain" for the Agent
├── spec/               # The Source of Truth (Modules A-G)
├── scripts/            # Build logic (Python)
└── templates/          # Ready-to-use CompText snippets
```

---

**Maintained by Caspar & The CompText Architecture Team.**
