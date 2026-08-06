from app.core.db import _normalize_url


def test_normalize_url_rewrites_plain_postgresql_scheme_to_psycopg():
    url = "postgresql://user:pass@host/dbname?sslmode=require"

    assert _normalize_url(url) == "postgresql+psycopg://user:pass@host/dbname?sslmode=require"


def test_normalize_url_leaves_other_schemes_untouched():
    assert _normalize_url("sqlite:///test.db") == "sqlite:///test.db"
    assert _normalize_url("postgresql+psycopg://already/explicit") == (
        "postgresql+psycopg://already/explicit"
    )
