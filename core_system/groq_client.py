"""Rate-limited Groq chat client (stdlib only).

Keeps every call inside the account's limits in two ways:
1. A client-side sliding 60s window for tokens-per-minute and requests-per-minute,
   so we never send a request that would exceed the budget.
2. Server feedback: the x-ratelimit-* headers and Retry-After on HTTP 429 push a
   "blocked until" time that the limiter waits out before the next call.
All waits are bounded by a deadline so a serverless invocation never hangs.
"""
import json
import logging
import re
import time
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass
from typing import Callable

from core_system.strike_core import StrikeError, parse_json_text

log = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# Strongest first. Fallbacks are used only if a model errors or returns bad JSON.
MODELS = ("openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b")
REASONING_MODELS = ("openai/gpt-oss-",)
WINDOW_SECONDS = 60.0
MAX_ATTEMPTS_PER_MODEL = 3
CHARS_PER_TOKEN = 3  # deliberately pessimistic estimate
USER_AGENT = "daily-strike/2.0"


@dataclass(frozen=True)
class RateLimits:
    """Groq limits for this key, read from the API's x-ratelimit-limit-* headers."""

    tokens_per_minute: int = 8000
    requests_per_minute: int = 30
    safety_margin: float = 0.9

    @property
    def token_budget(self) -> int:
        return int(self.tokens_per_minute * self.safety_margin)


class GroqError(StrikeError):
    pass


class GroqHTTPError(GroqError):
    def __init__(self, status: int, body: str, headers: dict[str, str]):
        super().__init__(f"Groq HTTP {status}: {body[:300]}")
        self.status = status
        self.headers = headers
        self.body = body

    @property
    def retryable(self) -> bool:
        # json_validate_failed = the model produced malformed JSON once; a retry usually works.
        return self.status == 429 or self.status >= 500 or "json_validate_failed" in self.body


def parse_duration(value: str | None) -> float:
    """Parse Groq reset values such as '2.28s', '1m26.4s', '120ms', '1h2m' or '7'."""
    if not value:
        return 0.0
    value = value.strip()
    try:
        return float(value)
    except ValueError:
        pass
    units = {"h": 3600.0, "m": 60.0, "s": 1.0, "ms": 0.001}
    total = 0.0
    for number, unit in re.findall(r"([\d.]+)(ms|h|m|s)", value):
        total += float(number) * units[unit]
    return total


class RateLimiter:
    def __init__(
        self,
        limits: RateLimits,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.limits = limits
        self._clock = clock
        self._sleep = sleep
        self._events: deque[list[float]] = deque()  # [timestamp, tokens]
        self._blocked_until = 0.0

    def _prune(self, now: float) -> None:
        while self._events and now - self._events[0][0] >= WINDOW_SECONDS:
            self._events.popleft()

    def _wait_needed(self, tokens: int, now: float) -> float:
        self._prune(now)
        wait = max(0.0, self._blocked_until - now)
        used = sum(t for _, t in self._events)
        count = len(self._events)
        # Let the oldest calls age out of the window until this one fits.
        for ts, t in self._events:
            if used + tokens <= self.limits.token_budget and count < self.limits.requests_per_minute:
                break
            used -= t
            count -= 1
            wait = max(wait, ts + WINDOW_SECONDS - now)
        return wait

    def acquire(self, tokens: int, deadline: float) -> None:
        if tokens > self.limits.token_budget:
            raise GroqError(f"Request needs ~{tokens} tokens; per-minute budget is {self.limits.token_budget}.")
        while True:
            now = self._clock()
            wait = self._wait_needed(tokens, now)
            if wait <= 0:
                self._events.append([now, float(tokens)])
                return
            if now + wait > deadline:
                raise GroqError(f"Rate limit needs a {wait:.1f}s wait, past the run deadline.")
            log.info("Rate limit: waiting %.1fs before calling Groq", wait)
            self._sleep(wait + 0.05)

    def record_usage(self, tokens: int) -> None:
        if self._events and tokens > 0:
            self._events[-1][1] = float(tokens)

    def block_for(self, seconds: float) -> None:
        self._blocked_until = max(self._blocked_until, self._clock() + seconds)

    def apply_headers(self, headers: dict[str, str], next_tokens: int) -> None:
        h = {k.lower(): v for k, v in headers.items()}
        if "retry-after" in h:
            self.block_for(parse_duration(h["retry-after"]))
        remaining_tokens = h.get("x-ratelimit-remaining-tokens")
        if remaining_tokens is not None and int(float(remaining_tokens)) < next_tokens:
            self.block_for(parse_duration(h.get("x-ratelimit-reset-tokens")))
        remaining_requests = h.get("x-ratelimit-remaining-requests")
        if remaining_requests is not None and int(float(remaining_requests)) <= 0:
            self.block_for(parse_duration(h.get("x-ratelimit-reset-requests")))


Transport = Callable[[str, dict, dict, float], tuple[int, dict[str, str], str]]


def urllib_transport(url: str, headers: dict, payload: dict, timeout: float) -> tuple[int, dict[str, str], str]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers.items()), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read().decode("utf-8", "replace")


class GroqClient:
    def __init__(
        self,
        api_key: str,
        limits: RateLimits = RateLimits(),
        models: tuple[str, ...] = MODELS,
        max_completion_tokens: int = 4500,  # real projects use ~1.4-1.8K; leaves 2.5x headroom
        deadline_seconds: float = 240.0,
        transport: Transport = urllib_transport,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if not api_key:
            raise GroqError("GROQ_API_KEY is not set.")
        self._api_key = api_key
        self.models = models
        self.max_completion_tokens = max_completion_tokens
        self.deadline_seconds = deadline_seconds
        self._transport = transport
        self._clock = clock
        self._sleep = sleep
        self.limiter = RateLimiter(limits, clock, sleep)

    def estimate_tokens(self, prompt: str) -> int:
        return len(prompt) // CHARS_PER_TOKEN + self.max_completion_tokens

    def _payload(self, model: str, prompt: str) -> dict:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a senior Python engineer. Respond with one valid JSON object only."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.8,
            "max_completion_tokens": self.max_completion_tokens,
        }
        if model.startswith(REASONING_MODELS):
            payload["reasoning_effort"] = "low"  # leave the token budget for the answer
        return payload

    def _call(self, model: str, prompt: str, tokens: int, deadline: float) -> dict:
        self.limiter.acquire(tokens, deadline)
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        timeout = max(5.0, min(120.0, deadline - self._clock()))
        status, resp_headers, body = self._transport(GROQ_URL, headers, self._payload(model, prompt), timeout)
        self.limiter.apply_headers(resp_headers, tokens)
        if status != 200:
            raise GroqHTTPError(status, body, resp_headers)
        try:
            data = json.loads(body)
        except ValueError as exc:
            raise ValueError(f"non-JSON body ({len(body)} chars): {body[:200]!r}") from exc
        self.limiter.record_usage(int(data.get("usage", {}).get("total_tokens", 0)))
        return data

    @staticmethod
    def _content(data: dict) -> str:
        choice = data["choices"][0]
        content = choice["message"].get("content") or ""
        if not content.strip():
            raise ValueError(f"empty content (finish_reason={choice.get('finish_reason')})")
        return content

    def chat_json(self, prompt: str) -> tuple[dict, str]:
        """Return (parsed JSON object, model used), trying models strongest-first."""
        deadline = self._clock() + self.deadline_seconds
        tokens = self.estimate_tokens(prompt)
        errors: list[str] = []
        for model in self.models:
            for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
                try:
                    log.info("Calling Groq model %s (attempt %d)", model, attempt)
                    data = self._call(model, prompt, tokens, deadline)
                    content = self._content(data)
                    try:
                        parsed = parse_json_text(content)
                    except ValueError as exc:
                        finish = data["choices"][0].get("finish_reason")
                        raise ValueError(f"invalid JSON content (finish_reason={finish}): {content[:200]!r}") from exc
                    return parsed, model
                except GroqHTTPError as exc:
                    errors.append(f"{model}: HTTP {exc.status}")
                    log.warning("Groq %s failed: %s", model, exc)
                    if exc.retryable:
                        if exc.status >= 500:
                            self._sleep(min(2.0 ** attempt, 10.0))
                        continue  # retry same model; limiter enforces Retry-After
                    break  # 401/404 etc: this model will not work, try the next
                except (ValueError, KeyError, IndexError) as exc:
                    errors.append(f"{model}: bad response ({exc.__class__.__name__})")
                    log.warning("Groq %s returned an unusable response: %s", model, exc)
                    if attempt >= 2:
                        break  # one retry on the same model, then fall back
                    continue
                except GroqError:
                    raise  # deadline or budget problems will not improve by retrying
                except OSError as exc:  # network errors / timeouts
                    errors.append(f"{model}: {exc.__class__.__name__}")
                    self._sleep(min(2.0 ** attempt, 10.0))
        raise GroqError("All Groq models failed: " + "; ".join(errors))
