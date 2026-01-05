# How to Write Your First Flow

This tutorial guides you through creating a custom multi-agent workflow using DeterminAgent. By the end, you'll have a working flow that uses multiple AI agents in a coordinated pipeline.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed
- **DeterminAgent** installed: `pip install determinagent`
- At least **one CLI tool** authenticated:
  - [Claude Code](https://claude.ai/code) (`claude`)
  - [GitHub Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli/using-github-copilot-in-the-cli) (`gh copilot`)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli) (`gemini`)
  - [OpenAI Codex](https://openai.com/codex) (`codex`)

Verify your CLI is working:

```bash
claude --version     # or your preferred tool
```

---

## Step 1: Project Setup

Create a new directory for your flow:

```bash
mkdir my-first-flow
cd my-first-flow
```

Create the main Python file:

```bash
touch main.py
```

---

## Step 2: Understanding the Core Components

DeterminAgent has three core building blocks:

### 1. **SessionManager**
Maintains conversation context across multiple calls to the same agent.

```python
from determinagent import SessionManager

session = SessionManager("claude")  # Provider name
```

### 2. **UnifiedAgent**
The main interface for sending prompts to AI CLI tools.

```python
from determinagent import UnifiedAgent, SessionManager

agent = UnifiedAgent(
    provider="claude",           # CLI to use
    model="balanced",            # Model alias: fast, balanced, powerful
    role="assistant",            # Role name for logging
    instructions="Be helpful.",  # System prompt
    session=SessionManager("claude"),
)
```

### 3. **send() Method**
Send prompts and receive responses:

```python
response = agent.send("Explain LangGraph in 3 sentences.")
print(response)
```

---

## Step 3: Create a Simple Two-Agent Flow

Let's build a flow with a **Writer** agent and an **Editor** agent.

```python
#!/usr/bin/env python3
"""My First DeterminAgent Flow: Writer + Editor Pipeline."""

from determinagent import UnifiedAgent, SessionManager


def create_writer() -> UnifiedAgent:
    """Create the Writer agent."""
    return UnifiedAgent(
        provider="claude",
        model="balanced",
        role="writer",
        instructions="""You are a skilled technical writer.
        Write clear, engaging content with proper structure.
        Use markdown formatting for headers and code blocks.""",
        session=SessionManager("claude"),
    )


def create_editor() -> UnifiedAgent:
    """Create the Editor agent."""
    return UnifiedAgent(
        provider="claude",
        model="balanced",
        role="editor",
        instructions="""You are a meticulous editor.
        Review content for clarity, grammar, and structure.
        Provide the improved version directly, not just suggestions.""",
        session=SessionManager("claude"),
    )


def run_flow(topic: str) -> str:
    """Run the Writer → Editor pipeline."""
    
    # Step 1: Writer creates initial draft
    print("📝 Writer creating draft...")
    writer = create_writer()
    draft = writer.send(f"Write a 200-word article about: {topic}")
    print(f"Draft complete ({len(draft)} chars)")
    
    # Step 2: Editor refines the draft
    print("\n✏️ Editor refining...")
    editor = create_editor()
    final = editor.send(f"Edit and improve this article:\n\n{draft}")
    print(f"Editing complete ({len(final)} chars)")
    
    return final


if __name__ == "__main__":
    import sys
    
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python async programming"
    
    print(f"🚀 Starting flow for topic: {topic}\n")
    result = run_flow(topic)
    
    print("\n" + "=" * 50)
    print("📄 FINAL ARTICLE:")
    print("=" * 50)
    print(result)
```

Run your flow:

```bash
python main.py "Introduction to LangGraph"
```

---

## Step 4: Add Configuration with YAML

Create `agents.yaml` for configurable defaults:

```yaml
# agents.yaml - Agent configuration for my flow
defaults:
  writer:
    provider: claude
    model: balanced
  editor:
    provider: claude
    model: balanced

settings:
  max_retries: 2
  timeout: 120
```

Update your Python code to use the config:

```python
from determinagent import UnifiedAgent, SessionManager, load_config

def create_agents_from_config():
    """Load agents from YAML configuration."""
    config = load_config("agents.yaml")
    
    writer_cfg = config["defaults"]["writer"]
    editor_cfg = config["defaults"]["editor"]
    
    writer = UnifiedAgent(
        provider=writer_cfg["provider"],
        model=writer_cfg["model"],
        role="writer",
        instructions="...",  # Your instructions
        session=SessionManager(writer_cfg["provider"]),
    )
    
    editor = UnifiedAgent(
        provider=editor_cfg["provider"],
        model=editor_cfg["model"],
        role="editor",
        instructions="...",
        session=SessionManager(editor_cfg["provider"]),
    )
    
    return writer, editor
```

---

## Step 5: Add CLI Arguments

Make your flow user-friendly with argparse:

```python
#!/usr/bin/env python3
"""My First Flow - with CLI arguments."""

import argparse
from determinagent import UnifiedAgent, SessionManager


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Writer → Editor pipeline"
    )
    parser.add_argument(
        "topic",
        help="Topic to write about"
    )
    parser.add_argument(
        "--writer-provider",
        default="claude",
        choices=["claude", "copilot", "gemini", "codex"],
        help="Provider for the Writer agent"
    )
    parser.add_argument(
        "--editor-provider",
        default="claude",
        choices=["claude", "copilot", "gemini", "codex"],
        help="Provider for the Editor agent"
    )
    parser.add_argument(
        "--model",
        default="balanced",
        choices=["fast", "balanced", "powerful"],
        help="Model tier to use"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    writer = UnifiedAgent(
        provider=args.writer_provider,
        model=args.model,
        role="writer",
        instructions="You are a skilled writer.",
        session=SessionManager(args.writer_provider),
    )
    
    editor = UnifiedAgent(
        provider=args.editor_provider,
        model=args.model,
        role="editor",
        instructions="You are a meticulous editor.",
        session=SessionManager(args.editor_provider),
    )
    
    print(f"📝 Writing about: {args.topic}")
    draft = writer.send(f"Write a 200-word article about: {args.topic}")
    
    print("✏️ Editing...")
    final = editor.send(f"Improve this article:\n\n{draft}")
    
    print("\n" + "=" * 50)
    print(final)


if __name__ == "__main__":
    main()
```

Now you can run with different providers:

```bash
python main.py "Async Python" --writer-provider claude --editor-provider copilot
```

---

## Step 6: Add Error Handling

DeterminAgent provides a unified exception hierarchy:

```python
from determinagent import (
    UnifiedAgent,
    SessionManager,
    # Exceptions
    DeterminAgentError,
    ProviderNotAvailable,
    ProviderAuthError,
    TimeoutError,
    RateLimitExceeded,
)


def safe_send(agent: UnifiedAgent, prompt: str) -> str | None:
    """Send prompt with comprehensive error handling."""
    try:
        return agent.send(prompt, timeout=120)
    
    except ProviderNotAvailable as e:
        print(f"❌ CLI tool not found: {e}")
        print("   Install the CLI and add to PATH")
        return None
    
    except ProviderAuthError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Run 'claude login' or equivalent")
        return None
    
    except TimeoutError as e:
        print(f"⏱️ Request timed out: {e}")
        return None
    
    except RateLimitExceeded as e:
        print(f"🚦 Rate limit hit: {e}")
        return None
    
    except DeterminAgentError as e:
        print(f"❌ Agent error: {e}")
        return None
```

---

## Step 7: Add LangGraph State Machine (Advanced)

For complex workflows, use LangGraph for state management:

```python
#!/usr/bin/env python3
"""Advanced Flow with LangGraph State Machine."""

from typing import TypedDict
from langgraph.graph import StateGraph, END
from determinagent import UnifiedAgent, SessionManager


class FlowState(TypedDict):
    """State passed between nodes."""
    topic: str
    draft: str
    edited: str
    revision_count: int
    approved: bool


def writer_node(state: FlowState) -> FlowState:
    """Writer creates the initial draft."""
    writer = UnifiedAgent(
        provider="claude",
        model="balanced",
        role="writer",
        instructions="""You are a skilled technical writer.
        Write clear, engaging content with proper structure.
        Use markdown formatting for headers and code blocks.""",
        session=SessionManager("claude"),
    )
    
    draft = writer.send(f"Write a 200-word article about: {state['topic']}")
    return {**state, "draft": draft}


def editor_node(state: FlowState) -> FlowState:
    """Editor reviews and improves the draft."""
    editor = UnifiedAgent(
        provider="claude",
        model="balanced",
        role="editor",
        instructions="""You are a meticulous editor.
        Review content for clarity, grammar, and structure.
        Provide the improved version directly, not just suggestions.""",
        session=SessionManager("claude"),
    )
    
    edited = editor.send(f"Edit this article:\n\n{state['draft']}")
    return {
        **state,
        "edited": edited,
        "revision_count": state["revision_count"] + 1,
    }


def review_decision(state: FlowState) -> str:
    """Decide: approve or revise again."""
    # Auto-approve after 2 revisions (customize as needed)
    if state["revision_count"] >= 2:
        return "approve"
    
    # In practice, you'd have a reviewer agent or human check
    return "approve"


# Build the graph
workflow = StateGraph(FlowState)

# Add nodes
workflow.add_node("write", writer_node)
workflow.add_node("edit", editor_node)

# Add edges
workflow.set_entry_point("write")
workflow.add_edge("write", "edit")
workflow.add_conditional_edges(
    "edit",
    review_decision,
    {
        "approve": END,
        "revise": "write",  # Loop back to writer
    }
)

# Compile
app = workflow.compile()


def run_langgraph_flow(topic: str) -> str:
    """Run the LangGraph-based flow."""
    initial_state: FlowState = {
        "topic": topic,
        "draft": "",
        "edited": "",
        "revision_count": 0,
        "approved": False,
    }
    
    result = app.invoke(initial_state)
    return result["edited"]


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "Introduction to DeterminAgent"
    
    print(f"🚀 Running LangGraph flow: {topic}\n")
    final = run_langgraph_flow(topic)
    print("\n📄 Final Article:\n")
    print(final)
```

---

## Next Steps

Congratulations! You've built your first DeterminAgent flow. Here's what to explore next:

1. **Study the Blog Flow**: See `flows/blog/` for a production-ready example with human review loops.

2. **Try Different Providers**: Mix providers for different roles (e.g., Claude for writing, Copilot for code).

3. **Add Structured Output**: Use `agent.send_structured()` with Pydantic models for typed responses.

4. **Explore Session Management**: Use the same session across a conversation for context continuity.

---

## Resources

- **[Architecture](../architecture.md)**: Deep dive into the library internals
- **[CLI Reference](../cli-reference.md)**: Provider-specific flag mappings
- **[API Documentation](../api/index.md)**: Full API reference
- **[Blog Flow Example](https://github.com/determinagent/determinagent/tree/main/flows/blog)**: Complete production flow

---

*Need help? Open an issue on [GitHub](https://github.com/determinagent/determinagent/issues).*
