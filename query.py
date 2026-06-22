"""
query.py — Generation layer for the LA Parks Unofficial Guide RAG pipeline.

Connects the retrieval layer (embed.retrieve) to the Groq Llama LLM.
The grounded prompt tells the model to answer only from the provided source
documents and to say "I don't have enough information on that." when the
documents are insufficient.

Usage:
    python query.py                                    # run 3 eval queries end-to-end
    python query.py --query "Which parks have views?"  # single custom query
"""

import argparse
import os

from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()  # reads GROQ_API_KEY from .env

GROQ_MODEL = "llama-3.3-70b-versatile"
K = 5  # number of chunks to retrieve per query, per planning.md spec

# Exact phrase the model must use when it cannot answer from the sources.
# Defined as a constant so the demo can detect it programmatically.
INSUFFICIENT_ANSWER = "I don't have enough information on that."


def build_prompt(query: str, chunks: list[dict]) -> tuple[str, str]:
    """
    Assemble the system and user messages for a grounded generation call.

    Grounding is enforced two ways:
      1. The system message explicitly forbids using outside knowledge and
         specifies the exact phrase to use when sources are insufficient.
      2. Each chunk is labeled [SOURCE 1] … [SOURCE N] so the model has
         clear numbered references — this reduces hallucinated specifics
         because the model can point to evidence rather than invent it.

    Returns:
        (system_message, user_message) — passed as separate chat roles.
    """
    # Build the numbered context block from retrieved chunks.
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[SOURCE {i}] {chunk['source_name']} (chunk {chunk['chunk_index']})\n"
            f"{chunk['text']}"
        )
    context = "\n\n".join(context_parts)

    # System message — grounding rule is stated explicitly and the fallback
    # phrase is quoted verbatim so the model knows exactly what to produce.
    system = (
        "You are a helpful assistant that answers questions about parks in the "
        "Los Angeles area.\n\n"
        "STRICT GROUNDING RULE: Answer ONLY using the source documents provided "
        "in the user message. Do not use any outside knowledge, training data, or "
        "information not present in those documents. If the provided sources do not "
        "contain enough information to answer the question, respond with exactly:\n"
        f'"{INSUFFICIENT_ANSWER}"\n\n'
        "When answering, you may reference sources by their [SOURCE N] label. "
        "Keep answers concise and directly responsive to the question."
    )

    # User message — retrieved context comes first, then the question.
    # Separating them makes it clear which text is evidence vs. the task.
    user = (
        f"Source documents:\n\n"
        f"{context}\n\n"
        f"Question: {query}"
    )

    return system, user


def generate_answer(query: str, chunks: list[dict]) -> str:
    """
    Send the grounded prompt to Groq Llama and return the answer text.

    Args:
        query:  The user's question string.
        chunks: Retrieved chunks from embed.retrieve() — used to build context.

    Returns:
        The model's answer as a plain string.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not found. Add it to .env.")

    client = Groq(api_key=api_key)
    system, user = build_prompt(query, chunks)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.2,   # low temperature reduces invented/creative additions
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()


def rag(query: str, k: int = K) -> dict:
    """
    Full RAG pipeline: retrieve → generate → return answer + sources.

    Source attribution is guaranteed programmatically: the sources list is
    built from the retrieved chunks in Python before and after generation.
    Even if the LLM omits citations, the caller always receives the full
    source list attached to the answer.

    Args:
        query: The user's natural-language question.
        k:     Number of chunks to retrieve (default 5, per planning.md).

    Returns:
        {
            "query":   str,
            "answer":  str,        — grounded LLM answer
            "sources": list[dict]  — retrieved chunks with all metadata
        }
    """
    # Step 1 — retrieve the top-k most relevant chunks from ChromaDB.
    chunks = retrieve(query, k=k)

    # Step 2 — generate a grounded answer using only those chunks as context.
    answer = generate_answer(query, chunks)

    # Step 3 — return answer + source list.
    # The sources list is constructed here in Python from the retrieved chunks,
    # not extracted from the LLM output. Attribution is guaranteed regardless
    # of whether the model remembered to cite in its answer text.
    return {
        "query":   query,
        "answer":  answer,
        "sources": chunks,
    }


def _print_rag_result(result: dict) -> None:
    """Pretty-print a single rag() result for CLI / demo use."""
    print(f"\n{'=' * 72}")
    print(f"QUERY: {result['query']}")
    print("=" * 72)

    print(f"\nANSWER:\n{result['answer']}")

    print("\nSOURCES (retrieved chunks):")
    for i, s in enumerate(result["sources"], 1):
        print(
            f"  [{i}] {s['source_name']}  chunk={s['chunk_index']}  "
            f"distance={s['distance']}"
        )
        print(f"       {s['source_url']}")
        preview = s["text"][:200]
        if len(s["text"]) > 200:
            preview += "..."
        print(f"       {preview}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the full LA Parks RAG pipeline."
    )
    parser.add_argument("--query", type=str, help="A single question to answer.")
    args = parser.parse_args()

    if args.query:
        _print_rag_result(rag(args.query))
    else:
        # Default: run 3 of the 5 evaluation-plan queries as a quick smoke test.
        test_queries = [
            "Which LA parks are recommended for scenic views?",
            "Which parks are recommended for picnics?",
            "Which park is best for someone who wants a beach park with views?",
        ]
        for q in test_queries:
            _print_rag_result(rag(q))
