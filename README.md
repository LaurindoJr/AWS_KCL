# Aplicação de Biblioteca de Livros

Este projeto implementa uma aplicação simples de biblioteca de livros com frontend e backend desacoplados, orquestrados usando Docker Compose. A aplicação permite gerenciar livros (CRUD), aluguéis, upload de imagens de capa usando MinIO, processamento assíncrono de miniaturas com RabbitMQ, e logging de auditoria opcional usando AWS DynamoDB.

## Funcionalidades

- **Gerenciamento de Livros**: Criar, Ler, Atualizar e Deletar (CRUD) livros.
  <h4>📸 Demonstração</h4>

<div align="center">

<img src="screenshots/1.jpeg" width="400"/>
<br>

<details>
<summary>Ver mais imagens</summary>
<img src="screenshots/2.jpeg" width="400"/><br>
<img src="screenshots/3.jpeg" width="400"/><br>
<img src="screenshots/4.jpeg" width="400"/><br>
<img src="screenshots/5.jpeg" width="400"/><br>
<img src="screenshots/6.jpeg" width="400"/><br>
<img src="screenshots/12.jpeg" width="400"/><br>
<img src="screenshots/13.jpeg" width="400"/><br>

</details>
</div>

- **Gerenciamento de Aluguéis**: Alugar e devolver livros.
  <h4>📸 Demonstração</h4>

<div align="center">

<img src="screenshots/10.jpeg" width="400"/>
<br>

<details>
<summary>Ver mais imagens</summary>
<img src="screenshots/11.jpeg" width="400"/><br>
</details>
</div>

- **Uploads de Imagens**: Upload de imagens de capa de livros usando MinIO (compatível com S3).
  <h4>📸 Demonstração</h4>

<div align="center">

<img src="screenshots/7.jpeg" width="400"/>
<br>

<details>
<summary>Ver mais imagens</summary>
<img src="screenshots/8.jpeg" width="400"/><br>
<img src="screenshots/9.jpeg" width="400"/><br>
<img src="screenshots/12.jpeg" width="400"/><br>
<img src="screenshots/13.jpeg" width="400"/><br>
<img src="screenshots/14.jpeg" width="400"/><br>

</details>
</div>

- **Fila de Mensagens**: Processamento assíncrono de miniaturas de imagens usando RabbitMQ.
  <h4>📸 Demonstração</h4>

<div align="center">

<img src="screenshots/15.jpeg" width="400"/>
<br>

</div>

- **Logging de Auditoria**: Auditoria de ações (CRIAR, ATUALIZAR, DELETAR, ALUGAR, DEVOLVER) usando AWS DynamoDB (opcional).
- **Documentação Interativa da API**: API do backend documentada com Swagger UI.
- **Frontend Moderno**: Aplicação de Página Única (SPA) construída com React e TypeScript.



## Tecnologias Utilizadas

- **Backend**: Flask (Python), Gunicorn, Flasgger (Swagger UI), Psycopg2 (adaptador PostgreSQL), Boto3 (SDK AWS para MinIO/DynamoDB), Pika (cliente RabbitMQ), Pydantic (validação de dados).
- **Frontend**: React, TypeScript, React Router DOM, Bootstrap (para estilização).
- **Banco de Dados**: PostgreSQL 13 (banco relacional para dados da aplicação).
  <h4>📸 Demonstração</h4>

<div align="center">

<img src="screenshots/16.jpeg" width="400"/>
<br>

<details>
<summary>Ver mais imagens</summary>
<img src="screenshots/13.jpeg" width="400"/><br>
<img src="screenshots/17.jpeg" width="400"/><br>
<img src="screenshots/18.jpeg" width="400"/><br>

</details>
</div>

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

## Instruções de Configuração (Docker Compose)

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

## Acesso à Aplicação (Docker Compose)

- **Frontend (Aplicação React)**: Abra seu navegador web e acesse `http://localhost:8080`
- **Swagger UI (Documentação da API do Backend)**: Acesse `http://localhost:5000/apidocs` para ver todos os endpoints da API e testá-los interativamente
- **MinIO Console**: Acesse `http://localhost:9001` (usuário: `minioadmin`, senha: `miniopassword`)
- **RabbitMQ Management**: Acesse `http://localhost:15672` (usuário: `guest`, senha: `guest`)


---

## Instruções de Implantação (Kubernetes)

Esta seção descreve como implantar a aplicação em um cluster Kubernetes. Todos os manifestos necessários estão localizados no diretório `k8s/`.

### Pré-requisitos (Kubernetes)

- Um cluster Kubernetes funcional.
- `kubectl` configurado para se comunicar com seu cluster.
- Um registro de contêiner (Docker Hub, GCR, ECR) para hospedar suas imagens.

### Passo 1: Build, Tag e Push das Imagens Docker

Você precisa construir as imagens Docker para o `backend`, `worker` e `frontend`, dar um `tag` a elas com o endereço do seu registro de contêiner e, em seguida, enviá-las.

**Exemplo (para o backend):**
```shell
# 1. Construir a imagem
docker build -t backend-image:latest ./backend

# 2. Taguear a imagem (substitua 'seu-usuario' pelo seu usuário no Docker Hub)
docker tag backend-image:latest seu-usuario/backend-image:latest

# 3. Enviar a imagem para o registro
docker push seu-usuario/backend-image:latest
```

**Ações:**
1.  Faça isso para os três serviços: `backend`, `worker` e `frontend`.
2.  **MUITO IMPORTANTE:** Após o push, atualize os arquivos `k8s/backend.yaml`, `k8s/worker.yaml` e `k8s/frontend.yaml`, substituindo os valores `image: backend-image:latest` (e similares) pelo nome completo da imagem que você acabou de enviar (ex: `image: seu-usuario/backend-image:latest`).

### Passo 2: Configurar os Segredos

O arquivo `k8s/secrets.yaml` contém placeholders para suas credenciais. Você **DEVE** substituí-los por valores codificados em Base64.

**Exemplo (para a senha do PostgreSQL):**
```shell
# No PowerShell ou terminal que suporte 'echo' e 'base64'
echo -n 'sua-senha-super-secreta' | base64
```

**Ações:**
1.  Execute o comando acima para cada segredo que você precisa configurar (`POSTGRES_PASSWORD`, `MINIO_ROOT_USER`, etc.).
2.  Copie a string de saída (ex: `c3VhLXNlbmhhLXN1cGVyLXNlY3JldGE=`).
3.  Abra o arquivo `k8s/secrets.yaml` e cole a string no campo correspondente.
4.  **NUNCA** comite este arquivo com segredos reais em um repositório público.

### Passo 3: Ajustar o ConfigMap

Você precisa fornecer uma URL externa para o MinIO.

**Ação:**
1.  Obtenha o endereço IP de um dos nós (nodes) do seu cluster Kubernetes. Você pode usar `kubectl get nodes -o wide` para ver os IPs.
2.  Abra o arquivo `k8s/configmap.yaml`.
3.  Encontre a linha `MINIO_PUBLIC_URL: "http://<IP_DO_SEU_CLUSTER_K8S>:9000"`.
4.  Substitua `<IP_DO_SEU_CLUSTER_K8S>` pelo endereço IP do nó e a porta pela `NodePort` do serviço do MinIO (30000). O resultado deve ser algo como `MINIO_PUBLIC_URL: "http://192.168.1.100:30000"`.

### Passo 4: Implantar no Kubernetes

Com tudo configurado, aplique os manifestos no seu cluster. A ordem é importante.

**Ação:**
Execute os seguintes comandos na ordem especificada:

```shell
# 1. Crie o Namespace
kubectl apply -f k8s/namespace.yaml

# 2. Crie os ConfigMaps e o Secret
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/init-db-configmap.yaml
kubectl apply -f k8s/secrets.yaml

# 3. Crie os serviços de backend (Postgres, MinIO, RabbitMQ)
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/minio.yaml
kubectl apply -f k8s/rabbitmq.yaml

# Espere um pouco para que os serviços acima iniciem.
# Você pode verificar o status com: kubectl get pods -n kcl-app

# 4. Crie os deployments da aplicação
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/worker.yaml
kubectl apply -f k8s/frontend.yaml
```

### Passo 5: Acessar a Aplicação (Kubernetes)

Após a implantação, você pode acessar os serviços expostos através das `NodePorts`. Use o mesmo endereço IP de nó que você usou no Passo 3.

- **Frontend (Aplicação Principal):** `http://<IP_DO_NÓ>:30080`
- **Console do MinIO:** `http://<IP_DO_NÓ>:30001`
- **Management do RabbitMQ:** `http://<IP_DO_NÓ>:30002`