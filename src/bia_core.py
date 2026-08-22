"""Dados, regras de segurança e integração da Bia com o Ollama."""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gpt-oss:20b"
DEFAULT_OPTIONS = {
    "temperature": 0.2,
    "num_ctx": 4096,
    "seed": 42,
}
CATEGORY_LABELS = {
    "alimentacao": "alimentação",
    "saude": "saúde",
}

SYSTEM_PROMPT = """Você é a Bia, uma educadora financeira virtual, amigável e responsável.

OBJETIVO
Ensinar conceitos de finanças pessoais em linguagem simples e usar somente os dados
fictícios fornecidos no contexto para criar exemplos didáticos.

REGRAS DE SEGURANÇA
- Nunca recomende um investimento, produto ou estratégia específica para o usuário.
- Ao receber um pedido de recomendação personalizada, explique os fatores que devem ser
  avaliados e oriente a busca por um profissional certificado.
- Não afirme que pode contatar, indicar ou validar profissionais.
- Não invente saldos, taxas atuais, cotações ou informações ausentes no contexto.
- Deixe claro quando uma informação não estiver disponível.
- Recuse pedidos de senhas, credenciais ou dados de terceiros.
- Para assuntos fora de finanças pessoais, explique brevemente o seu escopo.
- Não se apresente como um canal oficial do Bradesco ou da DIO.
- Responda em português, de forma acolhedora, direta e com no máximo três parágrafos.

EXEMPLOS DE COMPORTAMENTO
- Para "Quanto gastei com alimentação?", use o total de alimentação presente no contexto.
- Para "Onde devo investir?", não escolha um produto; explique critérios e limites.
- Para uma cotação atual, informe que a base não contém dados de mercado em tempo real.
- Para assuntos fora de finanças, explique que seu escopo é educação financeira.
"""


class BiaServiceError(RuntimeError):
    """Erro compreensível para falhas na integração com o modelo local."""


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def load_knowledge_base(data_dir: Path | str | None = None) -> dict[str, Any]:
    """Carrega a base fictícia independentemente do diretório de execução."""
    directory = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    return {
        "perfil": _read_json(directory / "perfil_investidor.json"),
        "transacoes": _read_csv(directory / "transacoes.csv"),
        "historico": _read_csv(directory / "historico_atendimento.csv"),
        "produtos": _read_json(directory / "produtos_financeiros.json"),
    }


def format_brl(value: float) -> str:
    """Formata um número no padrão monetário brasileiro."""
    formatted = f"{value:,.2f}"
    return f"R$ {formatted.replace(',', '_').replace('.', ',').replace('_', '.')}"


def display_category(category: str) -> str:
    """Devolve o nome legível de uma categoria."""
    return CATEGORY_LABELS.get(category, category)


def calculate_summary(knowledge_base: dict[str, Any]) -> dict[str, Any]:
    """Calcula os totais antes de enviar o contexto ao modelo."""
    categories: defaultdict[str, float] = defaultdict(float)
    total_income = 0.0
    total_expenses = 0.0

    for transaction in knowledge_base["transacoes"]:
        value = float(transaction["valor"])
        if transaction["tipo"] == "entrada":
            total_income += value
        else:
            total_expenses += value
            categories[transaction["categoria"]] += value

    return {
        "income": total_income,
        "expenses": total_expenses,
        "balance": total_income - total_expenses,
        "categories": dict(categories),
    }


def build_context(knowledge_base: dict[str, Any]) -> str:
    """Resume os dados relevantes para reduzir erros e uso de contexto."""
    profile = knowledge_base["perfil"]
    summary = calculate_summary(knowledge_base)
    category_summary = "\n".join(
        f"- {display_category(name)}: {format_brl(value)}"
        for name, value in sorted(
            summary["categories"].items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    products = "\n".join(
        f"- {item['nome']}: categoria {item['categoria']}, risco {item['risco']}, "
        f"rentabilidade descrita como '{item['rentabilidade']}'"
        for item in knowledge_base["produtos"]
    )
    history = "\n".join(
        f"- {item['data']} | {item['tema']}: {item['resumo']}"
        for item in knowledge_base["historico"]
    )

    return f"""DADOS FICTÍCIOS DA DEMONSTRAÇÃO
Cliente: {profile['nome']}, {profile['idade']} anos
Perfil declarado: {profile['perfil_investidor']}
Objetivo principal: {profile['objetivo_principal']}
Renda mensal informada: {format_brl(float(profile['renda_mensal']))}
Patrimônio informado: {format_brl(float(profile['patrimonio_total']))}
Reserva de emergência atual: {format_brl(float(profile['reserva_emergencia_atual']))}

RESUMO CALCULADO DAS TRANSAÇÕES
Entradas: {format_brl(summary['income'])}
Saídas: {format_brl(summary['expenses'])}
Saldo do período: {format_brl(summary['balance'])}
Saídas por categoria:
{category_summary}

PRODUTOS DISPONÍVEIS SOMENTE PARA EXPLICAÇÃO CONCEITUAL
{products}

HISTÓRICO FICTÍCIO
{history}

Não há taxas de mercado em tempo real, cotações, senhas ou dados bancários reais nesta base."""


def _format_conversation(conversation: Iterable[dict[str, str]] | None) -> str:
    if not conversation:
        return "Sem mensagens anteriores."

    recent_messages = list(conversation)[-6:]
    lines = []
    for message in recent_messages:
        role = "Usuário" if message.get("role") == "user" else "Bia"
        content = str(message.get("content", ""))[:2000]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def build_prompt(
    question: str,
    knowledge_base: dict[str, Any],
    conversation: Iterable[dict[str, str]] | None = None,
) -> str:
    """Combina regras, dados, histórico recente e a pergunta atual."""
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("A pergunta não pode estar vazia.")

    return f"""{SYSTEM_PROMPT}

CONTEXTO FINANCEIRO
{build_context(knowledge_base)}

CONVERSA RECENTE
{_format_conversation(conversation)}

PERGUNTA ATUAL
{clean_question}

RESPOSTA DA BIA"""


def _request_payload(
    question: str,
    knowledge_base: dict[str, Any],
    conversation: Iterable[dict[str, str]] | None,
    model: str,
    *,
    stream: bool,
) -> dict[str, Any]:
    return {
        "model": model,
        "prompt": build_prompt(question, knowledge_base, conversation),
        "stream": stream,
        "keep_alive": "5m",
        "options": DEFAULT_OPTIONS,
    }


def ask_ollama(
    question: str,
    knowledge_base: dict[str, Any],
    *,
    conversation: Iterable[dict[str, str]] | None = None,
    url: str | None = None,
    model: str | None = None,
    timeout: float = 300,
    http_client: Any = requests,
) -> str:
    """Executa uma chamada completa, útil para avaliação e automação."""
    ollama_url = url or os.getenv("BIA_OLLAMA_URL", DEFAULT_OLLAMA_URL)
    ollama_model = model or os.getenv("BIA_OLLAMA_MODEL", DEFAULT_MODEL)

    try:
        response = http_client.post(
            ollama_url,
            json=_request_payload(
                question,
                knowledge_base,
                conversation,
                ollama_model,
                stream=False,
            ),
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise BiaServiceError(
            "Não foi possível conversar com o Ollama. Confirme se ele está aberto "
            f"e se o modelo '{ollama_model}' foi instalado."
        ) from error
    except (TypeError, ValueError) as error:
        raise BiaServiceError("O Ollama retornou uma resposta em formato inválido.") from error

    answer = payload.get("response") if isinstance(payload, dict) else None
    if not isinstance(answer, str) or not answer.strip():
        raise BiaServiceError("O modelo não retornou uma resposta válida.")
    return answer.strip()


def stream_ollama(
    question: str,
    knowledge_base: dict[str, Any],
    *,
    conversation: Iterable[dict[str, str]] | None = None,
    url: str | None = None,
    model: str | None = None,
    timeout: float = 300,
    http_client: Any = requests,
) -> Iterator[str]:
    """Entrega a resposta em partes para reduzir a espera percebida na interface."""
    ollama_url = url or os.getenv("BIA_OLLAMA_URL", DEFAULT_OLLAMA_URL)
    ollama_model = model or os.getenv("BIA_OLLAMA_MODEL", DEFAULT_MODEL)
    response = None
    received_content = False

    try:
        response = http_client.post(
            ollama_url,
            json=_request_payload(
                question,
                knowledge_base,
                conversation,
                ollama_model,
                stream=True,
            ),
            timeout=timeout,
            stream=True,
        )
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            payload = json.loads(line)
            if payload.get("error"):
                raise BiaServiceError(str(payload["error"]))
            chunk = payload.get("response")
            if isinstance(chunk, str) and chunk:
                received_content = True
                yield chunk
    except BiaServiceError:
        raise
    except requests.RequestException as error:
        raise BiaServiceError(
            "Não foi possível conversar com o Ollama. Confirme se ele está aberto "
            f"e se o modelo '{ollama_model}' foi instalado."
        ) from error
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise BiaServiceError("O Ollama retornou uma resposta em formato inválido.") from error
    finally:
        if response is not None and hasattr(response, "close"):
            response.close()

    if not received_content:
        raise BiaServiceError("O modelo não retornou uma resposta válida.")
