#!/bin/bash
set -e

# docs.sh - Helper script for building and serving documentation

COMMAND=$1
PORT=${2:-8000}

function show_help {
    echo "Usage: ./scripts/docs.sh [command] [port]"
    echo ""
    echo "Commands:"
    echo "  build         Build the documentation (strict mode)"
    echo "  serve [port]  Serve the documentation locally (default: 8000)"
    echo "  help          Show this help message"
}

if [ -z "$COMMAND" ]; then
    show_help
    exit 1
fi

case $COMMAND in
    build)
        echo "🏗️  Building documentation..."
        poetry run mkdocs build
        ;;
    serve)
        echo "🚀 Serving documentation at http://127.0.0.1:$PORT"
        poetry run mkdocs serve -a 127.0.0.1:$PORT
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
