"""
Integration tests that require external services.

These tests interact with real external APIs (like Supabase) and require
proper credentials to be configured. They are skipped by default and should
be run explicitly before deployment.

Run with: pytest -m integration
"""