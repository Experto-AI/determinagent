# Security Policy

## Responsible Disclosure

If you discover a security vulnerability in DeterminAgent, please **do not** open a public issue. Instead, please report it privately to [INSERT EMAIL ADDRESS].

We will acknowledge your report within 48 hours and provide a timeline for addressing the issue.

## Security Model & Risks

DeterminAgent is a library that orchestrates AI CLI tools via subprocesses. This architecture introduces specific security considerations.

### 1. Subprocess Execution

The library calls external binaries (e.g., `claude`, `gh`, `gemini`). 
- **Risk**: If a provider name or command argument is maliciously constructed, it could lead to arbitrary command execution.
- **Mitigation**: We use `subprocess.run` with list-based arguments instead of shell strings where possible. We validate provider names against a whitelist of supported adapters.

### 2. Prompt Injection

As with any LLM-based system, DeterminAgent is susceptible to prompt injection.
- **Risk**: An untrusted input (e.g., a blog topic or user feedback) could contain instructions that trick the underlying AI model into ignoring its system prompt or performing unintended actions.
- **Mitigation**: We provide structured system prompts and use LangGraph to enforce a deterministic state machine. However, the library currently treats the output of providers as untrusted data.

### 3. Local Environment Security

DeterminAgent relies on the security of the local environment and the installed CLI tools.
- **Risk**: Malicious CLI tools or compromised local sessions could expose sensitive data.
- **Mitigation**: Users should only use DeterminAgent with trusted CLI tools and within secure environments.

## Reporting a Vulnerability

When reporting a vulnerability, please include:
- A description of the issue.
- A proof-of-concept or steps to reproduce.
- Potential impact.
- Any suggested remediations.

## Supported Versions

Currently, we only provide security updates for the latest stable release.

| Version | Supported          |
| ------- | ------------------ |
| 0.10.x  | :white_check_mark: |
| < 0.10.0| :x:                |
