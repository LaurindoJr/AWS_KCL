# Aplicação de Biblioteca de Livros

Este projeto implementa uma aplicação simples de biblioteca de livros com frontend e backend desacoplados, orquestrados usando Docker Compose. A aplicação permite gerenciar livros (CRUD), aluguéis, upload de imagens de capa usando MinIO, processamento assíncrono de miniaturas com RabbitMQ, e logging de auditoria opcional usando AWS DynamoDB.

## Funcionalidades

- **Gerenciamento de Livros**: Criar, Ler, Atualizar e Deletar (CRUD) livros.
- **Gerenciamento de Aluguéis**: Alugar e devolver livros.
- **Uploads de Imagens**: Upload de imagens de capa de livros usando MinIO (compatível com S3).
- **Fila de Mensagens**: Processamento assíncrono de miniaturas de imagens usando RabbitMQ.
- **Logging de Auditoria**: Auditoria de ações (CRIAR, ATUALIZAR, DELETAR, ALUGAR, DEVOLVER) usando AWS DynamoDB (opcional).
- **Documentação Interativa da API**: API do backend documentada com Swagger UI.
- **Frontend Moderno**: Aplicação de Página Única (SPA) construída com React e TypeScript.

## Tecnologias Utilizadas

- **Backend**: Flask (Python), Gunicorn, Flasgger (Swagger UI), Psycopg2 (adaptador PostgreSQL), Boto3 (SDK AWS para MinIO/DynamoDB), Pika (cliente RabbitMQ), Pydantic (validação de dados).
- **Frontend**: React, TypeScript, React Router DOM, Bootstrap (para estilização).
- **Banco de Dados**: PostgreSQL 13 (banco relacional para dados da aplicação).
- **Armazenamento de Objetos**: MinIO (armazenamento compatível com S3 para imagens).
- **Corretor de Mensagens**: RabbitMQ (para tarefas assíncronas como processamento de imagens).
- **Banco de Auditoria**: AWS DynamoDB (para logs de auditoria - opcional).
- **Containerização**: Docker, Docker Compose.
- **Servidor Web**: Nginx (como proxy reverso para o frontend).

## Pré-requisitos

Antes de executar a aplicação, certifique-se de ter os seguintes softwares instalados:

- [**Docker**](https://docs.docker.com/get-docker/) (versão 20.10 ou superior)
- [**Docker Compose**](https://docs.docker.com/compose/install/) (versão 1.29 ou superior)
- [**Git**](https://git-scm.com/book/pt-br/v2/Primeiros-passos-Instalando-o-Git)

### Verificação dos Pré-requisitos

Execute os comandos abaixo para verificar se os pré-requisitos estão instalados:

```bash
docker --version
docker-compose --version
git --version
```

## Instruções de Configuração

### 1. Clonagem do Repositório

```bash
git clone https://github.com/seu-usuario/AWS_KCL.git
cd AWS_KCL
```

### 2. Configuração das Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha as variáveis de ambiente necessárias:

```bash
cp .env.example .env
```

**Variáveis obrigatórias:**
- Configurações do banco PostgreSQL
- Configurações do MinIO
- Configurações do RabbitMQ

**Variáveis opcionais (para auditoria):**
- Credenciais AWS para DynamoDB (se desejar usar logging de auditoria)

**Nota:** A auditoria com DynamoDB é opcional. Se você não fornecer credenciais AWS válidas, a aplicação funcionará normalmente, mas os logs de auditoria serão apenas impressos no console do backend.

### 3. Inicialização da Aplicação

Use o Docker Compose para construir as imagens e iniciar todos os serviços:

```bash
docker-compose up --build -d
```
ou

```bash
docker-compose up --build
```
O sinalizador `-d` executa os containers em modo detached (em segundo plano).

A inicialização pode levar alguns minutos na primeira execução, especialmente durante o build das imagens.

### 4. Verificação da Inicialização

Verifique se todos os containers estão rodando:

```bash
docker ps
```

Você deve ver 6 containers em execução:
- `nginx_frontend`
- `flask_app`
- `postgres_db`
- `minio_storage`
- `rabbitmq_broker`
- `python_worker`

### 5. Inicialização do Banco de Dados

O serviço `db` executa automaticamente o script `backend/init.sql` na primeira execução para criar as tabelas necessárias (`books` e `rentals`).

## Acesso à Aplicação

- **Frontend (Aplicação React)**: Abra seu navegador web e acesse `http://localhost:8080`
- **Swagger UI (Documentação da API do Backend)**: Acesse `http://localhost:5000/apidocs` para ver todos os endpoints da API e testá-los interativamente
- **MinIO Console**: Acesse `http://localhost:9001` (usuário: `minioadmin`, senha: `miniopassword`)
- **RabbitMQ Management**: Acesse `http://localhost:15672` (usuário: `guest`, senha: `guest`)

## Uso da Aplicação

### Gerenciamento de Livros

1. Acesse `http://localhost:8080` no seu navegador
2. Visualize a lista de livros existentes
3. Clique em "➕ Novo livro" para adicionar um novo livro
4. Preencha os campos obrigatórios: Código, Título, Autor
5. Opcionalmente, adicione um resumo e uma imagem de capa
6. Clique em "Salvar" para criar o livro
7. Use os botões "Ver" para visualizar detalhes e "Excluir" para remover livros

### API Endpoints Principais

- `GET /api/books` - Listar todos os livros
- `POST /api/books` - Criar um novo livro
- `GET /api/books/{id}` - Obter detalhes de um livro específico
- `PUT /api/books/{id}` - Atualizar um livro
- `DELETE /api/books/{id}` - Deletar um livro
- `POST /api/rentals` - Alugar um livro
- `PUT /api/rentals/{id}/return` - Devolver um livro

## Testes

### Testes E2E com Cypress

Para executar os testes end-to-end (requer Node.js e Cypress instalados localmente):

```bash
cd frontend
npm install
npm run cypress:run
```

### Testes da API

Use o Swagger UI em `http://localhost:5000/apidocs` para testar os endpoints da API interativamente.

## Solução de Problemas

### Problemas Comuns

- **`Host is unreachable` ou `500 Internal Server Error`**:
  - Verifique se todos os containers estão rodando: `docker ps`
  - Tente limpar os serviços do Docker Compose e reconstruir: `docker-compose down --volumes` seguido de `docker-compose up --build -d`
  - Verifique os logs de serviços individuais: `docker logs <nome_do_servico>`

- **`ModuleNotFoundError` durante o build do backend**:
  - Certifique-se de que `backend/requirements.txt` está formatado corretamente e contém todas as dependências necessárias

- **Erros do DynamoDB**:
  - Verifique as credenciais AWS no arquivo `.env`
  - Certifique-se de que a tabela `DDB_AUDIT` existe na sua conta AWS e as credenciais fornecidas têm permissões de escrita

- **Portas ocupadas**:
  - Se as portas 8080, 5000, 5432, 9000, 9001, 5672 ou 15672 estiverem em uso, modifique o arquivo `docker-compose.yml` para usar portas diferentes

### Logs e Debug

Para visualizar logs de um serviço específico:

```bash
docker logs flask_app
docker logs postgres_db
docker logs minio_storage
```

Para visualizar logs de todos os serviços:

```bash
docker-compose logs
```

## Desenvolvimento Local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Arquitetura

A aplicação segue uma arquitetura de microsserviços com os seguintes componentes:

- **Frontend**: SPA React servida pelo Nginx
- **Backend**: API REST Flask com documentação Swagger
- **Banco de Dados**: PostgreSQL para dados persistentes
- **Armazenamento**: MinIO para arquivos estáticos (imagens)
- **Fila**: RabbitMQ para processamento assíncrono
- **Worker**: Serviço Python para processamento de imagens
- **Auditoria**: DynamoDB para logs (opcional)





