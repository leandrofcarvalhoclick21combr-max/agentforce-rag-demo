# Demo educacional de RAG com Gemini e ChromaDB

Um exemplo mínimo de **Retrieval-Augmented Generation (RAG)** para alunos. O projeto cria embeddings localmente, guarda três transcrições em memória no ChromaDB, recupera as mais próximas da pergunta e envia somente esse contexto ao Gemini para gerar a resposta.

## O que você vai aprender

1. **Load:** trazer textos para o projeto.
2. **Embed:** converter textos e perguntas em vetores semânticos.
3. **Retrieve:** encontrar os trechos mais próximos da pergunta.
4. **Augment:** juntar contexto recuperado e instruções em um prompt.
5. **Generate:** produzir uma resposta fundamentada no contexto com a API Gemini.

## Antes de começar

- Python 3.10 ou superior.
- Uma conta Google.
- Uma chave pessoal da API Gemini. Cada aluno deve criar e usar a sua; nunca compartilhe uma chave e nunca faça commit dela.

## Criar sua chave no Google AI Studio

1. Acesse [Google AI Studio - API keys](https://aistudio.google.com/apikey) com sua conta Google.
2. Clique em **Create API key** e siga o diálogo para criar ou escolher um projeto.
3. Copie a chave uma única vez e guarde-a em local seguro.
4. Na pasta do projeto, copie `.env.example` para `.env`.
5. No arquivo `.env`, substitua `cole_sua_chave_aqui` pela sua chave, sem aspas. Mantenha `GEMINI_MODEL=gemini-3.6-flash`.

Se uma chave for exposta, crie outra e revogue a antiga imediatamente. O arquivo `.env` é uma forma local de defini-la para este demo. Consulte a [documentação de chaves](https://ai.google.dev/gemini-api/docs/api-key) e o [guia de início rápido](https://ai.google.dev/gemini-api/docs/get-started).

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

Na primeira execução, o `sentence-transformers` baixa o modelo de embeddings multilíngue. Em seguida, o programa mostra o contexto recuperado e a resposta do Gemini.

## Experimente perguntas sobre as calls

Depois de executar `python rag_demo.py`, escreva uma pergunta em português no terminal. O programa continua ativo para você testar várias perguntas; pressione Enter sem texto para encerrar.

O demo usa um modelo de embeddings multilíngue e três calls em português. Exemplos que fazem sentido para a base atual:

```text
Que restrição de orçamento o cliente mencionou?
Do que o cliente gostou na demonstração de analytics?
Que problema técnico aconteceu durante os testes de carga de pico?
Quem está pronto para assinar o contrato e quando?
Que evidências apontam ao mesmo tempo uma restrição de orçamento e a assinatura próxima de um contrato?
Qual é o e-mail do cliente?
```

As calls atuais só tratam de orçamento no terceiro trimestre, uma demonstração de analytics, lentidão de API em testes de pico e próxima assinatura de contrato. A última pergunta é propositalmente sem resposta: o agente deve informar que o contexto não contém o e-mail. Evite perguntas sobre previsão de vendas, dados pessoais, detalhes de produto não citados ou informações externas. O RAG só pode responder bem quando há evidência na base.

Observe qual transcrição aparece em **Contexto recuperado**. O demo recupera uma call por pergunta, deixando a relação entre a pergunta, a evidência e a resposta mais clara. Para demonstrar uma pergunta que precisa cruzar duas calls, altere `RESULTS_PER_QUERY = 1` para `RESULTS_PER_QUERY = 2` no início de `rag_demo.py`.

## Por que essas perguntas funcionam

Cada pergunta abaixo tem evidência explícita em uma das três calls. O RAG não procura na internet nem conhece dados que não estejam na base: ele transforma a pergunta em vetor, recupera a call semanticamente mais próxima e envia essa call junto da pergunta ao Gemini.

| Pergunta | Evidência recuperada | Resposta que o contexto permite |
| --- | --- | --- |
| Que restrição de orçamento o cliente mencionou? | Call-001 | Há restrições de orçamento para o terceiro trimestre. |
| Do que o cliente gostou na demonstração de analytics? | Call-001 | Da demonstração de analytics empresarial. |
| Que problema técnico aconteceu durante os testes de carga de pico? | Call-002 | Houve lentidão no tempo de resposta da API. |
| Quem está pronto para assinar o contrato e quando? | Call-003 | A equipe de compras está pronta para assinar na próxima semana. |
| Qual é o e-mail do cliente? | Nenhuma call contém esse dado | O agente deve informar que não há e-mail disponível nas calls. |

O último caso é uma parte importante da demonstração: uma resposta segura reconhece que falta evidência, em vez de inventar uma informação. Os comentários em `rag_demo.py` mostram o mesmo caminho, etapa por etapa: **Load → Chunk → Embed → Store** e **Query → Embed → Retrieve → Augmented Prompt → Generate → Answer**.

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
- O modelo padrão do exemplo é `gemini-3.6-flash`. Caso ele não esteja disponível para sua conta, execute `python list_models.py`, escolha um modelo de texto listado e atualize `GEMINI_MODEL` no `.env`.

## Próximos passos

Para transformar este demo em um projeto mais próximo de produção, adicione metadados e filtros, persistência no banco vetorial, chunking para documentos longos, citações de fonte, testes com perguntas reais e observabilidade de custo, latência e qualidade.
