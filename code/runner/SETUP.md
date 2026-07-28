# PHONE SETUP — Safari only, tap by tap. No command line. No tokens.

## 0. Get the files onto the phone
1. In the Claude chat, tap the BRUTEFORCE_COMPLETE.zip -> Save to Files.
2. Open Files app -> tap the zip once (it extracts) -> open the folder -> open `gha_bundle`.
   Everything you upload comes from THIS folder only.

## 1. Create the repo (github.com in Safari)
3. Log in -> tap + (top right) -> New repository.
4. Name: `grind` . Set **Private** (see README quota note; Public = unlimited minutes but data is public — your call). Tap **Create repository**.

## 2. Upload the flat files
5. On the new repo page tap **uploading an existing file** (link in the middle).
6. Tap **choose your files** -> Browse -> the `gha_bundle` folder -> tap **Select** (top right) -> tap every file EXCEPT w1_grind.yml and w2_b5.yml (those two get pasted in step 3; uploading them here too is harmless, they just sit unused in root) -> **Open**.
7. Wait for all green ticks (17 files, largest ~13MB; cap is 25MB/file — all fit). Tap **Commit changes**.
   If Safari chokes on one big batch, upload in two batches — same button, repeat.

## 3. Install the two workflows (one paste each)
8. Repo page -> **Add file** -> **Create new file**.
9. In the name box type exactly: `.github/workflows/w1_grind.yml` (the slashes create the folders).
10. In Files app open `w1_grind.yml` -> long-press the text -> Select All -> Copy. Back in Safari, paste into the big editor box. Tap **Commit changes** (twice if it asks).
11. Repeat 8-10 with name `.github/workflows/w2_b5.yml` and the contents of `w2_b5.yml`.

## 4. Allow the workflows to save results (two taps)
12. Repo -> **Settings** -> **Actions** -> **General** -> scroll to **Workflow permissions** -> select **Read and write permissions** -> **Save**.

## 5. Run (whenever you choose — nothing runs by itself)
13. Repo -> **Actions** tab -> left list: **W1 grind** -> **Run workflow** button -> leave defaults (budget 230, mode grind, b4 0) -> green **Run workflow**.
14. A run appears. Tap it to watch. It builds the data table once (~10 min, cached after), then grinds ~4h and saves a checkpoint.
15. **Resume = just tap Run workflow again.** Canceled, expired, or timed-out runs lose at most one 200-combo block; the cursor is committed to the repo every block.
16. When a run's log ends with `chunk done; complete`: run once more with **mode: finalize** -> it writes the register parts, digest, and extinction map into the repo.
17. **W2 B5** works the same way: Actions -> W2 B5 forecaster -> Run workflow. Re-run to resume; it prints `B5 COMPLETE` with the score table when done.

## 6. Getting results back
18. Results live in the repo: `w1_digest.csv`, `w1_extinction.csv`, `out_register/` parts, `b5_scores.csv`. Tap a file -> **⋯** -> **Download** (or tap **Raw** then share-save). Upload them into our chat for adjudication.
