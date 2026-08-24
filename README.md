# Demo educacional de RAG com Gemini e ChromaDB

Um exemplo mínimo de **Retrieval-Augmented Generation (RAG)** para alunos. O projeto cria embeddings localmente, guarda três transcrições em memória no ChromaDB, recupera as mais próximas da pergunta e envia somente esse contexto ao Gemini para gerar a resposta.

## O que você vai aprender

1. **Load:** trazer textos para o projeto.
2. **Embed:** converter textos e perguntas em vetores semânticos.
3. **Retrieve:** encontrar os trechos mais próximos da pergunta.
4. **Augment:** juntar contexto recuperado e instruções em um prompt.
5. **Generate:** produzir uma resposta fundamentada no contexto.

## Antes de começar

- Python 3.10 ou superior.
- Uma conta Google.
- Uma chave pessoal do Gemini API. Cada aluno deve criar e usar a sua; nunca compartilhe uma chave e nunca faça commit dela.

## Criar sua chave no Google AI Studio

1. Acesse [Google AI Studio - API keys](https://aistudio.google.com/apikey) com sua conta Google.
2. Clique em **Create API key** e siga o diálogo para criar ou escolher um projeto.
3. Copie a chave uma única vez e guarde-a em local seguro.
4. Na pasta do projeto, copie `.env.example` para `.env`.
5. No arquivo `.env`, substitua `cole_sua_chave_aqui` pela sua chave, sem aspas.

O Google recomenda definir a chave como variável de ambiente e permite administrá-la no AI Studio. Se uma chave for exposta, crie outra e revogue a antiga imediatamente. Consulte a [documentação oficial de chaves](https://ai.google.dev/gemini-api/docs/api-key) e o [guia de início rápido](https://ai.google.dev/gemini-api/docs/get-started).

> O arquivo `.env` é ignorado pelo Git. Nunca cole uma chave real em `rag_demo.py`, no README, em issues ou em commits.

## Instalar e executar

No macOS ou Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env e inclua a sua GEMINI_API_KEY
python rag_demo.py
```

No Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edite .env e inclua a sua GEMINI_API_KEY
python rag_demo.py
```

Na primeira execução, o `sentence-transformers` baixa o modelo de embeddings. Em seguida, o programa mostra o contexto recuperado e a resposta do Gemini.

## Experimente outras perguntas

No arquivo `rag_demo.py`, altere a variável `question` e execute de novo. Por exemplo:

```python
question = "What problem did the customer report during peak load?"
```

Observe quais transcrições aparecem em **Contexto recuperado**. Se a evidência não for a esperada, o problema está na fonte, no chunking ou no retrieval - não necessariamente no modelo generativo.

## Estrutura

```text
.
├── rag_demo.py       # fluxo RAG completo
├── list_models.py    # lista os modelos liberados para sua chave
├── .env.example      # configuração de exemplo, sem segredo
├── requirements.txt  # dependências Python
└── README.md
```

## Segurança e custo

- Use uma chave por pessoa e revogue chaves que tenham sido compartilhadas ou expostas.
- Acompanhe consumo e limites no dashboard do Google AI Studio.
- O modelo padrão do exemplo é `gemini-3.6-flash`, validado no demo. Caso ele não esteja disponível para sua conta, execute `python list_models.py`, escolha um modelo listado e atualize `GEMINI_MODEL` no arquivo `.env`.

## Próximos passos

Para transformar este demo em um projeto mais próximo de produção, adicione metadados e filtros, persistência no banco vetorial, chunking para documentos longos, citações de fonte, testes com perguntas reais e observabilidade de custo, latência e qualidade.
