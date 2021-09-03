"""Package-level HQBot tests."""

from hqbot import __version__


def test_version():
    """Verify version string."""
    assert __version__ == '0.1.0'
