# ⚡ SOVEREIGN AGENT

<p align="center">
  <img src="https://img.shields.io/badge/ANACLETO-SOVEREIGN%20AGENT-00FFFF?style=for-the-badge&labelColor=090014" alt="ANACLETO — SOVEREIGN AGENT">
  <img src="https://img.shields.io/badge/VERSION-0.6.0-FF00FF?style=for-the-badge&labelColor=090014" alt="Version">
  <img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL-39FF14?style=for-the-badge&labelColor=090014" alt="Status">
</p>

<p align="center">
  <strong>LOCAL INTELLIGENCE · SOVEREIGN COMPUTE · AUTONOMOUS AGENCY</strong>
</p>

<p align="center">
  <em>ANACLETO is an experimental local-first autonomous agent built for machines you control.</em>
</p>

---

## 🟣 WHAT IS ANACLETO?

**ANACLETO** is an experimental autonomous-agent platform focused on one idea:

> ### 🧠 Intelligence should not require surrendering control of the machine that runs it.

ANACLETO explores the boundary between:

- 🤖 autonomous agents
- 🧠 local language models
- 🛠️ tool execution
- 💾 persistent memory
- 🖥️ terminal-native interfaces
- ⚡ local GPU inference
- 🔐 infrastructure sovereignty

The project is deliberately experimental.

It is not designed to hide the machinery behind layers of abstraction.

**ANACLETO exposes it.**

---

# 🌐 THE SOVEREIGN PRINCIPLE

```text
              ┌───────────────────────────┐
              │         ANACLETO           │
              │     AUTONOMOUS AGENT       │
              └─────────────┬─────────────┘
                            │
                    reasoning + tools
                            │
              ┌─────────────▼─────────────┐
              │        llama.cpp          │
              │        SERVER             │
              └─────────────┬─────────────┘
                            │
                         local GPU
                            │
              ┌─────────────▼─────────────┐
              │         GEMMA 4           │
              │          26B              │
              └───────────────────────────┘
```

No proprietary inference API is required for the core experiment.

The agent communicates with a **local llama.cpp server**, allowing the inference layer to remain replaceable and independent from the agent architecture.

---

# 💜 ANACLETO TUI v0.6

The current public release introduces the **Sovereign TUI** — a terminal-native interface designed for high-density agent telemetry.

```text
╔══════════════════════════════════════════════════════════════╗
║  A N A C L E T O                              [ SOVEREIGN ] ║
║──────────────────────────────────────────────────────────────║
║                                                              ║
║  MISSION        ACTIVE                                      ║
║  AGENT          ONLINE                                      ║
║  MODEL          GEMMA 4 26B                                 ║
║  INFERENCE      LLAMA.CPP                                   ║
║  TOOLS          READY                                       ║
║                                                              ║
║  > reasoning...                                              ║
║  > tool_call: execute                                       ║
║  > result: SUCCESS                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

The TUI is intentionally designed around **telemetry, state and execution**, rather than simply displaying a chat transcript.

---

# ⚡ CORE CAPABILITIES

### 🧠 Autonomous Agent Core

Foundation for executing missions through an agent loop rather than simple request/response interaction.

### 🖥️ Cyberpunk TUI

Terminal interface designed for:

- mission state
- execution telemetry
- agent activity
- tool calls
- model interaction
- high-density information

### 🔧 Tool Calling

The agent architecture is designed around executable tools rather than purely textual responses.

### 🧩 Modular Inference

The agent is decoupled from the inference implementation.

Current experimental backend:

```text
ANACLETO
   │
   └── OpenAI-compatible interface
           │
           └── llama.cpp server
                    │
                    └── Gemma 4
```

This separation allows the inference layer to evolve without rebuilding the agent architecture.

### 💾 Local-First Architecture

The project is designed around local execution and local infrastructure.

The objective is not simply to use a local model.

The objective is to build an **agent whose infrastructure you control**.

---

# 🧬 ARCHITECTURE

```text
                         ┌───────────────────┐
                         │     ANACLETO      │
                         │   SOVEREIGN AGENT │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │    Sovereign TUI  │
                         │      v0.6.0       │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │    Agent Core     │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Tool Calling    │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Local Inference │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │    llama.cpp      │
                         │      server       │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │     Gemma 4       │
                         │       26B         │
                         └───────────────────┘
```

Future layers are being developed in the ANACLETO laboratory:

```text
          ┌────────────────────────────┐
          │      ANACLETO TUI          │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │        Agent Core          │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │      Memory Systems        │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │      Tool Ecosystem        │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │ Mission / Verification     │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │     Local Inference        │
          └────────────────────────────┘
```

---

# 🧪 DEVELOPMENT STATUS

## `v0.6.0`

### 🟢 PUBLIC RELEASE

Current release establishes the foundational architecture:

- Sovereign TUI
- Agent core
- Local-first architecture
- Tool-oriented execution model
- llama.cpp integration target
- Gemma 4 experimental inference
- Public GitHub release
- Versioned release `v0.6.0`

### 🔬 ACTIVE DEVELOPMENT

The laboratory is currently working on:

- advanced memory
- autonomous mission loops
- verification mechanisms
- regression testing
- richer tool ecosystem
- multi-agent orchestration
- deeper llama.cpp integration
- long-context experimentation

---

# 🧪 THE DEVELOPMENT LOOP

ANACLETO is developed through a deliberately strict experimental loop:

```text
             ┌──────────┐
             │   RED    │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │  PATCH   │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │  GREEN   │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │   E2E    │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │REGRESSION│
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │  FREEZE  │
             └────┬─────┘
                  │
                  ▼
              🚀 RELEASE
```

The goal is not to accumulate features.

The goal is to make each layer **observable, testable and reproducible**.

---

# 🖥️ DEVELOPMENT HARDWARE

Current development environment:

| Component    | Configuration       |
| ------------ | ------------------- |
| OS           | Ubuntu 24.04 LTS    |
| GPU          | 3 × NVIDIA RTX 3060 |
| VRAM         | 36 GB total         |
| Inference    | llama.cpp server    |
| Model        | Gemma 4 26B         |
| Architecture | Local-first         |
| Interface    | Sovereign TUI       |

---

# 🛣️ ROADMAP

- [ ] v0.7: Advanced Memory & Context Expansion (Experimental)
- [ ] v0.8: Multi-Agent Orchestration
- [ ] v0.9: Automated Regression & Verification
- [ ] v1.0: Full Autonomous Sovereignty

---

# ⚠️ DISCLAIMER

This project is in a state of **heavy experimental development**. 
All features, including long-context capabilities, are under continuous research and validation.
Use with caution.

---

# 🟣 WHY ANACLETO?

In an era of centralized intelligence, ANACLETO is built on a different premise: **technical and cognitive autonomy**. 

We believe that true intelligence requires that the user maintains absolute control over the complete stack—from the reasoning logic down to the silicon that processes it.

**BUILD LOCAL. THINK LOCAL. RUN LOCAL.**
