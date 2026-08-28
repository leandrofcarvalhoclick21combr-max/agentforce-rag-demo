"""Demo educacional de RAG com ChromaDB, embeddings locais e Gemini.

Nunca coloque a chave de API neste arquivo. Configure GEMINI_API_KEY no arquivo
.env local (criado a partir de .env.example) ou como variável de ambiente.
"""

import os
from typing import Any

import chromadb
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
RESULTS_PER_QUERY = 1

# OFFLINE PREPARATION - LOAD
#
# Estas três calls são a base de conhecimento do demo. Em um caso real, elas
# poderiam vir de um CRM, de arquivos ou de uma transcrição. Aqui cada call é
# curta e já representa um chunk (um trecho com uma ideia completa):
# - Call-001 responde perguntas sobre orçamento e a demonstração de analytics;
# - Call-002 responde perguntas sobre lentidão da API em testes de pico;
# - Call-003 responde quem assinará o contrato e quando.
CALL_TRANSCRIPTS = [
    {
        "id": "Call-001",
        "text": "O cliente mencionou restrições de orçamento para o terceiro trimestre, mas adorou a demonstração de analytics empresarial.",
    },
    {
        "id": "Call-002",
        "text": "O cliente reclamou de lentidão no tempo de resposta da API durante testes de carga de pico.",
    },
    {
        "id": "Call-003",
        "text": "As conversas foram muito bem; a equipe de compras está pronta para assinar o contrato na próxima semana.",
    },
]


def build_collection(embedder: SentenceTransformer) -> Any:
    """Executa Load, Chunk, Embed e Store em uma coleção ChromaDB em memória."""
    collection = chromadb.Client().get_or_create_collection(name="sales_calls")

    # LOAD + CHUNK: cada texto curto abaixo já é um chunk completo. Por exemplo,
    # a Call-001 mantém juntas a restrição de orçamento e a reação positiva à
    # demonstração. Em documentos grandes, esta seria a etapa de dividi-los em
    # seções coerentes antes de criar os vetores.
    documents = [item["text"] for item in CALL_TRANSCRIPTS]
    identifiers = [item["id"] for item in CALL_TRANSCRIPTS]

    # EMBED: o texto de cada chunk vira um vetor numérico de significado. Esse
    # vetor não é enviado ao Gemini e não é uma resposta; ele permite que
    # "restrição de orçamento" seja aproximada de perguntas sobre orçamento,
    # mesmo quando a frase não é exatamente igual à da call.
    embeddings = embedder.encode(documents).tolist()

    # STORE: ChromaDB armazena o vetor junto do texto original e do id. Na busca,
    # ele compara vetores, mas devolve o texto original como evidência.
    collection.add(embeddings=embeddings, documents=documents, ids=identifiers)
    return collection


def run_rag(question: str, embedder: SentenceTransformer, collection: Any, client: genai.Client) -> str:
    """Recupera a evidência mais próxima e gera uma resposta fundamentada."""

    # ONLINE USAGE - QUERY: por exemplo, a pessoa pode perguntar:
    # "Que restrição de orçamento o cliente mencionou?"
    #
    # EMBED DA QUERY: usamos o mesmo modelo dos documentos para transformar a
    # pergunta em vetor. Assim, ela pode ser comparada de maneira semântica com
    # os vetores armazenados durante a preparação offline.
    query_embedding = embedder.encode([question]).tolist()

    # RETRIEVE: com RESULTS_PER_QUERY = 1, o demo traz uma única evidência para
    # tornar a demonstração fácil de acompanhar. Para a pergunta de orçamento,
    # a expectativa é recuperar apenas a Call-001. Para uma aula em que a
    # pergunta cruza duas calls, altere a constante para 2.
    result = collection.query(query_embeddings=query_embedding, n_results=RESULTS_PER_QUERY)
    retrieved_texts = result["documents"][0]

    if not retrieved_texts:
        return "Nenhum contexto relevante foi encontrado para essa pergunta."

    # AUGMENTED PROMPT: o contexto abaixo é o texto real recuperado - por
    # exemplo, a Call-002 para uma pergunta sobre lentidão em testes de carga.
    # O Gemini recebe a pergunta junto dessa evidência, e não as três calls.
    context = "\n".join(f"- {text}" for text in retrieved_texts)
    prompt = (
        "Use somente o contexto fornecido para responder à pergunta de forma direta. "
        "Se o contexto não for suficiente, diga isso claramente.\n\n"
        f"Contexto:\n{context}\n\nPergunta: {question}"
    )

    print(f"\n--- Contexto recuperado ---\n{context}\n")
    try:
        # GENERATE: uma nova sessão por pergunta envia o prompt aumentado ao
        # Gemini e impede que o contexto de uma resposta anterior seja
        # reutilizado na próxima demonstração.
        chat = client.chats.create(model=GEMINI_MODEL)
        response = chat.send_message(prompt)
    except Exception as exc:
        return f"Não foi possível chamar o Gemini: {exc}"
    # ANSWER: somente o texto gerado é devolvido ao terminal. Se a pessoa pedir
    # "Qual é o e-mail do cliente?", o dado não existe nas calls; o guardrail
    # do prompt orienta o modelo a declarar essa ausência, sem inventar e-mail.
    return response.text


def main() -> None:
    if not GEMINI_API_KEY:
        raise SystemExit(
            "GEMINI_API_KEY não foi encontrada. Copie .env.example para .env e adicione sua própria chave."
        )

    print("Carregando o modelo local de embeddings...")
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    collection = build_collection(embedder)
    client = genai.Client(api_key=GEMINI_API_KEY)

    print("\nFaça perguntas sobre as calls. Pressione Enter sem texto para encerrar.")
    while True:
        question = input("\nPergunta: ").strip()
        if not question:
            print("Demo encerrado.")
            break

        answer = run_rag(question, embedder, collection, client)
        print(f"--- Resposta do Gemini ---\n{answer}")


if __name__ == "__main__":
    main()
