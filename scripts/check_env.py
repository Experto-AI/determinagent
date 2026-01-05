#!/usr/bin/env python3
"""
Environment Check Script for DeterminAgent.

This script checks for the presence of required CLI tools and dependencies.
Run this to verify your environment is ready for DeterminAgent workflows.
"""

import shutil
import sys
import subprocess
from typing import NamedTuple

class ToolCheck(NamedTuple):
    name: str
    cmd: str
    install_url: str
    critical: bool = True

TOOLS = [
    ToolCheck(
        "Python 3", "python3", "https://python.org", critical=True
    ),
    ToolCheck(
        "Claude Code", "claude", "https://docs.anthropic.com/en/docs/claude-code", critical=False
    ),
    ToolCheck(
        "GitHub CLI", "gh", "https://cli.github.com/", critical=False
    ),
    ToolCheck(
        "Gemini CLI", "gemini", "https://pypi.org/project/google-generativeai/", critical=False
    ),
    ToolCheck(
        "OpenAI Codex", "codex", "https://platform.openai.com/docs/guides/codex", critical=False
    ),
]

def check_tool(tool: ToolCheck) -> bool:
    """Check if a tool is installed and accessible."""
    path = shutil.which(tool.cmd)
    
    if path:
        print(f"✅ {tool.name:<12} Found at: {path}")
        return True
    else:
        status = "MISSING"
        if tool.critical:
            status = "CRITICAL MISSING"
        print(f"❌ {tool.name:<12} {status}")
        print(f"   -> Install instructions: {tool.install_url}")
        return False

def main():
    print("🔍 Checking DeterminAgent Environment...\n")
    
    all_passed = True
    missing_optional = False
    
    for tool in TOOLS:
        found = check_tool(tool)
        if not found:
            if tool.critical:
                all_passed = False
            else:
                missing_optional = True
                
    print("\n" + "-"*40 + "\n")
    
    if not all_passed:
        print("❌ Critical dependencies are missing. Please install them before proceeding.")
        sys.exit(1)
    
    if missing_optional:
        print("⚠️  Some optional providers are missing. You can only use providers that are installed.")
        print("   (e.g., if you don't have 'claude', you can't use the Claude Code provider)")
    else:
        print("✨ All systems go! Your environment is fully ready.")
        
    sys.exit(0)

if __name__ == "__main__":
    main()
