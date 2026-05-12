import time
from prometheus_client import Counter, Histogram, Gauge

GATEWAY_REQUESTS = Counter("gateway_requests_total", "Total gateway requests", ["status"])
GATEWAY_LATENCY = Histogram("gateway_request_latency_seconds", "Gateway request latency seconds")
AUDIT_CHAIN_OK = Gauge("audit_chain_ok", "Audit chain status (1 ok, 0 fail)")

class timer:
    def __enter__(self):
        self.t0 = time.time()
        return self
    def __exit__(self, exc_type, exc, tb):
        GATEWAY_LATENCY.observe(time.time() - self.t0)
