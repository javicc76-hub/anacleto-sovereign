# ═══ ANACLETO SOVEREIGN AGENT ═══

**Status:** `Experimental / Active Development` (v0.6.0)  
**Focus:** Sovereign TUI & Local Agent Interface  
**Inference (Test Environment):** llama.cpp (Local-first)

## ⚡ Overview

ANACLETO is a local-first autonomous agent experiment focused on the interaction between high-level agentic reasoning and local hardware sovereignty. This repository contains the foundational implementation of the **Sovereign TUI** (v0.6) and the core interface for local agent execution.

This code represents a specific module of the broader ANACLETO development laboratory. It is designed to demonstrate how an agent can be decoupled from external cloud providers, enabling operation on local compute clusters.

### The Philosophy: Sovereign Agency

The goal of the ANACLETO project is the **decoupling of the Agent from the Inference Infrastructure**. By separating reasoning logic from the underlying LLM provider, we explore the potential for running intelligence entirely on local hardware, ensuring privacy and eliminating dependency on external inference APIs.

## 🛠 Current Capabilities (v0.6)

This repository implements the following core components:

- **Cyberpunk TUI:** A custom terminal user interface designed for high-density telemetry and monitoring of agent status.
- **Core Agent Interface:** Foundations for local-first tool-calling and mission monitoring.

*Note: Advanced components such as the Codex Gateway, Sovereign Runtime, and automated Verification Loops are part of the ongoing ANACLETO laboratory development and are not fully contained within this specific repository version.*

## 🖥 Development & Test Environment

This project is optimized for and has been tested on:
- **OS:** Ubuntu 24.04 LTS
- **Compute:** 3× NVIDIA RTX 3060 (Local Cluster)
- **Model:** Gemma 4 26B (via llama.cpp)
- **Context Window:** 128K

## 🚀 Getting Started (Experimental)

> **WARNING:** This is an ongoing research project. It is not intended for production use or as a plug-and-play framework. It is a laboratory for testing agentic sovereignty.

## 📜 Roadmap

- [x] v0.6: Core TUI and basic agent interaction interface.
- [ ] v0.7: Integration with advanced memory modules.
- [ ] v0.8: Multi-agent orchestration (CrewAI integration).
- [ ] v0.9: Automated regression testing for local inference.

---
*Built by the Anacleto Lab.*
