"""Lista os modelos Gemini disponíveis para a chave configurada localmente."""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit("GEMINI_API_KEY não foi encontrada. Configure o arquivo .env antes de continuar.")

client = genai.Client(api_key=api_key)
print("Modelos disponíveis:\n")
for model in client.models.list():
    print(f"- {model.name}")
