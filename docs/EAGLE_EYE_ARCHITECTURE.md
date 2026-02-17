# Eagle Eye Architecture

## Goal

Produce a ranked, explainable view of active market narratives using multiple feeds.

## Pipeline

1. Source adapters fetch raw signals.
2. Events are normalized into `SourceEvent`.
3. Theme mapper tags each event with one or more narratives.
4. Scoring layer computes:
   - `impact_score`
   - `relevance_score`
   - `event_score = 0.6 * impact + 0.4 * relevance`
5. Aggregator groups events by theme and emits ranked `Narrative` objects.

## Source Adapters

- `PolymarketAdapter`: tries multiple base URLs/paths to tolerate endpoint migrations.
- `PolygonAdapter`: reads stock snapshot momentum data.
- `SquawkAdapter`: reads headline events from URL or local JSON.

## Outputs

- MCP tools for `snapshot`, `theme breakdown`, and `source health`.
- FastAPI routes:
  - `/api/eagle-eye`
  - `/api/themes/{theme}`
  - `/health`

