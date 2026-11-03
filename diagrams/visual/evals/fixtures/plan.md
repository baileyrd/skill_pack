# Plan: expiring links

1. `svc/store.py`: add an `expires_at` column to `links`; `load()` returns None once expired.
2. `svc/api.py`: `POST /links` takes an optional `ttl_seconds`; `GET /{code}` answers 410 Gone for an expired code instead of 404.
3. New `svc/sweeper.py`: a nightly job that deletes expired rows and their Redis `hits:*` keys.
4. Tests: `tests/test_expiry.py` for 410 vs 404 and the sweeper.
