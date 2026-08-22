"""Executa os cenários documentados contra o modelo local."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from bia_core import BiaServiceError, ask_ollama, load_knowledge_base  # noqa: E402


def main() -> int:
    scenarios_path = PROJECT_ROOT / "evaluation" / "scenarios.json"
    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
    knowledge_base = load_knowledge_base()
    results = []

    for scenario in scenarios:
        print(f"\n[{scenario['id']}] {scenario['question']}")
        try:
            answer = ask_ollama(scenario["question"], knowledge_base)
        except BiaServiceError as error:
            print(f"ERRO: {error}")
            return 1

        print(answer)
        results.append(
            {
                **scenario,
                "answer": answer,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "human_review": {
                    "assertiveness": None,
                    "safety": None,
                    "coherence": None,
                    "notes": "",
                },
            }
        )

    output_path = PROJECT_ROOT / "evaluation" / "latest-results.json"
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nResultados salvos em {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
