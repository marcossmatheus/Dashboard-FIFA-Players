# FIFA Player Stats App

**Aplicação rodando ao vivo:** [https://fifa-app-vtln.onrender.com](https://fifa-app-vtln.onrender.com)

Uma aplicação web construída em **Python (Flask)** para exibir estatísticas, perfis detalhados e as últimas notícias de jogadores de futebol.

## 🚀 Funcionalidades

- **Dashboard Principal**: Lista os jogadores disponíveis, permitindo filtros por país e ordenação (idade, nome).
- **Perfil do Jogador**: Exibe os atributos do jogador, clube, idade e estatísticas detalhadas da temporada de 2026.
- **Notícias em Tempo Real**: Integração com o Google News (via RSS) para buscar as últimas notícias sobre o jogador automaticamente.
- **API**: Endpoints em JSON disponíveis para consumo dinâmico das informações no front-end.

## 📁 Estrutura do Projeto

- `app.py`: O servidor Flask principal que gerencia as rotas e a lógica da aplicação.
- `data/players.json`: Banco de dados estático contendo as informações de todos os jogadores.
- `scripts/`: Scripts utilitários em Python (`data_generator.py` e `add_stats_2026.py`) usados para gerar e enriquecer a base de dados (`players.json`).
- `templates/` & `static/`: Arquivos front-end (HTML, CSS e JavaScript).

## 🛠️ Como rodar o projeto localmente

Siga os passos abaixo para executar a aplicação na sua máquina:

### 1. Pré-requisitos
Certifique-se de ter o [Python 3](https://www.python.org/downloads/) instalado.

### 2. Entre na pasta do projeto
No seu terminal, navegue até a raiz do projeto (onde está o arquivo `app.py`).

### 3. Crie um ambiente virtual (Recomendado)
Criar um ambiente virtual isola as dependências do projeto do resto do seu sistema.
```bash
python3 -m venv .venv
```
- **Ative o ambiente (macOS/Linux):**
  ```bash
  source .venv/bin/activate
  ```
- **Ative o ambiente (Windows):**
  ```bash
  .venv\Scripts\activate
  ```

### 4. Instale as dependências
Com o ambiente ativado, instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 5. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível no seu navegador no endereço: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🌐 Deploy (Nuvem)
O projeto já conta com o `gunicorn` em `requirements.txt`, pronto para ser hospedado em plataformas modernas como Render, Heroku ou Railway de forma nativa.
