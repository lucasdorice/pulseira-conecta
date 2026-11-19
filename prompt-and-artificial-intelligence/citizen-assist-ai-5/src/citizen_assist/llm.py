"""Chamada ao modelo local via Ollama. Nada sai da máquina do usuário."""
import os

MODELO_AGENTE = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
MODELO_JUIZ = os.getenv("OLLAMA_JUDGE_MODEL", "qwen2.5:7b")   # modelo diferente do agente, para reduzir viés
URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def gerar_ollama(sistema: str, usuario: str, modelo: str = None) -> str:
    from langchain_ollama import ChatOllama   # import tardio: os testes não exigem Ollama
    llm = ChatOllama(model=modelo or MODELO_AGENTE, temperature=0, base_url=URL,
                     client_kwargs={"timeout": 180})   # evita ficar travado sem resposta
    return llm.invoke([("system", sistema), ("human", usuario)]).content.strip()
