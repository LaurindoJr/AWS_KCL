# 📚 Biblioteca na Nuvem – KCL (Versão Docker)

Este projeto é a segunda versão da "Biblioteca na Nuvem", reimplementada para rodar em um ambiente totalmente containerizado utilizando Docker e Docker Compose.

A arquitetura original baseada em serviços gerenciados da AWS (RDS, S3, SQS) foi migrada para serviços auto-hospedados (self-hosted) em contêineres, conforme especificado no Trabalho Prático 2.

---

## 🏛️ Arquitetura

A aplicação é orquestrada pelo Docker Compose e consiste nos seguintes serviços:

-   **`app`**: A aplicação web em **Flask**, responsável pela interface do usuário e lógica de negócio.
-   **`worker`**: Um processador de tarefas em Python que consome mensagens para processamento assíncrono de imagens (geração de thumbnails).
-   **`db`**: Um banco de dados **PostgreSQL** para armazenar os dados de livros e aluguéis (substituindo o Amazon RDS).
-   **`minio`**: Um serviço de armazenamento de objetos compatível com a API S3, para guardar as imagens dos livros (substituindo o Amazon S3).
-   **`rabbitmq`**: Um message broker para gerenciar a fila de processamento de imagens (substituindo o Amazon SQS).
-   **`dynamodb`**: O único serviço externo mantido, o **Amazon DynamoDB**, continua sendo utilizado para logs de auditoria e status de processamento, conforme o requisito.

![Arquitetura Docker](https://i.imgur.com/your-architecture-diagram.png) 
*(Substitua com um diagrama da nova arquitetura, se desejar)*

---

## ⚙️ Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚀 Executando a Aplicação

Siga os passos abaixo para colocar toda a infraestrutura no ar.

### 1. Configure as Variáveis de Ambiente

Primeiro, crie o seu arquivo de configuração a partir do exemplo fornecido.

Abra o arquivo `.env` e **preencha as credenciais da AWS** (`AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`). O usuário do IAM correspondente a estas credenciais precisa de permissão de escrita (`PutItem`, `UpdateItem`) nas tabelas do DynamoDB (`kcl-AuditLogs` e `kcl-ProcessingStatus`).

As demais variáveis (Postgres, MinIO, RabbitMQ) já possuem valores padrão e não precisam ser alteradas para o ambiente de desenvolvimento.

### 2. Construa as Imagens e Inicie os Serviços

Com o Docker em execução, execute o seguinte comando na raiz do projeto:

```bash
docker compose up --build
```

Este comando irá:
- Baixar as imagens oficiais do Postgres, MinIO e RabbitMQ.
- Construir as imagens customizadas para a `app` e o `worker` a partir dos Dockerfiles.
- Iniciar todos os contêineres em uma rede compartilhada.
- Montar volumes para persistir os dados do Postgres e do MinIO.

Após a execução, você terá todo o ambiente rodando localmente.

### 3. Acessando os Serviços

-   **Aplicação Principal (Biblioteca)**
    -   URL: [http://localhost:5000](http://localhost:5000)

-   **Console do MinIO (Armazenamento de Objetos)**
    -   URL: [http://localhost:9001](http://localhost:9001)
    -   **Usuário:** `minioadmin`
    -   **Senha:** `miniopassword` (ou o que você definiu no `.env`)
    -   O bucket `books` será criado automaticamente na primeira vez que um arquivo for enviado.

-   **Painel de Gerenciamento do RabbitMQ**
    -   URL: [http://localhost:15672](http://localhost:15672)
    -   **Usuário:** `guest`
    -   **Senha:** `guest` (ou o que você definiu no `.env`)

---

## ✅ Evidências de Funcionamento

Abaixo estão algumas capturas de tela que demonstram a aplicação em funcionamento.

### Aplicação Web

*Tela inicial listando os livros. A imagem do thumbnail é carregada a partir do MinIO.*
![Listagem de Livros](https://....png)

### Upload e Fila de Mensagens

*Ao fazer o upload de um livro com imagem, uma mensagem é publicada no RabbitMQ.*
![Painel do RabbitMQ](https://....png)

### Worker em Ação

*O log do `worker` mostra o recebimento da mensagem e o processamento da imagem.*
```
$ docker compose logs -f worker
...
[2024-01-02T12:00:00Z] Received message: b'{"bucket": "books", "key": "uploads/..."}'
[2024-01-02T12:00:01Z] SUCCESS: uploads/... -> thumb/....jpg
```

### Armazenamento no MinIO

*A imagem original (`uploads/`) e o thumbnail (`thumb/`) são armazenados no bucket `books` no MinIO.*
![Console do MinIO](https://....png)

### Persistência no Postgres

*Os dados do livro são salvos na tabela `books` do banco de dados PostgreSQL.*
![Dados no Postgres](https://....png)

### Auditoria no DynamoDB

*O log de auditoria da criação do livro é mantido na tabela do DynamoDB na AWS.*
![Tabela do DynamoDB](https://....png)