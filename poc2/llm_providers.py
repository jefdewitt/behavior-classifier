"""Chat-model providers for the POC 2 experiment runner.

Each provider exposes the same `chat()` call, so the runner's prompts, agent sequence, and
evaluation stay identical across models. A provider returns raw text, or JSON text matching
`response_model` when one is given; the runner validates it.
"""

from typing import Any, Protocol

from pydantic import BaseModel


class ChatProvider(Protocol):
    name: str
    model: str
    options: dict[str, Any]

    def chat(self, system: str, user: str, response_model: type[BaseModel] | None = None) -> str: ...


class OllamaProvider:
    """Local model via Ollama. Deterministic: temperature 0 with a fixed seed."""

    name = "ollama"
    default_model = "llama3.2"

    def __init__(self, model: str | None = None) -> None:
        from ollama import Client

        self.model = model or self.default_model
        self.options = {"temperature": 0, "seed": 42}
        self._client = Client()

    def chat(self, system: str, user: str, response_model: type[BaseModel] | None = None) -> str:
        response = self._client.chat(
            model=self.model,
            options=self.options,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            format=response_model.model_json_schema() if response_model else None,
        )
        return response["message"]["content"]


class AnthropicProvider:
    """Hosted Claude model via the Anthropic API.

    Claude Opus 5.5 rejects temperature and seed, and its adaptive thinking cannot be disabled;
    effort is the only sampling control, so it is fixed here and recorded with the results.
    Server-side refusal fallbacks are deliberately not enabled: a fallback would answer with a
    different model and break the controlled model comparison. A refusal raises instead.
    """

    name = "anthropic"
    default_model = "claude-opus-5-5"

    def __init__(self, model: str | None = None) -> None:
        import anthropic
        from dotenv import load_dotenv

        load_dotenv()
        self.model = model or self.default_model
        self.options = {"effort": "high", "max_tokens": 16000}
        self._client = anthropic.Anthropic(max_retries=5)

    def chat(self, system: str, user: str, response_model: type[BaseModel] | None = None) -> str:
        request = {
            "model": self.model,
            "max_tokens": self.options["max_tokens"],
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": self.options["effort"]},
        }
        if response_model:
            response = self._client.messages.parse(**request, output_format=response_model)
        else:
            response = self._client.messages.create(**request)

        if response.stop_reason == "refusal":
            category = response.stop_details.category if response.stop_details else None
            raise RuntimeError(f"{self.model} refused the request (category: {category}, id: {response._request_id})")
        if response.stop_reason == "max_tokens":
            raise RuntimeError(f"{self.model} hit max_tokens before finishing (id: {response._request_id})")

        if response_model:
            return response.parsed_output.model_dump_json()
        return "".join(block.text for block in response.content if block.type == "text")


PROVIDERS: dict[str, type[OllamaProvider] | type[AnthropicProvider]] = {
    OllamaProvider.name: OllamaProvider,
    AnthropicProvider.name: AnthropicProvider,
}


def create_provider(name: str, model: str | None = None) -> ChatProvider:
    return PROVIDERS[name](model)
