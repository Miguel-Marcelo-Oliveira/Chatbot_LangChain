"""
Demonstração de "context rot" (Aula 04): a MESMA sequência de turnos é
rodada duas vezes, variando só o limite de tokens da memória — mostra na
prática a degradação quando o histórico é descartado cedo demais.
"""
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ConversationTokenBufferMemory
from langchain_classic.chains import ConversationChain

from llm_utils import ChatOllamaComContagemDeTokens
from prompts import SYSTEM_PROMPT_CHAT

load_dotenv()
MODELO = "gemma4:cloud"

TEMPLATE = (
    SYSTEM_PROMPT_CHAT
    + "\n\nHistórico da conversa:\n{history}\n\nUsuário: {input}\nAssistente:"
)
PROMPT = PromptTemplate(input_variables=["history", "input"], template=TEMPLATE)

# Mesma conversa nas duas rodadas — só o limite de tokens da memória muda
TURNOS = [
    "Meu nome é Beatriz e preciso estudar para a prova de História.",
    "A prova é sobre a Revolução Industrial, daqui a 10 dias.",
    "Tenho 45 minutos por dia disponíveis, à noite.",
    "Tenho dificuldade em lembrar datas e nomes de eventos.",
    "Qual é a minha matéria e a minha maior dificuldade mesmo?",
]


def rodar_conversa(max_token_limit: int) -> str:
    """Roda os TURNOS com um limite de tokens específico e devolve a última resposta."""
    # ChatOllamaComContagemDeTokens (llm_utils.py) conta tokens com tiktoken —
    # evita o ImportError do metodo padrão do LangChain (exigiria `transformers`).
    llm = ChatOllamaComContagemDeTokens(model=MODELO, temperature=0.3)
    memoria = ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=max_token_limit,
        memory_key="history",
        return_messages=False,
    )
    chat = ConversationChain(llm=llm, memory=memoria, prompt=PROMPT, verbose=False)

    ultima_resposta = ""
    for pergunta in TURNOS:
        ultima_resposta = chat.predict(input=pergunta)
    return ultima_resposta


if __name__ == "__main__":
    print("=== Memória com limite pequeno (100 tokens) ===")
    print("Espera-se: o nome, a matéria e a dificuldade, ditos no início, já saíram")
    print("da janela — a resposta final tende a 'não saber' ou inventar.\n")
    resposta_pequena = rodar_conversa(max_token_limit=100)
    print(resposta_pequena)

    print("\n=== Memória com o limite do projeto (1000 tokens) ===")
    print("Espera-se: o histórico inteiro cabe na janela — a resposta final recupera")
    print("corretamente a matéria e a dificuldade relatada.\n")
    resposta_projeto = rodar_conversa(max_token_limit=1000)
    print(resposta_projeto)

    print(
        "\nConclusão: o mesmo prompt e a mesma sequência de turnos produzem respostas "
        "diferentes dependendo só do quanto de contexto a memória consegue reter — "
        "essa é a evidência de context rot que justifica o limite de 1000 tokens "
        "escolhido para este projeto (ver README.md)."
    )
