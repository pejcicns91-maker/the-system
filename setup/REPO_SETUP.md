# PHONE SETUP — new repo, Safari, tap by tap. No command line, no tokens.

## 0. Get the files onto the phone
Save from chat -> Files: THE_SYSTEM_REPO_SEED_2026-07-27.zip, BOOTSTRAP_PASTE.txt, RUN_PASTE.txt.

## 1. Create the repo
github.com -> + -> New repository -> Name: `the-system` ->
**Private or Public — your call here**: Public = unlimited runner minutes, but data + system visible to anyone.
Private = hidden, 2,000 free minutes/month (~8 four-hour grinds). -> Create repository.

## 2. Install the two workflows (one paste each)
Add file -> Create new file -> name exactly `.github/workflows/bootstrap.yml`
-> open BOOTSTRAP_PASTE.txt in Files -> Select All -> Copy -> paste -> Commit changes.
Repeat with name `.github/workflows/run.yml` and RUN_PASTE.txt.

## 3. Allow workflows to save results (two taps)
Settings -> Actions -> General -> Workflow permissions -> **Read and write permissions** -> Save.

## 4. Upload the seed once (the only big transfer)
Repo main page -> Releases -> **Create a new release** -> Tag: type `seed` -> tap "Create new tag: seed" ->
Attach binaries -> pick THE_SYSTEM_REPO_SEED zip from Files -> **Publish release**. (94MB — wifi.)

## 5. Bootstrap
Actions tab -> **Bootstrap** -> Run workflow -> green button. ~2-3 min to a green check.
The whole tree (244 files) appears in the repo.

## 6. Prove the loop
Actions -> **Run job** -> Run workflow -> script: `smoke.py` -> run.
Log must end `SMOKE ALL PASS` with the eight counts. Anything else = drift: STOP, paste the log in chat.

## 7. The new ritual
New chat: paste the repo URL — I fetch README + only what the task needs (no more 94MB attaches).
Grinds: Actions -> Run job -> script name -> go. Resume = run again. Results land in results/, readable from chat.
Optional after step 5: delete the release (the tree is in the repo; keeping it = free backup).
