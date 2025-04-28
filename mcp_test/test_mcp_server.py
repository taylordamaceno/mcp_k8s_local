import requests
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# URL do MCP Server
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3333")

def test_connection():
    """Testa a conexão com o MCP Server."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/v1/health")
        if response.status_code == 200:
            print("Conexão com o MCP Server estabelecida com sucesso!")
            return True
        else:
            print(f"Falha na conexão. Código de status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao conectar ao MCP Server: {e}")
        return False

def get_kubernetes_resources(resource_type, namespace="default"):
    """Obtém recursos Kubernetes do cluster."""
    url = f"{MCP_SERVER_URL}/v1/tools/get"
    payload = {
        "resourceType": resource_type,
        "namespace": namespace
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Recursos obtidos com sucesso:")
            print(json.dumps(response.json(), indent=2))
            return response.json()
        else:
            print(f"Falha ao obter recursos. Código de status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao obter recursos: {e}")
        return None

def apply_kubernetes_config(config_yaml):
    """Aplica uma configuração YAML no cluster Kubernetes."""
    url = f"{MCP_SERVER_URL}/v1/tools/apply"
    payload = {
        "config": config_yaml
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Configuração aplicada com sucesso!")
            print(json.dumps(response.json(), indent=2))
            return response.json()
        else:
            print(f"Falha ao aplicar configuração. Código de status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao aplicar configuração: {e}")
        return None

# Exemplo de YAML para criar um deployment do Nginx
nginx_deployment_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
"""

if __name__ == "__main__":
    # Testar conexão
    if test_connection():
        # Listar pods
        print("\n--- Listando pods ---")
        get_kubernetes_resources("pods")
        
        # Aplicar configuração YAML para criar um deployment do Nginx
        print("\n--- Criando deployment do Nginx ---")
        apply_kubernetes_config(nginx_deployment_yaml)
        
        # Verificar se o deployment foi criado
        print("\n--- Verificando deployments ---")
        get_kubernetes_resources("deployments")
    else:
        print("Não foi possível se conectar ao MCP Server. Verifique se o servidor está em execução.") 