# Prose exemplars — plain English, from Angelica's review (2026-10-06)

Real passages from shipped readings, with the rewrite Angelica asked for.
Read these before writing explanatory prose. When a sentence you have written
resembles a "Written" column below, it is wrong for the same reason.

## Why this file exists

Ben's writing guide governs **the completeness of reasoning between
sentences**: whether a "so" has its premise on the page, whether a consequence
is named, whether the rule behind a result is stated. It says nothing about how
to construct a sentence.

Applied as a *style* rule it produces contorted prose: abstract subjects,
modifiers stranded after nouns, actions turned into noun phrases, and openings
that defer the point to build suspense. **When Ben's guide and plain English
pull in opposite directions, plain English wins.** A reader who has to re-read
a sentence to find its subject has already lost the reasoning the guide exists
to protect.

## The exemplars

**1. Say the fact plainly. Do not restate it abstractly.**

> Written: "The app had not lost anything. It had her number, and her number was 0."
>
> Wanted: "The app did not lose her data. She just hadn't spent anything yet."

"Her number" is an abstraction standing in for a fact the reader already has.
Name the real thing that happened.

**2. Answer the question you just raised. Do not defer it.**

> Written: "Read `if not total:` out loud and it sounds like 'if there is no total.' Python reads that line differently, and the gap between those two readings is what this whole reading is about: which line of a program runs next, and what an `if` statement really does with the value you hand it."
>
> Wanted: "…Python reads the line as 'if total is X'. This leads to unexpected results, and knowing how Python interprets X is…"

Stating that a gap exists, then promising to explain it later, is suspense, not
teaching. Say what Python actually does, in the same breath as the misreading.
Never write "what this whole reading is about" — the reader is already reading it.

**3. Use a natural subject. Do not nominalize an action.**

> Written: "A week of $250 and a week of $20 should not get the same sentence out of Ledger Lite."
>
> Wanted: "Spending $250 a week vs. $20 should not get the same output. Python runs statements from top to bottom by default…"

"A week of $250" is an action bent into a noun phrase. "Spending $250 a week"
is the action. Prefer the verb.

**4. Keep modifiers next to what they modify.**

> Written: "prints the delivery routes busiest first"
>
> Wanted: "prints the busiest routes first"

An adjective belongs before its noun. This is the "swapping the adjective after
the noun" pattern Angelica named explicitly — do not do it.

**5. No gendered pronouns for people in examples.**

> Written: "A wrong order hands a student a single label for the wrong tier. A second mistake hands her several labels at once, and it looks even more innocent on the page."

Three faults in two sentences:
- **"a student" then "her"** — a hypothetical person was silently gendered.
  **Eliminate gendered pronouns for people throughout.** Use "they/them", repeat
  the noun, or rewrite to avoid the pronoun. This applies to invented characters
  too, not only to generic ones.
- **"innocent"** — the wrong word, and it does not mean anything here. A mistake
  is not innocent. If the point is that the mistake is hard to spot, write "hard
  to spot".
- **"A wrong order hands a student…"** — an abstract subject performing a human
  action. Rule 6 ("make the subject the actual code element") is for sentences
  explaining what code does. In a sentence about a person, it produces nonsense.

A rewrite: "Putting the conditions in the wrong order shows one label from the
wrong tier. Deleting the `el` from each `elif` is harder to spot, and it shows
several labels at once."

**6. Prefer select-all over type-the-answer for recalling a fixed set.**

> Written: "List the falsy values. Python has a short, fixed set of them, and everything else is truthy. Three are already named below. Type the other three, one per box. / Already named: False, 0.0, and empty collections such as [] and {}."
>
> Wanted: a select-all-that-applies.

Partially pre-filling a list and asking for "the other three" makes the student
reverse-engineer which three are missing, which tests bookkeeping, not
knowledge. **This reverses an earlier instruction of mine** that favored typed
production over recognition — Angelica's call, and it stands: for a short fixed
set like the falsy values, select-all is the better activity.

## The standing rules these add up to

1. **Plain English wins** over any rule in the writing guide.
2. **Say the fact, then the rule it illustrates** — not an abstraction of the fact.
3. **Do not defer.** No "that gap is what this reading is about."
4. **Natural subject, natural word order.** No nominalizations, no stranded modifiers.
5. **Subject-verb agreement, and a pronoun that unambiguously points at one noun.**
6. **No gendered pronouns for people.** `qa/reading_qa.py` WARNs on them.
7. **Every word has to mean something** in its sentence. "Innocent", "elegant",
   "powerful" usually do not.