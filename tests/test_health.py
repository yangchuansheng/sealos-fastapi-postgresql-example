from app.api.routes import health


def test_health() -> None:
    assert health() == {"status": "ok", "framework": "FastAPI"}
