"""Testes do núcleo da Bia sem exigir um modelo instalado."""

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from bia_core import (  # noqa: E402
    DEFAULT_MODEL,
    BiaServiceError,
    ask_ollama,
    build_context,
    build_prompt,
    calculate_summary,
    load_knowledge_base,
    stream_ollama,
)


class FakeResponse:
    def __init__(self, payload=None, stream_payloads=None):
        self.payload = payload
        self.stream_payloads = stream_payloads or []
        self.closed = False

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload

    def iter_lines(self, decode_unicode=False):
        for payload in self.stream_payloads:
            yield json.dumps(payload, ensure_ascii=False)

    def close(self):
        self.closed = True


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.last_request = None

    def post(self, url, **kwargs):
        self.last_request = {"url": url, **kwargs}
        return self.response


class BiaCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge_base = load_knowledge_base()

    def test_uses_original_challenge_model(self):
        self.assertEqual(DEFAULT_MODEL, "gpt-oss:20b")

    def test_loads_all_knowledge_sources(self):
        self.assertEqual(
            set(self.knowledge_base),
            {"perfil", "transacoes", "historico", "produtos"},
        )

    def test_calculates_expenses_before_calling_model(self):
        summary = calculate_summary(self.knowledge_base)
        self.assertEqual(summary["expenses"], 2488.90)
        self.assertEqual(summary["categories"]["alimentacao"], 570.00)

    def test_builds_compact_context(self):
        context = build_context(self.knowledge_base)
        self.assertIn("Saídas: R$ 2.488,90", context)
        self.assertIn("alimentação: R$ 570,00", context)
        self.assertIn("Não há taxas de mercado em tempo real", context)

    def test_prompt_includes_rules_question_and_conversation(self):
        prompt = build_prompt(
            "Pode explicar melhor?",
            self.knowledge_base,
            conversation=[
                {"role": "user", "content": "O que é CDI?"},
                {"role": "assistant", "content": "É uma taxa de referência."},
            ],
        )
        self.assertIn("Nunca recomende", prompt)
        self.assertIn("Usuário: O que é CDI?", prompt)
        self.assertIn("Pode explicar melhor?", prompt)

    def test_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            build_prompt("   ", self.knowledge_base)

    def test_non_streaming_request_has_safe_options(self):
        client = FakeHttpClient(FakeResponse({"response": "Resposta segura."}))
        answer = ask_ollama(
            "O que é CDI?",
            self.knowledge_base,
            url="http://ollama.test/api/generate",
            http_client=client,
        )
        request = client.last_request["json"]
        self.assertEqual(answer, "Resposta segura.")
        self.assertEqual(request["model"], "gpt-oss:20b")
        self.assertFalse(request["stream"])
        self.assertEqual(request["options"]["temperature"], 0.2)
        self.assertEqual(request["options"]["num_ctx"], 4096)

    def test_streams_partial_responses(self):
        response = FakeResponse(
            stream_payloads=[
                {"response": "Olá", "done": False},
                {"response": "!", "done": True},
            ]
        )
        client = FakeHttpClient(response)
        chunks = list(
            stream_ollama(
                "O que é CDI?",
                self.knowledge_base,
                http_client=client,
            )
        )
        self.assertEqual(chunks, ["Olá", "!"])
        self.assertTrue(client.last_request["json"]["stream"])
        self.assertTrue(response.closed)

    def test_rejects_empty_model_response(self):
        client = FakeHttpClient(FakeResponse({"response": ""}))
        with self.assertRaises(BiaServiceError):
            ask_ollama("O que é CDI?", self.knowledge_base, http_client=client)

    def test_evaluation_scenarios_have_required_fields(self):
        scenarios_path = PROJECT_ROOT / "evaluation" / "scenarios.json"
        scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(scenarios), 6)
        for scenario in scenarios:
            self.assertIn("id", scenario)
            self.assertIn("question", scenario)
            self.assertIn("expected_behavior", scenario)


if __name__ == "__main__":
    unittest.main()
