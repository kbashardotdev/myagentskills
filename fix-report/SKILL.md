---
name: fix-report
description: Use when the user asks for a report on a fix, a fix report, an evidence page for the fix, or a page that shows what was wrong, how it was fixed and the proof that the tests ran.
---

# Fix report

One HTML page for one fix. The reader reads it on a phone in 1 minute.
The page shows what was wrong, how it was fixed, and the evidence of real test runs.

Files next to this file: `template.html` (structure and style), `check.py` (page checks), `checklist.md` (review).

## 1. Collect the facts first

Write `.task/<name>-fix-facts.md` before the page. One line per fact, with its source path or command.

| Fact | Where to find it |
|---|---|
| Symptom the user saw, error text | issue, bug report, logs, the fix notes in `.task/` |
| Cause, changed files | `git diff <base>...HEAD`, `git status`, the fix notes |
| Commit, branch, deploy | `git log -1`, `git branch --show-current`, the deploy record |
| Cause commit (the commit that added the defect) | the fix notes, `git log -S '<bad line>'`, `git blame` on the base |
| Unit tests on base and on branch | the test output files; else run the tests on both and save the output |
| Local real run, before and after | run notes, command output, screenshots |
| Deployed real run, before and after | job ids, status codes, times, screenshots from the environment |

**Missing evidence.** Write `not done` in the facts file and in the page cell (`<td class="none">not done</td>`).
Add one sentence that names what is missing, for example "Real run on staging: not done. The fix is not deployed."
Do not write a number, an id or a status that has no source line. A plausible number is still an invented number.
Do not run anything on a shared or production environment to fill a gap. Ask the user.

## 2. Write the page

Copy `template.html` to `.task/<name>-fix.html` and replace every `{{...}}` mark. Keep the CSS as it is.

The parts, in this order:

1. **Header.** `h1` says the result in user words. The meta line gives the fix commit, branch and deploy, and the cause commit when it is known. Not committed or not deployed: the meta line says so.
2. **Terms.** 2 to 4 terms, one sentence each.
3. **1. What was wrong.** 2 to 4 sentences, then one figure (a chain, a sequence with its error exit, or the broken state).
4. **2. How it was fixed.** 2 to 3 sentences, then one figure (before and after, or one card per case). A closed card "What changed in the code".
5. **3. Test evidence.** The table: unit tests (base and branch counts), local real run, deployed real run, what the user sees. Then before and after screenshots. Then closed cards with commands and output.
   - Put each run in the row of the place where it ran. Before on staging and after on local: the other two cells say `not done`.
   - Each run cell gives the proof value and the time. The proof value is what the run measured: a job id, a status code, the element on top, an error text.
6. **4. Lifecycle.** One strip of numbered operations for one real item (real id). Under each: the actor and the store change, or "no change". Mark a step that no run tested as "not tested". Closed cards: the same steps before the fix, and repeat or empty cases.
   - A fix that changes only the screen: the store is the page (DOM). Say in one sentence that no server store changes.

Screenshots: JPEG data URIs, at most 960 px wide, at most 300 KB each.
First crop to the part that shows the fault, so that its text is readable on a phone. Use the same crop for before and after.

```bash
# crop box: left top right bottom in pixels; omit it to keep the full image
python3 -c "import sys,io,base64;from PIL import Image;i=Image.open(sys.argv[1]).convert('RGB');c=sys.argv[2:];i=i.crop(tuple(map(int,c))) if c else i;i.thumbnail((960,960));b=io.BytesIO();i.save(b,'JPEG',quality=72);print('data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode())" shot.png 720 640 1600 1000 > shot.uri
```

## 3. Language and limits

- ASD-STE100. One idea per sentence, at most 20 words. Active voice. The same term every time.
- At most 600 visible words (text outside `details`, `svg`, `pre`). Aim for 250 to 400.
- At most 120 words per closed card.
- Name things. Do not use codes such as B1 or "issue 8" as references.
- Quote error text exactly. Write no secret.
- SVG viewBox width 640. Count 7 px per character at 12 px font.

## 4. Checks before the user sees the page

1. `python3 <this folder>/check.py <page>` exits 0. Code text such as `style={{ ... }}` is no problem: the check looks only for `{{UPPER_CASE}}` marks.
2. If `~/dev/personal/swiss-knife/.claude/skills/copilot/bin/page-check.py` exists, run it too. If it does not exist, continue.
3. Style pass. If you can run the `unslop` skill, run `/unslop <page>`. If you cannot, apply its rules yourself, or tell the user to run it. Do not change quotes, numbers or ids.
4. A fresh subagent (or you, if no subagent is possible) goes through `checklist.md` with the page and the facts file. Fix each fail, then run step 1 and this step again.
5. Do not publish. Tell the user the page path, the check result and each `not done` cell. The user decides to publish.
