import os
import time
import json
import requests
import openai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar a API key da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# URL do MCP Server
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

# Flag para indicar se devemos usar simulação local
USE_SIMULATION = False

# Verificar se a chave está presente
if not openai.api_key:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique o arquivo .env")

# Criar um novo Assistant (só precisa ser feito uma vez)
def create_assistant():
    assistant = openai.beta.assistants.create(
        name="Kubernetes Assistant",
        instructions="""
        Você é um assistente especializado em gerenciar clusters Kubernetes. 
        Use a ferramenta applyKubernetesConfig para aplicar configurações YAML no cluster.
        Use a ferramenta getKubernetesResources para obter informações sobre recursos do cluster.
        Forneça respostas claras e concisas sobre o estado dos recursos Kubernetes.
        """,
        model="gpt-4o",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "applyKubernetesConfig",
                    "description": "Aplica uma configuração YAML no cluster Kubernetes",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "config": {
                                "type": "string",
                                "description": "YAML ou JSON contendo a configuração Kubernetes a ser aplicada"
                            }
                        },
                        "required": ["config"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "getKubernetesResources",
                    "description": "Obtém recursos Kubernetes do cluster",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "resourceType": {
                                "type": "string",
                                "description": "Tipo de recurso Kubernetes (pods, deployments, services, etc.)"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace dos recursos (padrão: default)"
                            }
                        },
                        "required": ["resourceType"]
                    }
                }
            }
        ]
    )
    return assistant.id

# Função para se comunicar com o MCP Server
def call_mcp_server(endpoint, payload):
    if USE_SIMULATION:
        return simulate_mcp_response(endpoint, payload)
    
    url = f"{MCP_SERVER_URL}/v1/{endpoint}"
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro na chamada do MCP Server: {response.status_code}")
            print(f"Resposta: {response.text}")
            return {"error": f"Erro na chamada do MCP Server: {response.status_code}"}
    except Exception as e:
        print(f"Exceção ao chamar o MCP Server: {e}")
        print("Usando simulação local como fallback...")
        return simulate_mcp_response(endpoint, payload)

# Função para simular respostas do MCP Server
def simulate_mcp_response(endpoint, payload):
    if endpoint == "tools/get":
        resource_type = payload.get("resourceType", "")
        namespace = payload.get("namespace", "default")
        
        # Simular diferentes tipos de recursos
        if resource_type.lower() == "pods":
            return {
                "items": [
                    {"metadata": {"name": "nginx-pod"}, "status": {"phase": "Running"}},
                    {"metadata": {"name": "app-backend"}, "status": {"phase": "Running"}},
                    {"metadata": {"name": "coredns-1"}, "namespace": "kube-system", "status": {"phase": "Running"}},
                    {"metadata": {"name": "coredns-2"}, "namespace": "kube-system", "status": {"phase": "Running"}},
                    {"metadata": {"name": "etcd"}, "namespace": "kube-system", "status": {"phase": "Running"}},
                    {"metadata": {"name": "kube-apiserver"}, "namespace": "kube-system", "status": {"phase": "Running"}},
                    {"metadata": {"name": "kube-controller-manager"}, "namespace": "kube-system", "status": {"phase": "Running"}},
                    {"metadata": {"name": "kube-scheduler"}, "namespace": "kube-system", "status": {"phase": "Running"}},
                    {"metadata": {"name": "kube-proxy"}, "namespace": "kube-system", "status": {"phase": "Running"}}
                ]
            }
        elif resource_type.lower() == "deployments":
            return {
                "items": [
                    {"metadata": {"name": "nginx-deployment"}, "spec": {"replicas": 3}, "status": {"readyReplicas": 3}},
                    {"metadata": {"name": "app-deployment"}, "spec": {"replicas": 2}, "status": {"readyReplicas": 2}}
                ]
            }
        elif resource_type.lower() == "services":
            return {
                "items": [
                    {"metadata": {"name": "kubernetes"}, "spec": {"type": "ClusterIP", "clusterIP": "10.96.0.1"}},
                    {"metadata": {"name": "nginx-service"}, "spec": {"type": "ClusterIP", "clusterIP": "10.96.0.100"}}
                ]
            }
        elif resource_type.lower() == "nodes":
            return {
                "items": [
                    {"metadata": {"name": "kind-control-plane"}, "status": {"conditions": [{"type": "Ready", "status": "True"}]}}
                ]
            }
        elif resource_type.lower() == "namespaces":
            return {
                "items": [
                    {"metadata": {"name": "default"}},
                    {"metadata": {"name": "kube-system"}},
                    {"metadata": {"name": "kube-public"}},
                    {"metadata": {"name": "kube-node-lease"}}
                ]
            }
        else:
            return {"items": []}
            
    elif endpoint == "tools/apply":
        config = payload.get("config", "")
        
        # Verificar tipo de recurso no YAML
        resource_type = "desconhecido"
        if "kind: Deployment" in config:
            resource_type = "Deployment"
        elif "kind: Pod" in config:
            resource_type = "Pod"
        elif "kind: Service" in config:
            resource_type = "Service"
            
        # Extrair nome do recurso
        import re
        name_match = re.search(r"name:\s*([a-zA-Z0-9-]+)", config)
        resource_name = name_match.group(1) if name_match else "recurso"
        
        return {
            "status": "success", 
            "message": f"{resource_type} '{resource_name}' aplicado com sucesso",
            "resource": {"kind": resource_type, "name": resource_name}
        }
    
    return {"status": "error", "message": "Função não suportada na simulação"}

# Função para processar as chamadas de função
def process_tool_calls(run, thread_id):
    tool_outputs = []
    
    # Para cada chamada de ferramenta
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        # Pegar o nome da função e os argumentos
        function_name = tool_call.function.name
        function_args = tool_call.function.arguments
        
        args = json.loads(function_args)
        
        # Definimos os resultados como uma string vazia por padrão
        result = ""
        
        # Interação real ou simulada com o MCP Server
        if function_name == "getKubernetesResources":
            resource_type = args.get("resourceType")
            namespace = args.get("namespace", "default")
            
            # Chamar o MCP Server para obter recursos
            mcp_response = call_mcp_server("tools/get", {
                "resourceType": resource_type,
                "namespace": namespace
            })
            
            # Converter a resposta para string JSON
            result = json.dumps(mcp_response)
                
        elif function_name == "applyKubernetesConfig":
            config = args.get("config")
            
            # Chamar o MCP Server para aplicar a configuração
            mcp_response = call_mcp_server("tools/apply", {
                "config": config
            })
            
            # Converter a resposta para string JSON
            result = json.dumps(mcp_response)
        
        # Adicionar o resultado à lista de saídas
        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": result
        })
    
    # Submeter todas as saídas de ferramentas
    openai.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )

# Função principal para executar o chat
def chat_with_assistant():
    global USE_SIMULATION
    
    # Verificar conexão com o MCP Server
    try:
        response = requests.get(f"{MCP_SERVER_URL}/v1/health")
        if response.status_code != 200:
            print(f"AVISO: O MCP Server não está respondendo corretamente em {MCP_SERVER_URL}")
            print(f"Status: {response.status_code}")
            print("Usando simulação local...")
            USE_SIMULATION = True
    except Exception as e:
        print(f"AVISO: Não foi possível conectar ao MCP Server em {MCP_SERVER_URL}")
        print(f"Erro: {e}")
        print("Usando simulação local...")
        USE_SIMULATION = True
    
    # Criar ou usar um assistant existente
    assistant_id = create_assistant()
    print(f"Assistant ID: {assistant_id}")
    
    # Criar uma nova thread
    thread = openai.beta.threads.create()
    print(f"Thread criada com ID: {thread.id}")
    
    print("\n=== Kubernetes Assistant ===")
    if USE_SIMULATION:
        print("MODO DE SIMULAÇÃO: Usando dados simulados do Kubernetes")
    print("Digite suas mensagens (digite 'sair' para encerrar):")
    
    while True:
        # Obter mensagem do usuário
        user_input = input("\nVocê: ")
        
        if user_input.lower() == 'sair':
            print("Encerrando o chat...")
            break
        
        # Adicionar a mensagem à thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        
        # Executar o assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Verificar o status do run
        while True:
            run = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run.status == "completed":
                # Exibir a resposta do assistant
                messages = openai.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                # A primeira mensagem é a mais recente
                assistant_message = messages.data[0].content[0].text.value
                print(f"\nAssistant: {assistant_message}")
                break
            
            elif run.status == "requires_action":
                # O assistant está solicitando informações
                process_tool_calls(run, thread.id)
            
            elif run.status in ["failed", "cancelled", "expired"]:
                print(f"\nErro: A execução falhou com status: {run.status}")
                if hasattr(run, 'last_error'):
                    print(f"Detalhes: {run.last_error}")
                break
            
            # Aguardar antes de verificar novamente
            time.sleep(1)

if __name__ == "__main__":
    chat_with_assistant() 