# Blog Writer Flow

Multi-agent blog generation with AI revision loops and human review.

---

## Quick Start

```bash
python main.py "Your Topic" --provider claude
```

## Usage

```bash
# Use same provider for all agents
python main.py "AI Agents" --provider claude

# Use different providers per role
python main.py "Kubernetes" --writer-provider claude --editor-provider copilot --reviewer-provider claude

# Configure word count and revisions
python main.py "DevOps" --min-words 1000 --max-words 1500 --max-revisions 5
```

## Workflow

![Blog Workflow](https://raw.githubusercontent.com/Experto-AI/determinagent/main/docs/assets/blog_flow.svg)

## Configuration

Edit `main.yaml` to customize defaults:

```yaml
defaults:
  writer:
    provider: claude
    model: balanced
  editor:
    provider: copilot
    model: fast
  reviewer:
    provider: claude
    model: balanced

word_count:
  min: 800
  max: 1200

review:
  max_revisions: 3
```

## CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `topic` | (required) | Blog post topic |
| `--provider` | - | Use same provider for all agents |
| `--writer-provider` | claude | Provider for writer |
| `--editor-provider` | copilot | Provider for editor |
| `--reviewer-provider` | claude | Provider for reviewer |
| `--min-words` | 800 | Minimum word count |
| `--max-words` | 1200 | Maximum word count |
| `--max-revisions` | 3 | Max AI revision attempts |

## Output

Saves to: `YYYY-MM-DD-blog-<topic>.md` in current directory.

---

*Part of [DeterminAgent](https://github.com/Experto-AI/determinagent) template flows.*
