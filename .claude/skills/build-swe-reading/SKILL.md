---
name: build-swe-reading
description: Build a standalone interactive HTML reading for the Marcy Lab School Software Engineering Fellowship, hosted on GitHub Pages. Use when asked to create, refactor, or QA a reading in this repo (SWE_Interactive_Readings).
---

# Build an SWE interactive reading

This is the Software Engineering Fellowship's own reading format — a **short, focused sibling** of the Data Analytics Fellowship's reading-kit pattern (same visual brand, same underlying activity primitives), but deliberately smaller in scope. Read this whole file before building or refactoring a reading. Read one already-shipped reading in this repo as a worked example before writing a new one.

## What's different from the DA fellowship's readings (don't port these over)
- **10-15 minutes total, including the video.** This is a hard ceiling, not a soft target — if the honest count (see "Time estimate" below) comes out over 15 minutes, cut an activity or trim the video pick, don't just under-report the number.
- **No recall/prerequisite-check section.** Don't open with a "test what you already know" block. Teach the topic directly.
- **No GitHub submission flow, no persona/leaderboard.** The only export/persistence story is: localStorage autosave (so a refresh doesn't lose progress) plus a single **"Copy Plain Text Answers"** button (`ReadingKit.copyPlainText`) that copies the reading's title, score, and every free-response answer to the clipboard as plain text. That's it — no download-to-file, no GitHub issue, no alias picker.
- **Real-world use case required, and it can be a real, named public event or product**, not only a fictional-but-realistic scenario. E.g. "the CrowdStrike outage that took down Windows machines worldwide" or "GitHub's own Nov. 2024 rate-limit changes" are fair game here, as-is or lightly fictionalized. A realistic simulated scenario (invented company, real-shaped problem) is equally fine when a real citable event doesn't fit the topic. Either way the scenario must be genuinely tied to the mechanism being taught, not decorative.

## What's the same as the DA fellowship's readings (keep these)
- Same brand: `assets/brand-tokens.css` + `assets/reading-kit.css`. Never hand-pick a hex outside the token file's palette.
- Same shared engine, `assets/reading-kit.js` (a trimmed fork — see its own header comment for exactly what's missing vs. the DA kit's version). Same function names for everything it does keep: `ReadingKit.quiz()`, `.selectAll()`, `.flipCards()`, `.dragDrop()`, `.orderSteps()`, `.selfCheck()`, `.traceStepper()`, `.terminal()`, `.video()`, `.freeResponse()`, `.activity()`, `.Scoring`, `.init()`.
- Expandable hints via native `<details class="mlrk-hint"><summary>Need a hint?</summary>...</details>` — never an always-visible callout for something that's genuinely a hint.
- Expandable/revealed answers when a check makes sense (predict-then-reveal, self-check with 2 tries before showing the answer) — same 1st-try/2nd-try/reveal scoring pattern as the DA kit for quiz-shaped questions; ungraded self-checks (drag-drop, order-steps) still get 2 tries before revealing.
- Full activity variety: aim for 4-6+ different interactive types across one reading (flip cards, fill-in-the-blank/typed prediction, drag-and-drop, order-the-steps, a terminal/code simulator where the topic calls for it, select-all, single-answer quiz). Prefer typed-input activities over pure reveal-buttons where it fits.
- No module numbers, no "before lecture"/"pre-lecture"/"bridge to lecture" language anywhere in visible text — same ban as the DA fellowship, for the same reason (a reading should read as self-contained, not positioned relative to a specific class session).
- No literal or HTML-entity arrow characters (`→`, `&rarr;`, `&#8594;`, etc.) and no ASCII `->` used as narrative shorthand (e.g. "10 -> 20") — spell it out ("then", "leads to"). The one legitimate exception is a real Python return-type annotation (`def foo() -> int:`).
- WCAG AA: real alt text/`<title>`+`<desc>` on every SVG, heading hierarchy that doesn't skip levels, body text never below 14px, visible keyboard focus states, no meaning conveyed by color alone.
- **Every reading with an inline SVG diagram needs an actual headless-Chrome screenshot check, not just a source-code read.** Text overlapping a same-colored line, a text block wider than its box, and a label sitting where two diverging lines haven't yet spread apart are all real bugs that pass every other check clean and only show up by looking at the rendered page. Take a real screenshot (`google-chrome --headless --disable-gpu --no-sandbox --window-size=900,<tall> --screenshot=path.png <file-url>`; check the actual output height with `sips -g pixelHeight` or PIL before assuming a fixed height covered the whole page) and view it (crop into sections with PIL if the image is very tall). Re-screenshot after any fix to confirm it actually worked.
- Real video-duration verification before picking one — YouTube's watch page is JS-rendered, so `WebFetch` cannot see the real duration. Use:
  ```bash
  curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "https://www.youtube.com/watch?v=<id>" | grep -o '"lengthSeconds":"[0-9]*"' | head -1
  ```
  Given the 10-15-minute *total* ceiling, a video here needs to be short — typically under 5 minutes, definitely never more than ~7, since it has to leave room for the actual interactive content. If nothing short enough and on-topic exists from a reputable channel, it's fine to skip the video for that reading rather than force a bad fit.
- Copyright footer, same wording as the DA fellowship's: "This reading is the property of The Marcy Lab School and Angelica Spratley. Contact the owners before republishing, reusing, or monetizing this content elsewhere." (adjust the named owner only if Angelica says to).
- **When a real company/product is the actual subject of the scenario (not just a passing citation), briefly say what it is/does inline, in the same sentence or the next one — don't assume the reader recognizes the name.** A first real bug found this way: a reading opened with "Valve's own Steam client" and "Knight Capital Group's trading system" with no explanation of either — fine for a reader who already knows Steam is a PC game storefront or that Knight Capital was a Wall Street trading firm, useless for one who doesn't. Universally-known names (Amazon, Microsoft, Excel) don't need this; anything narrower does. A source citation in a footnote-style aside is fine to leave unexplained (e.g. naming the journal or court order a fact came from) — this rule is about the company/product the scenario is actually built around.
- **An SVG tree/hierarchy diagram must show depth via each line's own `x` coordinate, never via leading whitespace inside a `<text>` element's content.** A first real bug found this way: a folder-tree diagram used `<text x="24" y="100">    └── weather-app/</text>` (four leading spaces) to indent a nested folder one level in — the leading spaces silently failed to render as visible indentation, so the nested folder looked like a sibling of its parent instead of a child. Shift `x` itself per depth level (e.g. `+34` per level) instead.
- **A long, unbroken inline `<code>` string (a full path, a long identifier) must be able to wrap inside a narrow container like a flip card.** `reading-kit.css` sets `code{overflow-wrap:break-word}` globally for exactly this — don't override it with a container that forces `white-space:nowrap` or `overflow:hidden` around code text. If you add a genuinely long code snippet anywhere narrow, sanity-check it by flipping/opening that element in a real screenshot, not just reading the source.

## Structure of a reading
No numbered "Recall" section, otherwise similar shape to the DA readings:

1. **Header**: eyebrow ("Interactive reading"), `<h1>` title, a one-paragraph lead that opens inside the real-world scenario (not a dry definition), meta pills (estimated time, "Interactive", etc.).
2. **The scenario, stated concretely** — what happened (real event or realistic simulation), why it's relevant to the reader, and what question/problem the rest of the reading is going to answer using the target topic. This doubles as the "why does this matter" hook; don't write a separate generic "why this matters" paragraph on top of it — one strong scenario open is enough for a 10-15 minute reading.
3. **Vocabulary** (flip cards) — only the terms actually needed for this topic, not an exhaustive glossary.
4. **Teach the mechanism** — the actual explanation, with a real diagram (inline SVG, screenshot-verified) when the relationship between parts is genuinely hard to hold in your head, plus at least one hands-on activity (fill-in-the-blank code, a terminal simulator, a predict-the-output check, a drag-drop, etc.) woven directly into the explanation rather than bolted on at the end.
5. **A short video**, only if a genuinely good, verified-short one exists for this exact topic.
6. **One more practice activity** of a different type than step 4's, to hit the activity-variety bar without padding the reading long.
7. **Quick close**: 1-2 sentence summary + one real critical-thinking or reflection question (free response, `data-save` so it's captured by "Copy Plain Text Answers"). Never phrase this as a "bridge" to anything else.
8. **Score chip** (`ReadingKit.Scoring.renderChip`) + **Copy Plain Text Answers** button (`ReadingKit.copyPlainText`) + copyright footer.

## Time estimate methodology (10-15 min ceiling, video included)
Build the top-of-page time pill from real counts:
- ~40 seconds per quiz/question-style item.
- ~90 seconds per hands-on activity (flip-card set, drag-drop, order-the-steps, terminal run, fill-in-the-blank).
- ~90 seconds per free-response box.
- The video's actual verified duration.
- ~2-3 minutes baseline for reading the scenario/explanation prose itself.

Add it up. If it's over 15, cut something — don't shrink the displayed number to hide an honest overage. A typical reading here should land around 3-5 quiz/activity items total (not the 15-20+ item readings the DA fellowship builds) — this format is intentionally lean.

## Pipeline
1. **Scope the topic** against this repo's README/existing readings so two readings don't cover the same mechanism.
2. **Pick the real-world scenario** — a real named event/product or a realistic simulation, tied directly to the mechanism being taught.
3. **Author `index.html`** at `Mod<N>/<topic-slug>/index.html` (module numbers 0/1/2 mirror this fellowship's own curriculum: Mod0 = command line/environment/git, Mod1 = Python fundamentals, Mod2 = basic OOP), using `assets/brand-tokens.css` + `assets/reading-kit.css` + `assets/reading-kit.js`. Write a sidecar `reading.meta.json`: `{title, topic_area, time_minutes}` (`topic_area` is a short human label like "Command Line & Environment", "Python Fundamentals", "Object-Oriented Programming" — used to group the README table, no controlled-vocabulary file needed at this scale).
4. **QA pass**: run `python3 qa/reading_qa.py <path>/index.html`, fix every ERROR. Syntax-check the inline `<script>`. Take the headless-Chrome screenshot pass described above for any SVG.
5. **Regenerate the README**: `python3 build_readme.py` (rebuilds the table between `<!-- READINGS_TABLE_START/END -->` markers from every `reading.meta.json` — never hand-edit the table).