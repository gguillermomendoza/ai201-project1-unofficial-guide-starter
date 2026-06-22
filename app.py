"""
app.py — Gradio web interface for the LA Parks Unofficial Guide RAG system.

Wires the full RAG pipeline (query.rag) into a simple two-panel UI:
  - left/top:  question input + submit button
  - middle:    generated answer
  - bottom:    retrieved source chunks with metadata

Run:
    python app.py
"""

import gradio as gr

from query import INSUFFICIENT_ANSWER, rag


def answer_question(question: str) -> tuple[str, str]:
    """
    Gradio event handler.

    Runs the full RAG pipeline on the submitted question and returns
    two strings: the generated answer and a formatted sources block.
    The sources block is built in Python from the retrieved chunks —
    it is always populated regardless of what the LLM chose to cite.
    """
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    result = rag(question)
    answer = result["answer"]

    # Build the sources display from the retrieved chunks directly.
    # This guarantees attribution even if the model omitted citations.
    source_lines = []
    for i, s in enumerate(result["sources"], 1):
        preview = s["text"][:220]
        if len(s["text"]) > 220:
            preview += "..."
        source_lines.append(
            f"[{i}] {s['source_name']}  (chunk {s['chunk_index']}, "
            f"distance: {s['distance']})\n"
            f"    {s['source_url']}\n"
            f"    {preview}"
        )
    sources_text = "\n\n".join(source_lines)

    return answer, sources_text


# ---------------------------------------------------------------------------
# Gradio layout
# ---------------------------------------------------------------------------

with gr.Blocks(title="LA Parks Unofficial Guide") as app:
    gr.Markdown(
        "## LA Parks Unofficial Guide\n"
        "Ask anything about parks in the Los Angeles area. "
        "Answers come from community reviews, Reddit threads, and travel guides — "
        f"not official park pages. If sources are insufficient the system will say: "
        f'*"{INSUFFICIENT_ANSWER}"*'
    )

    question_box = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which parks are good for picnics?",
        lines=2,
    )
    submit_btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(
        label="Answer",
        lines=7,
        interactive=False,
    )
    sources_box = gr.Textbox(
        label="Retrieved sources (top 5)",
        lines=14,
        interactive=False,
    )

    # Wire submit button and Enter key to the same handler.
    submit_btn.click(
        fn=answer_question,
        inputs=[question_box],
        outputs=[answer_box, sources_box],
    )
    question_box.submit(
        fn=answer_question,
        inputs=[question_box],
        outputs=[answer_box, sources_box],
    )


if __name__ == "__main__":
    app.launch()
