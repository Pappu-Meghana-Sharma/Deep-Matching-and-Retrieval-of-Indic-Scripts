Project Database Pipeline Instructions
=====================================

This project handles the processing and mapping of Telugu word pairs. The codebase is organized into modular directories:
- `src/core/`: Contains core helper and processing logic (e.g., Levenshtein distance, Telugu Unicode checks).
- `src/pipelines/`: Contains runnable script pipelines to generate or modify database files.

Data directories:
- `data/raw/`: Contains vocab database mapping and the staging file for new pairs.
- `data/processed/`: Contains master files (base pairs, codepoint integers database, and vocabulary indices database).

Commands for Running the Pipelines
==================================
All python scripts must be executed from the project root directory. Use the local virtual environment Python:

1. Rebuilding/Initializing all Processed Databases
   ----------------------------------------------
   If you want to re-process all data from scratch (for example, if 'vocab_database.xlsx' in 'data/raw/' has changed, or to clear out all data and start fresh using the Telugu base list 'db1_utf8_pairs.csv'):
   
   Command:
   .\btp_venv\Scripts\python.exe -m src.pipelines.initialize
   
   This script regenerates the following files inside 'data/processed/':
   - db2_unicode_integers.csv
   - db2_unicode_pairs.xlsx
   - db3_processed.csv

2. Appending New Pairs
   -------------------
   If you want to add new Telugu word pairs:
   
   Step 1: Write the new pairs into the staging file 'data/raw/new_pairs.txt' (one pair per line, comma-separated):
           Example contents of 'data/raw/new_pairs.txt':
           సూర్యుడు,నీరు
           అమ్మ,నాన్న

   Step 2: Run the append pipeline:
           Command:
           .\btp_venv\Scripts\python.exe -m src.pipelines.append

   This script will:
   - Read and parse new pairs from 'data/raw/new_pairs.txt'.
   - Perform a deduplication check against already existing pairs.
   - Calculate Levenshtein distances, codepoints, and vocabulary index sequences.
   - Append new unique records to:
     - data/processed/db1_utf8_pairs.csv (retaining Excel compatible UTF-8 BOM encoding)
     - data/processed/db2_unicode_integers.csv
     - data/processed/db2_unicode_pairs.xlsx
     - data/processed/db3_processed.csv
   - Automatically clear the contents of 'data/raw/new_pairs.txt' once done.
