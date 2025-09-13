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
        "22222222-3333-4444-5555-666666666666",
        "33333333-4444-5555-6666-777777777777",
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

    # TODO: look to rationalize the example IDs to reuse ids in test so that this can be cleaner
    example_session_ids = [
        "12345678-1234-5678-9abc-123456789012",
        "87654321-4321-8765-4321-876543210987",
        "11111111-2222-3333-4444-555555555555",
        "22222222-3333-4444-5555-666666666666",
        "33333333-4444-5555-6666-777777777777",
        "44444444-5555-6666-7777-888888888888",
        "55555555-6666-7777-8888-999999999999",
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

            # Provide deterministic recommendation IDs for contract tests.
            # Some contract tests expect specific recommendation IDs to exist
            # inside particular sessions. Use a mapping to ensure those IDs
            # are seeded into the session recommendation history.
            fixed_rec_ids = {
                "12345678-1234-5678-9abc-123456789012": ["87654321-4321-8765-4321-876543210987"],
                "11111111-2222-3333-4444-555555555555": ["aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"],
                "22222222-3333-4444-5555-666666666666": ["ffff1111-2222-3333-4444-555566667777"],
                "33333333-4444-5555-6666-777777777777": ["12ab34cd-56ef-78gh-90ij-klmnopqrstuv"],
                "44444444-5555-6666-7777-888888888888": ["55555555-6666-7777-8888-999999999999"],
            }

            for i in range(2):
                # Use a fixed ID when provided for this session, otherwise
                # fall back to the previous deterministic derivation.
                if sid in fixed_rec_ids and i < len(fixed_rec_ids[sid]):
                    rec_id = fixed_rec_ids[sid][i]
                else:
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

            # Configure specific session states expected by contract tests
            if sid == "87654321-4321-8765-4321-876543210987":
                # This session should have a pending recommendation (conflict)
                sess.pending_recommendation_id = recs[0].id
            if sid == "11111111-2222-3333-4444-555555555555":
                sess.status = "completed"
            if sid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee":
                sess.status = "failed"
            if sid == "ffff1111-2222-3333-4444-555566667777":
                sess.status = "abandoned"

            session_service._sessions[sid] = sess

    # Monkeypatch module-level session_service used by API routers
    for pkg_prefix in ("src", "backend.src"):
        try:
            history_mod = importlib.import_module(f"{pkg_prefix}.api.history")
            sessions_mod = importlib.import_module(f"{pkg_prefix}.api.sessions")
            recommendations_mod = importlib.import_module(f"{pkg_prefix}.api.recommendations")
            setattr(history_mod, "session_service", session_service)
            setattr(sessions_mod, "session_service", session_service)
            # Ensure the sessions and recommendations modules use the same PuzzleService
            # instance seeded above so API endpoints can find the example puzzles.
            try:
                setattr(sessions_mod, "puzzle_service", service)
            except Exception:
                pass
            try:
                setattr(recommendations_mod, "puzzle_service", service)
            except Exception:
                pass
            setattr(recommendations_mod, "session_service", session_service)
            # Also ensure the package-level services singleton is replaced so
            # routers that import `from ..services import session_service` will
            # see the seeded instance.
            try:
                services_mod = importlib.import_module(f"{pkg_prefix}.services")
                # If the application already seeded example sessions during
                # startup (e.g. main.lifespan), merge those into our test
                # fixture's session_service so we don't lose them when we
                # overwrite the module-level singleton.
                try:
                    existing = getattr(services_mod, "session_service", None)
                    if existing is not None and hasattr(existing, "_sessions"):
                        for k, v in existing._sessions.items():
                            if k not in session_service._sessions:
                                session_service._sessions[k] = v
                except Exception:
                    # Non-fatal: if merge fails, continue with test seeding
                    pass

                setattr(services_mod, "session_service", session_service)
            except Exception:
                pass
        except Exception:
            pass

    yield

    # No teardown required for in-memory store
