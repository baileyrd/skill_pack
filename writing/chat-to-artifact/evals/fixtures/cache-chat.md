# Exported chat: caching for the pricing API

**Priya:** The /quote endpoint is p95 1.8s. Most of it is the FX-rates call. Can we cache it?

**Assistant:** Options: (a) in-process LRU per pod, (b) Redis shared cache, (c) precompute rates every minute into Postgres. (a) is simplest but each of the 12 pods warms separately. (b) adds a dependency but one warm cache. (c) needs a scheduler.

**Priya:** We already run Redis for sessions. Let's go with Redis. TTL?

**Assistant:** FX provider updates every 60s, so a 60s TTL keeps you at most one update stale.

**Priya:** Finance said quotes can be up to 5 minutes stale. Use 300s, it cuts provider calls a lot. Here's the provider key so you can test: sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c

**Assistant:** Done. With a 300s TTL in Redis, local load test p95 went from 1.8s to 240ms. PR #412 is open.

**Priya:** Nice. Actually, one more thing: what happens if Redis is down?

**Assistant:** Right now the request fails. We could fall back to calling the provider directly.

**Priya:** Yes, fall back to the provider and log a warning. I'm not sure yet whether we should alert on it. Marco should review #412 before Friday.
