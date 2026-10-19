---
name: gee-growth-diary
description: Secondary source-index and article-derived idea skill for the 153-article "GEE" WeChat album by GEEer成长日记. Use only when the user explicitly asks about that article collection, wants Chinese GEE cookbook inspiration, or needs source/title recall from the album. Do not use as the authority for current Earth Engine dataset ids, QA masks, scale factors, exports, or API behavior; use EasyGEE official-doc-grounded references first.
---

# GEE Growth Diary

Use this skill as a source-aware companion for the GEEer成长日记 WeChat album.
It is not the canonical EasyGEE method router.

## Trust Boundary

1. Official Earth Engine docs and catalog pages win.
2. The `easygee` skill and its references win for current workflow shape,
   dataset QA, exports, quotas, authentication, and Map Console behavior.
3. This skill is useful for finding article-inspired task ideas, Chinese
   phrasing, historical examples, and source attribution.
4. Article code and dataset ids must be re-verified before reuse. Many GEE
   tutorials age quickly because catalog versions, QA bands, and best practices
   change.
5. Do not reproduce source article text. The skill contains distilled guidance
   and a source index only.

## When To Use

- The user asks about GEEer成长日记, this WeChat album, or "那 153 篇文章".
- The user wants a Chinese GEE cookbook-style brainstorm, and EasyGEE's
  canonical references do not already answer the method choice.
- You need article titles, links, or rough topic tags for attribution.
- You want to compare an article-inspired method against current official docs.

For routine GEE work such as NDVI, water, classification, time series, export,
Map Console layers, auth, quota, or dataset search, start with `easygee`.

## Resource Map

- Read `references/source-index.md` for article titles, links, dates, and
  heuristic topic tags. Tags are retrieval aids, not reviewed classifications.
- Read `references/workflow-patterns.md` for article-observed workflow motifs
  and known age-related risks.
- Read `references/dataset-method-router.md` only as secondary candidate notes;
  verify candidates through EasyGEE dataset search and official catalog docs.

## Review Checklist

Before turning any article-derived idea into EasyGEE code or documentation:

1. Verify the dataset id in the official Earth Engine catalog or current
   community catalog docs.
2. Replace outdated collections with current versions when appropriate, for
   example Landsat Collection 2 and MODIS/061.
3. Re-check scale factors, units, QA bands, masks, and date coverage.
4. Decide whether the method is product-backed, derived remote sensing,
   supervised/unsupervised classification, thresholding, or current-image
   recognition.
5. Add a visual probe and a small numeric probe before export.
6. Label any unverified article-derived step as provisional.
