"""ThoughtMap web server — runs pipeline then serves the interactive visualization.

Start with:  python -m thoughtmap server
Or via Docker Compose (preferred).
"""

from __future__ import annotations

import json
import os
import socketserver
import threading
import time
import traceback
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

import thoughtmap.config as config

# ─── Global pipeline state (read by the HTTP handler) ───

_state = {
    "phase": "starting",       # starting | waiting | pulling | running | done | error
    "message": "Initializing...",
    "step": "",                 # current pipeline step text
    "error": None,
}
_state_lock = threading.Lock()


def _set_state(phase: str, message: str, step: str = ""):
    with _state_lock:
        _state["phase"] = phase
        _state["message"] = message
        _state["step"] = step


def _set_error(message: str):
    with _state_lock:
        _state["phase"] = "error"
        _state["message"] = message
        _state["error"] = message


# ─── Loading page served while the pipeline runs ───

LOADING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ThoughtMap — Loading</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0d1117; color: #c9d1d9;
    display: flex; align-items: center; justify-content: center;
    height: 100vh;
  }
  .card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 48px 56px; text-align: center; max-width: 480px;
  }
  h1 { font-size: 28px; margin-bottom: 8px; }
  .subtitle { color: #8b949e; font-size: 14px; margin-bottom: 32px; }
  .spinner {
    width: 48px; height: 48px; border: 3px solid #30363d;
    border-top-color: #58a6ff; border-radius: 50%;
    animation: spin 1s linear infinite; margin: 0 auto 24px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  #status { font-size: 15px; color: #c9d1d9; margin-bottom: 8px; min-height: 22px; }
  #step { font-size: 13px; color: #8b949e; min-height: 18px; }
  .error { color: #f85149; }
  .done { color: #3fb950; }
</style>
</head>
<body>
<div class="card">
  <h1>ThoughtMap</h1>
  <p class="subtitle">Personal Thought Vector Visualization</p>
  <div class="spinner" id="spinner"></div>
  <div id="status">Initializing...</div>
  <div id="step"></div>
</div>
<script>
async function poll() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('status').textContent = d.message;
    document.getElementById('step').textContent = d.step || '';

    if (d.phase === 'done') {
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('status').className = 'done';
      document.getElementById('status').textContent = 'Ready! Redirecting...';
      setTimeout(() => { window.location.href = '/'; }, 800);
      return;
    }
    if (d.phase === 'error') {
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('status').className = 'error';
      return;
    }
  } catch (e) { /* server may not be ready yet */ }
  setTimeout(poll, 1500);
}
poll();
</script>
</body>
</html>
"""


# ─── HTTP Request Handler ───

class ThoughtMapHandler(SimpleHTTPRequestHandler):
    """Serves loading page during pipeline, then the visualization."""

    def __init__(self, *args, output_dir: str, **kwargs):
        self._output_dir = output_dir
        super().__init__(*args, directory=output_dir, **kwargs)

    def do_GET(self):
        # Status API endpoint
        if self.path == "/api/status":
            with _state_lock:
                payload = json.dumps(_state)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(payload.encode())
            return

        # Re-run trigger
        if self.path == "/api/rerun":
            t = threading.Thread(target=_run_pipeline, daemon=True)
            t.start()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        # Search API — semantic search over chunks
        if self.path.startswith("/api/search"):
            self._handle_search()
            return

        # Clusters list API
        if self.path.startswith("/api/clusters") and not self.path.startswith("/api/clusters/"):
            self._handle_clusters()
            return

        # Single cluster API
        if self.path.startswith("/api/clusters/"):
            self._handle_cluster_detail()
            return

        # Cluster thoughts API — all chunks for a cluster
        if self.path.startswith("/api/cluster-thoughts/"):
            self._handle_cluster_thoughts()
            return

        # Entities list API
        if self.path == "/api/entities" or self.path.startswith("/api/entities?"):
            self._handle_entities()
            return

        # Single entity detail API
        if self.path.startswith("/api/entities/"):
            self._handle_entity_detail()
            return

        # Directories list API (for note creation)
        if self.path == "/api/directories":
            self._handle_directories()
            return

        # Root path
        if self.path in ("/", "/index.html"):
            with _state_lock:
                phase = _state["phase"]

            if phase == "done":
                viz = Path(self._output_dir) / "thoughtmap-condensed.html"
                if viz.exists():
                    self.path = "/thoughtmap-condensed.html"
                    return super().do_GET()
                # Fallback to original if condensed not available
                viz = Path(self._output_dir) / "thoughtmap.html"
                if viz.exists():
                    self.path = "/thoughtmap.html"
                    return super().do_GET()

            # Otherwise serve loading page
            content = LOADING_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/notes":
            self._handle_create_note()
            return
        if self.path == "/api/query":
            self._handle_query()
            return
        self.send_error(404)

    def _json_response(self, data: dict | list, status_code: int = 200):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)

    def _handle_search(self):
        """GET /api/search?q=...&n=10 — semantic search over ChromaDB."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0]
        n_results = min(int(params.get("n", ["10"])[0]), 50)

        if not query:
            self._json_response({"error": "Missing ?q= parameter"}, 400)
            return

        try:
            from thoughtmap.core.embed import get_chroma_client, embed_text
            client = get_chroma_client()
            collection = client.get_collection(name=config.CHROMA_COLLECTION)
        except Exception as e:
            self._json_response({"error": f"ChromaDB error: {e}"}, 500)
            return

        try:
            query_embedding = embed_text(query)
        except Exception as e:
            self._json_response({"error": f"Embedding failed: {e}"}, 500)
            return

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        items = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i] or {}
            items.append({
                "text": results["documents"][0][i],
                "source_file": meta.get("source_file", ""),
                "source": meta.get("source", ""),
                "timestamp": meta.get("timestamp", ""),
                "section": meta.get("section", ""),
                "project_tag": meta.get("project_tag", ""),
                "category": meta.get("category", ""),
                "distance": round(results["distances"][0][i], 4),
            })

        self._json_response({"results": items, "query": query, "count": len(items)})

    def _handle_clusters(self):
        """GET /api/clusters?domain=... — list all clusters."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        domain = params.get("domain", [""])[0].lower()

        clusters_path = Path(self._output_dir) / "clusters.json"
        if not clusters_path.exists():
            self._json_response({"error": "No clusters.json found"}, 404)
            return

        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        items = []
        for c in clusters:
            label = c.get("label", "")
            if domain and domain not in label.lower():
                continue
            items.append({
                "cluster_id": c["cluster_id"],
                "label": label,
                "size": c["size"],
            })

        items.sort(key=lambda x: x["size"], reverse=True)
        self._json_response({"clusters": items, "count": len(items)})

    def _handle_cluster_detail(self):
        """GET /api/clusters/<id> — get cluster detail."""
        try:
            cluster_id = int(self.path.split("/api/clusters/")[1].split("?")[0])
        except (ValueError, IndexError):
            self._json_response({"error": "Invalid cluster ID"}, 400)
            return

        clusters_path = Path(self._output_dir) / "clusters.json"
        if not clusters_path.exists():
            self._json_response({"error": "No clusters.json found"}, 404)
            return

        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        for c in clusters:
            if c["cluster_id"] == cluster_id:
                self._json_response({
                    "cluster_id": c["cluster_id"],
                    "label": c.get("label", ""),
                    "size": c["size"],
                    "representative_texts": c.get("representative_texts", []),
                })
                return

        self._json_response({"error": f"Cluster {cluster_id} not found"}, 404)

    def _handle_cluster_thoughts(self):
        """GET /api/cluster-thoughts/<id> — all chunks belonging to a cluster."""
        try:
            cluster_id = int(self.path.split("/api/cluster-thoughts/")[1].split("?")[0])
        except (ValueError, IndexError):
            self._json_response({"error": "Invalid cluster ID"}, 400)
            return

        clusters_path = Path(self._output_dir) / "clusters.json"
        chunks_path = Path(self._output_dir) / "chunks.json"
        if not clusters_path.exists() or not chunks_path.exists():
            self._json_response({"error": "Data files not found"}, 404)
            return

        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        cluster = None
        for c in clusters:
            if c["cluster_id"] == cluster_id:
                cluster = c
                break

        if cluster is None:
            self._json_response({"error": f"Cluster {cluster_id} not found"}, 404)
            return

        member_indices = cluster.get("member_indices", [])
        thoughts = []
        for idx in member_indices:
            if 0 <= idx < len(chunks):
                ch = chunks[idx]
                thoughts.append({
                    "idx": idx,
                    "text": ch.get("text", "")[:500],
                    "timestamp": ch.get("timestamp", ""),
                    "source": ch.get("source", ""),
                    "source_file": ch.get("source_file", ""),
                    "section": ch.get("section", ""),
                    "repeat_count": ch.get("repeat_count", 1),
                })

        self._json_response({
            "cluster_id": cluster_id,
            "label": cluster.get("label", ""),
            "size": cluster.get("size", 0),
            "thoughts": thoughts,
            "count": len(thoughts),
        })

    def _load_entities(self):
        """Load entities.json from output directory."""
        entities_path = Path(self._output_dir) / "entities.json"
        if not entities_path.exists():
            return None
        with open(entities_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _handle_entities(self):
        """GET /api/entities — list all entities."""
        entities = self._load_entities()
        if entities is None:
            self._json_response({"error": "No entities.json found"}, 404)
            return

        items = []
        for e in entities:
            items.append({
                "name": e.get("name", ""),
                "type": e.get("type", ""),
                "aliases": e.get("aliases", []),
                "mention_count": e.get("mention_count", 0),
                "cluster_ids": e.get("cluster_ids", []),
                "summary": e.get("summary", ""),
                "boundaries": e.get("boundaries", ""),
            })
        items.sort(key=lambda x: x["mention_count"], reverse=True)
        self._json_response({"entities": items, "count": len(items)})

    def _handle_entity_detail(self):
        """GET /api/entities/<name> — get entity detail by URL-encoded name."""
        try:
            from urllib.parse import unquote
            entity_name = unquote(self.path.split("/api/entities/")[1].split("?")[0])
        except (IndexError,):
            self._json_response({"error": "Invalid entity name"}, 400)
            return

        entities = self._load_entities()
        if entities is None:
            self._json_response({"error": "No entities.json found"}, 404)
            return

        entity_name_lower = entity_name.lower()
        for e in entities:
            if e.get("name", "").lower() == entity_name_lower or \
               e.get("normalized", "").lower() == entity_name_lower:
                self._json_response(e)
                return

        self._json_response({"error": f"Entity '{entity_name}' not found"}, 404)

    def _handle_directories(self):
        """GET /api/directories — list available target directories for notes."""
        sb_dir = Path(os.environ.get(
            "THOUGHTMAP_SECOND_BRAIN_DIR", str(config.SECOND_BRAIN_DIR)
        ))
        dirs = []
        for area in ("Projects", "Personal"):
            area_dir = sb_dir / area
            if area_dir.exists():
                for d in sorted(area_dir.iterdir()):
                    if d.is_dir() and not d.name.startswith('.') \
                       and d.name not in config.SECOND_BRAIN_EXCLUDE_DIRS:
                        dirs.append(f"{area}/{d.name}")
        self._json_response({"directories": dirs})

    def _handle_create_note(self):
        """POST /api/notes — create an Obsidian note in the Second Brain."""
        import re
        from datetime import date

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 100_000:
            self._json_response({"error": "Payload too large"}, 413)
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, ValueError):
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        title = str(body.get("title", "")).strip()
        content = str(body.get("content", "")).strip()
        directory = str(body.get("directory", "")).strip()

        if not title or not content or not directory:
            self._json_response(
                {"error": "title, content and directory are required"}, 400,
            )
            return

        # Sanitize filename — strip characters illegal on Windows / in URLs
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
        if not safe_title:
            self._json_response({"error": "Invalid title after sanitization"}, 400)
            return

        sb_dir = Path(os.environ.get(
            "THOUGHTMAP_SECOND_BRAIN_DIR", str(config.SECOND_BRAIN_DIR)
        )).resolve()
        target_dir = (sb_dir / directory).resolve()

        # Path-traversal guard
        if not str(target_dir).startswith(str(sb_dir)):
            self._json_response({"error": "Invalid directory path"}, 400)
            return
        if not target_dir.is_dir():
            self._json_response(
                {"error": f"Directory not found: {directory}"}, 404,
            )
            return

        filepath = target_dir / f"{safe_title}.md"
        counter = 1
        while filepath.exists():
            filepath = target_dir / f"{safe_title} ({counter}).md"
            counter += 1

        today = date.today().isoformat()
        md = f"---\ncreated: {today}\nsource: thoughtmap\n---\n\n# {title}\n\n{content}\n"
        filepath.write_text(md, encoding="utf-8")

        rel_path = str(filepath.relative_to(sb_dir)).replace("\\", "/")
        self._json_response({"ok": True, "path": rel_path, "filename": filepath.name})

    def _handle_query(self):
        """POST /api/query — query thoughts in a cluster or super-cluster.

        Body JSON:
          mode: "latest" | "context"
          scope: "cluster" | "super"
          scope_id: int (cluster_id or super_id)
          query: str (required when mode="context")
          n: int (max results, default 10)
        """
        import numpy as np

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 50_000:
            self._json_response({"error": "Payload too large"}, 413)
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, ValueError):
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        mode = body.get("mode", "latest")
        scope = body.get("scope", "cluster")
        scope_id = body.get("scope_id")
        query_text = str(body.get("query", "")).strip()
        n = min(int(body.get("n", 10)), 50)

        if scope_id is None:
            self._json_response({"error": "scope_id is required"}, 400)
            return
        if mode == "context" and not query_text:
            self._json_response({"error": "query is required for mode=context"}, 400)
            return

        # Load data
        chunks_path = Path(self._output_dir) / "chunks.json"
        clusters_path = Path(self._output_dir) / "clusters.json"
        condensed_path = Path(self._output_dir) / "condensed.json"
        if not chunks_path.exists() or not clusters_path.exists():
            self._json_response({"error": "Data files not found"}, 404)
            return

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        # Resolve member indices for the requested scope
        if scope == "super":
            if not condensed_path.exists():
                self._json_response({"error": "condensed.json not found"}, 404)
                return
            with open(condensed_path, "r", encoding="utf-8") as f:
                condensed = json.load(f)
            sc = next(
                (s for s in condensed.get("super_clusters", [])
                 if s["super_id"] == scope_id),
                None,
            )
            if sc is None:
                self._json_response({"error": f"Super-cluster {scope_id} not found"}, 404)
                return
            member_indices = set()
            for cid in sc["member_ids"]:
                cl = next((c for c in clusters if c["cluster_id"] == cid), None)
                if cl:
                    member_indices.update(cl.get("member_indices", []))
            scope_label = sc["label"]
        else:
            cl = next((c for c in clusters if c["cluster_id"] == scope_id), None)
            if cl is None:
                self._json_response({"error": f"Cluster {scope_id} not found"}, 404)
                return
            member_indices = set(cl.get("member_indices", []))
            scope_label = cl.get("label", "")

        # Gather the subset of chunks
        subset = []
        for idx in member_indices:
            if 0 <= idx < len(chunks):
                ch = chunks[idx]
                subset.append({
                    "idx": idx,
                    "text": ch.get("text", ""),
                    "timestamp": ch.get("timestamp", ""),
                    "source": ch.get("source", ""),
                    "source_file": ch.get("source_file", ""),
                    "section": ch.get("section", ""),
                    "repeat_count": ch.get("repeat_count", 1),
                })

        if mode == "latest":
            # Sort by timestamp descending, return top N
            subset.sort(key=lambda x: x["timestamp"] or "", reverse=True)
            results = subset[:n]
            self._json_response({
                "mode": "latest",
                "scope": scope,
                "scope_label": scope_label,
                "results": results,
                "count": len(results),
                "total": len(subset),
            })
        else:
            # mode == "context": vectorize query, similarity search on subset
            try:
                from thoughtmap.core.embed import embed_text, load_all_embeddings
                query_embedding = np.array(embed_text(query_text))
            except Exception as e:
                self._json_response({"error": f"Embedding failed: {e}"}, 500)
                return

            # Load all embeddings and pick the subset
            try:
                all_items, all_embeddings = load_all_embeddings()
            except Exception as e:
                self._json_response({"error": f"Failed to load embeddings: {e}"}, 500)
                return

            # Build index mapping: chunk idx → embedding idx
            # chunks.json is the deduplicated list; all_embeddings is the raw ChromaDB load
            # We need to match by text since dedup may have reordered
            subset_embeddings = []
            subset_matched = []
            text_to_emb = {}
            for i, item in enumerate(all_items):
                key = (item.get("text", "") or "").strip()
                if key not in text_to_emb:
                    text_to_emb[key] = all_embeddings[i]

            for s in subset:
                key = (s["text"] or "").strip()
                emb = text_to_emb.get(key)
                if emb is not None:
                    subset_embeddings.append(emb)
                    subset_matched.append(s)

            if not subset_embeddings:
                self._json_response({
                    "mode": "context",
                    "scope": scope,
                    "scope_label": scope_label,
                    "query": query_text,
                    "results": [],
                    "count": 0,
                    "total": len(subset),
                })
                return

            # Cosine similarity
            emb_matrix = np.array(subset_embeddings)
            norms = np.linalg.norm(emb_matrix, axis=1)
            norms[norms == 0] = 1
            normed = emb_matrix / norms[:, np.newaxis]
            q_norm = query_embedding / (np.linalg.norm(query_embedding) or 1)
            similarities = normed @ q_norm

            top_indices = np.argsort(similarities)[::-1][:n]
            results = []
            for i in top_indices:
                item = subset_matched[i].copy()
                item["similarity"] = round(float(similarities[i]), 4)
                item["text"] = item["text"][:500]
                results.append(item)

            self._json_response({
                "mode": "context",
                "scope": scope,
                "scope_label": scope_label,
                "query": query_text,
                "results": results,
                "count": len(results),
                "total": len(subset),
            })

    def log_message(self, format, *args):
        # Suppress noisy request logs; status polls are frequent
        if "/api/status" in str(args[0]):
            return
        super().log_message(format, *args)


# ─── Ollama readiness check ───

def _wait_for_ollama():
    """Wait for Ollama to be reachable and ensure the model is available."""
    _set_state("waiting", "Waiting for Ollama...", "Connecting to embedding server")

    for attempt in range(120):  # up to ~4 minutes
        try:
            resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if resp.ok:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(2)
    else:
        raise RuntimeError(
            f"Ollama not reachable at {config.OLLAMA_BASE_URL} after 4 minutes"
        )

    # Check if model is already pulled
    resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=10)
    resp.raise_for_status()
    model_names = [m.get("name", "") for m in resp.json().get("models", [])]
    if config.EMBEDDING_MODEL not in model_names:
        _set_state("pulling", f"Pulling {config.EMBEDDING_MODEL}...",
                    "First run — downloading embedding model (~274 MB)")
        pull_resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/pull",
            json={"name": config.EMBEDDING_MODEL, "stream": False},
            timeout=600,
        )
        pull_resp.raise_for_status()

    _set_state("running", "Ollama ready", "Model loaded")


# ─── Pipeline runner (background thread) ───

def _run_pipeline():
    """Orchestrate: wait for Ollama → run pipeline → mark done."""
    try:
        _wait_for_ollama()

        # If we're already serving previous results, stay in "done" until
        # the pipeline actually needs to do heavy work (embedding).
        # The status callback from run.py will update step info regardless.
        with _state_lock:
            already_serving = _state["phase"] == "done"

        if not already_serving:
            _set_state("running", "Running pipeline...", "Checking for new data...")

        def on_status(msg: str):
            with _state_lock:
                _state["step"] = msg
                # If embedding starts (step 3), switch to "running" even if
                # we were serving previous results — user should see progress
                if msg.startswith("[3/") and _state["phase"] == "done":
                    _state["phase"] = "running"
                    _state["message"] = "Updating with new data..."

        from thoughtmap.run import main
        result = main(on_status=on_status)

        if result is None:
            _set_state("done", "Pipeline finished (limited data)", "")
        else:
            _set_state("done", "Pipeline complete", "")

    except Exception as e:
        traceback.print_exc()
        _set_error(f"Pipeline failed: {e}")


# ─── Entry point ───

def serve():
    """Start the ThoughtMap server: run pipeline in background, serve results."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    port = config.SERVER_PORT
    handler = partial(ThoughtMapHandler, output_dir=str(config.OUTPUT_DIR))

    has_previous = (config.OUTPUT_DIR / "thoughtmap-condensed.html").exists() or (config.OUTPUT_DIR / "thoughtmap.html").exists()
    if has_previous:
        # Serve previous results immediately — don't show loading screen
        _set_state("done", "Serving previous results", "")
        print("Previous output found — serving immediately while checking for new data...")

    # Start pipeline in background (will skip embedding if no new data)
    pipeline_thread = threading.Thread(target=_run_pipeline, daemon=True)
    pipeline_thread.start()

    # Start HTTP server (blocks)
    with socketserver.ThreadingTCPServer(("0.0.0.0", port), handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"\n  ThoughtMap server: http://localhost:{port}")
        print(f"  Output directory:  {config.OUTPUT_DIR}")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


def serve_static():
    """Serve the generated ThoughtMap output without re-running the pipeline."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    viz = config.OUTPUT_DIR / "thoughtmap-condensed.html"
    if not viz.exists():
        viz = config.OUTPUT_DIR / "thoughtmap.html"
    if not viz.exists():
        raise RuntimeError(
            f"Static UI not found in {config.OUTPUT_DIR}. Run the pipeline once first."
        )

    port = config.SERVER_PORT
    handler = partial(SimpleHTTPRequestHandler, directory=str(config.OUTPUT_DIR))

    with socketserver.ThreadingTCPServer(("0.0.0.0", port), handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"\n  ThoughtMap static UI: http://localhost:{port}/{viz.name}")
        print(f"  Serving from:        {config.OUTPUT_DIR}")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    serve()
