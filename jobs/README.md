# jobs/ — runner conventions
Every study script lives here and follows the proven grind pattern (re-checked from repo Cb13):
accept --budget-min N (stop cleanly inside it); resume via a cursor file under results/state/;
write outputs under results/ only; print row counts (the drift law: unexpected counts = STOP);
seeds fixed and printed; n floors and laws per docs/newproject/PROJECT_INSTRUCTIONS.md.
Run from the Actions tab: "Run job" -> script name -> go. Resume = run again.
Adjudication and any promotion happen in chat, never on the runner.
