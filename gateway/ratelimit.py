import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self):
        self._req = defaultdict(deque)

    def allow(self, key: str, per_minute: int) -> bool:
        now = time.time()
        q = self._req[key]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= per_minute:
            return False
        q.append(now)
        return True
