# Kubernetes Assistant: Interação com Kubernetes em Linguagem Natural

![Kubernetes + AI](https://img.shields.io/badge/Kubernetes-AI-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

Este projeto permite que você **interaja com seu cluster Kubernetes usando linguagem natural**, eliminando a necessidade de memorizar comandos kubectl complexos. Basta descrever o que você deseja fazer, e o assistente traduz suas intenções em ações no cluster.

<div align="center">

```
Você: "Crie um deployment do nginx com 3 réplicas"

[Assistente processa em segundo plano]
↓
Deployment criado com sucesso!
```

</div>

## 🎯 Objetivo Principal

O objetivo central deste projeto é **revolucionar a forma como você interage com o Kubernetes**, tornando-a acessível a administradores de todos os níveis através de comandos em linguagem natural. Sem mais memorização complexa, sem mais consultas à documentação para cada tarefa.

## 🚀 Exemplos do que você pode fazer

- "Liste todos os pods no namespace default"
- "Crie um deployment do nginx com 3 réplicas"
- "Mostre informações sobre o serviço 'frontend'"
- "Escale o deployment 'api-backend' para 5 réplicas"
- "Quais namespaces existem no cluster?"
- "Exiba o status de todos os nós"
- "Crie um ingress para o serviço 'web' usando o domínio app.example.com"

## 🧩 Arquitetura

O sistema é composto por três componentes principais:

```
[Seu Terminal/Chat] ←→ [Python + OpenAI API] ←→ [MCP Server Kubernetes] ←→ [Cluster Kubernetes]
    Interface            Processamento            Executor de Comandos       Infraestrutura
```

1. **Interface (Python)**: Onde você digita comandos em linguagem natural
2. **OpenAI API**: Processa a linguagem natural e determina as ações a serem executadas
3. **MCP Server**: Traduz as intenções em comandos kubectl
4. **Kubernetes**: Executa as operações no cluster

## 🛠️ Estado Atual do Projeto

> **⚠️ AVISO IMPORTANTE**: Atualmente, o MCP Server enfrenta problemas de conexão com a configuração kubectl. Por este motivo, o assistente opera em **Modo de Simulação**, permitindo demonstrar a funcionalidade sem conexão real com um cluster.

O Modo de Simulação é **totalmente funcional** e permite demonstrar a interface e o fluxo de trabalho do assistente, sendo ideal para:
- Apresentações e demonstrações
- Aprendizado dos conceitos
- Desenvolvimento de casos de uso

### Próximos Passos Técnicos

Para conectar ao seu cluster real, estamos planejando:
1. Corrigir a integração entre o MCP Server e a autenticação kubectl
2. Implementar suporte a múltiplos clusters e contextos
3. Adicionar melhor tratamento de erros e logging para depuração

## 🛠️ Configuração do Ambiente

### Pré-requisitos

- Python 3.8+
- Node.js 18+ (para o MCP Server)
- Um cluster Kubernetes em execução (KIND, minikube, etc.)
- Chave de API da OpenAI
- kubectl configurado e funcionando

### Passo 1: Configurar o Cluster Kubernetes (KIND)

Se ainda não tiver um cluster:

```bash
# Instalar KIND
# No Linux/Mac
brew install kind
# Ou no Windows
choco install kind

# Criar cluster
kind create cluster --name mcp-test
```

Verifique o funcionamento:
```bash
kubectl get nodes
```

### Passo 2: Instalar e Configurar o MCP Server

```bash
# Clonar o repositório
git clone https://github.com/Flux159/mcp-server-kubernetes.git
cd mcp-server-kubernetes

# Instalar dependências
npm install

# Compilar
npm run build

# Definir porta personalizada (opcional)
echo "PORT=9000" > .env

# Iniciar o servidor
npm start
```

O MCP Server será executado localmente, escutando na porta padrão (3000 ou a definida pela env PORT). Você pode verificar isso executando:

```bash
curl http://localhost:9000/v1/health  # Ajuste para sua porta
```

### Passo 3: Configurar o Assistente Python

```bash
# Clonar este repositório (se já não estiver nele)
cd ..

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Passo 4: Configurar a Chave da API OpenAI e o MCP Server URL

Crie um arquivo `.env` na raiz do projeto:

```
OPENAI_API_KEY=sua_chave_da_api_openai
MCP_SERVER_URL=http://localhost:9000  # Ajuste para porta do seu MCP Server
```

> **⚠️ IMPORTANTE**: O arquivo `.env` contém sua chave de API da OpenAI e **não deve ser compartilhado ou commitado** no repositório. O arquivo `.gitignore` já está configurado para ignorá-lo.

## 💬 Como Usar

1. **Iniciar o Assistente**:
   ```bash
   source venv/bin/activate
   python k8s_assistant.py
   ```

2. **Interagir em linguagem natural** (no modo de simulação):
   ```
   === Kubernetes Assistant ===
   MODO DE SIMULAÇÃO: Usando dados simulados do Kubernetes
   Digite suas mensagens (digite 'sair' para encerrar):

   Você: Liste todos os pods no namespace default
   ```

## 🔄 Como Funciona (Fluxo Detalhado)

1. **Seu comando em linguagem natural** é enviado para a API da OpenAI (modelo GPT-4o)
2. **O modelo AI** analisa sua intenção e decide qual ferramenta usar:
   - `getKubernetesResources` para consultas
   - `applyKubernetesConfig` para criar/atualizar recursos
3. **No modo de simulação**, o assistente gera respostas simuladas para demonstrar a funcionalidade

## 🔄 Modo de Simulação

Se o MCP Server não estiver acessível, o sistema entra automaticamente no **Modo de Simulação**, permitindo testar a interface sem um cluster real.

```
=== Kubernetes Assistant ===
MODO DE SIMULAÇÃO: Usando dados simulados do Kubernetes
```

Este modo é útil para:
- Testar a interface sem um cluster Kubernetes
- Aprender sobre os diferentes recursos do Kubernetes
- Demonstrar a ferramenta sem infraestrutura

## 📂 Estrutura do Projeto

```
.
├── mcp-server-kubernetes/  # Servidor MCP para Kubernetes (não versionado)
├── venv/                   # Ambiente virtual Python (não versionado)
├── .env                    # Variáveis de ambiente (não versionado)
├── .gitignore              # Arquivos ignorados pelo git
├── k8s_assistant.py        # Script principal do assistente
├── requirements.txt        # Dependências Python
└── README.md               # Esta documentação
```

## 📋 Comandos Comuns para Testar no Modo de Simulação

- "Liste todos os pods em todos os namespaces"
- "Verifique o status de todos os nós"
- "Crie um pod nginx simples"
- "Quais serviços estão rodando no namespace kube-system?"
- "Escale o deployment 'app-deployment' para 3 réplicas"

## 🔧 Solução de Problemas

- **MCP Server não conecta**: 
  - Verifique se está rodando com `npm start`
  - Confirme a porta correta no arquivo `.env` (padrão: 3000)
  - Verifique se o processo está em execução com `ps aux | grep node`

- **Erros na API OpenAI**: 
  - Verifique se sua chave está correta no arquivo `.env`
  - Confirme que sua conta OpenAI tem créditos disponíveis

- **Problemas com o Kubernetes**: 
  - Execute `kubectl get nodes` para verificar a conexão
  - Verifique o contexto atual do kubectl com `kubectl config current-context`

- **Erro no Python**: 
  - Certifique-se de que todas as dependências estão instaladas
  - Verifique se o ambiente virtual está ativado

## 🔧 Solução de Problemas Comuns

### Erro "No active cluster!" ao iniciar o MCP Server

O erro `Error: No active cluster!` ocorre quando o MCP Server não consegue acessar a configuração do kubectl. Isto geralmente acontece quando:

1. A configuração kubectl está disponível apenas para o usuário root
2. O contexto atual do kubectl não está definido ou é inválido

**Solução 1:** Copie a configuração do kubectl do root para seu usuário:
```bash
mkdir -p ~/.kube
sudo cp /root/.kube/config ~/.kube/
sudo chown $(id -u):$(id -g) ~/.kube/config
```

**Solução 2:** Verifique se há um contexto ativo:
```bash
kubectl config current-context
```

**Solução 3:** Se você precisa executar o MCP Server com sudo, ajuste o arquivo .env do assistente Python para a porta correta (definida no .env do MCP Server):
```
OPENAI_API_KEY=sua_chave_da_api_openai
MCP_SERVER_URL=http://localhost:9000
```

### Assistente entra em "Modo de Simulação"

O assistente entra neste modo quando não consegue se conectar ao MCP Server. Verifique:

1. O MCP Server está rodando? Execute `ps aux | grep node` para verificar
2. A porta definida no arquivo .env do assistente corresponde à porta em que o MCP Server está escutando?
3. O endpoint de health do MCP Server responde? Teste com `curl http://localhost:9000/v1/health`

### MCP Server inicia mas não está acessível

Se o MCP Server inicia sem erros, mas você não consegue acessá-lo:

1. Verifique a porta que está sendo usada no log de inicialização
2. Certifique-se de que nenhum firewall ou outro serviço está bloqueando a porta
3. Configure a mesma porta no arquivo .env tanto do MCP Server quanto do assistente Python

## 🔒 Segurança

- Sua chave da API OpenAI é armazenada apenas localmente no arquivo `.env`
- O MCP Server só executa comandos através do kubectl configurado no seu sistema
- Recomenda-se usar um contexto de cluster com permissões limitadas para testes
- Nunca comita ou compartilhe seu arquivo `.env` contendo a chave da API

## 🌱 Próximos Passos

- Integrar autenticação para acesso seguro
- Adicionar suporte para mais recursos do Kubernetes
- Criar uma interface web para interação mais amigável
- Adicionar histórico persistente de comandos
- Conectar com múltiplos clusters simultaneamente

## 📜 Licença



---

