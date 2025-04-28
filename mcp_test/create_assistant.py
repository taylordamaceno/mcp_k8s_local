import os
import openai
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Usar a chave da API a partir das variáveis de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verificar se a chave foi carregada corretamente
if not openai.api_key:
    raise ValueError("Erro: Chave da API não encontrada. Verifique se o arquivo .env existe com OPENAI_API_KEY definida.")

# Especificação OpenAPI do MCP Server Kubernetes
# Esta é uma versão simplificada para ilustrar a conexão
mcp_openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "MCP Server Kubernetes API",
        "version": "1.0.0",
        "description": "API para gerenciar recursos Kubernetes via MCP Server"
    },
    "servers": [
        {
            "url": "http://localhost:3333"
        }
    ],
    "paths": {
        "/v1/tools/apply": {
            "post": {
                "summary": "Aplicar uma configuração Kubernetes",
                "operationId": "applyKubernetesConfig",
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
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
                    }
                },
                "responses": {
                    "200": {
                        "description": "Configuração aplicada com sucesso"
                    }
                }
            }
        },
        "/v1/tools/get": {
            "post": {
                "summary": "Obter recursos Kubernetes",
                "operationId": "getKubernetesResources",
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceType": {
                                        "type": "string",
                                        "description": "Tipo de recurso Kubernetes (pods, deployments, services, etc.)"
                                    },
                                    "namespace": {
                                        "type": "string",
                                        "description": "Namespace dos recursos"
                                    }
                                },
                                "required": ["resourceType"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Recursos obtidos com sucesso"
                    }
                }
            }
        }
    }
}

# Criação do Assistant
assistant = openai.beta.assistants.create(
    name="Kubernetes MCP Assistant",
    instructions="""
    Você é um assistente especializado em gerenciar clusters Kubernetes. 
    Você pode ajudar a criar, listar e gerenciar recursos como pods, deployments, services, etc.
    Use as ferramentas disponíveis para interagir com o cluster Kubernetes via MCP Server.
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

print(f"Assistant criado com ID: {assistant.id}")
print("Você pode usar este ID para interagir com o Assistant na sua aplicação.")
print("Exemplo de como iniciar uma thread e enviar uma mensagem:")
print("""
import openai
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Iniciar uma nova thread
thread = openai.beta.threads.create()

# Adicionar uma mensagem à thread
message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Liste todos os pods no namespace default"
)

# Executar o assistant na thread
run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id="ID_DO_ASSISTANT_AQUI"
)

# Aguardar a resposta (em um caso real, você faria polling para verificar o status)
# ...

# Recuperar as mensagens mais recentes
messages = openai.beta.threads.messages.list(
    thread_id=thread.id
)

# Imprimir a resposta mais recente do assistant
print(messages.data[0].content[0].text.value)
""") 