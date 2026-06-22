"""
embed.py — Embedding and vector store for the LA Parks Unofficial Guide.

Loads chunks from chunks.json, encodes each one with sentence-transformers
(all-MiniLM-L6-v2), and stores embeddings in a persistent ChromaDB collection.

Usage:
    python embed.py                                        # embed and store all chunks
    python embed.py --query "Which parks are best for picnics?"   # embed + test retrieval
"""

import argparse
import hashlib
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("chunks.json")
CHROMA_DIR = Path("chroma_db")           # ChromaDB persists to this directory on disk
COLLECTION_NAME = "la_parks"
EMBED_MODEL = "all-MiniLM-L6-v2"


def _chunk_id(text: str) -> str:
    """
    Derive a stable ID from the chunk text itself (first 16 hex chars of SHA-1).

    Using a content hash rather than a sequential index means the same chunk
    always gets the same ID even if chunks.json is regenerated or reordered.
    This makes upsert truly idempotent: re-running embed.py never creates
    duplicates and never mis-assigns an old ID to different content.
    """
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def _get_collection(client):
    """
    Return (or create) the ChromaDB collection for LA Parks.

    get_or_create_collection:
      - Creates a new collection the first time the script runs.
      - Returns the existing collection on every subsequent run without
        clearing it — so previously stored embeddings are preserved.

    metadata={"hnsw:space": "cosine"}:
      - Tells ChromaDB to use cosine similarity for its HNSW index.
      - Cosine similarity is appropriate for sentence embeddings because it
        measures the angle between vectors (semantic direction) rather than
        their absolute magnitude, which is what all-MiniLM-L6-v2 is trained for.
    """
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def embed_and_store(chunks: list | None = None) -> chromadb.Collection:
    """
    Encode all chunks with all-MiniLM-L6-v2 and upsert them into ChromaDB.

    Args:
        chunks: Optional list of chunk dicts. If None, loads from chunks.json.

    Returns:
        The ChromaDB collection (already populated).
    """
    if chunks is None:
        chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    print(f"Encoding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]

    # batch_size=64 keeps memory usage reasonable; show_progress_bar gives
    # feedback since encoding 664 chunks takes ~10–15 seconds on CPU.
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    # PersistentClient writes the vector index to chroma_db/ on disk so
    # embeddings survive between Python sessions — no need to re-embed on
    # every run.
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = _get_collection(client)

    # Build stable IDs and metadata lists aligned with the texts list.
    # chunk_index tracks how many chunks we have seen from each source so far,
    # giving each chunk its position within its source document (0-based).
    ids = [_chunk_id(text) for text in texts]
    source_counters: dict[str, int] = {}
    metadatas = []
    for c in chunks:
        src = c["source_name"]
        idx = source_counters.get(src, 0)
        source_counters[src] = idx + 1
        metadatas.append(
            {
                "source_name":  c["source_name"],
                "source_type":  c["source_type"],
                "source_url":   c["source_url"],
                "chunk_index":  idx,   # position of this chunk within its source
            }
        )

    # upsert vs add:
    #   collection.add()    — fails with an error if any ID already exists.
    #   collection.upsert() — inserts new IDs and overwrites existing ones.
    # upsert is the right choice here because re-running the script after a
    # chunking fix should silently refresh every chunk rather than crash.
    collection.upsert(
        ids=ids,
        embeddings=embeddings.tolist(),  # ChromaDB expects plain Python lists
        documents=texts,                 # stored as the retrievable text
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB at '{CHROMA_DIR}'")
    return collection


def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Encode a query string and return the top-k most similar chunks.

    Args:
        query: Natural-language question or search phrase.
        k:     Number of results to return (default 5, per planning.md spec).

    Returns:
        List of dicts with keys: text, source_name, source_type, source_url,
        chunk_index, distance.
        chunk_index is the 0-based position of the chunk within its source document.
        Distance is the cosine distance (0 = identical, 2 = opposite).
        Lower distance → more relevant chunk.
    """
    model = SentenceTransformer(EMBED_MODEL)
    query_embedding = model.encode([query])[0]

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = _get_collection(client)

    # collection.query():
    #   query_embeddings: the encoded query vector (wrapped in a list because
    #     ChromaDB supports batch queries — we're only sending one here).
    #   n_results: how many nearest neighbours to return.
    #   include: which payload fields to return alongside the IDs.
    #     "documents"  → the stored chunk text
    #     "metadatas"  → source_name, source_type, source_url we stored at upsert
    #     "distances"  → cosine distance scores (lower = more similar)
    #
    # results["documents"] and results["metadatas"] are lists-of-lists because
    # ChromaDB supports batch queries. We index [0] to get the results for our
    # single query.
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text":        text,
                "source_name": meta["source_name"],
                "source_type": meta["source_type"],
                "source_url":  meta["source_url"],
                "chunk_index": meta["chunk_index"],
                "distance":    round(dist, 4),
            }
        )
    return chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed chunks and optionally test retrieval.")
    parser.add_argument("--query", type=str, help="Run a retrieval query.")
    parser.add_argument(
        "--skip-embed",
        action="store_true",
        help="Skip embedding step (use when chroma_db/ already exists).",
    )
    args = parser.parse_args()

    if not args.skip_embed:
        embed_and_store()

    if args.query:
        print(f"\nQuery: {args.query}")
        print("-" * 60)
        for i, r in enumerate(retrieve(args.query), 1):
            print(f"\n[{i}] {r['source_name']} | distance: {r['distance']}")
            print(f"    URL: {r['source_url']}")
            print(f"    {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}")
