# DeterminAgent Template Flows

Pre-built workflow templates demonstrating the DeterminAgent library.

Each flow is a complete, runnable Python application that you can copy and customize for your needs.

---

## Available Flows

### 📝 [Blog Writer](./blog/)

Multi-agent blog generation pipeline with AI revision loops and human review.

```bash
cd flows/blog
python main.py "Your Topic Here" --provider claude
```

**Agents:** Writer → Editor → Reviewer (loop) → Human Review → Final Output

**Features:**
- Configurable providers per role (Claude, Copilot, Gemini, Codex)
- AI-driven revision loop with scoring
- Interactive human approval phase
- Session management with resume capability

---

## Flow Structure

Each flow follows a standard structure:

```
flows/<name>/
├── main.py        # Entry point - runnable Python script
├── agents.yaml    # Agent configuration (providers, models, settings)
└── README.md      # Usage guide for this specific flow
```

## Using a Flow

1. **Navigate to the flow directory:**
   ```bash
   cd flows/blog
   ```

2. **Review configuration (optional):**
   Edit `agents.yaml` to customize providers, models, and settings.

3. **Run the flow:**
   ```bash
   python main.py "Topic" --writer-provider claude --editor-provider copilot
   ```

4. **Customize:** Copy the entire flow folder and modify for your needs.

---

## Creating Your Own Flow

Start by copying an existing flow:

```bash
cp -r flows/blog flows/my-flow
```

Then modify:
- `main.py` - Workflow logic using LangGraph
- `agents.yaml` - Default agent settings
- `README.md` - Documentation

**Key Pattern:** Each flow uses the DeterminAgent library directly:

```python
from determinagent import UnifiedAgent, SessionManager
from determinagent.config import load_config

# Load agent configuration
config = load_config()

# Create agents
writer = UnifiedAgent(
    provider=config["defaults"]["writer"]["provider"],
    model="balanced",
    role="writer",
    session=SessionManager("claude")
)

# Build your workflow with LangGraph
from langgraph.graph import StateGraph
workflow = StateGraph(YourState)
# ... add nodes, edges, compile, invoke
```

---

## Prerequisites

- Python 3.10+
- DeterminAgent library: `pip install -e .`
- At least one CLI tool installed (Claude Code, Copilot, etc.)

---

*See [PLAN.md](../PLAN.md) for roadmap, [ARCHITECTURE.md](../ARCHITECTURE.md) for technical details.*
