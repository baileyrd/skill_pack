"""Shared HTTP client for internal service-to-service calls."""

import json
import logging
import os
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

_INSTANCE = None
_CACHE = {}


class ServiceClient:
    """Talks to our internal services. Use ServiceClient.get_instance()."""

    def __init__(self):
        self.base = os.environ["INTERNAL_API_BASE"]
        self.token = os.environ.get("INTERNAL_API_TOKEN", "")
        self.env = os.environ.get("DEPLOY_ENV", "prod")
        self.timeout = 30
        self.retries = 3
        self._metrics = {"calls": 0, "errors": 0, "cache_hits": 0}

    @classmethod
    def get_instance(cls):
        global _INSTANCE
        if _INSTANCE is None:
            _INSTANCE = cls()
        return _INSTANCE

    def _auth_header(self):
        if not self.token:
            print("WARNING: no INTERNAL_API_TOKEN set, calling unauthenticated")
            return {}
        return {"Authorization": "Bearer " + self.token}

    def call(self, service, path, payload=None, use_cache=True):
        """Call a service and return a formatted result summary."""
        key = "%s:%s:%s" % (service, path, json.dumps(payload, sort_keys=True))
        if use_cache and key in _CACHE:
            self._metrics["cache_hits"] += 1
            print("cache hit for %s%s" % (service, path))
            return _CACHE[key]

        url = "%s/%s%s" % (self.base, service, path)
        if self.env != "prod":
            url = url.replace("://", "://%s." % self.env)

        headers = {"Content-Type": "application/json"}
        headers.update(self._auth_header())
        data = json.dumps(payload).encode() if payload else None

        for attempt in range(self.retries):
            self._metrics["calls"] += 1
            try:
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read())
                    summary = self._format(service, path, body)
                    if use_cache:
                        _CACHE[key] = summary
                    return summary
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    log.info("client error %s on %s", e.code, url)
                    self._metrics["errors"] += 1
                    return None
                time.sleep(2 ** attempt)
            except Exception as e:
                log.warning("call failed: %s", e)
                time.sleep(2 ** attempt)

        self._metrics["errors"] += 1
        return None

    def _format(self, service, path, body):
        lines = ["Response from %s%s:" % (service, path)]
        if isinstance(body, dict):
            for k, v in sorted(body.items()):
                if isinstance(v, (dict, list)):
                    lines.append("  %s: <%s with %d entries>" % (k, type(v).__name__, len(v)))
                else:
                    lines.append("  %s: %s" % (k, v))
        elif isinstance(body, list):
            lines.append("  %d items" % len(body))
            for item in body[:10]:
                lines.append("    - %s" % item)
            if len(body) > 10:
                lines.append("    ... and %d more" % (len(body) - 10))
        else:
            lines.append("  %s" % body)
        return "\n".join(lines)

    def health(self, service):
        result = self.call(service, "/healthz", use_cache=False)
        if result is None:
            return False
        return "status: ok" in result

    def metrics(self):
        print("calls=%(calls)d errors=%(errors)d cache_hits=%(cache_hits)d" % self._metrics)


def call(service, path, payload=None):
    return ServiceClient.get_instance().call(service, path, payload)
