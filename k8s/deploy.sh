#!/bin/bash

# Script de deployment para o Kubernetes
# Este script realiza o deployment completo da aplicação KCL

set -e

echo "=================================="
echo "   KCL Application Deployment"
echo "=================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para imprimir mensagens
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se kubectl está instalado
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl não está instalado. Por favor, instale o kubectl primeiro."
    exit 1
fi

print_info "Verificando conexão com o cluster Kubernetes..."
if ! kubectl cluster-info &> /dev/null; then
    print_error "Não foi possível conectar ao cluster Kubernetes. Verifique sua configuração."
    exit 1
fi

print_info "Conexão com o cluster estabelecida com sucesso!"
echo ""

# Criar namespace
print_info "Criando namespace 'kcl-app'..."
kubectl apply -f k8s/namespace.yaml

# Aguardar namespace estar pronto
sleep 2

# Aplicar Secrets
print_info "Aplicando Secrets..."
kubectl apply -f k8s/secrets.yaml

# Aplicar ConfigMaps
print_info "Aplicando ConfigMaps..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/init-db-configmap.yaml

# Deploy dos serviços de infraestrutura
print_info "Deployando PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

print_info "Deployando RabbitMQ..."
kubectl apply -f k8s/rabbitmq.yaml

print_info "Deployando MinIO..."
kubectl apply -f k8s/minio.yaml

print_warning "Aguardando serviços de infraestrutura iniciarem (60 segundos)..."
sleep 60

# Verificar status dos pods de infraestrutura
print_info "Verificando status dos pods de infraestrutura..."
kubectl get pods -n kcl-app -l app=postgres
kubectl get pods -n kcl-app -l app=rabbitmq
kubectl get pods -n kcl-app -l app=minio

# Deploy da aplicação
print_info "Deployando Backend..."
kubectl apply -f k8s/backend.yaml

print_info "Deployando Worker..."
kubectl apply -f k8s/worker.yaml

print_info "Deployando Frontend..."
kubectl apply -f k8s/frontend.yaml

print_warning "Aguardando aplicação iniciar (30 segundos)..."
sleep 30

# Verificar status geral
echo ""
print_info "=== Status do Deployment ==="
kubectl get all -n kcl-app

echo ""
print_info "=== Persistent Volume Claims ==="
kubectl get pvc -n kcl-app

echo ""
print_info "=== HorizontalPodAutoscalers ==="
kubectl get hpa -n kcl-app

echo ""
print_info "=== PodDisruptionBudgets ==="
kubectl get pdb -n kcl-app

echo ""
echo "=================================="
print_info "Deployment concluído com sucesso!"
echo "=================================="
echo ""

print_info "Portas de acesso:"
echo "  - Frontend: http://<node-ip>:30080"
echo "  - MinIO API: http://<node-ip>:30000"
echo "  - MinIO Console: http://<node-ip>:30001"
echo "  - RabbitMQ Management: http://<node-ip>:30002"
echo ""

print_info "Para obter o IP do nó, execute:"
echo "  kubectl get nodes -o wide"
echo ""

print_info "Para monitorar os logs:"
echo "  kubectl logs -f -n kcl-app deployment/backend-deployment"
echo "  kubectl logs -f -n kcl-app deployment/frontend-deployment"
echo "  kubectl logs -f -n kcl-app deployment/worker-deployment"
echo ""

print_info "Para verificar a saúde dos pods:"
echo "  kubectl get pods -n kcl-app -w"
echo ""
