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
