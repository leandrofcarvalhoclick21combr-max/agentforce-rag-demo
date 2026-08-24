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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

CALL_TRANSCRIPTS = [
    {
        "id": "Call-001",
        "text": "The client mentioned budget constraints for Q3 but loved the enterprise analytics demo.",
    },
    {
        "id": "Call-002",
        "text": "Customer complained about slow API response times during peak load testing.",
    },
    {
        "id": "Call-003",
        "text": "Discussions went great; the procurement team is ready to sign the contract next week.",
    },
]


def build_collection(embedder: SentenceTransformer) -> Any:
    """Indexa os exemplos em uma coleção ChromaDB que existe apenas em memória."""
    collection = chromadb.Client().get_or_create_collection(name="sales_calls")
    documents = [item["text"] for item in CALL_TRANSCRIPTS]
    identifiers = [item["id"] for item in CALL_TRANSCRIPTS]
    embeddings = embedder.encode(documents).tolist()
    collection.add(embeddings=embeddings, documents=documents, ids=identifiers)
    return collection


def run_rag(question: str, embedder: SentenceTransformer, collection: Any, client: genai.Client) -> str:
    """Recupera as duas evidências mais próximas e pede ao Gemini uma resposta fundamentada."""
    query_embedding = embedder.encode([question]).tolist()
    result = collection.query(query_embeddings=query_embedding, n_results=2)
    retrieved_texts = result["documents"][0]

    if not retrieved_texts:
        return "Nenhum contexto relevante foi encontrado para essa pergunta."

    context = "\n".join(f"- {text}" for text in retrieved_texts)
    prompt = (
        "Use somente o contexto fornecido para responder à pergunta de forma direta. "
        "Se o contexto não for suficiente, diga isso claramente.\n\n"
        f"Contexto:\n{context}\n\nPergunta: {question}"
    )

    print(f"\n--- Contexto recuperado ---\n{context}\n")
    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    except Exception as exc:
        return f"Não foi possível chamar o Gemini: {exc}"
    return response.text


def main() -> None:
    if not GEMINI_API_KEY:
        raise SystemExit(
            "GEMINI_API_KEY não foi encontrada. Copie .env.example para .env e adicione sua própria chave."
        )

    print("Carregando o modelo local de embeddings...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    collection = build_collection(embedder)
    client = genai.Client(api_key=GEMINI_API_KEY)

    question = "Is the customer worried about money or pricing?"
    answer = run_rag(question, embedder, collection, client)
    print(f"--- Resposta do Gemini ---\n{answer}")


if __name__ == "__main__":
    main()
