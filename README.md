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

Three strategies depending on source type:
- **Reddit** — one chunk per comment; thread title prepended as `"Thread topic: <title>. Comment: ..."` so anonymous comments carry topic context; skip < 20 words, split > 500 words with 50-word overlap
- **TripAdvisor / Yelp** — one chunk per review; park name extracted from `#` section headers and prepended as `"Park: <name>. ..."` so every review is self-identifying even when the reviewer never names the park; same skip/split rules as Reddit
- **Article sources** — sentence-boundary chunks of ~300 words with ~75-word sentence overlap (avoids mid-sentence cuts that lose the park name at the start of a sentence)

**Overlap:**

- Articles: ~75 words, at sentence boundaries (not raw word count)
- Standalone reviews: 50-word overlap only when a single comment/review exceeds 500 words; no overlap otherwise

**Why these choices fit your documents:**

Reviews and Reddit comments are self-contained thoughts — splitting them mid-comment would break context and make individual opinions unretreivable. Article sources are longer and park information is spread across paragraphs, so sentence-boundary chunking at ~300 words keeps each chunk large enough to contain a full recommendation while staying small enough for specific queries like "picnic" or "scenic views" to return targeted results. The park name prefix on review chunks was added after discovering that Yelp/TripAdvisor reviews frequently never mention the park by name, making them impossible to retrieve by park name query without the prefix.

**Final chunk count:**

664 total chunks across 10 sources (up from 288 in an earlier version — the increase came from the TripAdvisor source, which produced 454 chunks once each review was split into its own chunk rather than grouped).

---

## Sample Chunks

<!-- 5 representative chunks from chunks.json, one per source.
     For each: does it make sense on its own? Could someone answer a question from it alone? -->

**Chunk 1** — Source: `tripadvisor_la_parks`

> Park: Griffith Park. The largest urban wilderness municipal park in the United States Griffith Park in Los Angeles is the largest urban wilderness municipal park in the United States. With over 4,300 acres of natural Chaparral-covered terrain and landscaped parkland and picnic areas, it is filled with hiking trails, trees trains and attractions, from the Hollywood Sign to the Griffith Park Observatory to the Los Angeles Zoo and Botanical Gardens to the Autry Museum of the American West to the Greek Theatre to Travel Town. There is something for everyone. To see it all, or at least most of it, hop on the Griffith Parkline, which offers convenient transportation for the park's 10 million annual visitors. The bus runs from noon to 10 p.m. on Saturdays and Sundays and delivers passengers to more than a dozen locations. Among the most interesting are the 133-acre zoo, which was founded in 1966 and is home to more than 2,100 animals representing over 270 species; the Griffith Observatory, which dates to 1935 and offers some of the best views of Los Angeles, from the Pacific Ocean to Downtown; the 45-foot-tall, 350-foot-long Hollywood Sign; the 5,900-seat Greek Theatre, one of Los Angeles' premier outdoor venues; the Autry Museum of the American West, which realized legendary recording and movie star Gene Autry's dream to build a museum to exhibit and interpret the heritage of the West and showcase its influence on the United States and the world; and Travel Town Museum, which focuses on the history of railroad transportation in the western United States from 1880 to the 1930s. Open daily from 5 a.m. to 10:30 p.m., Griffith Park is located on the eastern end of the Santa Monica Mountain range and Hollywood Hills, just west of the Golden State Freeway or I-5, between Los Feliz Boulevard on the south and the Ventura Freeway on the north. Hiking is one of the most popular forms of recreation in the park with a 53-mile network of trails, fire roads and bridle paths. One trail leads from the observatory parking lot to the top of 1,625-foot Mount Hollywood, the park's highest point.


---

**Chunk 2** — Source: `yelp_la_parks`

> Park: Vista Hermosa Park. This is a small park located just a bit northwest of downtown LA. There's a small parking lot which is freeee; otherwise, you will need to find street parking, and good luck with that. The area around the park is legitimately sketchy but I didn't see any bad characters inside the park whatsoever. The park could be maintained better. The weeds are high in some areas and the grass needs watering in other locations. Having said all that, it's a nice enough little park with at least one spot for an amazing view of downtown. I have never seen the movie, "(500) Days of Summer," but some people believe the striking view of downtown with the park bench in the foreground was shown in the movie. I can't vouch for that but that particular spot is gorgeous and perfect for a photo op. You'll know the spot when you see it. Worth checking out. Gorgeous view of DTLA.


---

**Chunk 3** — Source: `hotels_com_la_parks`

> 1. Grand Park — A 12-acre space in central Los Angeles. Grand Park covers 12 acres of greenery in Los Angeles' civic centre. You can find tree-shaded walking paths, botanic gardens, casual sitting areas, and historic fountains. It was founded in 1966 as a place where residents can unwind throughout the day. Grand Park offers excellent views of Los Angeles, stretching from the Music Center to City Hall. It has 4 distinct sections that work together to provide a wide range of recreational activities. Some of its highlights include a community terrace with a diverse array of drought-tolerant plants and a small lawn hosting cultural events and weekly farmers' markets. A must-see is Arthur J. Will Memorial Fountain, which has a membrane pool that's open for wading. 2. Palisades Park — Santa Monica's ocean-facing park. Palisades Park offers expansive views of the Pacific Ocean and coastal mountains of Santa Monica. You can find all sorts of fun in this family-friendly park, including walking paths, a collection of art installations and diverse tree species. The best time to visit is in the evenings – from the cliffs, you can take in the breathtaking sunset, ocean, and mountains.


---

**Chunk 4** — Source: `discover_la_parks_guide`

> Today, it is home to the Frank Lloyd Wright-designed Hollyhock House, LA's first UNESCO World Heritage Site; Los Angeles Municipal Art Gallery, Barnsdall Art Center, Junior Arts Center and the Barnsdall Gallery Theatre. Open from sunrise to sunset, Lake Hollywood Park is an idyllic escape from the hustle and bustle of the city with a fantastic view of the Hollywood Sign. The park features a children's play area, picnic tables, barbecue pits, and a grass field for on-leash dogs to enjoy. Formally known as Hancock Park La Brea, this city park in the Miracle Mile district is home to two of L.A.'s most popular cultural attractions, the Los Angeles County Museum of Art (LACMA) and the La Brea Tar Pits & Museum. Located on Wilshire Boulevard just east of Fairfax Avenue, the park has open spaces and landscaped areas for walking, picnicking, and other recreation. Hancock Park La Brea is registered as California Historical Landmark #170, and the iconic La Brea Tar Pits are a designated U.S. National Natural Landmark. Centrally located across the street from The Grove, Pan Pacific Park was once home to the famous Pan-Pacific Auditorium. Today it's one of the most popular and family-friendly parks in the city, with features that include barbecue pits, a baseball diamond (lighted), basketball courts (lighted/indoor/outdoor), a children's play area, an indoor gym (no weights) and picnic tables. Pan Pacific Park is also the site of the Los Angeles Museum of the Holocaust, the oldest Holocaust museum in the United States.


---

**Chunk 5** — Source: `reddit_picnic_parks`

> Thread topic: Best parks for picnics?. Comment: Elysian is probably the easiest. You park, walk like 10 steps then you're there. It's also wide open. Personally I like Barnsdall the best, great view and perfect for a picnic, but it's pretty tiny.


---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

`all-MiniLM-L6-v2` via `sentence-transformers` (local, no API key required). Chosen because it runs entirely locally (no API cost or latency for embedding), produces 384-dimensional vectors that are fast to compute and store in ChromaDB, and performs well on short English text such as park reviews and Reddit comments.

**Production tradeoff reflection:**

For a real deployment, I would weigh several tradeoffs. A larger model like `text-embedding-3-large` (OpenAI) or `voyage-large-2` would likely score higher on retrieval benchmarks, especially for nuanced semantic queries, but adds API cost and latency per query. A multilingual model (e.g. `paraphrase-multilingual-MiniLM-L12-v2`) would help if expanding to Spanish-language reviews, which are common in LA. Context length matters too — `all-MiniLM-L6-v2` is capped at 256 tokens, which is tight for the longest article chunks; a model with a 512+ token window (e.g. `all-mpnet-base-v2`) would encode those without truncation. For this project's scale (664 chunks, English-only, no cost constraint), `all-MiniLM-L6-v2` is a reasonable choice.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**


> "STRICT GROUNDING RULE: Answer ONLY using the source documents provided in the user message. Do not use any outside knowledge, training data, or information not present in those documents. If the provided sources do not contain enough information to answer the question, respond with exactly: 'I don't have enough information on that.'"

The fallback phrase is defined as the `INSUFFICIENT_ANSWER` constant in `query.py` so the exact string is used consistently in the prompt, in the demo's grounding check, and in the UI description — no risk of a typo causing a mismatch.

Each retrieved chunk is labeled `[SOURCE 1]` through `[SOURCE 5]` in the user message, with the source name and chunk index shown above the text. This gives the model clear numbered references to cite rather than needing to invent specifics — the labels reduce hallucination by making evidence explicit.

The context block is placed before the question in the user message (context first, then "Question: …"), which keeps the instruction structure clean and matches the pattern the model was trained on for reading comprehension tasks.

**How source attribution is surfaced in the response:**

Source attribution is enforced at the Python layer, not left to the LLM. In `query.py:rag()`, the retrieved chunks are stored in a list before the LLM call. After generation, that same list is returned alongside the answer as the `"sources"` field of the result dict. The Gradio UI (`app.py`) and the demo (`demo.py`) both read attribution from this programmatic list — not from the model's answer text. Even if the model forgets to cite a source in its prose, the source panel always shows all retrieved chunks with their URL, chunk index, and cosine distance score.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which LA parks are recommended for scenic views? | Parks known for their views (Griffith Observatory area, Runyon Canyon) | Named Griffith Park, Runyon Canyon, and Elysian Park; cited specific viewpoints (Observatory, Angel's Point, Mt. Hollywood); all citations backed by retrieved chunks | Relevant (distances 0.24–0.27) | Accurate |
| 2 | Which parks are recommended for picnics? | Accessible, open parks suited for groups | Named 10 specific parks (Elysian, Barnsdall, Kenneth Hahn, Lake Balboa, Veterans Park in Sylmar, etc.) drawn directly from Reddit picnic thread and Yelp; one Yelp chunk (Pan Pacific) noted it was not great for picnics | Relevant (distances 0.16–0.25) | Accurate |
| 3 | Which parks seem good for relaxing or hanging out alone? | Quieter parks with seating, low activity | Named MacArthur Park, Lake Balboa Park, and Everett Park (with daytime caveat); distances were the highest of the passing queries (~0.31–0.33), suggesting the corpus covers "relaxing" only incidentally | Partially relevant (distances 0.31–0.33) | Partially accurate — correct parks, but limited coverage; "hanging out alone" matched group/activity reviews rather than solitude-specific content |
| 4 | Which parks should I avoid at night? | Parks with reviewer-reported safety concerns or conditions that worsen after dark | Named Everett Park (Yelp review: "gets a bit ghetto at night time") and flagged Ladera Park for noise/trash; one chunk (Griffith Park) described night views positively, slightly diluting relevance | Partially relevant (distances 0.29–0.39) | Partially accurate — only one chunk directly addressed night safety; other retrieved chunks were tangentially related |
| 5 | Which park is best for someone who wants a beach park with views? | A coastal park with ocean views | Recommended Point Fermin over White Point, citing "GREAT OCEAN VIEWS" and "Nice views of the cliffs ocean" from TripAdvisor reviews; explained reasoning across sources | Relevant (distances 0.31–0.35) | Accurate |

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

"What are some differences between official park information and user review information?"

**What the system returned:**

The model answered that official sources provide "data-driven statistics and rankings" while user reviews offer "personal experiences and anecdotal evidence," and cited broken playgrounds and poor maintenance as examples reviewers raised that official reports miss. Cosine distances on all 5 retrieved chunks were 0.53–0.60 (>0.50 grounding-concern threshold. The demo flagged this as a potential grounding issue.

**Root cause (tied to a specific pipeline stage):**

The failure is at the retrieval stage. The question asks for a meta-comparison between two types of sources, but the corpus contains no documents that make this comparison. Every document is either an official source or a user review, not a text that analyzes the difference between them. Because no chunk is semantically close to the question, retrieval returns loosely related Reddit comments about park quality complaints (distances ~0.53–0.60). The generation stage then produces a plausible-sounding answer by synthesizing across those chunks, but the reasoning is the model's own inference, not something stated in the retrieved text. Grounding is technically violated even though the answer sounds reasonable.

**What you would change to fix it:**

Add a distance-based fallback in `query.py`: if all retrieved chunks exceed a threshold, return `INSUFFICIENT_ANSWER` before calling the LLM at all, rather than passing weak context to the model. This would catch exactly this case but the fix should happen before generation. Alternatively, I could add a source that explicitly compares official and community park information (e.g., a journalism piece or community advocacy report on LA park equity).

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

Having the evaluation questions written down before I touched any code gave me a concrete target to test against at every stage. As soon as retrieval was working, I could immediately run "Which parks are recommended for picnics?" and check whether the returned chunks were actually about picnic parks — rather than guessing whether the system was working. The spec also forced me to think about source variety before collection, which is why the corpus ended up with Reddit threads, Yelp reviews, TripAdvisor reviews, official city pages, and article sources rather than just one type of source that would have produced a retrieval blind spot.

**One way your implementation diverged from the spec, and why:**

The spec described a single chunking strategy — ~250–500 word chunks with 50-word overlap for articles and no overlap for standalone reviews. The implementation ended up with three distinct strategies after I inspected the actual document text. The key discovery was that Yelp and TripAdvisor reviews almost never mention the park by name inside the review body — the park name appears only in a section header above the review. Without the `"Park: <name>. ..."` prefix I added to every review chunk, a query like "Griffith Park reviews" would return zero relevant results because the word "Griffith" didn't appear in any chunk text. That fix wasn't in the spec because I hadn't looked at the raw documents yet when I wrote it.

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

- *What I gave the AI:* I gave Claude the Chunking Strategy section and Documents table from planning.md and asked it to implement `chunk_text()`. I told it I had three source types (Reddit comments, Yelp/TripAdvisor reviews, and article sources) and described the skip/split rules from the spec.
- *What it produced:* A `chunk_text()` function that applied a single sliding-window split across all source types, with a 50-word overlap and a minimum word threshold.
- *What I changed or overrode:* I split it into three separate strategies after inspecting the actual document text and discovering that review chunks never named the park. I directed Claude to add a park-name prefix extracted from `#` section headers for Yelp and TripAdvisor chunks, and to prepend the thread title for Reddit comments. I also changed article overlap from 50 words to ~75 words at sentence boundaries to avoid mid-sentence cuts.

**Instance 2**

- *What I gave the AI:* I gave Claude the Retrieval Approach section and the Architecture diagram from planning.md (embedding model: `all-MiniLM-L6-v2`, top-k=5, ChromaDB vector store) and asked it to implement `embed_and_store()` and `retrieve()`.
- *What it produced:* Both functions working end-to-end — `embed_and_store()` encoded chunks and upserted them into a persistent ChromaDB collection, and `retrieve()` took a query string and returned the top-5 most similar chunks with metadata.
- *What I changed or overrode:* The initial version used sequential integer IDs for ChromaDB documents, which caused duplicate entries every time `embed.py` was re-run on the same chunks. I directed Claude to switch to SHA-1 hashes of the chunk text as IDs so that re-runs would upsert cleanly rather than accumulate duplicates. I also added the `distance` field to the `retrieve()` return value so the demo could use it for the grounding check.
