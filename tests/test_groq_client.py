import json
import unittest

from core_system.groq_client import GroqClient, GroqError, RateLimiter, RateLimits, parse_duration

GOOD_PROJECT = {"name": "x", "code": "print(1)", "readme": "# x", "requirements": []}


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def ok_response(content=GOOD_PROJECT, tokens=3000, headers=None):
    body = {"choices": [{"message": {"content": json.dumps(content)}}], "usage": {"total_tokens": tokens}}
    return 200, headers or {}, json.dumps(body)


class ScriptedTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, headers, payload, timeout):
        self.calls.append(payload)
        return self.responses.pop(0)


class ParseDurationTests(unittest.TestCase):
    def test_parses_groq_formats(self):
        self.assertAlmostEqual(parse_duration("2.28s"), 2.28)
        self.assertAlmostEqual(parse_duration("1m26.4s"), 86.4)
        self.assertAlmostEqual(parse_duration("120ms"), 0.12)
        self.assertAlmostEqual(parse_duration("7"), 7.0)
        self.assertEqual(parse_duration(None), 0.0)


class RateLimiterTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeClock()
        self.limiter = RateLimiter(RateLimits(tokens_per_minute=1000, requests_per_minute=3, safety_margin=1.0),
                                   self.fake.clock, self.fake.sleep)

    def test_waits_until_token_window_frees(self):
        self.limiter.acquire(600, deadline=1000)
        self.fake.now = 10
        self.limiter.acquire(600, deadline=1000)  # 1200 > 1000: must wait until t=60
        self.assertGreaterEqual(self.fake.now, 60)

    def test_enforces_requests_per_minute(self):
        for _ in range(3):
            self.limiter.acquire(10, deadline=1000)
        self.limiter.acquire(10, deadline=1000)
        self.assertGreaterEqual(self.fake.now, 60)

    def test_rejects_request_larger_than_budget(self):
        with self.assertRaises(GroqError):
            self.limiter.acquire(2000, deadline=1000)

    def test_raises_when_wait_exceeds_deadline(self):
        self.limiter.acquire(900, deadline=1000)
        with self.assertRaises(GroqError):
            self.limiter.acquire(900, deadline=5)

    def test_retry_after_header_blocks_next_call(self):
        self.limiter.apply_headers({"Retry-After": "12"}, next_tokens=10)
        self.limiter.acquire(10, deadline=1000)
        self.assertGreaterEqual(self.fake.now, 12)

    def test_low_remaining_tokens_header_waits_for_reset(self):
        self.limiter.apply_headers(
            {"x-ratelimit-remaining-tokens": "100", "x-ratelimit-reset-tokens": "7.5s"}, next_tokens=500
        )
        self.limiter.acquire(500, deadline=1000)
        self.assertGreaterEqual(self.fake.now, 7.5)

    def test_record_usage_replaces_estimate(self):
        self.limiter.acquire(900, deadline=1000)
        self.limiter.record_usage(100)
        self.limiter.acquire(800, deadline=1000)  # fits now that real usage was 100
        self.assertEqual(self.fake.sleeps, [])


class GroqClientTests(unittest.TestCase):
    def make_client(self, transport, **kwargs):
        fake = FakeClock()
        client = GroqClient("test-key", transport=transport, clock=fake.clock, sleep=fake.sleep,
                            max_completion_tokens=1000, **kwargs)
        return client, fake

    def test_returns_parsed_json_and_model(self):
        transport = ScriptedTransport([ok_response()])
        client, _ = self.make_client(transport)
        data, model = client.chat_json("make a project")
        self.assertEqual(data, GOOD_PROJECT)
        self.assertEqual(model, "openai/gpt-oss-120b")
        self.assertEqual(transport.calls[0]["reasoning_effort"], "low")
        self.assertEqual(transport.calls[0]["response_format"], {"type": "json_object"})

    def test_schema_uses_strict_json_schema_on_gpt_oss_only(self):
        schema = {"type": "object"}
        transport = ScriptedTransport([(404, {}, "gone"), ok_response()])
        client, _ = self.make_client(transport)
        client.chat_json("p", schema)
        self.assertEqual(transport.calls[0]["response_format"]["type"], "json_schema")
        self.assertTrue(transport.calls[0]["response_format"]["json_schema"]["strict"])
        self.assertEqual(transport.calls[1]["response_format"], {"type": "json_object"})  # qwen

    def test_429_honours_retry_after_then_succeeds(self):
        transport = ScriptedTransport([(429, {"retry-after": "20"}, "{}"), ok_response()])
        client, fake = self.make_client(transport)
        _, model = client.chat_json("p")
        self.assertEqual(model, "openai/gpt-oss-120b")
        self.assertGreaterEqual(fake.now, 20)

    def test_falls_back_to_next_model_on_404(self):
        transport = ScriptedTransport([(404, {}, '{"error":"gone"}'), ok_response()])
        client, _ = self.make_client(transport)
        _, model = client.chat_json("p")
        self.assertEqual(model, "qwen/qwen3.8-27b")
        self.assertNotIn("reasoning_effort", transport.calls[1])

    def test_json_validate_failed_retries_same_model(self):
        failed = (400, {}, '{"error":{"code":"json_validate_failed"}}')
        transport = ScriptedTransport([failed, ok_response()])
        client, _ = self.make_client(transport)
        _, model = client.chat_json("p")
        self.assertEqual(model, "openai/gpt-oss-120b")
        self.assertEqual(len(transport.calls), 2)

    def test_invalid_json_retries_same_model_once(self):
        bad = (200, {}, json.dumps({"choices": [{"message": {"content": "not json"}}], "usage": {}}))
        transport = ScriptedTransport([bad, ok_response()])
        client, _ = self.make_client(transport)
        _, model = client.chat_json("p")
        self.assertEqual(model, "openai/gpt-oss-120b")

    def test_falls_back_after_repeated_empty_content(self):
        empty = (200, {}, json.dumps({"choices": [{"message": {"content": ""}, "finish_reason": "length"}]}))
        transport = ScriptedTransport([empty, empty, ok_response()])
        client, _ = self.make_client(transport)
        _, model = client.chat_json("p")
        self.assertEqual(model, "qwen/qwen3.8-27b")

    def test_raises_when_all_models_fail(self):
        transport = ScriptedTransport([(400, {}, "bad")] * 3)
        client, _ = self.make_client(transport)
        with self.assertRaises(GroqError):
            client.chat_json("p")

    def test_missing_key_is_rejected(self):
        with self.assertRaises(GroqError):
            GroqClient("")


if __name__ == "__main__":
    unittest.main()
