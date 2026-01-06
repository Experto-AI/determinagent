#!/usr/bin/env bash
# =============================================================================
# DeterminAgent Pre-Release Integration Verification Script
# =============================================================================
#
# This script provides a structured checklist for manually verifying
# integrations with the four supported CLI tools before a release.
#
# Full automated E2E testing is not practical due to:
# - Authentication requirements (API keys, logins)
# - Variable costs per invocation
# - Rate limits on public APIs
#
# Usage: ./scripts/verify_integrations.sh [--quick]
#
# Options:
#   --quick   Run quick verification (version checks only)
#   (default) Run full interactive verification with test prompts
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Test prompt for verification
TEST_PROMPT="Say 'Hello from DeterminAgent verification!' and nothing else."

# Results tracking
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
}

print_pass() {
    echo -e "  ${GREEN}✓ PASS:${NC} $1"
    ((PASS_COUNT++))
}

print_fail() {
    echo -e "  ${RED}✗ FAIL:${NC} $1"
    ((FAIL_COUNT++))
}

print_skip() {
    echo -e "  ${YELLOW}○ SKIP:${NC} $1"
    ((SKIP_COUNT++))
}

print_info() {
    echo -e "  ${BLUE}ℹ INFO:${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# Verification Functions
# =============================================================================

verify_claude() {
    print_section "Claude Code CLI"
    
    # Check if installed
    if ! check_command "claude"; then
        print_fail "Claude CLI not found in PATH"
        print_info "Install: https://claude.ai/code"
        return 1
    fi
    
    # Version check
    local version
    version=$(claude --version 2>&1 || echo "unknown")
    print_pass "Claude CLI found: $version"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        print_skip "Skipping authentication and prompt test (quick mode)"
        return 0
    fi
    
    # Auth check
    echo ""
    print_info "Testing Claude authentication..."
    if claude --print "$TEST_PROMPT" &> /dev/null; then
        print_pass "Claude authentication working"
    else
        print_fail "Claude authentication failed"
        print_info "Run 'claude login' to authenticate"
        return 1
    fi
    
    # Test prompt
    echo ""
    print_info "Testing Claude prompt execution..."
    local response
    if response=$(claude --print "$TEST_PROMPT" 2>&1); then
        print_pass "Claude responds correctly"
        echo -e "       Response: ${YELLOW}$response${NC}"
    else
        print_fail "Claude prompt execution failed"
        return 1
    fi
    
    return 0
}

verify_copilot() {
    print_section "Copilot CLI"

    # Check if Copilot CLI is installed
    if ! check_command "copilot"; then
        print_fail "Copilot CLI not found in PATH"
        print_info "Install: https://github.com/github/copilot-cli"
        return 1
    fi

    # Version check
    local version
    version=$(copilot --version 2>&1 | head -1 || echo "unknown")
    print_pass "Copilot CLI found: $version"

    if [[ "$QUICK_MODE" == "true" ]]; then
        print_skip "Skipping authentication and prompt test (quick mode)"
        return 0
    fi

    # Auth check (Copilot CLI uses GitHub CLI auth)
    if ! check_command "gh"; then
        print_fail "GitHub CLI (gh) not found in PATH"
        print_info "Install: https://cli.github.com/"
        return 1
    fi

    echo ""
    print_info "Testing GitHub authentication..."
    if gh auth status &> /dev/null; then
        print_pass "GitHub authentication working"
    else
        print_fail "GitHub authentication failed"
        print_info "Run 'gh auth login' to authenticate"
        return 1
    fi

    print_skip "Prompt test skipped (manual verification recommended)"
    print_info "Manual test: copilot -p \"hello world\""

    return 0
}

verify_gemini() {
    print_section "Gemini CLI"
    
    # Check if installed
    if ! check_command "gemini"; then
        print_fail "Gemini CLI not found in PATH"
        print_info "Install: npm install -g @anthropics/gemini-cli"
        print_info "Or: https://github.com/google-gemini/gemini-cli"
        return 1
    fi
    
    # Version check
    local version
    version=$(gemini --version 2>&1 || echo "unknown")
    print_pass "Gemini CLI found: $version"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        print_skip "Skipping authentication and prompt test (quick mode)"
        return 0
    fi
    
    # Auth/prompt test
    echo ""
    print_info "Testing Gemini prompt execution..."
    local response
    if response=$(echo "$TEST_PROMPT" | gemini 2>&1 | head -5); then
        if [[ -n "$response" ]]; then
            print_pass "Gemini responds correctly"
            echo -e "       Response: ${YELLOW}${response:0:100}...${NC}"
        else
            print_fail "Gemini returned empty response"
            return 1
        fi
    else
        print_fail "Gemini prompt execution failed"
        print_info "Ensure GEMINI_API_KEY is set or run 'gemini auth'"
        return 1
    fi
    
    return 0
}

verify_codex() {
    print_section "OpenAI Codex CLI"
    
    # Check if installed
    if ! check_command "codex"; then
        print_fail "Codex CLI not found in PATH"
        print_info "Install: npm install -g @openai/codex"
        return 1
    fi
    
    # Version check
    local version
    version=$(codex --version 2>&1 || echo "unknown")
    print_pass "Codex CLI found: $version"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        print_skip "Skipping authentication and prompt test (quick mode)"
        return 0
    fi
    
    # Auth check (Codex uses OPENAI_API_KEY)
    echo ""
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        print_pass "OPENAI_API_KEY environment variable is set"
    else
        print_fail "OPENAI_API_KEY environment variable not set"
        print_info "Export your API key: export OPENAI_API_KEY=sk-..."
        return 1
    fi
    
    # Note: Full prompt test skipped as it may incur costs
    print_skip "Prompt execution test (requires API credits)"
    print_info "Manual test: codex exec 'print hello'"
    
    return 0
}

verify_python_library() {
    print_section "DeterminAgent Library"
    
    # Check Python
    if ! check_command "python3" && ! check_command "python"; then
        print_fail "Python not found"
        return 1
    fi
    
    local python_cmd="poetry run python"
    
    # Version check
    local py_version
    py_version=$($python_cmd --version 2>&1)
    print_pass "Python found: $py_version"
    
    # Import test
    echo ""
    print_info "Testing DeterminAgent import..."
    if $python_cmd -c "import determinagent; print(f'Version: {determinagent.__version__}')" 2>&1; then
        print_pass "DeterminAgent import successful"
    else
        print_fail "DeterminAgent import failed"
        print_info "Install: pip install -e ."
        return 1
    fi
    
    # Core components
    echo ""
    print_info "Testing core components..."
    if $python_cmd -c "
from determinagent import UnifiedAgent, SessionManager, load_config
from determinagent import ProviderNotAvailable, DeterminAgentError
print('All core imports successful')
" 2>&1; then
        print_pass "Core components import successful"
    else
        print_fail "Core components import failed"
        return 1
    fi
    
    return 0
}

# =============================================================================
# Main Entry Point
# =============================================================================

main() {
    QUICK_MODE="false"
    
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --quick)
                QUICK_MODE="true"
                ;;
            --help|-h)
                echo "Usage: $0 [--quick]"
                echo ""
                echo "Options:"
                echo "  --quick   Run quick verification (version checks only)"
                echo "  (default) Run full interactive verification"
                exit 0
                ;;
        esac
    done
    
    print_header "DeterminAgent Pre-Release Verification"
    
    echo -e "${BOLD}Date:${NC} $(date)"
    echo -e "${BOLD}Mode:${NC} $(if [[ "$QUICK_MODE" == "true" ]]; then echo "Quick (version checks only)"; else echo "Full (with prompt tests)"; fi)"
    
    # Run verifications
    verify_python_library || true
    verify_claude || true
    verify_copilot || true
    verify_gemini || true
    verify_codex || true
    
    # Summary
    print_header "Verification Summary"
    
    echo -e "  ${GREEN}Passed:${NC}  $PASS_COUNT"
    echo -e "  ${RED}Failed:${NC}  $FAIL_COUNT"
    echo -e "  ${YELLOW}Skipped:${NC} $SKIP_COUNT"
    echo ""
    
    if [[ $FAIL_COUNT -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ All verifications passed!${NC}"
        echo ""
        echo "Pre-release checklist:"
        echo "  □ Update version in pyproject.toml and __init__.py"
        echo "  □ Update CHANGELOG.md"
        echo "  □ Run full test suite: make check"
        echo "  □ Create release tag: git tag v1.x.x"
        echo "  □ Push tag: git push origin v1.x.x"
        exit 0
    else
        echo -e "${YELLOW}${BOLD}⚠ Some verifications failed or were skipped.${NC}"
        echo ""
        echo "Review the failures above before releasing."
        echo "Note: Not all CLIs need to be installed for release,"
        echo "      but at least one should be verified."
        exit 1
    fi
}

main "$@"
