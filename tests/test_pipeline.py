import os
import json 
from src.retrieve import retrieve
from src.generate import generate_answer

def test_retrieval_returns_results();
    results = retrieve('operating system', top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0
    assert 'book_id' in results[0]
    assert 'chunk_id' in results[0]

def test_generation_structure():
    response = generate_answer("What is a computer network?")
    assert "answer" in response
    assert "sources" in response
    assert "insufficient_evidence" in response
    if not response["insufficient_evidence"]:
        assert len(response["sources"]) > 0
    