#!/usr/bin/env python3
"""
Scripts for optimizing and analyzing game code.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def analyze_file(filepath: str) -> None:
    """
    Analyze a Python file for code metrics.

    Args:
        filepath: Path to the Python file to analyze
    """
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    with open(path, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    classes = []
    functions = []
    methods_per_class = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
            classes.append(node.name)
            methods_per_class[node.name] = method_count

        if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
            functions.append(node.name)

    print(f"\n{'=' * 60}")
    print(f"Analysis: {path.name}")
    print(f"{'=' * 60}")
    print(f"Total lines: {len(source.splitlines())}")
    print(f"Classes: {len(classes)}")
    for cls, count in methods_per_class.items():
        print(f"  - {cls}: {count} methods")
    print(f"Module functions: {len(functions)}")

    # Find long methods
    print("\nLong methods (>50 lines):")
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            lines = node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
            if lines > 50:
                print(f"  - {node.name}: {lines} lines")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze.py <file.py>")
        sys.exit(1)

    analyze_file(sys.argv[1])


if __name__ == "__main__":
    main()
