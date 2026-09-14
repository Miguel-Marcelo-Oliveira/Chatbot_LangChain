"""
Utilitários de LLM compartilhados pelo projeto.

O `ConversationTokenBufferMemory` (Aula 02) precisa contar quantos tokens
cabem na janela de memória, e por padrão faz isso chamando
`llm.get_num_tokens_from_messages()`. Esse método padrão do LangChain tenta
baixar um tokenizador do Hugging Face e exige o pacote `transformers`
instalado — o que não faz sentido para um modelo que roda via Ollama Cloud
e gera o erro:

    ImportError: Could not import transformers python package.

Para evitar essa dependência pesada e desnecessária, sobrescrevemos a
contagem de tokens usando `tiktoken` — a mesma biblioteca já usada na
Aula 04 para medir tokens do system prompt.
"""
from typing import List

import tiktoken
from langchain_ollama import ChatOllama

_ENCODING = tiktoken.get_encoding("cl100k_base")


class ChatOllamaComContagemDeTokens(ChatOllama):
    """ChatOllama que conta tokens com tiktoken, sem depender do pacote `transformers`."""

    def get_token_ids(self, text: str) -> List[int]:
        return _ENCODING.encode(text)
