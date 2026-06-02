<<<<<<< HEAD
# 🐛 Debug Buddy

> An AI-powered CLI debugging agent that doesn't just suggest fixes — it **executes, validates, and iteratively refines** them until your code actually works.

---

## What is Debug Buddy?

Debug Buddy is an intelligent command-line tool that acts like a senior engineer reviewing your broken code. You hand it a Python file and an error traceback; it handles the rest — analyzing the root cause, retrieving relevant documentation, generating a fix, running it, and looping until the code passes.

Most AI coding tools stop at "here's a suggestion." Debug Buddy closes the loop.

```
Understand → Fix → Execute → Evaluate → Refine
```

---

## Key Features

**Intelligent Error Analysis** — Parses tracebacks to identify root causes and categorize errors (syntax, runtime, or logical) before attempting any fix.

**Context-Aware Fix Generation** — Retrieves relevant documentation via RAG (Retrieval-Augmented Generation) before prompting the LLM, reducing hallucinations and grounding fixes in real knowledge.

**Iterative Refinement Loop** — Automatically re-generates and re-evaluates fixes until a correctness threshold is met or the maximum iteration count is reached. No manual back-and-forth required.

**Execution-Based Validation** — Actually runs the corrected code and captures runtime behavior, rather than just doing static analysis.

**Threshold-Based Scoring** — Each fix is evaluated against multiple signals: error resolution, execution success, and output correctness.

**Clean CLI Interface** — Built with [Typer](https://typer.tiangolo.com/) for a developer-friendly command-line experience.

---

## Architecture

```
User Input (Code + Traceback)
         │
         ▼
 Error Analysis & Classification
         │
         ▼
 Context Retrieval (RAG / Documentation)
         │
         ▼
 Fix Generation (LLM)
         │
         ▼
 Code Execution & Evaluation
         │
    ┌────┴────┐
    │  Pass?  │
    └────┬────┘
    No   │   Yes
    │    ▼
    │  Final Corrected Code
    │
    ▼
 Refinement Loop (repeat)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| LLM Orchestration | LangChain, LangChain-Core, LangChain-Community |
| LLM Provider | NVIDIA AI Endpoints (via `langchain-nvidia-ai-endpoints`) |
| Vector Store / RAG | LanceDB |
| Embeddings | Sentence Transformers |
| Web Crawling (docs) | Crawl4AI |
| Data Validation | Pydantic |
| CLI Framework | Typer |

---

## Project Structure

```
debug-buddy/
├── agents/          # Agent logic and LLM orchestration
├── chroma_db/       # Vector store for document retrieval
├── core/            # Core debugging engine and evaluation logic
├── graph/           # LangGraph workflow definitions
├── routes/          # CLI route handlers (Typer commands)
├── schemas/         # Pydantic data models
├── sources/         # Documentation ingestion and crawling
├── main.py          # Entry point
└── requirements.txt
```

---

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/Sohan-patnaik/debug-buddy.git
cd debug-buddy
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set your API key**

```bash
export NVIDIA_API_KEY=your_key_here
```

**4. Run it**

```bash
# Debug a file
python main.py debug file.py

# Debug with a specific error message
python main.py debug file.py --error "TypeError: unsupported operand..."
```

---

## Why This Project?

This project was built to explore agentic AI patterns — specifically, how to move beyond single-shot LLM responses toward systems that **reason, act, and self-correct**. It demonstrates:

- Building multi-step LLM pipelines with LangChain and LangGraph
- Implementing RAG with real-time document retrieval (Crawl4AI + LanceDB)
- Designing feedback loops with structured evaluation and scoring
- Wrapping complex backend logic in a clean developer-facing CLI

---

## Skills Demonstrated

`Python` · `LangChain` · `LangGraph` · `RAG` · `LLM Engineering` · `Agentic AI` · `Vector Databases` · `CLI Development` · `Pydantic` · `Prompt Engineering`

---

## Author

**Sohan Patnaik**
[GitHub](https://github.com/Sohan-patnaik)
=======
🚀 AI CLI Debugger Agent

An intelligent CLI-based debugging assistant that goes beyond code generation — it analyzes, executes, validates, and iteratively refines code fixes using LLM-driven reasoning and feedback loops.

🧠 Overview

Most AI coding tools stop at suggesting fixes.
This project is designed to behave more like a real engineer:

Understand → Fix → Validate → Improve

It takes code and error tracebacks as input, retrieves relevant context, generates fixes, and continuously refines them until correctness is achieved.

⚙️ Architecture
User Input (Code + Traceback)
        ↓
Error Analysis & Classification
        ↓
Context Retrieval (Documentation)
        ↓
Fix Generation (LLM)
        ↓
Code Execution & Evaluation
        ↓
Refinement Loop (Iterative Improvement)
        ↓
Final Corrected Code

🔍 Features
✅ Intelligent Error Analysis
Parses traceback and identifies root cause
Categorizes errors (syntax, runtime, logical)
📚 Context-Aware Fixes
Retrieves relevant documentation before generating fixes
Reduces hallucination via grounded reasoning
🔁 Iterative Debugging Loop
Generates fixes → evaluates → refines
Continues until:
correctness threshold is met
or max iterations reached
🧪 Execution-Based Validation
Runs corrected code
Captures runtime errors and output behavior
🎯 Threshold-Based Evaluation
Scores fixes based on:
error resolution
execution success
output correctness (if applicable)
💻 CLI Interface
Built with Typer for clean developer experience

🛠️ Tech Stack
Python
LangChain (LLM orchestration)
Typer (CLI)
AST / Static Analysis
LLM APIs (OpenAI / compatible)

🚀 Installation
git clone https://github.com/your-username/ai-cli-debugger.git
cd ai-cli-debugger

pip install -r requirements.txt

▶️ Usage
python main.py debug file.py
Or with traceback:
python main.py debug file.py --error "TypeError: unsupported operand..."
>>>>>>> 433b590c07db1396a141b29b17d6e724117bf40e
