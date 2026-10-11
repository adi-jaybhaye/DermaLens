import pytest
from app.utils.rate_limiter import auth_limiter, upload_limiter, api_limiter


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Clear in-memory sliding window history before and after each test."""
    auth_limiter.history.clear()
    upload_limiter.history.clear()
    api_limiter.history.clear()
    yield
    auth_limiter.history.clear()
    upload_limiter.history.clear()
    api_limiter.history.clear()
