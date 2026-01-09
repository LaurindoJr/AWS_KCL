# Backend Service README

Este documento fornece uma explicação detalhada da arquitetura, responsabilidades dos arquivos e fluxos de trabalho do serviço de backend.

## Visão Geral da Arquitetura

O backend é construído usando Flask e segue uma arquitetura em camadas para separar as responsabilidades:

-   **Camada de Controle (Controller):** Responsável por receber requisições HTTP, validar entradas e orquestrar a resposta. Fica em `src/*/book_controller.py`.
-   **Camada de Serviço (Service):** Contém a lógica de negócios principal da aplicação. Fica em `src/*/book_service.py`.
-   **Camada de Repositório (Repository):** Abstrai o acesso aos dados, lidando com a comunicação com os bancos de dados (PostgreSQL e DynamoDB). Fica em `src/*/book_repository.py`.

A aplicação também interage com outros serviços, como MinIO para armazenamento de objetos e RabbitMQ para mensagens assíncronas, com o apoio de módulos utilitários.

---

## Responsabilidades dos Arquivos

### Diretório Raiz (`backend/`)

-   **`app.py`**: Ponto de entrada principal da aplicação web Flask. É responsável por inicializar o aplicativo, registrar os *Blueprints* (rotas) dos controllers e configurar o tratamento de erros e o health check.
-   **`worker.py`**: Ponto de entrada para o processo de worker assíncrono. Ele consome mensagens de uma fila RabbitMQ para executar tarefas em segundo plano (como processamento de imagens).
-   **`requirements.txt`**: Lista todas as dependências Python necessárias para a aplicação e o worker.
-   **`Dockerfile`**: Define as instruções para construir a imagem Docker do serviço web `flask_app`.
-   **`Dockerfile.worker`**: Define as instruções para construir a imagem Docker do serviço `worker`.
-   **`init.sql`**: Script SQL executado na inicialização do container PostgreSQL para criar as tabelas `books` e `rentals` iniciais.

### `src/`

-   **`__init__.py`**: Transforma o diretório `src` em um pacote Python.

### `src/common/`

-   **`database.py`**: Centraliza a gestão de conexões com os bancos de dados. A classe `DatabaseManager` é responsável por inicializar e fornecer conexões para o PostgreSQL e objetos de tabela para o DynamoDB. Garante que a lógica de conexão não seja duplicada pela aplicação.
-   **`audit.py`**: Fornece a função `log_audit` para registrar eventos de auditoria (ex: criação de aluguel) em uma tabela DynamoDB. Ele obtém a tabela do `DatabaseManager`.
-   **`minio_utils.py`**: Contém funções utilitárias para interagir com o MinIO, como inicializar o bucket de armazenamento na inicialização da aplicação.
-   **`rabbitmq_utils.py`**: Contém funções para interagir com o RabbitMQ, como publicar mensagens em uma fila.
-   **`dynamo_health.py`**: Fornece a função `dynamo_rentals_available` para verificar a disponibilidade do DynamoDB. Essa verificação é usada pelo `RentalRepositoryRouter` para decidir qual banco de dados usar.

### `src/books/`

-   **`book_controller.py`**: Define o *Blueprint* Flask para as rotas da API relacionadas a livros (ex: `GET /api/books`, `POST /api/books`). Ele delega a lógica de negócios para o `BookService`.
-   **`book_service.py`**: Implementa a lógica de negócios para operações com livros, como criar, listar e buscar livros. Ele coordena o `BookRepository` e outras dependências.
-   **`book_repository.py`**: Responsável pela comunicação com o banco de dados PostgreSQL para todas as operações CRUD (Criar, Ler, Atualizar, Deletar) relacionadas a livros.
-   **`book_dto.py`**: Define os *Data Transfer Objects* (DTOs) para livros, usados para estruturar os dados que fluem entre as camadas.

### `src/rentals/`

-   **`rental_controller.py`**: Define o *Blueprint* Flask para as rotas da API relacionadas a aluguéis (ex: `POST /api/books/<id>/rentals`, `PUT /api/rentals/<id>/return`). Delega a lógica para o `RentalService` e registra os eventos de auditoria.
-   **`rental_service.py`**: Implementa a lógica de negócios para alugar e devolver livros. Ele usa o `RentalRepositoryRouter` para interagir com a camada de dados.
-   **`rental_repository_router.py`**: Atua como um roteador para o repositório de aluguéis. Com base na variável de ambiente `RENTALS_STORE`, ele decide se as operações de aluguel devem ser direcionadas para o PostgreSQL (`PgRepo`) ou para o DynamoDB (`DdbRepo`). Se o modo for `auto`, ele usa o `dynamo_health.py` para decidir.
-   **`rental_repository_postgres.py`**: Implementação do repositório de aluguéis que usa o PostgreSQL como banco de dados.
-   **`rental_repository_dynamo.py`**: Implementação do repositório de aluguéis que usa o DynamoDB. Ele modela os dados usando um design de lista de adjacência com chaves `pk` e `sk` para permitir consultas flexíveis.
-   **`rental_dto.py`**: Define os DTOs para os dados de aluguel.

---

## Fluxos de Trabalho da Aplicação

### Fluxo 1: Criar um Novo Livro

1.  Uma requisição `POST` chega em `/api/books` com os dados do livro.
2.  O `book_controller` recebe a requisição, valida os dados e chama o `book_service.create_book()`.
3.  O `book_service` executa a lógica de negócios (se houver) e chama o `book_repository.create()`.
4.  O `book_repository` estabelece uma conexão com o PostgreSQL (via `database.py`) e insere um novo registro na tabela `books`.
5.  A resposta retorna pela mesma cadeia, e o `book_controller` envia uma resposta JSON `201 Created`.

### Fluxo 2: Alugar um Livro (usando DynamoDB)

1.  Uma requisição `POST` chega em `/api/books/<book_id>/rentals` com o nome do locatário.
2.  O `rental_controller` recebe a requisição e chama o `rental_service.create_rental()`.
3.  O `rental_service` chama `self.rental_repository.create()`, que é uma instância do `RentalRepositoryRouter`.
4.  O `RentalRepositoryRouter` verifica a variável de ambiente `RENTALS_STORE`. Assumindo que seja `dynamo` ou `auto` (com DynamoDB disponível), ele chama o método `create()` da instância de `RentalRepositoryDynamo`.
5.  O `RentalRepositoryDynamo` obtém a tabela DynamoDB do `DatabaseManager` centralizado.
6.  Ele primeiro atualiza um item de sequência no DynamoDB para gerar um novo `rental_id` atômico.
7.  Em seguida, ele cria o item do aluguel na tabela, associado ao livro.
8.  O `rental_id` retorna pela cadeia até o `rental_controller`.
9.  O `rental_controller` então chama a função `log_audit()` de `src/common/audit.py`.
10. A função `log_audit()` escreve um registro na tabela de auditoria do DynamoDB.
11. Finalmente, o `rental_controller` retorna uma resposta JSON `201 Created`.

### Fluxo 3: Worker Assíncrono (Exemplo)

1.  Um evento na aplicação (ex: upload de imagem de capa de um livro) precisa de processamento em segundo plano.
2.  O código relevante (provavelmente no `book_service`) usa `rabbitmq_utils.py` para publicar uma mensagem na fila do RabbitMQ. A mensagem contém informações sobre a tarefa (ex: ID do livro).
3.  O container `worker`, que está executando o script `worker.py`, está constantemente escutando essa fila.
4.  Ao receber a mensagem, o `worker.py` executa a tarefa de processamento (ex: redimensiona a imagem).
5.  Durante ou após o processamento, o worker pode usar o `DatabaseManager` para atualizar o status em uma tabela do DynamoDB (`DDB_STATUS`) ou atualizar um campo no registro do livro em PostgreSQL.
