# pln-rag-normas-estruturais

Chatbot RAG para consulta de normas brasileiras de Engenharia Estrutural com citações normativas e avaliação experimental.

## Como rodar o projeto manualmente (macOS/Linux)

### 1. Crie o ambiente virtual

Na pasta raiz do projeto, crie um ambiente isolado (virtual environment) chamado `.venv`:

```bash
python3 -m venv .venv
```

### 2. Ative o ambiente virtual

Ative o ambiente para que o terminal passe a utilizar o Python e pacotes locais:

```bash
source .venv/bin/activate
```

_(O prefixo `(.venv)` deverá aparecer no início do seu terminal indicando sucesso)_

### 3. Instale as dependências

Certifique-se de que o ambiente está ativado e instale as bibliotecas requeridas:

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` baseado no modelo disponível no repositório:

```bash
cp .env.example .env
```

Edite o arquivo `.env` recém-criado, incluindo a sua chave de API do Gemini:

```env
GEMINI_API_KEY=sua_chave_secreta_aqui
```

### 5. Execute o notebook do projeto

Executre o notebook com o comando:

```bash
jupyter notebook notebooks/rag_normas.ipynb
```

### 6. Execute o projeto

Finalmente, suba a aplicação com o Streamlit:

```bash
streamlit run app.py
```

O seu navegador principal abrirá automaticamente no endereço `http://localhost:8501`. Para interromper o servidor a qualquer momento, retorne ao terminal e aperte `Ctrl + C`.
