#!/bin/bash
# Linting and formatting scripts for the backend

set -e

case "$1" in
    lint)
        echo "Running flake8..."
        flake8 src tests
        ;;
    format)
        echo "Running black and isort..."
        black src tests
        isort src tests
        ;;
    check-format)
        echo "Checking formatting..."
        black --check src tests
        isort --check-only src tests
        ;;
    typecheck)
        echo "Running mypy..."
        mypy src
        ;;
    all)
        echo "Running all checks..."
        flake8 src tests
        black --check src tests
        isort --check-only src tests
        mypy src
        ;;
    *)
        echo "Usage: $0 {lint|format|check-format|typecheck|all}"
        exit 1
        ;;
esac
