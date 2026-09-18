#!/usr/bin/env python
"""Search EasyGEE local reference files with lightweight keyword scoring."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DEFAULT_GLOBS = (
    "references/*.md",
    "references/*.json",
    "references/geoai-with-python/**/*.md",
    "../../extras/gee-growth-diary/SKILL.md",
    "../../extras/gee-growth-diary/references/*.md",
)

CORE_METHOD_REFERENCES = {
    "references/landsat-cloud-mask-methods.md",
    "references/cross-sensor-harmonization.md",
    "references/temporal-compositing.md",
    "references/sentinel1-sar-methods.md",
}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "when",
    "into",
    "will",
    "should",
    "use",
    "using",
    "gee",
    "gee",
    "aoi",
}


@dataclass(frozen=True)
class SearchHit:
    score: float
    path: str
    title: str
    snippet: str


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def query_terms(query: str) -> list[str]:
    terms: list[str] = []
    for term in re.findall(r"[\w./:+-]+|[\u4e00-\u9fff]{2,}", query.lower(), flags=re.UNICODE):
        token = term.strip().strip(".,;:()[]{}<>\"'")
        if len(token) >= 2 and token not in STOPWORDS and token not in terms:
            terms.append(token)
    return terms or [query.lower().strip()]


def title_for(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def chunk_text(text: str, chunk_chars: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if not current:
            current = paragraph
        elif len(current) + len(paragraph) + 2 <= chunk_chars:
            current += "\n\n" + paragraph
        else:
            chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    if not chunks and text.strip():
        chunks = [text.strip()[:chunk_chars]]
    return chunks


def score_chunk(path: str, title: str, chunk: str, terms: list[str], query: str) -> float:
    path_l = path.lower()
    title_l = title.lower()
    text_l = chunk.lower()
    score = 0.0
    for term in terms:
        score += 6.0 * title_l.count(term)
        score += 3.0 * path_l.count(term)
        score += text_l.count(term)
    if query.lower() in text_l:
        score += 8.0
    # Curated EasyGEE references are the operational knowledge layer. The
    # growth diary remains searchable as secondary teaching material, but it
    # should not outrank a matching curated method card merely by repetition.
    if path_l.startswith("references/"):
        score += 12.0
    if path_l in CORE_METHOD_REFERENCES:
        score += 10.0
    if path_l.startswith("../../extras/gee-growth-diary/"):
        score *= 0.20
    return score


def normalize_snippet(chunk: str, chars: int) -> str:
    snippet = re.sub(r"\s+", " ", chunk).strip()
    return snippet[:chars]


def iter_files(root: Path, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and path not in files:
                files.append(path)
    return sorted(files)


def search(query: str, limit: int, chunk_chars: int, snippet_chars: int, patterns: list[str]) -> list[SearchHit]:
    root = skill_dir()
    terms = query_terms(query)
    hits: list[SearchHit] = []
    for path in iter_files(root, patterns):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(root).as_posix()
        title = title_for(text, path.stem)
        for chunk in chunk_text(text, chunk_chars):
            score = score_chunk(rel, title, chunk, terms, query)
            if score > 0:
                hits.append(
                    SearchHit(
                        score=score,
                        path=rel,
                        title=title,
                        snippet=normalize_snippet(chunk, snippet_chars),
                    )
                )
    hits.sort(key=lambda hit: (-hit.score, hit.path, hit.title))
    return hits[:limit]


def print_text(query: str, hits: list[SearchHit]) -> None:
    print(f"query: {query}")
    print("search: easygee-local-keyword")
    if not hits:
        print("No local reference matches.")
        return
    for index, hit in enumerate(hits, start=1):
        print(f"\n{index}. score={hit.score:.2f} {hit.title}")
        print(f"   path={hit.path}")
        print(f"   {hit.snippet}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--chunk-chars", type=int, default=1800)
    parser.add_argument("--snippet-chars", type=int, default=360)
    parser.add_argument("--pattern", action="append", dest="patterns", help="Additional or replacement glob under skills/easygee")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    if not query:
        parser.error("provide search query")
    patterns = args.patterns if args.patterns else list(DEFAULT_GLOBS)
    hits = search(query, max(1, args.limit), max(400, args.chunk_chars), max(120, args.snippet_chars), patterns)
    if args.json:
        print(json.dumps([asdict(hit) for hit in hits], ensure_ascii=False, indent=2))
    else:
        print_text(query, hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
