"""Lightweight FastAPI dashboard for Eagle Eye narratives."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from .config import load_config
from .eagle_eye import EagleEyeService

config = load_config()
service = EagleEyeService(config)

app = FastAPI(title="Market Eagle Eye Dashboard", version="0.3.0")


@app.get("/health")
async def health() -> dict:
    source_health = await service.get_source_health()
    return {"status": "ok", "sources": source_health}


@app.get("/api/eagle-eye")
async def eagle_eye_snapshot(
    window_minutes: int | None = Query(default=None),
    top_narratives: int | None = Query(default=None),
    source_limit: int | None = Query(default=None),
) -> dict:
    snapshot = await service.get_snapshot(
        window_minutes=window_minutes,
        top_narratives=top_narratives,
        source_limit=source_limit,
    )
    return snapshot.model_dump(mode="json")


@app.get("/api/themes/{theme}")
async def theme_breakdown(
    theme: str,
    window_minutes: int | None = Query(default=None),
    event_limit: int = Query(default=20),
    source_limit: int | None = Query(default=None),
) -> dict:
    return await service.get_theme_breakdown(
        theme=theme,
        window_minutes=window_minutes,
        event_limit=event_limit,
        source_limit=source_limit,
    )


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Market Eagle Eye</title>
  <style>
    :root { --bg:#0a1729; --panel:#132846; --text:#edf3ff; --muted:#8fb0d7; --good:#2ecc71; --bad:#e74c3c; }
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: radial-gradient(circle at top,#16375f,#081224); color: var(--text); margin: 0; padding: 24px; }
    h1 { margin: 0 0 8px; }
    p { color: var(--muted); margin: 0 0 24px; }
    .grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
    .card { background: var(--panel); border: 1px solid #1f3e64; border-radius: 12px; padding: 14px; }
    .score { font-size: 24px; font-weight: 700; }
    .meta { color: var(--muted); font-size: 13px; margin-top: 6px; }
    .bullish { color: var(--good); }
    .bearish { color: var(--bad); }
    .mixed { color: #f1c40f; }
  </style>
</head>
<body>
  <h1>Market Eagle Eye</h1>
  <p>Current market narratives ranked by impact and relevance. Auto-refresh every 30s.</p>
  <div id="cards" class="grid"></div>
  <script>
    async function load() {
      const res = await fetch('/api/eagle-eye');
      const data = await res.json();
      const cards = document.getElementById('cards');
      cards.innerHTML = '';
      for (const n of data.narratives || []) {
        const div = document.createElement('div');
        div.className = 'card';
        div.innerHTML = `
          <div class="score">${(n.narrative_score * 100).toFixed(1)}</div>
          <div><strong>${n.theme}</strong></div>
          <div class="meta">Trend: <span class="${n.trend}">${n.trend}</span> | Events: ${n.event_count}</div>
          <div class="meta">Sources: ${n.sources.join(', ') || 'n/a'}</div>
          <div class="meta">Assets: ${n.top_assets.join(', ') || 'n/a'}</div>
          <div class="meta">Catalyst: ${(n.catalysts && n.catalysts[0]) || 'n/a'}</div>
        `;
        cards.appendChild(div);
      }
    }
    load();
    setInterval(load, 30000);
  </script>
</body>
</html>"""


def run() -> None:
    """CLI entrypoint for local dashboard."""
    uvicorn.run(
        "polymarket_mcp.dashboard:app",
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        reload=False,
    )

