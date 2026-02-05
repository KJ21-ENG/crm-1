# Documentation Build Script

#!/bin/bash

# Build documentation using MkDocs
# Usage: ./build_docs.sh [serve|build|deploy]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DOCS_DIR")"

cd "$PROJECT_ROOT"

# Install dependencies if needed
check_dependencies() {
    if ! command -v mkdocs &> /dev/null; then
        echo "Installing MkDocs..."
        pip install mkdocs mkdocs-material
    fi
}

# Build static site
build() {
    echo "Building documentation..."
    mkdocs build
    echo "Documentation built to site/ directory"
}

# Serve locally for development
serve() {
    echo "Starting local documentation server..."
    echo "Access at http://localhost:8001"
    mkdocs serve -a localhost:8001
}

# Deploy to GitHub Pages
deploy() {
    echo "Deploying to GitHub Pages..."
    mkdocs gh-deploy
    echo "Documentation deployed"
}

# Main
check_dependencies

case "${1:-build}" in
    serve)
        serve
        ;;
    build)
        build
        ;;
    deploy)
        deploy
        ;;
    *)
        echo "Usage: $0 [serve|build|deploy]"
        exit 1
        ;;
esac
