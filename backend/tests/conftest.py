"""Test fixtures for backend tests.

Provide an autouse session-scoped fixture that seeds the in-memory PuzzleService
used by the FastAPI app so contract tests have deterministic puzzles available.
"""

from typing import List

import pytest

import importlib


@pytest.fixture(scope="session", autouse=True)
def seed_puzzles_for_contract_tests():
    """Seed the PuzzleService in-memory store with known example puzzles.

    This fixture runs once per test session and ensures the PuzzleService has
    the example IDs used by contract tests. It avoids modifying application
    code directly and centralizes test-only setup.
    """
    # Try to create a PuzzleService from the same package namespace the app uses.
    service = None
    # Prefer runtime package 'src' (tests import from 'src.main'), fallback to 'backend.src'
    tried = []
    for pkg_prefix in ("src", "backend.src"):
        try:
            svc_mod = importlib.import_module(f"{pkg_prefix}.services.puzzle_service")
            PuzzleService = getattr(svc_mod, "PuzzleService")
            service = PuzzleService()
            tried.append(pkg_prefix)
            break
        except Exception:
            continue

    if service is None:
        # Last-resort: import from backend path used in some contexts
        from backend.src.services.puzzle_service import PuzzleService as PuzzleServiceFallback

        service = PuzzleServiceFallback()

    # If the service already seeded via __init__ (dev-time), do nothing
    example_ids = [
        "12345678-1234-5678-9abc-123456789012",
        "87654321-4321-8765-4321-876543210987",
        "11111111-2222-3333-4444-555555555555",
        "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "ffff1111-2222-3333-4444-555566667777",
        "12ab34cd-56ef-78gh-90ij-klmnopqrstuv",
    ]

    # Only seed if not present
    for eid in example_ids:
        if service.get_puzzle(eid) is None:
            # Create a minimal 16-word puzzle
            words: List[str] = [f"WORD{i+1}" for i in range(16)]

            # Instantiate Puzzle model from same package namespace the app uses so
            # the Puzzle.id field matches the example ID.
            PuzzleCls = None
            for pkg_prefix in ("src", "backend.src"):
                try:
                    mod = importlib.import_module(f"{pkg_prefix}.models.puzzle")
                    PuzzleCls = getattr(mod, "Puzzle")
                    break
                except Exception:
                    continue

            if PuzzleCls is None:
                from backend.src.models.puzzle import Puzzle as PuzzleCls

            p = PuzzleCls(id=eid, words=words, uploaded_filename="example.txt", user_id=None)
            service._puzzles[eid] = p

    # Monkeypatch the module-level PuzzleService instance used by routers.
    # Try both package variants so the fixture works regardless of import path used in tests.
    for pkg_prefix in ("src", "backend.src"):
        try:
            puzzles_module = importlib.import_module(f"{pkg_prefix}.api.puzzles")
            setattr(puzzles_module, "puzzle_service", service)
        except Exception:
            # ignore missing package variant
            pass

    # Also seed SessionService with example sessions and some recommendation history
    # so contract tests for sessions/recommendations/history pass deterministically.
    session_service = None
    for pkg_prefix in ("src", "backend.src"):
        try:
            svc_mod = importlib.import_module(f"{pkg_prefix}.services.session_service")
            SessionService = getattr(svc_mod, "SessionService")
            session_service = SessionService()
            break
        except Exception:
            continue

    if session_service is None:
        from backend.src.services.session_service import SessionService as SessionServiceFallback

        session_service = SessionServiceFallback()

    # Import Session and Recommendation model classes from same package namespace
    SessionCls = None
    RecommendationCls = None
    for pkg_prefix in ("src", "backend.src"):
        try:
            s_mod = importlib.import_module(f"{pkg_prefix}.models.session")
            r_mod = importlib.import_module(f"{pkg_prefix}.models.recommendation")
            SessionCls = getattr(s_mod, "Session")
            RecommendationCls = getattr(r_mod, "Recommendation")
            break
        except Exception:
            continue

    if SessionCls is None:
        from backend.src.models.session import Session as SessionCls
        from backend.src.models.recommendation import Recommendation as RecommendationCls

    example_session_ids = [
        "12345678-1234-5678-9abc-123456789012",
        "87654321-4321-8765-4321-876543210987",
        "11111111-2222-3333-4444-555555555555",
    ]

    # Create minimal sessions and add a few recommendations for history tests
    for sid in example_session_ids:
        if session_service.get_session(sid) is None:
            # Create a session with a full set of remaining words (16 words)
            remaining_words = [f"word_{i+1}" for i in range(16)]
            sess = SessionCls(
                id=sid,
                puzzle_id=example_ids[0],
                llm_model_config="gpt-4",
                remaining_words=remaining_words,
            )

            # Attach a small recommendation history for sessions that need it
            recs = []
            # Create two sample recommendations
            from datetime import datetime

            for i in range(2):
                rec_id = f"{sid[:-2]}{i:02d}"
                recommended_words = [f"W{i}{j}" for j in range(4)]
                rec = RecommendationCls(
                    id=rec_id,
                    session_id=sid,
                    recommended_words=recommended_words,
                    explanation="Example explanation text",
                    timestamp=datetime.now(),
                    llm_model="gpt-4",
                    processing_time_ms=123,
                    user_evaluation=None,
                    evaluation_timestamp=None,
                )
                recs.append(rec)

            sess.recommendation_history = recs
            session_service._sessions[sid] = sess

    # Monkeypatch module-level session_service used by API routers
    for pkg_prefix in ("src", "backend.src"):
        try:
            history_mod = importlib.import_module(f"{pkg_prefix}.api.history")
            sessions_mod = importlib.import_module(f"{pkg_prefix}.api.sessions")
            recommendations_mod = importlib.import_module(f"{pkg_prefix}.api.recommendations")
            setattr(history_mod, "session_service", session_service)
            setattr(sessions_mod, "session_service", session_service)
            setattr(recommendations_mod, "session_service", session_service)
        except Exception:
            pass

    yield

    # No teardown required for in-memory store
