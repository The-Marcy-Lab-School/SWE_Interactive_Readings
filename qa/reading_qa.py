#!/usr/bin/env python3
"""QA pass for a Marcy Lab SWE Fellowship reading `index.html` file. Stdlib
only — no deps. Adapted from the Data Analytics Fellowship's reading_qa.py;
see that repo if this one and it ever need to be reconciled.

Usage:
    python3 qa/reading_qa.py Mod0/wsl-setup/index.html
    python3 qa/reading_qa.py Mod1/**/index.html          (shell-expanded glob)

Exits non-zero if any ERROR-level finding exists (WARN-level findings are
judgment calls a human/QA agent should still read, not hard fails).
"""
import re
import sys
import glob
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path

_INSECURE_CTX = ssl.create_default_context()
_INSECURE_CTX.check_hostname = False
_INSECURE_CTX.verify_mode = ssl.CERT_NONE

BRAND_HEXES = {
    "#FFFCF7","#FFF6E4","#FFEECA","#264326","#327A5F","#A6C2B4","#2274B5","#2F5A8B",
    "#EF541E","#EEBC32","#FECC5B","#83671C","#C92929","#F7DFDF","#F8BAC9","#261F1D",
    "#E9EFEB","#E4E7EB","#E1E3E0","#CFD9E3","#B3BBB0","#DEEAF4","#FFFFFF","#FFF","#000",
    "#FFBF47",  # focus ring
    # Darkened text-only variants of border tones, for WCAG AA (4.5:1) text contrast on
    # their matching light fill — the border tones themselves (#C92929/#83671C/#2274B5/
    # #327A5F) are fine for strokes/borders but fall short (2.7-4.3:1) when used as text.
    "#B72525",  # red-700 text-safe, on #F7DFDF
    "#675116",  # gold-700 text-safe, on #FECC5B
    "#1E659D",  # blue-700 text-safe, on #DEEAF4
    "#204D3C",  # forest-600 text-safe, on #A6C2B4
}

BANNED_PHRASES = [
    r"\bmodule\s*\d+\b", r"\bmod\s*\d+\b",
    r"before\s+the\s+lecture", r"before\s+lecture",
    r"upcoming\s+reading", r"upcoming\s+lecture",
    r"required\s+bridge", r"bridge\s+to\s+(the\s+)?lecture", r"bridge\s+to\s+(the\s+)?project",
    r"let'?s\s+dive\s+in", r"delve\s+into", r"unleash\s+the\s+power\s+of",
    r"game-?changer", r"at\s+the\s+end\s+of\s+the\s+day", r"when\s+it\s+comes\s+to",
    r"it'?s\s+important\s+to\s+note\s+that",
    r"recall\s+before", r"before\s+you\s+start\s+this\s+reading\s+let'?s\s+recall",
]
BANNED_UNICODE = ["→","✅","❌","✓","✨","🔥","💡","🚀"]
BANNED_ARROW_ENTITIES = ["&rarr;", "&#8594;", "&#x2192;", "&larr;", "&rArr;"]

EXPORT_BUTTON_HINTS = ("copy", "copyplain", "plaintext")


def find(pattern, text, flags=re.I):
    return re.findall(pattern, text, flags)


def check_banned_phrases(text):
    findings = []
    for pat in BANNED_PHRASES:
        for m in re.finditer(pat, text, re.I):
            findings.append(("ERROR", f"banned phrase near: ...{text[max(0,m.start()-20):m.end()+20]}..."))
    for ch in BANNED_UNICODE:
        if ch in text:
            findings.append(("ERROR", f"banned literal character used instead of a real icon: {ch}"))
    for entity in BANNED_ARROW_ENTITIES:
        if entity in text:
            findings.append(("ERROR", f"banned typed-arrow HTML entity (renders the same as a literal arrow): {entity}"))
    # 3+ em-dashes in a single line is the density tell, not a single stray one
    for line in text.splitlines():
        if line.count("—") >= 3:
            findings.append(("WARN", f"em-dash pileup (3+) in one line: {line.strip()[:80]}"))
    # ASCII "->" is the same typed-arrow problem in disguise (e.g. "10 -> 20 -> None"
    # in a trace/summary string). A real Python return-type annotation
    # ("def foo(x: int) -> str:") is the one legitimate use — skip only that shape.
    PY_RETURN_TYPE = re.compile(r"\)\s*->\s*[\w\[\], .\"']+\s*:")
    # HTML comment closers ("-->") trivially contain "->" as a substring — strip
    # comments out first so an authoring note like "<!-- LEFT: ... -->" never
    # false-positives here.
    text_no_comments = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for line in text_no_comments.splitlines():
        if "->" not in line:
            continue
        if PY_RETURN_TYPE.search(line):
            continue
        findings.append(("WARN", f"possible typed arrow ('->') outside a Python return-type annotation — spell it out ('then'/'leads to') unless this is real command output: {line.strip()[:90]}"))
    return findings


def check_headings(text):
    tags = re.findall(r"<h([1-6])[ >]", text, re.I)
    findings = []
    if tags.count("1") != 1:
        findings.append(("ERROR", f"expected exactly one <h1>, found {tags.count('1')}"))
    prev = None
    for t in tags:
        t = int(t)
        if prev is not None and t > prev + 1:
            findings.append(("ERROR", f"heading level skips from h{prev} to h{t}"))
        prev = t
    return findings


def check_font_sizes(text):
    findings = []
    for m in re.finditer(r"font-size\s*:\s*([\d.]+)(px|rem|pt)", text, re.I):
        val, unit = float(m.group(1)), m.group(2).lower()
        px = val if unit == "px" else val*16 if unit == "rem" else val*1.333
        if px < 14:
            findings.append(("ERROR", f"font-size below 14px floor: {m.group(0)} (~{px:.1f}px)"))
    # SVG presentation-attribute form: font-size="12" (no colon, not caught above).
    # Diagram text has its own, lower preferred floor (16px) since it sits inside a
    # fixed viewBox next to much larger surrounding body text.
    for m in re.finditer(r'font-size="([\d.]+)"', text):
        px = float(m.group(1))
        if px < 14:
            findings.append(("ERROR", f'SVG font-size below 14px floor: {m.group(0)} (~{px:.1f}px)'))
        elif px < 16:
            findings.append(("WARN", f'SVG font-size below the preferred 16px floor for diagram text: {m.group(0)}'))
    return findings


def check_unknown_colors(text):
    findings = []
    for m in re.finditer(r"#[0-9A-Fa-f]{3,6}\b", text):
        hexval = m.group(0).upper()
        if hexval not in {h.upper() for h in BRAND_HEXES}:
            findings.append(("WARN", f"color not in the brand palette, verify contrast manually: {hexval}"))
    return findings


def check_alt_text(text):
    findings = []
    for m in re.finditer(r"<img\b[^>]*>", text, re.I):
        if not re.search(r'alt\s*=\s*"[^"]*"', m.group(0), re.I):
            findings.append(("ERROR", f"<img> missing alt text: {m.group(0)[:80]}"))
    return findings


def check_links(text):
    findings = []
    urls = set(re.findall(r'(?:href|src)\s*=\s*"(https?://[^"]+)"', text, re.I))
    for url in urls:
        if "youtube.com/embed" in url or "youtube.com/iframe_api" in url:
            continue  # known-good, skip network call for speed
        findings.extend(check_one_url(url))
    return findings


def _http_error_finding(code, url):
    if code == 999:
        # LinkedIn's (and a few other sites') non-standard anti-bot status for
        # automated requests — observed to be intermittent and inconsistent,
        # not a real broken link. Always a WARN, never a hard failure.
        return ("WARN", f"link returned 999 (likely anti-bot rate-limiting, not a dead link): {url}")
    if code >= 400 and code != 405:  # some sites reject HEAD; 405 isn't a dead link
        return ("ERROR", f"link returned {code}: {url}")
    return None


def check_one_url(url, _retried=False):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (reading-qa)"})
    try:
        urllib.request.urlopen(req, timeout=8)
        return []
    except urllib.error.HTTPError as e:
        if e.code == 999 and not _retried:
            return check_one_url(url, _retried=True)
        finding = _http_error_finding(e.code, url)
        return [finding] if finding else []
    except urllib.error.URLError as e:
        if not isinstance(getattr(e, "reason", None), ssl.SSLError):
            if not _retried:
                return check_one_url(url, _retried=True)
            return [("WARN", f"link could not be verified ({e}): {url}")]
        try:
            urllib.request.urlopen(req, timeout=8, context=_INSECURE_CTX)
            return []
        except urllib.error.HTTPError as e2:
            if e2.code == 999 and not _retried:
                return check_one_url(url, _retried=True)
            finding = _http_error_finding(e2.code, url)
            return [finding] if finding else []
        except Exception as e2:
            if not _retried:
                return check_one_url(url, _retried=True)
            return [("WARN", f"link could not be verified even with relaxed SSL ({e2}): {url}")]
    except Exception as e:
        if not _retried:
            return check_one_url(url, _retried=True)
        return [("WARN", f"link could not be verified ({e}): {url}")]


def check_export_wiring(text):
    findings = []
    button_ids = re.findall(r'<button[^>]*\bid="([^"]+)"', text, re.I)
    candidates = [b for b in button_ids if any(h in b.lower() for h in EXPORT_BUTTON_HINTS)]
    for bid in candidates:
        if not re.search(re.escape(bid), text.split("<script", 1)[-1] if "<script" in text else ""):
            findings.append(("WARN", f"button id '{bid}' looks like the copy-plain-text control but no matching JS reference found"))
    if "ReadingKit" in text and not re.search(r"\.copyPlainText\s*\(", text):
        findings.append(("ERROR", "no ReadingKit.copyPlainText(...) call found — every reading needs the 'Copy Plain Text Answers' control"))
    return findings


def check_time_estimate(text, word_count):
    findings = []
    m = re.search(r"~?(\d+)(?:[–-](\d+))?\s*min", text, re.I)
    if not m:
        findings.append(("WARN", "no visible time estimate pill found (e.g. '~12 minutes')"))
        return findings
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    if hi > 15:
        findings.append(("ERROR", f"stated time ~{hi} min exceeds this format's 15-minute hard ceiling (including video) — trim an activity or the video, don't just under-report"))
    reading_minutes = word_count / 200
    if reading_minutes > lo * 2.5:
        findings.append(("WARN", f"stated time ~{lo} min looks low next to ~{word_count} words (~{reading_minutes:.0f} min reading alone, before activities/video)"))
    return findings


def visible_text(html):
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def check_copyright(text):
    if "marcy" not in text.lower() or "property" not in text.lower():
        return [("ERROR", "no copyright/ownership footer found (expected an 'is the property of The Marcy Lab School...' line)")]
    return []


def check_meta_sidecar(path):
    meta_path = Path(path).parent / "reading.meta.json"
    if not meta_path.exists():
        return [("ERROR", "no sibling reading.meta.json found")]
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [("ERROR", f"reading.meta.json is not valid JSON: {e}")]
    for field in ("title", "skill", "topic_area", "time_minutes"):
        if not meta.get(field):
            return [("ERROR", f"reading.meta.json is missing required field '{field}'")]
    return []


def check_no_recall_section(text_lower):
    if re.search(r"\brecall\b.{0,20}\b(before|first|check)\b", text_lower):
        return [("WARN", "found the word 'recall' near 'before/first/check' — this format has no recall/prerequisite-check section, confirm this isn't one")]
    return []


def _count_syllables(word):
    word = word.lower()
    vowel_groups = re.findall(r"[aeiouy]+", word)
    count = len(vowel_groups)
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1
    return max(count, 1)


def check_reading_level(html):
    # Strip anything that isn't real prose the student reads continuously:
    # code blocks, the technical-vocabulary flip cards (explicitly allowed to
    # run more technical per the format's own rule), and quiz/button/label UI
    # chrome, which isn't prose either.
    no_code = re.sub(r"<(code|pre)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    no_vocab = re.sub(r'<div class="mlrk-grid">.*?</div>\s*</section>', " ", no_code, flags=re.S | re.I)
    text = visible_text(no_vocab)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    if len(sentences) < 3 or len(words) < 50:
        return []  # not enough real prose to score meaningfully
    syllables = sum(_count_syllables(w) for w in words)
    grade = 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59
    if grade > 10.5:
        return [("WARN", f"Flesch-Kincaid grade level ~{grade:.1f} (target: ~9th grade outside the vocabulary section) — check for long sentences or dense wording in the prose, not just technical terms")]
    return []


AI_TELL_PHRASES = [
    r"\bin today'?s\b", r"\bin the (?:ever[- ]evolving|fast[- ]paced|digital)\b",
    r"\bit'?s worth noting\b", r"\blet'?s explore\b", r"\bdive deep(?:er)?\b",
    r"\bunlock(?:s|ing)?\s+the\b", r"\bpowerful tool\b", r"\bwhether you'?re\b.{0,20}\bor\b",
    r"\bin conclusion\b", r"\bin summary\b", r"\bplays a (?:crucial|vital|key) role\b",
]


def check_ai_sounding_language(text):
    findings = []
    for pat in AI_TELL_PHRASES:
        for m in re.finditer(pat, text, re.I):
            findings.append(("WARN", f"AI-tutorial-sounding phrase, reword to something more personable: ...{text[max(0,m.start()-15):m.end()+15]}..."))
    return findings


_VIDEO_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (reading-qa)"


def _urlopen_relaxed(req):
    try:
        return urllib.request.urlopen(req, timeout=8)
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), ssl.SSLError):
            return urllib.request.urlopen(req, timeout=8, context=_INSECURE_CTX)
        raise


def _fetch_watch_page(video_id):
    req = urllib.request.Request(f"https://www.youtube.com/watch?v={video_id}", headers={"User-Agent": _VIDEO_UA})
    with _urlopen_relaxed(req) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def check_video_language(html, skip_network=False):
    # A video's title/channel name being in English is not proof its spoken
    # audio is — a real bug shipped this way (English title, Hindi audio).
    # The reliable signal is the watch page's default (first) caption track.
    ids = re.findall(r'videoId\s*:\s*"([A-Za-z0-9_-]{6,})"', html)
    if not ids:
        return []
    if skip_network:
        return [("WARN", f"reminder: manually confirm the recommended video ({', '.join(ids)}) is in English before shipping — network checks skipped")]
    findings = []
    for vid in ids:
        try:
            body = _fetch_watch_page(vid)
        except Exception as e:
            findings.append(("WARN", f"could not verify language of video {vid} ({e}) — confirm manually via its caption track"))
            continue
        m = re.search(r'"captionTracks":\[\{"baseUrl":"[^"]*","name":\{"simpleText":"[^"]*"\},"vssId":"[^"]*","languageCode":"([a-z-]+)"', body)
        if not m:
            findings.append(("WARN", f"could not find a caption track for video {vid} to verify language — confirm manually"))
        elif not m.group(1).startswith("en"):
            findings.append(("ERROR", f"video {vid}'s default caption track is language '{m.group(1)}', not English — its audio likely isn't English either, swap this video"))
    return findings


def check_video_embeddable(html, skip_network=False):
    ids = re.findall(r'videoId\s*:\s*"([A-Za-z0-9_-]{6,})"', html)
    if not ids or skip_network:
        return []
    findings = []
    for vid in ids:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json",
            headers={"User-Agent": _VIDEO_UA},
        )
        try:
            _urlopen_relaxed(req)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                findings.append(("ERROR", f"video {vid} returns 401 from oEmbed — its owner has disabled embedding (shows as Error 153 in the player), swap this video"))
        except Exception as e:
            findings.append(("WARN", f"could not verify embeddability of video {vid} ({e}) — confirm manually"))
    return findings


def check_video_duration(html, skip_network=False):
    ids = re.findall(r'videoId\s*:\s*"([A-Za-z0-9_-]{6,})"', html)
    if not ids or skip_network:
        return []
    findings = []
    for vid in ids:
        try:
            body = _fetch_watch_page(vid)
        except Exception as e:
            findings.append(("WARN", f"could not verify duration of video {vid} ({e}) — confirm manually it's under 5 minutes"))
            continue
        m = re.search(r'"lengthSeconds":"(\d+)"', body)
        if not m:
            findings.append(("WARN", f"could not read duration of video {vid} — confirm manually it's under 5 minutes"))
            continue
        secs = int(m.group(1))
        if secs > 300:
            findings.append(("ERROR", f"video {vid} is {secs//60}:{secs%60:02d} — exceeds this format's 5-minute video cap; find a shorter one, or drop the video section (not every reading needs one)"))
    return findings


def run(path, skip_links=False):
    html = Path(path).read_text(encoding="utf-8")
    text = visible_text(html)
    word_count = len(text.split())
    findings = []
    findings += check_banned_phrases(text)
    findings += check_banned_phrases(html)  # catch phrases inside attributes/comments too
    findings += check_headings(html)
    findings += check_font_sizes(html)
    findings += check_unknown_colors(html)
    findings += check_alt_text(html)
    findings += check_export_wiring(html)
    findings += check_time_estimate(html, word_count)
    findings += check_copyright(text)
    findings += check_meta_sidecar(path)
    findings += check_no_recall_section(text.lower())
    findings += check_reading_level(html)
    findings += check_ai_sounding_language(text)
    findings += check_video_language(html, skip_network=skip_links)
    findings += check_video_embeddable(html, skip_network=skip_links)
    findings += check_video_duration(html, skip_network=skip_links)
    if not skip_links:
        findings += check_links(html)
    return findings


def main():
    args = sys.argv[1:]
    skip_links = "--skip-links" in args
    args = [a for a in args if a != "--skip-links"]
    paths = []
    for a in args:
        paths.extend(glob.glob(a, recursive=True))
    if not paths:
        print("No files matched.", file=sys.stderr)
        sys.exit(2)
    had_error = False
    for path in paths:
        print(f"\n=== {path} ===")
        findings = run(path, skip_links=skip_links)
        if not findings:
            print("  OK — no findings.")
            continue
        for level, msg in findings:
            print(f"  [{level}] {msg}")
            if level == "ERROR":
                had_error = True
    sys.exit(1 if had_error else 0)


if __name__ == "__main__":
    main()