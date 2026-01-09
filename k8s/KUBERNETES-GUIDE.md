# Guia Completo de Kubernetes - Aplicação KCL

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Recursos Implementados](#recursos-implementados)
4. [Deployment](#deployment)
5. [Monitoramento](#monitoramento)
6. [Troubleshooting](#troubleshooting)
7. [Manutenção](#manutenção)
8. [Escalabilidade](#escalabilidade)
9. [Segurança](#segurança)

## 🎯 Visão Geral

Este projeto implementa uma aplicação robusta e altamente disponível no Kubernetes com as seguintes características:

- **Alta Disponibilidade**: Múltiplas réplicas com distribuição anti-afinidade
- **Auto-scaling**: HPA configurado para escalar automaticamente
- **Health Checks**: Liveness e Readiness probes em todos os serviços
- **Persistência de Dados**: PVCs para bancos de dados e armazenamento
- **Segurança**: Security contexts e restrições de privilégios
- **Resiliência**: PodDisruptionBudgets para garantir disponibilidade mínima

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Frontend   │  │ Frontend   │  │ Frontend   │       │
│  │ (3 pods)   │  │ (replica)  │  │ (replica)  │       │
│  └─────┬──────┘  └──────┬─────┘  └──────┬─────┘       │
│        │                 │                │              │
│        └─────────────────┴────────────────┘              │
│                          │                                │
│  ┌───────────────────────┴──────────────────────────┐   │
│  │           Backend Service (ClusterIP)             │   │
│  └───────────────────────┬──────────────────────────┘   │
│                          │                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ Backend    │  │ Backend    │  │ Backend    │        │
│  │ (3 pods)   │  │ (replica)  │  │ (replica)  │        │
│  └─────┬──────┘  └──────┬─────┘  └──────┬─────┘        │
│        │                 │                │               │
│        └─────────────────┴────────────────┘               │
│                          │                                │
│        ┌─────────────────┼─────────────────┐             │
│        │                 │                 │             │
│  ┌─────▼─────┐    ┌──────▼──────┐   ┌─────▼─────┐      │
│  │ Postgres  │    │  RabbitMQ   │   │   MinIO   │      │
│  │(StatefulSet)│  │(StatefulSet)│   │(StatefulSet)│    │
│  └───────────┘    └─────────────┘   └───────────┘      │
│        │                 │                 │             │
│  ┌─────▼─────┐    ┌──────▼──────┐   ┌─────▼─────┐      │
│  │  PVC 5Gi  │    │  PVC 2Gi    │   │  PVC 10Gi │      │
│  └───────────┘    └─────────────┘   └───────────┘      │
│                                                          │
│  ┌────────────┐  ┌────────────┐                        │
│  │  Worker    │  │  Worker    │                        │
│  │  (2 pods)  │  │ (replica)  │                        │
│  └────────────┘  └────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## ✨ Recursos Implementados

### 1. Health Checks

**Backend, Frontend e Worker:**
- **Liveness Probes**: Detecta e reinicia pods travados
- **Readiness Probes**: Garante que pods só recebam tráfego quando prontos

**Postgres, RabbitMQ e MinIO:**
- **Liveness Probes**: Monitora saúde do processo
- **Readiness Probes**: Verifica conectividade antes de aceitar requisições

### 2. Resource Management

Todos os pods têm:
- **Requests**: Recursos mínimos garantidos
- **Limits**: Teto máximo para evitar consumo excessivo

### 3. Auto-scaling (HPA)

Configurado para Backend, Frontend e Worker:
- **Min Replicas**: 2-3 (dependendo do serviço)
- **Max Replicas**: 8-10
- **Métricas**: CPU (70%) e Memória (80%)
- **Comportamento Inteligente**: Scale-up rápido, scale-down gradual

### 4. Alta Disponibilidade

- **Pod Anti-Affinity**: Distribui pods em diferentes nós
- **PodDisruptionBudgets**: Mantém número mínimo de pods durante manutenção
- **Rolling Updates**: Updates sem downtime

### 5. Persistência de Dados

- **Postgres**: 5Gi (StatefulSet)
- **RabbitMQ**: 2Gi (StatefulSet)
- **MinIO**: 10Gi (StatefulSet)

### 6. Segurança

- **Security Contexts**: Restrição de privilégios
- **Secrets**: Credenciais seguras
- **Read-only Root Filesystem**: Onde possível
- **Non-root Users**: Execução com usuários não privilegiados

## 🚀 Deployment

### Pré-requisitos

1. Cluster Kubernetes funcional
2. kubectl configurado
3. Namespace criado
4. Secrets e ConfigMaps configurados

### Deployment Automatizado

```bash
cd k8s
chmod +x deploy.sh
./deploy.sh
```

### Deployment Manual

```bash
# 1. Criar namespace
kubectl apply -f namespace.yaml

# 2. Aplicar secrets e configmaps
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml
kubectl apply -f init-db-configmap.yaml

# 3. Deploy infraestrutura
kubectl apply -f postgres.yaml
kubectl apply -f rabbitmq.yaml
kubectl apply -f minio.yaml

# Aguardar pods ficarem prontos
kubectl wait --for=condition=ready pod -l app=postgres -n kcl-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=rabbitmq -n kcl-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=minio -n kcl-app --timeout=300s

# 4. Deploy aplicação
kubectl apply -f backend.yaml
kubectl apply -f worker.yaml
kubectl apply -f frontend.yaml
```

### Verificação

```bash
# Status geral
kubectl get all -n kcl-app

# Pods específicos
kubectl get pods -n kcl-app -w

# HPAs
kubectl get hpa -n kcl-app

# PVCs
kubectl get pvc -n kcl-app
```

## 📊 Monitoramento

### Verificar Status dos Pods

```bash
# Todos os pods
kubectl get pods -n kcl-app

# Pods com mais detalhes
kubectl get pods -n kcl-app -o wide

# Descrever um pod específico
kubectl describe pod <pod-name> -n kcl-app
```

### Logs

```bash
# Backend logs
kubectl logs -f deployment/backend-deployment -n kcl-app

# Frontend logs
kubectl logs -f deployment/frontend-deployment -n kcl-app

# Worker logs
kubectl logs -f deployment/worker-deployment -n kcl-app

# Logs de um pod específico
kubectl logs <pod-name> -n kcl-app --tail=100

# Logs anteriores (após crash)
kubectl logs <pod-name> -n kcl-app --previous
```

### Métricas de Recursos

```bash
# CPU e memória por pod
kubectl top pods -n kcl-app

# CPU e memória por nó
kubectl top nodes

# Status do HPA
kubectl get hpa -n kcl-app -w
```

### Eventos

```bash
# Eventos do namespace
kubectl get events -n kcl-app --sort-by='.lastTimestamp'

# Eventos de um pod específico
kubectl describe pod <pod-name> -n kcl-app | grep -A 10 Events
```

### Health Checks

```bash
# Verificar probes de um pod
kubectl describe pod <pod-name> -n kcl-app | grep -A 5 "Liveness\|Readiness"

# Executar health check manual
kubectl exec -it <backend-pod> -n kcl-app -- curl http://localhost:5000/health
```

## 🔧 Troubleshooting

### Pod não inicia (CrashLoopBackOff)

```bash
# 1. Ver logs do pod
kubectl logs <pod-name> -n kcl-app

# 2. Ver logs anteriores
kubectl logs <pod-name> -n kcl-app --previous

# 3. Descrever pod para ver eventos
kubectl describe pod <pod-name> -n kcl-app

# 4. Verificar configuração
kubectl get pod <pod-name> -n kcl-app -o yaml
```

**Causas comuns:**
- Falha no health check
- Secrets/ConfigMaps não encontrados
- Imagem não disponível
- Recursos insuficientes
- Erro na aplicação

### Pod em Pending

```bash
# Verificar motivo
kubectl describe pod <pod-name> -n kcl-app
```

**Causas comuns:**
- Recursos insuficientes no cluster
- PVC não pode ser montado
- Node selector/affinity não satisfeito

### Serviço não acessível

```bash
# 1. Verificar service
kubectl get svc -n kcl-app

# 2. Verificar endpoints
kubectl get endpoints -n kcl-app

# 3. Testar conectividade interna
kubectl run test-pod --image=busybox -n kcl-app --rm -it -- wget -O- http://backend-service:5000/health

# 4. Verificar logs do pod
kubectl logs <pod-name> -n kcl-app
```

### HPA não está escalando

```bash
# 1. Verificar métricas
kubectl top pods -n kcl-app

# 2. Verificar status do HPA
kubectl describe hpa <hpa-name> -n kcl-app

# 3. Verificar metrics-server
kubectl get deployment metrics-server -n kube-system
```

**Solução:**
Se metrics-server não estiver instalado:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### PVC não está bound

```bash
# 1. Verificar PVC
kubectl get pvc -n kcl-app

# 2. Descrever PVC
kubectl describe pvc <pvc-name> -n kcl-app

# 3. Verificar PVs disponíveis
kubectl get pv
```

**Causas comuns:**
- StorageClass não existe ou não tem dynamic provisioning
- Nenhum PV disponível com capacidade solicitada
- AccessMode incompatível

### Banco de dados não conecta

```bash
# 1. Verificar se postgres está rodando
kubectl get pods -l app=postgres -n kcl-app

# 2. Verificar logs do postgres
kubectl logs -l app=postgres -n kcl-app

# 3. Testar conectividade do backend
kubectl exec -it <backend-pod> -n kcl-app -- env | grep POSTGRES

# 4. Testar conexão direta
kubectl exec -it <postgres-pod> -n kcl-app -- psql -U postgres -c "SELECT 1"
```

## 🔄 Manutenção

### Atualizar Imagem

```bash
# Atualizar deployment com nova imagem
kubectl set image deployment/backend-deployment backend=backend-image:v2 -n kcl-app

# Verificar rollout
kubectl rollout status deployment/backend-deployment -n kcl-app

# Ver histórico
kubectl rollout history deployment/backend-deployment -n kcl-app
```

### Rollback

```bash
# Voltar para versão anterior
kubectl rollout undo deployment/backend-deployment -n kcl-app

# Voltar para revisão específica
kubectl rollout undo deployment/backend-deployment --to-revision=2 -n kcl-app
```

### Escalar Manualmente

```bash
# Escalar deployment
kubectl scale deployment/backend-deployment --replicas=5 -n kcl-app

# Escalar statefulset
kubectl scale statefulset/postgres --replicas=1 -n kcl-app
```

### Reiniciar Pods

```bash
# Reiniciar todos os pods de um deployment
kubectl rollout restart deployment/backend-deployment -n kcl-app

# Deletar pod específico (será recriado automaticamente)
kubectl delete pod <pod-name> -n kcl-app
```

### Backup do Banco de Dados

```bash
# Backup do Postgres
kubectl exec -it <postgres-pod> -n kcl-app -- pg_dump -U postgres library > backup.sql

# Restore
cat backup.sql | kubectl exec -i <postgres-pod> -n kcl-app -- psql -U postgres library
```

### Limpar Jobs Completados

```bash
# Listar jobs
kubectl get jobs -n kcl-app

# Deletar job específico
kubectl delete job minio-init-bucket -n kcl-app

# Deletar todos jobs completados
kubectl delete jobs --field-selector status.successful=1 -n kcl-app
```

## 📈 Escalabilidade

### Escalabilidade Horizontal (HPA)

Já configurado automaticamente para:
- Backend: 3-10 pods
- Frontend: 3-10 pods
- Worker: 2-8 pods

### Escalabilidade Vertical (VPA)

Para implementar VPA:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
  namespace: kcl-app
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-deployment
  updatePolicy:
    updateMode: "Auto"
```

### Cluster Autoscaler

Configure o cluster autoscaler para adicionar nós automaticamente quando necessário.

## 🔒 Segurança

### Melhores Práticas Implementadas

1. **Secrets**: Todas as credenciais em Secrets
2. **Security Contexts**: Restrição de privilégios
3. **Network Policies**: (Recomendado adicionar)
4. **RBAC**: (Recomendado adicionar)
5. **Pod Security Policies**: (Recomendado adicionar)

### Adicionar Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: kcl-app
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: rabbitmq
    ports:
    - protocol: TCP
      port: 5672
```

## 📝 Checklist de Produção

- [ ] Métricas e logging centralizados (Prometheus, Grafana, ELK)
- [ ] Alertas configurados
- [ ] Backups automáticos dos bancos de dados
- [ ] Disaster recovery plan
- [ ] Network policies aplicadas
- [ ] RBAC configurado
- [ ] Ingress controller configurado (nginx, traefik)
- [ ] Certificados SSL/TLS
- [ ] Rate limiting
- [ ] Resource quotas por namespace
- [ ] Monitoring de custos
- [ ] Documentação atualizada

## 🆘 Suporte

Para problemas ou questões:
1. Verificar logs: `kubectl logs -n kcl-app`
2. Verificar eventos: `kubectl get events -n kcl-app`
3. Descrever recurso: `kubectl describe -n kcl-app`
4. Consultar este guia de troubleshooting

## 📚 Recursos Adicionais

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [12 Factor App](https://12factor.net/)
- [CNCF Cloud Native Trail Map](https://github.com/cncf/trailmap)
