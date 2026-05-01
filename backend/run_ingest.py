"""Runner script to call ingestion with correct sys.path."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from scripts.ingest_docs import main

# Override sys.argv before calling main
sys.argv = [
    "run_ingest.py",
    "--source", "../docs",
    "--collection", "graph_ai_tutor_knowledge",
    "--reset",
    "--smoke-check",
    "--embedding-model", "gemini-embedding-001",
]
main()