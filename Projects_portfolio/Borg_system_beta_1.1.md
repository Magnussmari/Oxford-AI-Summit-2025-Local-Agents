# BORG: A Modular AI Development Environment for Higher Education

**Built by Magnús Smári Smárason and team at the University of Akureyri**
**Status: Beta v1.1 – Independent system with legacy auth SSO integration**
**For: Diverse university userbase – faculty, staff, and research groups**

## 🔍 Overview

BORG is a full-stack, GPU-accelerated digital environment designed to provide secure, multilingual, and AI-integrated functionality for universities. It was developed in-house over six months by a compact, focused team. The system is designed for extensibility, local AI deployment, and optimal user experience across roles – from educators and administrators to researchers and support staff.

The system operates independently from legacy software stacks, relying solely on centralized Single Sign-On (SSO) authentication to maximize user continuity while retaining full backend autonomy and innovation capacity.

![BORG System Interface](../presentation/images/borg-system-interface.png)
*BORG v1.1 Beta - Modern, multilingual AI-integrated interface for higher education*

---

## 🚀 Development Methodology

Due to the innovative nature of this project and its scope within higher education AI integration, the development approach diverged from traditional DevOps terminology and practices. The methodology centered around:

### Problem-First Approach

* **Broad Problem Statement:** Addressing AI accessibility and integration challenges in Icelandic higher education
* **Use Case Discovery:** Iterative identification of real-world faculty, staff, and research needs
* **User-Centered Design:** Direct feedback loops with diverse university stakeholders

### Experimental Development Cycle

* **Rapid Prototyping:** Quick iteration cycles to test AI integration concepts
* **Continuous Experimentation:** Testing different AI models, interfaces, and workflows
* **Progressive Polishing:** Incremental refinement based on user feedback and technical learnings

### Current State: Beta & Beyond

Now entering beta phase, the system has evolved to embrace:

* **CI/CD Implementation:** Structured deployment pipelines for production stability
* **DevOps Best Practices:** Infrastructure as code, monitoring, and automated testing
* **LLM-Assisted Architecture:** Full system designed to leverage AI-assisted coding workflows
* **Best Practices Focus:** Code quality, security, and maintainability standards

This approach allowed for genuine innovation while building toward enterprise-grade reliability and maintainability.

---

## 💻 System Architecture

### 🧊 "Borg Cubes" Design Philosophy

The system is architected around modular "Borg cubes" - interchangeable AI tool components designed for rapid evolution and institutional resilience:

* **Interchangeable Components:** Due to the rapid pace of AI progress, all AI tools are designed as modular, swappable units
* **Zero Critical Dependencies:** No institutional-sensitive dependencies ensure the system remains operational even if external services go offline
* **Future-Proof Architecture:** Components can be easily replaced, upgraded, or reconfigured without affecting the core system
* **Institutional Independence:** Critical university functions continue operating regardless of external AI service availability
* **Workflow Integration Focus:** Tools are designed to integrate seamlessly into users' existing workflows rather than providing "ready-made solutions"

### ▶️ Frontend

* **Framework:** Next.js 14
* **UI Components:** Radix UI
* **Styling:** Tailwind CSS
* **State Management:** React Hooks
* **Real-Time:** Socket.IO (Client)
* **Features:**

  * Fully responsive UI
  * Modern UX (dark/light modes, collapsible sidebars)
  * Glossary integration for multilingual users
  * Live chat and transcription interface

### 🧠 Backend

* **API Framework:** Next.js 14 (API routes)
* **Database ORM:** Prisma
* **Database:** PostgreSQL
* **Authentication:** NextAuth.js with JWT
* **Real-Time Communication:** Socket.IO
* **Transcription AI:** OpenAI Whisper (local + API fallback)
* **Text-to-Speech:** Supports OpenAI voices (`nova`, `alloy`, `shimmer`, etc.)

---

## 🧪 Local AI Lab Infrastructure

* **Hardware:**

  * RTX 4090 and RTX 5090 GPUs
  * Intel i9-14900K CPUs
  * 128 GB DDR5 RAM
* **Use Cases:**

  * Transcription (Fine tuned Whisper model)  [Carlos Daniel Hernandez Mena](https://huggingface.co/carlosdanielhernandezmena/whisper-large-icelandic-10k-steps-1000h)
  * Future planned support for local LLMs and multimodal inference
  * GPU-aware backend health-check and load reporting

---

## 🔡 Translation System

* **Internationalization:**

  * All strings migrated to PostgreSQL
  * Supports runtime loading of multilingual UI components
  * Translation system managed via `update-translations.js` and `fix-titles.sh`

---

## 🧰 Features (Functional Modules)

### Transcription Tools

* Real-time microphone capture
* File upload (WAV, WebM)
* YouTube audio transcription
* Icelandic language support (optimized model configs)

### Chat System

* Group chats and DMs
* Live presence indicators
* Message history
* Admin stats and management tools

### AI Chatbots - Specialized Assistants

#### Úrðarmal - Policy Guidance Chatbot (Senior/Production)
* **Purpose:** Comprehensive policy guidance for AI adoption in higher education
* **Status:** Rigorously tested and evaluated - production-ready
* **Knowledge Base:** Complete policy documentation and reference materials
* **Implementation:** GPT-4.1 with custom system prompts and OpenAI vector store integration
* **Use Cases:** Policy interpretation, compliance guidance, best practice recommendations

#### Askver - Pedagogical Support Chatbot (Development)
* **Purpose:** Supporting educators with curriculum development and evaluation
* **Status:** In development but showing strong promise
* **Capabilities:** 
  * Syllabus review and updates based on AI evolution
  * Project evaluation and recommendations
  * Assessment methodology guidance
* **Implementation:** GPT-4.1 with specialized educational system prompts and vector store
* **Target Users:** Faculty and educational staff adapting to rapid AI changes

**Technical Implementation:** Both chatbots utilize simple yet effective architecture with GPT-4.1 models, custom system prompts, and OpenAI vector store databases for enhanced context and knowledge retrieval.

### Blog System

* **Content Management:** Full-featured blog platform for university news and updates
* **Multilingual Support:** Content creation and display in multiple languages
* **User Roles:** Faculty and staff can create and manage blog posts
* **Integration:** Seamlessly integrated with the main BORG interface

### Technical Wiki

* **Knowledge Base:** Comprehensive technical documentation system
* **Collaborative Editing:** Multiple contributors can create and maintain documentation
* **Version Control:** Track changes and maintain documentation history
* **Search Functionality:** Advanced search capabilities across all wiki content
* **Cross-Reference:** Link between wiki articles and other BORG features

### AI Model Documentation & Configuration

* **Comprehensive Documentation:** All AI tools include extensive documentation covering:
  * Model specifications and versions used
  * Parameter configurations and settings
  * Vector store implementation (where applicable)
  * System prompts and prompt engineering details
* **Current Implementation:**
  * Chatbots powered by GPT-4.1 via OpenAI Assistants API
  * Integrated vector store for enhanced context and retrieval
  * Transparent model behavior and decision-making processes

### Admin Controls

* Key-based AI API management (CRUD)
* System analytics endpoint
* Role-based access enforcement

---

## 🧪 API Reference

**RESTful Endpoints (Next.js API + FastAPI Python backend):**

* `/api/auth`, `/api/users`, `/api/chat`, `/api/admin`
* `/api/transcribe/file` and `/api/transcribe/youtube`
* `/api/tts` (voice synthesis)

**Health Monitoring:**

* `/health` – returns backend AI model/device status
* `/status` – detailed system and model diagnostics

All secured with JWT tokens + admin role enforcement.

---

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

Supports local and production mode with GPU inference, PostgreSQL, and frontend-backend linking out-of-the-box. Example `.env` templates are provided for all tiers.

---

## 🛠 Tech Stack Summary

| Layer     | Stack                                  |
| --------- | -------------------------------------- |
| Frontend  | Next.js 14, Radix UI, Tailwind CSS     |
| Backend   | Next.js (API), FastAPI (AI), Socket.IO |
| Auth      | NextAuth.js + JWT                      |
| Database  | PostgreSQL via Prisma ORM              |
| AI Models | Whisper (on-device and API fallback)   |
| Hardware  | RTX 4090 + 5090, i9-14900K, 128GB RAM  |

---

## 🧑‍💻 Development Notes

* Repository follows modern monorepo practices (Python + TypeScript)
* Language switching logic fully separated from UI
* All hardcoded UI text now dynamically sourced from the DB
* Legacy system integration limited to SSO only — all core services run independently

---

## 🌱 Purpose & Vision

BORG is designed not as a commercial platform, but as a **public-good innovation framework** for responsible AI adoption within Icelandic higher education. It supports transparency, user sovereignty, and ethical AI integration at scale — and will evolve with local LLM support, student onboarding, and future research toolkits.

---

## 👥 Dev - Team

* **Magnús Smári Smárason** – AI Project Manager & Responsible Person
* **Collaborative Development:** Development, design, and architecture are cooperative efforts between the two main developers
* **Ólafur Búi Ólafsson** – Fullstack developer - Hacker https://github.com/olibuijr
* **IT Systems Team @ University of Akureyri** – Infrastructure Support

**Developer-Friendly Framework:** The system is specifically architected to enable other developers to quickly start developing within the framework, with clear documentation, modular architecture, and standardized development patterns.