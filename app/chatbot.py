"""
Chatbot do domínio "Assistente Pessoal de Estudos" — CKP01.

Arquitetura de 2 chains, como ensinado na Aula 03:
1) ConversationChain + memória (TokenBuffer)      -> conversa livre com o usuário
2) Pipeline LCEL (prompt | llm | PydanticOutputParser) -> saída estruturada (plano de estudo)

Ao rodar `python chatbot.py`, um menu oferece 3 opções:
    1) Rodar os testes automáticos (demonstração com 5 turnos + extração estruturada)
    2) Conversar com o chatbot (chat contínuo, você decide quando encerrar)
    3) Opção 1 e, em seguida, a opção 2
"""
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.memory import ConversationTokenBufferMemory
from langchain_classic.chains import ConversationChain

from llm_utils import ChatOllamaComContagemDeTokens
from prompts import SYSTEM_PROMPT_CHAT, SYSTEM_PROMPT_EXTRACAO
from schemas import PlanoDeEstudo

load_dotenv()  # lê o .env (OLLAMA_HOST e OLLAMA_API_KEY)

MODELO = "gemma4:cloud"  # modelo exigido pelo CKP01 — via Ollama Cloud


def montar_chat() -> ConversationChain:
    """Monta a chain de conversa com memória gerenciada (TokenBuffer, 1000 tokens)."""
    # ChatOllamaComContagemDeTokens (llm_utils.py) conta tokens com tiktoken —
    # o ChatOllama puro cairia no metodo padrão do LangChain, que exige o
    # pacote `transformers` e não é necessário aqui.
    llm = ChatOllamaComContagemDeTokens(model=MODELO, temperature=0.7)

    # Template customizado — precisa conter {history} e {input}
    template = (
        SYSTEM_PROMPT_CHAT
        + "\n\nHistórico da conversa:\n{history}\n\nUsuário: {input}\nAssistente:"
    )
    prompt = PromptTemplate(input_variables=["history", "input"], template=template)

    # TokenBuffer: janela de 1000 tokens — justificativa completa no README.md
    memoria = ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=1000,
        memory_key="history",
        return_messages=False,
    )

    return ConversationChain(llm=llm, memory=memoria, prompt=prompt, verbose=False)


def montar_extrator():
    """Monta a chain LCEL de extração estruturada, validada com Pydantic v2."""
    parser = PydanticOutputParser(pydantic_object=PlanoDeEstudo)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_EXTRACAO),
            ("human", "{pedido}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    # format="json" garante JSON válido; o PydanticOutputParser garante o schema certo
    # (esta chain não usa memória, então não precisa do contador de tokens especial)
    llm_json = ChatOllama(model=MODELO, format="json", temperature=0.3)

    return prompt | llm_json | parser


def rodar_demo() -> None:
    """Demonstração automática: 5 turnos de conversa + 1 extração estruturada."""
    print("=== Conversa com memória gerenciada (5 turnos) ===\n")
    chat = montar_chat()

    turnos = [
        "Oi! Preciso estudar para uma prova de matemática em 2 semanas.",
        "O assunto é funções quadráticas.",
        "Tenho 1 hora por dia disponível para estudar.",
        "Já estudei o básico, mas erro muito nos exercícios de vértice da parábola.",
        "Lembra qual é a matéria e a minha dificuldade mesmo?",
    ]
    for pergunta in turnos:
        resposta = chat.predict(input=pergunta)
        print(f"Usuário: {pergunta}\nEstudaBot: {resposta}\n")

    print("\n=== Saída estruturada com Pydantic v2 ===\n")
    extrator = montar_extrator()
    pedido = "Quero montar um plano de estudos de Química, nível avançado, para revisar antes do vestibular."
    try:
        plano = extrator.invoke({"pedido": pedido})
        print(type(plano))
        print(plano.model_dump())
    except Exception as erro:
        print(f"Erro ao validar o plano: {erro}")


def modo_interativo() -> None:
    """Chat contínuo no terminal — a mesma memória vale para toda a sessão."""
    chat = montar_chat()
    print("=== EstudaBot — modo interativo (digite 'sair' para encerrar) ===\n")
    while True:
        pergunta = input("Você: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("EstudaBot: Até a próxima sessão de estudos!")
            break
        if not pergunta:
            continue
        resposta = chat.predict(input=pergunta)
        print(f"EstudaBot: {resposta}\n")


def exibir_menu() -> None:
    """Mostra o menu principal com as 3 opções do chatbot."""
    print("=== EstudaBot — Assistente Pessoal de Estudos ===")
    print("1. Rodar os testes automáticos (5 turnos + extração estruturada)")
    print("2. Conversar com o chatbot (encerra só quando você quiser)")
    print("3. Opção 1 e, em seguida, a opção 2")


if __name__ == "__main__":
    exibir_menu()
    escolha = input("Escolha uma opção (1/2/3): ").strip()

    if escolha == "1":
        rodar_demo()
    elif escolha == "2":
        modo_interativo()
    elif escolha == "3":
        rodar_demo()
        print("\n--- Testes automáticos concluídos. Iniciando o chat interativo. ---\n")
        modo_interativo()
    else:
        print("Opção inválida. Encerrando.")