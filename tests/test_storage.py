"""Tests for the storage layer — all offline, in-memory SQLite."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models import CitationRecord, ResearchResult, SourceResult
from src.services.cache import (
    InMemoryCache,
    FilesystemCache,
    canonicalize_query,
    _cache_key,
)


# ---- cache key helpers ---------------------------------------------------

def test_canonicalize_query_lowercases():
    assert canonicalize_query("PHOTOSYNTHESIS?") == "photosynthesis"


def test_canonicalize_query_collapses_whitespace():
    assert canonicalize_query("  what  is  AI  ") == "what is ai"


def test_canonicalize_strips_trailing_punctuation():
    q = canonicalize_query("photosynthesis!")
    assert not q.endswith("!")


def test_cache_key_stable():
    k1 = _cache_key("wiki", "photosynthesis")
    k2 = _cache_key("wiki", "photosynthesis")
    assert k1 == k2


def test_cache_key_different_sources():
    assert _cache_key("wiki", "photosynthesis") != _cache_key("arxiv", "photosynthesis")


# ---- InMemoryCache -------------------------------------------------------

def test_in_memory_cache_miss():
    cache = InMemoryCache()
    assert cache.get("wiki", "photosynthesis") is None


def test_in_memory_cache_set_and_get():
    cache = InMemoryCache(ttl_seconds=3600)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "wikipedia"}]
    cache.set("wiki", "photosynthesis", data)
    result = cache.get("wiki", "photosynthesis")
    assert result == data


def test_in_memory_cache_ttl_expiry():
    cache = InMemoryCache(ttl_seconds=1)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "wikipedia"}]
    cache.set("wiki", "old query", data)
    import time
    time.sleep(1.1)
    assert cache.get("wiki", "old query") is None


def test_in_memory_cache_invalidate():
    cache = InMemoryCache(ttl_seconds=3600)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "wikipedia"}]
    cache.set("wiki", "photosynthesis", data)
    cache.invalidate("wiki", "photosynthesis")
    assert cache.get("wiki", "photosynthesis") is None


def test_in_memory_cache_clear():
    cache = InMemoryCache(ttl_seconds=3600)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "wikipedia"}]
    cache.set("wiki", "q1", data)
    cache.set("wiki", "q2", data)
    cache.clear()
    assert cache.size == 0


def test_in_memory_cache_zero_ttl_never_expires():
    """TTL=0 means infinite (never expire)."""
    cache = InMemoryCache(ttl_seconds=0)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "wikipedia"}]
    cache.set("wiki", "test", data)
    import time
    time.sleep(0.1)
    assert cache.get("wiki", "test") is not None


# ---- FilesystemCache -----------------------------------------------------

def test_filesystem_cache_roundtrip(tmp_path):
    cache = FilesystemCache(cache_dir=str(tmp_path), ttl_seconds=3600)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "arxiv"}]
    cache.set("arxiv", "photosynthesis", data)
    result = cache.get("arxiv", "photosynthesis")
    assert result == data


def test_filesystem_cache_miss(tmp_path):
    cache = FilesystemCache(cache_dir=str(tmp_path), ttl_seconds=3600)
    assert cache.get("arxiv", "nonexistent") is None


def test_filesystem_cache_invalidate(tmp_path):
    cache = FilesystemCache(cache_dir=str(tmp_path), ttl_seconds=3600)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "web"}]
    cache.set("web", "photosynthesis", data)
    cache.invalidate("web", "photosynthesis")
    assert cache.get("web", "photosynthesis") is None


def test_filesystem_cache_clear(tmp_path):
    cache = FilesystemCache(cache_dir=str(tmp_path), ttl_seconds=3600)
    data = [{"title": "T", "url": "U", "snippet": "S", "origin": "web"}]
    cache.set("web", "q1", data)
    cache.set("web", "q2", data)
    cache.clear()
    json_files = list(tmp_path.glob("*.json"))
    assert json_files == []


# ---- ResearchRepository (uses temp SQLite) --------------------------------

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Point the repository at a temporary database file."""
    db_file = str(tmp_path / "test.db")
    monkeypatch.setattr("src.storage.repository._DB_PATH", db_file)
    return db_file


def _make_result(question: str = "What is photosynthesis?") -> ResearchResult:
    return ResearchResult(
        question=question,
        answer="Photosynthesis is the process [1].",
        citations=[CitationRecord(index=1, title="T", url="U", origin="wikipedia")],
        sources_used=[SourceResult(title="T", url="U", snippet="S", origin="wikipedia")],
        sources_failed=[],
        elapsed_seconds=1.23,
    )


@pytest.mark.asyncio
async def test_save_and_retrieve_session(tmp_db):
    from src.storage.repository import ResearchRepository
    repo = ResearchRepository()
    result = _make_result()
    sid = await repo.save_session(result)
    assert isinstance(sid, int)
    session = await repo.get_session(sid)
    assert session is not None
    assert session["question"] == result.question


@pytest.mark.asyncio
async def test_list_sessions_returns_recent(tmp_db):
    from src.storage.repository import ResearchRepository
    repo = ResearchRepository()
    for q in ["Q1", "Q2", "Q3"]:
        await repo.save_session(_make_result(q))
    sessions = await repo.list_sessions(limit=2)
    assert len(sessions) == 2
    assert sessions[0]["question"] == "Q3"


@pytest.mark.asyncio
async def test_get_session_missing_returns_none(tmp_db):
    from src.storage.repository import ResearchRepository
    repo = ResearchRepository()
    result = await repo.get_session(9999)
    assert result is None


# ---- Backend factory / dual-backend tests --------------------------------

def test_get_repository_returns_sqlite_for_default_url(monkeypatch):
    """Factory returns SQLiteRepository when DATABASE_URL is sqlite."""
    from src.config import settings
    from src.storage.repository import get_repository, SQLiteRepository
    monkeypatch.setattr(settings, "database_url", "sqlite+aiosqlite:///./test.db")
    # Re-import after patch isn't needed — get_repository reads settings live.
    repo = get_repository()
    assert isinstance(repo, SQLiteRepository)


def test_get_repository_returns_postgres_for_pg_url(monkeypatch):
    """Factory returns PostgreSQLRepository when DATABASE_URL is postgresql."""
    from src.config import settings
    from src.storage.repository import get_repository, PostgreSQLRepository
    monkeypatch.setattr(
        settings,
        "database_url",
        "postgresql+asyncpg://researcher:researcher@localhost:5432/researcher",
    )
    repo = get_repository()
    assert isinstance(repo, PostgreSQLRepository)


def test_is_postgres_helper():
    from src.storage.repository import _is_postgres
    assert _is_postgres("postgresql+asyncpg://user:pass@localhost/db")
    assert _is_postgres("postgres://user:pass@localhost/db")
    assert not _is_postgres("sqlite+aiosqlite:///./researcher.db")


@pytest.mark.asyncio
async def test_sqlite_save_and_list(tmp_db):
    """SQLiteRepository.save_session + list_sessions roundtrip."""
    from src.storage.repository import SQLiteRepository
    repo = SQLiteRepository()
    r = _make_result("SQLite roundtrip question?")
    sid = await repo.save_session(r)
    assert isinstance(sid, int) and sid > 0
    sessions = await repo.list_sessions(limit=5)
    assert any(s["question"] == "SQLite roundtrip question?" for s in sessions)


@pytest.mark.asyncio
async def test_sqlite_get_session_returns_none_for_missing(tmp_db):
    from src.storage.repository import SQLiteRepository
    repo = SQLiteRepository()
    result = await repo.get_session(99999)
    assert result is None
