# Crazy Punishment Server — Render

Arquivos:
- server.py -> servidor Flask
- templates/dashboard.html -> painel roxo para consultar PIN
- requirements.txt -> dependências
- render.yaml -> configuração opcional do Render
- .python-version -> Python 3.13
- reports/ -> pasta usada para testes locais

## Render
Crie um Web Service apontando para este projeto.

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn server:app

Depois de publicar, o Render fornecerá uma URL parecida com:
https://seu-nome.onrender.com

No scanner, coloque somente o endereço base:
SERVER_URL = "https://seu-nome.onrender.com"

Não coloque /api/submit no SERVER_URL.

IMPORTANTE:
A pasta reports é adequada para teste. Em hospedagem sem armazenamento persistente, os arquivos podem ser perdidos após reinício/deploy. Para uso permanente, troque o armazenamento por banco de dados ou armazenamento persistente.
