# Reviewer checklist

The reviewer is a fresh subagent or the author, with the page and the facts file open.
Mark each line pass or fail. A fail goes back to the page, then the check runs again.

1. **Each number matches a source.** For each count, time, size, id, commit hash and status code on the page, find the same text in the facts file or in an evidence file. Write the source next to it.
2. **No claim without a source.** "Passed", "fixed", "deployed", "merged" each have a line in the evidence. A cell without evidence says "not done".
3. **Commit and deploy state are true.** `git log` and `git status` agree with the meta line. An uncommitted fix says "Not committed". When the facts name the commit that caused the defect, the meta line names it.
4. **Quotes are exact.** Error text and log lines match the evidence character for character.
5. **No secret.** No password, key, token, cookie, connection string or private e-mail on the page, in a `pre` or in a screenshot.
6. **No codes as references.** No "B1", "issue 8", "F13" for a thing on the page. Use its name.
7. **The parts are there, in order.** Terms, 1. What was wrong (one figure), 2. How it was fixed (one figure), 3. Test evidence (table, screenshots), 4. Lifecycle.
8. **The screenshots show what the caption says.** Open each image. Before shows the fault, after shows the fixed state.
9. **The checks pass.** `python3 <skill>/check.py <page>` exits 0.
