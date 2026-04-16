"""ThoughtMap configuration — paths, thresholds, model settings.

All paths support environment variable overrides for Docker deployment.
"""

import os
from pathlib import Path

# Load .env from the thoughtmap project directory
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

# ─── Repo paths ───
# thoughtmap lives at: <repo>/Second Brain/Projects/thoughtmap/
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_DIR = Path(os.environ.get(
    "THOUGHTMAP_OUTPUT_DIR",
    str(REPO_ROOT / "Second Brain" / "Operations" / "thoughtmap-out"),
))
DATA_DIR = Path(os.environ.get(
    "THOUGHTMAP_DATA_DIR",
    str(Path(__file__).resolve().parent / "data"),
))
CHROMA_DIR = DATA_DIR / "chroma"
CACHE_DIR = DATA_DIR / "cache"

# ─── Data source paths (env-overridable for Docker) ───
OBSIDIAN_VAULT = Path(os.environ.get(
    "THOUGHTMAP_OBSIDIAN_VAULT",
    r"C:\Users\mateu\Documents\Obsidian Vault",
))
OBSIDIAN_DAILY = Path(os.environ.get(
    "THOUGHTMAP_OBSIDIAN_DAILY",
    str(OBSIDIAN_VAULT / "10. Operations" / "Daily"),
))
JOINTHUBS_DAILY = Path(os.environ.get(
    "THOUGHTMAP_JOINTHUBS_DAILY",
    str(REPO_ROOT / "Second Brain" / "Personal" / "daily"),
))
WISPR_DB = Path(os.environ.get(
    "THOUGHTMAP_WISPR_DB",
    r"C:\Users\mateu\AppData\Roaming\Wispr Flow\flow.sqlite",
))
SECOND_BRAIN_DIR = Path(os.environ.get(
    "THOUGHTMAP_SECOND_BRAIN_DIR",
    str(REPO_ROOT / "Second Brain"),
))

# ─── Date filter ───
MIN_YEAR = int(os.environ.get("THOUGHTMAP_MIN_YEAR", "2025"))

# ─── Second Brain extraction ───
# Folder names to skip when walking Second Brain (generated output, data, etc.)
SECOND_BRAIN_EXCLUDE_DIRS = {
    "graphify-out", "graphify-out-strategic", "graphify-strategic",
    "thoughtmap-out", "thoughtmap", "tmp", "data",
    ".obsidian", "automation-logs", "assets", "attachments",
    "budget-calculator", "demo", "cache",
    "node_modules", ".git", "dist", "build",
    ".venv", "venv", "env", "__pycache__", "site-packages",
    ".mypy_cache", ".pytest_cache",
}

# File name patterns to skip (case-insensitive stem matching)
SECOND_BRAIN_EXCLUDE_FILES = {
    "license", "licence", "contributing", "changelog",
    "code_of_conduct", "security", "authors",
}

# ─── Chunking ───
CHUNK_TARGET_TOKENS = 200       # Target chunk size in tokens
CHUNK_MIN_TOKENS = 40           # Minimum chunk size (smaller → discard)
CHUNK_OVERLAP_SENTENCES = 2     # Overlap between chunks in sentences
MERGE_SIMILARITY_THRESHOLD = 0.85  # Cosine similarity above which chunks merge

# ─── Embedding ───
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "ollama")  # "ollama" | "openai" | "google"

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:8b")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_EMBEDDING_MODEL = os.environ.get("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")

# Legacy alias — resolved from provider
EMBEDDING_MODEL = {
    "ollama": OLLAMA_EMBEDDING_MODEL,
    "openai": OPENAI_EMBEDDING_MODEL,
    "google": GOOGLE_EMBEDDING_MODEL,
}.get(EMBEDDING_PROVIDER, OLLAMA_EMBEDDING_MODEL)

EMBEDDING_DIMENSIONS = int(os.environ.get("EMBEDDING_DIMENSIONS", "1024"))
VIZ_DIMENSIONS = 256            # Matryoshka truncation for visualization

# ─── Clustering ───
UMAP_N_NEIGHBORS = 15           # Higher = more global structure → fewer, broader clusters
UMAP_MIN_DIST = 0.05            # Tighter packing → cleaner cluster boundaries
UMAP_N_COMPONENTS = 2           # For visualization
UMAP_CLUSTER_COMPONENTS = 15    # Intermediate dims for HDBSCAN (lower = smoother, fewer clusters)
HDBSCAN_MIN_CLUSTER_SIZE = 30   # Smallest allowed cluster (higher = fewer, larger clusters)
HDBSCAN_MIN_SAMPLES = 10        # Density sensitivity (higher = stricter density requirement)
CLUSTER_MERGE_THRESHOLD = 0.94  # Cosine similarity above which cluster centroids get merged

# ─── Wispr Flow matching ───
WISPR_MATCH_THRESHOLD = 0.15    # Max normalized Levenshtein distance for match

# ─── Wispr Flow app → category mapping ───
APP_CATEGORIES = {
    "Code": "coding",
    "Terminal": "coding",
    "WindowsTerminal": "coding",
    "chrome": "browsing",
    "Chrome": "browsing",
    "Edge": "browsing",
    "Firefox": "browsing",
    "Obsidian": "note-taking",
    "Discord": "communication",
    "Slack": "communication",
    "WhatsApp": "communication",
    "Teams": "communication",
}
APP_DEFAULT_CATEGORY = "general"

# ─── Condensation ───
CONDENSE_MODEL = os.environ.get("THOUGHTMAP_CONDENSE_MODEL", "gemma4:e2b")
CONDENSE_EDGE_THRESHOLD = float(os.environ.get(
    "THOUGHTMAP_CONDENSE_EDGE_THRESHOLD", "0.70",
))  # cosine similarity — clusters above this get an edge in condensed graph
SUPER_CLUSTER_MIN_SIZE = int(os.environ.get(
    "THOUGHTMAP_SUPER_CLUSTER_MIN_SIZE", "3",
))  # minimum clusters per super-cluster
TOPICS_DIR = OUTPUT_DIR / "topics"

# ─── Named Entity Recognition ───
NER_ENABLED = os.environ.get("THOUGHTMAP_NER_ENABLED", "true").lower() == "true"
NER_SPACY_MODEL = os.environ.get("THOUGHTMAP_NER_SPACY_MODEL", "xx_ent_wiki_sm")
NER_MIN_MENTIONS = int(os.environ.get("THOUGHTMAP_NER_MIN_MENTIONS", "2"))
NER_MAX_ENTITIES = int(os.environ.get("THOUGHTMAP_NER_MAX_ENTITIES", "250"))
NER_MAX_OLLAMA_SUMMARIES = int(os.environ.get("THOUGHTMAP_NER_MAX_OLLAMA_SUMMARIES", "50"))
NER_ENTITY_TYPES = {"PERSON", "PER", "ORG", "GPE", "PRODUCT", "WORK_OF_ART", "LOC", "FAC"}
NER_CACHE_FILE = DATA_DIR / "entities_cache.json"
ENTITIES_DIR = OUTPUT_DIR / "entities"

# ─── ChromaDB ───
CHROMA_COLLECTION = "thoughtmap"

# ─── Server ───
SERVER_PORT = int(os.environ.get("THOUGHTMAP_PORT", "8585"))
