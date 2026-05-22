# Deep Matching and Retrieval of Indic Script Documents

**BTP — IIIT Sri City, ongoing**  
Supervisor: Dr. Pavan Kumar Perepu, Dept. of CSE

---

## What this is about

Telugu (and Indic scripts in general) have a problem that breaks 
standard string matching.

In English, one character = one Unicode symbol. In Telugu, a 
single visible unit called an *akshara* can be made of 3-5 
Unicode code points combined. So when you compare two Telugu 
words using Levenshtein edit distance, you're comparing at the 
wrong level — the algorithm sees a flat sequence of abstract 
codes, not the actual linguistic units a human reads.

This project trains a CNN-based Siamese network to *learn* the 
edit distance between Telugu word pairs from their Unicode 
sequences, instead of computing it mechanically. At inference, 
complexity drops from O(|x₁|·|x₂|) to O(|x₁|) + O(|x₂|).

The end goal is a retrieval system: given a query Telugu word, 
find the closest matches in a database — handling spelling 
variations, OCR errors, and script-level structural differences.

---

## Architecture — CNN Siamese Network

Both input words go through the same shared encoder:

    Input: Unicode sequence → one-hot (60 vocab, 1×60 per code point)
    ↓
    Embedding layer (d=64)
    ↓
    Conv1D × 2 (learns spatial patterns between code points)
    ↓
    GlobalMaxPool1D (handles variable-length input)
    ↓
    Dense → 250-dim word vector (z₁, z₂)
    ↓
    Concatenate z₁ ⊕ z₂
    ↓
    Dense (1, linear) → predicted LED (ŷ)

    Loss: MSE — L = ||ŷ − y||²  (supervised on ground truth LED)

Vocabulary: 60 Telugu Unicode code points from the 0x0C00–0x0C7F 
block, filtered to remove rare elements. Each mapped to index 0–59.

---

## Current Status

**Phase 1 — Complete:**
- 122 Telugu word pairs collected
- Full preprocessing pipeline built (UTF-8 → Unicode hex →
  integer indices → vocab-indexed sequences)
- LED computed for all pairs as ground truth labels
- LED range: 2–19, mean 7.85 — good diversity for training
- Final (x₁, x₂, y) dataset built in db3_processed.csv

**Phase 2 — In Progress:**
- Learn embedding space (dim < 128)
- Replace one-hot inputs with learned embeddings
- Train CNN Siamese network on db3 dataset
- Evaluate MSE alignment with ground truth LED

**Phase 3 — Planned:**
- Explore comparison strategies (concat, dot product, cosine)
- Cluster analysis of learned representations
- Benchmark against baseline LED

**Phase 4 — Future:**
- Expand vocabulary to include modifier characters
- Glyph-level matching (visual representation layer)
- Generalize to other Indic scripts (Kannada, Devanagari)

---

## Repository Structure & Pipeline Notes For ME

    data/
    ├── raw/
    │   ├── vocab_database.xlsx        # source vocabulary — edit this to add words
    │   └── new_pairs.txt              # staging file — write new pairs here before appending
    └── processed/
        ├── db1_utf8_pairs.csv         # 122 raw UTF-8 Telugu word pairs
        ├── db2_unicode_pairs.csv      # hex code point sequences + LED labels
        ├── db2_unicode_integers.csv   # decimal integer encoding
        ├── db3_processed.csv          # final vocab-indexed (x1, x2, y) dataset
        └── vocab.txt                  # 60 code points, index 0-59

    src/
    ├── core/                          # Levenshtein distance, Telugu Unicode validation
    └── pipelines/
        ├── initialize.py              # rebuilds all processed files from scratch
        └── append.py                  # adds new pairs from new_pairs.txt

**Rebuild everything from scratch** (if vocab_database.xlsx changes):

    .\btp_venv\Scripts\python.exe -m src.pipelines.initialize

**Add new word pairs** (write into data/raw/new_pairs.txt first,
one pair per line, comma-separated like అమ్మ,నాన్న):

    .\btp_venv\Scripts\python.exe -m src.pipelines.append

The append script auto-clears new_pairs.txt after running,
deduplicates, computes LED, and updates all four processed files.

---

## Tech Stack

Python, NumPy, TensorFlow/Keras (Phase 2), scikit-learn  
Telugu Unicode block: 0x0C00–0x0C7F
