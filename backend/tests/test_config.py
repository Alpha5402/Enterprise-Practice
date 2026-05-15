"""Configuration parsing tests."""

from app.core.config import Settings


def test_cors_origins_parse_comma_separated_env_value() -> None:
    """CORS origins accept comma-separated values from Docker env files."""
    settings = Settings(backend_cors_origins="http://localhost:5173,https://example.com")

    assert settings.backend_cors_origins == ["http://localhost:5173", "https://example.com"]


def test_cors_origins_parse_json_array_env_value() -> None:
    """CORS origins remain compatible with JSON list values."""
    settings = Settings(backend_cors_origins='["http://localhost:5173"]')

    assert settings.backend_cors_origins == ["http://localhost:5173"]

