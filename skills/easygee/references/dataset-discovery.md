# Dataset Discovery

Use this reference whenever the user names a dataset, asks for a theme such as
DEM, or describes an analysis task without knowing which Earth Engine products
are appropriate.

## Plugin Architecture

EasyGEE separates dataset discovery into three layers:

1. The **catalog engine** in `scripts/dataset_catalog_engine.py` loads the
   official Earth Engine STAC catalog plus the GEE Community Catalog, then
   performs deterministic bilingual retrieval, filtering, ranking, comparison,
   and verification.
2. This **skill** interprets the scientific intent, chooses search versus task
   recommendation, explains trade-offs, and carries the selected records into
   the GEE/geemap workflow.
3. The **MCP server** exposes stable tools for agents that should not need to
   know script paths or catalog implementation details.

The ontology is deliberately small and inspectable. It expands common Chinese
and English remote-sensing concepts without requiring an embedding service or
sending a user's task to a third party. The full catalog remains the source of
records; the ontology is only a retrieval and task-role aid.

## Choose The Entry Point

- Known id or approximate product name: use `search`, normally in `auto` mode.
- Theme such as `DEM`, `土壤湿度`, or `night lights`: use `search`; the engine
  detects concepts and ranks matching current products.
- Outcome such as `山区洪水风险评估`: use `recommend`; it builds a role-based
  bundle such as event hazard, historical baseline, terrain, rainfall forcing,
  and exposure.
- Two or more candidates already selected: use `compare` before choosing.
- Final candidate about to be coded: use `verify`. Catalog verification is
  offline/cache-friendly; `--live` additionally probes the Earth Engine API
  with existing credentials and never starts OAuth.

## Commands

```powershell
python scripts/dataset_catalog_engine.py search DEM --limit 8
python scripts/dataset_catalog_engine.py search "土壤湿度" --source official
python scripts/dataset_catalog_engine.py search "Sentinel-2" --max-resolution-m 10
python scripts/dataset_catalog_engine.py recommend "山区洪水风险评估" --limit-per-role 2
python scripts/dataset_catalog_engine.py compare COPERNICUS/DEM/GLO30_2024_1 USGS/SRTMGL1_003
python scripts/dataset_catalog_engine.py verify COPERNICUS/DEM/GLO30_2024_1
python scripts/dataset_catalog_engine.py stats
```

Catalog modes are `auto`, `official`, `community`, `all`, `giswqs`, and
`curated`. `auto` merges official and community sources and uses local caches
when possible. Filters include source, provider, category, dataset kind, maximum
known resolution, and deprecated-product inclusion.

## Ranking Contract

The score combines exact id/title evidence, token matches across weighted
fields, bilingual concept matches, preferred current products for recognized
concepts, source provenance, and a deprecation penalty. The engine returns
`match_reasons` so an agent can explain why a result was surfaced.

Official provenance is a useful trust signal, not an absolute relevance rule.
A community record may rank highly when it is a much better thematic match.
Deprecated datasets are excluded by default. If the user explicitly needs an
older product, pass `--include-deprecated`, explain the status, and compare it
with the current replacement.

Resolution filtering only accepts records whose resolution can be parsed from
safe title/tag metadata. It does not guess resolution from arbitrary numbers in
descriptions, where depths, revisit periods, and version numbers are common.

## No-Match And Clarification Policy

Never substitute a generic optical dataset when retrieval has no evidence. An
empty candidate list with `needs_clarification: true` is a valid result. Ask for
the missing variable, AOI, time range, required spatial/temporal resolution, or
whether official-only sources are required. This prevents plausible-looking
but irrelevant dataset recommendations.

## Final Verification Gate

Before generating analysis code, verify:

- exact asset id and deprecation/replacement status;
- asset kind (`Image`, `ImageCollection`, or table/feature collection);
- band names, units, scale/offset, masks, and class semantics;
- temporal coverage, update cadence, and AOI availability;
- native/proposed analysis scale and projection implications;
- license, citation, provider, and community-source maintenance status;
- whether companion QA, baseline, forcing, or exposure datasets are required.

Task-role recommendations are starting bundles. Do not imply that every role is
mandatory, and do not silently collapse hazard, baseline, and exposure into a
single dataset choice.

## Scripts

- Use `scripts/search_easygee_references.py "<query>"` for token-efficient
  local recall across EasyGEE references and the distilled GEEer growth-diary
  index. Treat results as pointers into local references, not as authority over
  official Earth Engine docs.
- Use `scripts/search_gee_dataset.py "<task>" --workflow` before selecting
  datasets when compatibility with the curated workflow cards is useful.
- Use `scripts/dataset_catalog_engine.py search "<id, theme, or task>"` as the
  primary broad-catalog retrieval path. Use its `recommend`, `compare`,
  `verify`, and `stats` subcommands for task-role bundles, product trade-offs,
  final asset gates, and source coverage. Empty results must trigger
  clarification, not a generic Sentinel/Landsat fallback. Verify official
  entries in the Google catalog and community entries on their source page and
  sample code before analysis.
