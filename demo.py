"""
demo.py — End-to-end RAG demo for the LA Parks Unofficial Guide.

Runs all 5 evaluation-plan queries through the full pipeline
(retrieval → grounded generation) and prints:
  - the query
  - retrieved chunks with source names, chunk positions, and distances
  - the generated answer
  - the source list
  - a grounding check flag

Grounding check heuristic:
  A result is flagged as a POTENTIAL GROUNDING ISSUE if:
    (a) the answer is not the standard "insufficient info" refusal, AND
    (b) all 5 retrieved chunks have cosine distance > 0.50
        (weak retrieval → the model had little relevant context to draw from,
        increasing the risk that it filled gaps with outside knowledge).
  This is a signal to manually inspect the answer, not a definitive verdict.

Run:
    python demo.py
"""

from query import INSUFFICIENT_ANSWER, rag

# All 5 queries from the Evaluation Plan in planning.md.
EVAL_QUERIES = [
    "Which LA parks are recommended for scenic views?",
    "Which parks are recommended for picnics?",
    "Which parks seem good for relaxing or hanging out alone?",
    "What are some differences between official park information and user review information?",
    "Which park is best for someone who wants a beach park with views?",
]

# Cosine-distance threshold above which retrieval is considered weak.
# When all top-k chunks exceed this, the model had marginal context and the
# answer is more likely to contain outside-knowledge fill-ins.
WEAK_RETRIEVAL_THRESHOLD = 0.50


def grounding_check(result: dict) -> str:
    """
    Return a one-line grounding verdict for a rag() result.

    Returns "OK" or a warning string explaining the concern.
    """
    answer = result["answer"]
    sources = result["sources"]

    # If the model properly declined, grounding is fine by definition.
    if answer.strip().startswith(INSUFFICIENT_ANSWER[:20]):
        return "OK — model correctly declined (insufficient sources)"

    # Check whether ALL retrieved chunks were weak matches.
    distances = [s["distance"] for s in sources]
    if all(d > WEAK_RETRIEVAL_THRESHOLD for d in distances):
        worst = round(max(distances), 4)
        return (
            f"POTENTIAL GROUNDING ISSUE — all {len(sources)} chunks have distance "
            f"> {WEAK_RETRIEVAL_THRESHOLD} (worst: {worst}). "
            "Verify that the answer comes only from retrieved text."
        )

    return "OK"


def print_result(result: dict) -> None:
    """Print a single rag() result with chunks, answer, sources, and grounding check."""
    print(f"\n{'=' * 72}")
    print(f"QUERY: {result['query']}")
    print("=" * 72)

    # Retrieved chunks
    print("\nRETRIEVED CHUNKS:")
    for i, s in enumerate(result["sources"], 1):
        print(
            f"  [{i}] {s['source_name']}  chunk={s['chunk_index']}  "
            f"distance={s['distance']}"
        )
        print(f"       {s['source_url']}")
        preview = s["text"][:220]
        if len(s["text"]) > 220:
            preview += "..."
        print(f"       {preview}")

    # Generated answer
    print(f"\nGENERATED ANSWER:\n{result['answer']}")

    # Source list — built from retrieved chunks, not from LLM output
    print("\nSOURCE LIST (programmatic attribution):")
    seen = {}
    for s in result["sources"]:
        key = s["source_name"]
        if key not in seen:
            seen[key] = s["source_url"]
    for name, url in seen.items():
        print(f"  • {name}: {url}")

    # Grounding check
    verdict = grounding_check(result)
    print(f"\nGROUNDING CHECK: {verdict}")


if __name__ == "__main__":
    print("Running end-to-end RAG demo on all 5 evaluation-plan queries...\n")
    print("(chroma_db/ must already exist — run 'python embed.py' first if not)\n")

    for query in EVAL_QUERIES:
        result = rag(query)
        print_result(result)

    print(f"\n{'=' * 72}")
    print("Demo complete.")
    print("\nOther ways to run:")
    print('  Single query:       python query.py --query "your question"')
    print("  Gradio interface:   python app.py")
