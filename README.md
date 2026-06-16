# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
Reviews of parks in the city of Los Angeles - useful because there are so many parks and reviews. You can't really grasp what the vibe is at every park to make an informed decision.  
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #  | Source                                                                    | Type                                        | URL or file path                                                                                                                                                                             |
| -- | ------------------------------------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | Reddit thread: “LA parks are now ranked 93rd out of 100 of the...”        | Reddit discussion / community reviews       | https://www.reddit.com/r/LosAngeles/comments/1tq8bqp/la_parks_are_now_ranked_93rd_out_of_100_of_the/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button |
| 2  | Reddit thread: “Best scenic parks in LA?”                                 | Reddit discussion / recommendations         | https://www.reddit.com/r/AskLosAngeles/comments/1k6krhx/best_scenic_parks_in_la/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button                     |
| 3  | Reddit thread: “Best parks for picnics?”                                  | Reddit discussion / recommendations         | https://www.reddit.com/r/AskLosAngeles/comments/1omxq33/best_parks_for_picnics/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button                      |
| 4  | Discover Los Angeles: “The Guide to Los Angeles Parks”                    | Travel / tourism guide                      | https://www.discoverlosangeles.com/things-to-do/the-guide-to-los-angeles-parks                                                                                                               |
| 5  | City of Los Angeles Department of Recreation and Parks: Park addresses    | Official government park directory          | https://recreation.parks.lacity.gov/parks                                                                                                                                                    |
| 6  | Los Angeles Times: “Chill Los Angeles parks for hanging out and relaxing” | Newspaper / lifestyle article               | https://www.latimes.com/lifestyle/list/chill-los-angeles-parks-for-hanging-out-and-relaxing                                                                                                  |
| 7  | Tripadvisor: Best parks in Los Angeles                                    | Review platform / travel rankings           | https://www.tripadvisor.com/Attractions-g32655-Activities-c57-t70-Los_Angeles_California.html                                                                                                |
| 8  | Yelp: Parks in Los Angeles, CA                                            | Review platform / local business listings   | https://www.yelp.com/search?find_desc=Parks&find_loc=Los+Angeles%2C+CA                                                                                                                       |
| 9  | Modern Luxury: “Best Parks in Los Angeles”                                | Lifestyle article / curated recommendations | https://www.modernluxury.com/best-parks-los-angeles/                                                                                                                                         |
| 10 | Hotels.com: “Best Parks in Los Angeles”                                   | Travel guide / curated recommendations      | http://de.hotels.com/go/usa/best-parks-los-angeles                                                                                                                                           |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
