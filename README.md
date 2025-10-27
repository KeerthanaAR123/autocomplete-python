# Meesho DICE Hackathon - Query Auto-Complete Challenge

This repository contains the winning solution of Meesho DICE 2025 DS Track. The goal is to build a system that, given a user's search prefix, retrieves the 150 most relevant query completions.

The two solutions explore the primary trade-off in auto-complete systems (ACS): **retrieval quality vs. inference speed.**

---

## 1. Best Quality - Hybrid Search

This folder contains a high-performance solution focused on maximizing the semantic quality and relevance of completions.

### High-Level Approach

This solution implements a sophisticated **hybrid search** model that combines:
1.  **Dense (Semantic) Retrieval:** Uses a SentenceTransformer model (`all-MiniLM-L6-v2`) to understand the *meaning* of the prefix.
2.  **Sparse (Lexical) Retrieval:** Uses a `BM25` model (implemented with `HashingVectorizer`) to find queries that match the *keywords* of the prefix.
3.  **Popularity Boost:** Uses query features (orders, clicks, volume) to boost the score of popular and trending items.

During inference, the input prefix is encoded into both dense and sparse vectors. These are then scored against the *entire* pre-computed index of all 4.1 million queries from the pool. The dense, sparse, and popularity scores are combined to produce the final ranking.

### Performance
* **Quality:** This approach yields the highest quality completions, as it can find semantically relevant queries even if the keywords don't match perfectly (e.g., "shoe for running" -> "men's sneakers").
* **Inference Time:** The inference time is **very high**. Scoring every prefix against the full 4.1M+ dense and sparse vectors is computationally expensive, making it unsuitable for a real-time production environment without significant optimization.

---

## 2. Final Submission - Low-Latency

This folder contains the final, production-ready solution. It prioritizes **inference speed** and memory efficiency, which are critical for a real-world auto-complete system that must respond in milliseconds.

### High-Level Approach

This solution uses an optimized, multi-stage heuristic and lexical search pipeline. It completely avoids heavy semantic models in favor of fast dictionary lookups.

The retrieval function works in stages:

1.  **Historical Matches:** The system first checks a pre-built map (`prefix_query_freq`) for prefixes seen in the training data. This is the highest-priority match.
2.  **Direct Prefix Index:** If no historical match is found (or more candidates are needed), it looks up the prefix in a memory-efficient prefix index (`prefix_index`). This `defaultdict` maps prefixes to queries that start with them (e.g., "lapt" -> "laptop", "laptop bag").
3.  **Fuzzy Matching (for Typos):** If the prefix yields few results (e.g., a typo like "ifon"), the system runs `rapidfuzz` (a fast fuzzy matching library) against a *small subset* (50,000) of the most popular queries to find corrections.
4.  **Popularity Fallback:** If the system still doesn't have 150 candidates, it fills the remaining slots with the most popular queries from the entire pool.

### Performance

* **Quality:** The completions are highly relevant for common prefixes and typos. However, it lacks the deep semantic understanding of the hybrid model and may miss completions that are related by meaning but not by text.
* **Inference Time:** The inference time is **negligible**. The entire prediction process for all 522,726 test prefixes completes in minutes. This highlights the real-world importance of designing auto-complete systems that prioritize speed to ensure a smooth user experience.

---

## Future Improvements

* **Finetune SBERT:** Finetune the `SentenceTransformer` model from Pinakin's solution on the `(prefix, query)` pairs from the training data. This would teach the model the specific relationship between partial text and full queries, improving semantic relevance.
* **Optimize Dense Retrieval:** To get the best of both worlds (quality *and* speed), the dense retrieval pipeline could be heavily optimized. Instead of a full search, an Approximate Nearest Neighbor (ANN) index (e.g., using `FAISS` or `ScaNN`) could be built. This would allow the system to find the top-k semantic matches in milliseconds, making the hybrid search approach viable for production.
* **LightGBM Ranking:** Train a LightGBM ranking model that takes features from both the dense and sparse retrievals, as well as query popularity metrics. This model could learn to optimally combine these signals to produce a final ranking that balances relevance and speed.