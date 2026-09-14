# CKP01 — Chatbot Profissional · Assistente Pessoal de Estudos

**Prompt Engineering & Artificial Intelligence · FIAP · 2º Semestre 2026**

## Integrantes

| Nome                                        | RM     |
|---------------------------------------------|--------|
| Miguel Marcelo Alves Ramos de Oliveira      | 569467 |
| Felipe de Oliveira Doern                    | 568798 |
| Tom Stringasci Albuquerque Coelho de Morais | 568844 |
| Eric dos Santos Mendes da Silva             | 569528 |
| Ligia de Andrade Matheus                    | 568973 |

## Domínio

O domínio escolhido é **estudos e organização acadêmica**. O chatbot ("EstudaBot") atua como um
assistente pessoal de estudos: conversa com o usuário sobre a matéria que precisa estudar, seu nível
de domínio sobre o assunto e o tempo disponível, e sugere um plano de estudo — sem fazer a tarefa ou
a prova por ele.

**Por que esse domínio:** conversas de planejamento de estudo costumam ser curtas e focadas em um
objetivo imediato (a próxima prova, o próximo tópico) — o que importa de verdade é o que foi dito
*recentemente* (matéria atual, dificuldade relatada), não um histórico longo desde o início. Isso
favorece uma memória de janela fixa (`TokenBuffer`) em vez de guardar tudo ou pagar por um resumo a
cada turno.

**Usuários-alvo:** estudantes que precisam organizar o próprio tempo de estudo e entender por onde
começar — sem substituir professores, cursinhos ou material didático oficial.


## Requisitos atendidos

| Requisito | Status | Implementação |
|---|---|---|
| Pipeline LCEL | ✅| `app/chatbot.py` — `prompt \| llm_json \| PydanticOutputParser()` |
| ChatOllama | ✅ | `gemma4:cloud` via Ollama Cloud, chave em `.env` |
| ChatPromptTemplate | ✅ | `app/prompts.py` (system) + templates com variáveis em `app/chatbot.py` |
| Memória gerenciada | ✅ | `ConversationChain` + `ConversationTokenBufferMemory` (limite de 1000 tokens), contando tokens via `tiktoken` (`app/llm_utils.py`) |
| Pydantic v2 (≥4 campos) | ✅ | `PlanoDeEstudo` com 5 campos tipados em `app/schemas.py` |
| Context rot | ✅ | `app/context_rot.py` — compara memória com limite pequeno x limite do projeto |
| System prompt com persona | ✅ | `app/prompts.py`, com XML tagging (`<persona>`, `<restricoes>`, `<formato>`) |
| Domínio documentado | ✅ | Este README |

## Como executar (estado atual — terminal, sem Gradio ainda)

```bash
cp .env.example .env             # edite com sua OLLAMA_API_KEY 
pip install -r requirements.txt
python app/chatbot.py            # abre um menu:
                                 #   1) demonstração automática (5 turnos) + extração estruturada
                                 #   2) chat interativo contínuo no terminal
                                 #   3) opção 1 seguida da opção 2
python app/context_rot.py        # demonstração de degradação de memória (context rot)
```

> Rode os comandos a partir da raiz do projeto `python app/chatbot.py`  
> Abre um **menu interativo** (você escolhe 1, 2 ou 3).

## Observação técnica — contagem de tokens

O `ConversationTokenBufferMemory` precisa contar tokens para saber quando descartar mensagens
antigas. Por padrão, o LangChain faz isso com um método que depende do pacote `transformers` (baixa
um tokenizador do Hugging Face) — o que não faz sentido para um modelo rodando via Ollama Cloud e
gera `ImportError: Could not import transformers python package`.

Para evitar essa dependência pesada e o erro, `app/llm_utils.py` define uma pequena subclasse do
`ChatOllama` que conta tokens com `tiktoken` (a mesma biblioteca usada na Aula 04). Ela é usada em
`app/chatbot.py` e `app/context_rot.py` sempre que o LLM precisa ser combinado com o
`ConversationTokenBufferMemory`.

## Justificativa da memória

Escolhemos `ConversationTokenBufferMemory` com `max_token_limit=1000` (dentro da faixa 800–1500
pedida). O domínio tem conversas curtas e focadas em um objetivo de estudo pontual — o que precisa
sobreviver de um turno para o outro é o contexto recente (matéria atual, dificuldade relatada), não
o histórico inteiro desde a primeira mensagem. Por isso:

- **Buffer** (guarda tudo) seria desperdício: cresce sem necessidade em conversas curtas e pontuais.
- **Summary** (resume com o próprio LLM) paga uma chamada extra por turno, custo que não se justifica
  para conversas curtas como as desse domínio.
- **TokenBuffer** mantém uma janela recente e descarta automaticamente o que é mais antigo — barato e
  suficiente para o caso de uso.

Testamos com 5 turnos (ver `app/chatbot.py`) e o chatbot mantém coerência sobre a matéria e a
dificuldade do usuário dentro da janela de 1000 tokens.

## Sobre a seção "context rot"

`app/context_rot.py` roda a **mesma sequência de turnos** duas vezes, variando só o
`max_token_limit` da memória:

- **100 tokens** (bem pequeno): as primeiras informações (nome, matéria, dificuldade relatada) saem
  da janela rapidamente. Ao perguntar sobre elas no fim, a resposta perde precisão ou "esquece".
- **1000 tokens** (o limite escolhido pelo projeto): o histórico inteiro cabe na janela, e a resposta
  final recupera corretamente a matéria e a dificuldade relatadas no início da conversa.

Isso evidencia o trade-off central da aula: memória maior = mais fidelidade, memória menor = mais
barata — e o TokenBuffer permite escolher esse ponto explicitamente.
