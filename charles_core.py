import requests
import subprocess
import json
import os
import re
import shlex
import webbrowser  
from pathlib import Path

# ================= CONFIGURAÇÕES =================
CONFIG = {
    "ollama_url": "http://localhost:11434/api/generate",
    "modelo": "gemma4:31b-cloud",
    "memory_file": "charles_memory.json",
    "request_timeout": 30,
    "command_timeout": 60,
    "max_output_chars": 5000,
    "blacklist": ["rm -rf", "format", "del /s /q", "mkfs", "shutdown"]
}

SYSTEM_PROMPT = (
    "Você é o C.H.A.R.L.E.S., um assistente de IA sofisticado. "
    "Você possui duas formas de interagir com o sistema:\n"
    "1. [COMMAND] comando [/COMMAND] -> Para comandos de terminal REAIS (ex: ipconfig, ping).\n"
    "2. [ACTION] acao:argumento [/ACTION] -> Para automações nativas:\n"
    "   - [ACTION] open_url:url [/ACTION] (Abre sites)\n"
    "   - [ACTION] open_app:app [/ACTION] (Abre apps)\n"
    "   - [ACTION] create_folder:caminho [/ACTION] (Cria pastas em qualquer disco, ex: E:\\Test)\n"
    "   - [ACTION] list_files:caminho [/ACTION] (Lista arquivos de qualquer disco, ex: E:\\)\n"
    "   - [ACTION] search_file:nome [/ACTION] (Procura arquivos)\n"
    "Regras: NUNCA use o comando 'wmic'. Se precisar de pastas ou arquivos, use as [ACTION]. "
    "Para conversas, responda apenas com texto."
)
# =================================================

def carregar_memoria():
    try:
        if os.path.exists(CONFIG["memory_file"]):
            with open(CONFIG["memory_file"], "r", encoding="utf-8") as f:
                return json.load(f)
    except: return []

def salvar_memoria(historico):
    with open(CONFIG["memory_file"], "w", encoding="utf-8") as f:
        json.dump(historico[-20:], f, ensure_ascii=False, indent=4)

def perguntar_ao_gemma(prompt, historico):
    contexto = "\n".join([f"{m['role']}: {m['content']}" for m in historico]) 
    full_prompt = f"{SYSTEM_PROMPT}\n\nContexto:\n{contexto}\n\nUsuário: {prompt}"
    payload = {"model": CONFIG["modelo"], "prompt": full_prompt, "stream": False}
    try:
        response = requests.post(CONFIG["ollama_url"], json=payload, timeout=CONFIG["request_timeout"])
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e: return f"Erro de conexão: {e}"

# --- NOVAS CAPACIDADES DE AUTOMAÇÃO ---
def processar_acao(acao_str):
    try:
        comando, argumento = acao_str.split(":", 1)
        comando = comando.strip().lower()
        argumento = argumento.strip()

        if comando == "open_url":
            webbrowser.open(argumento)
            return f"Abrindo o site {argumento}."
        
        elif comando == "open_app":
            os.system(f"start {argumento}")
            return f"Iniciando o aplicativo {argumento}."

        elif comando == "create_folder":
            # os.makedirs cria a pasta e todas as pastas pai necessárias
            # exist_ok=True evita erro se a pasta já existir
            os.makedirs(argumento, exist_ok=True)
            return f"Pasta criada com sucesso em: {argumento}"
        
        elif comando == "list_files":
            # Lista arquivos de forma segura usando a biblioteca os
            try:
                arquivos = os.listdir(argumento)
                return f"Conteúdo de {argumento}: {arquivos[:20]}" # Limita a 20 itens
            except Exception as e:
                return f"Não consegui listar a pasta {argumento}. Erro: {e}"

        elif comando == "search_file":
            arquivos = list(Path('.').rglob(f"*{argumento}*"))
            if arquivos:
                return f"Encontrei: {[str(f) for f in arquivos[:5]]}"
            return "Nenhum arquivo encontrado."
        
        else:
            return f"Ação '{comando}' não reconhecida."
    except Exception as e:
        return f"Erro ao processar ação: {e}"

def executar_comando(comando_str):
    for termo in CONFIG["blacklist"]:
        if termo in comando_str.lower(): return "🚨 BLOQUEADO: Comando proibido."

    print(f"\n🛡️  C.H.A.R.L.E.S. solicita permissão: {comando_str}")
    confirmacao = input("Permitir? (s/n): ").strip().lower()
    if confirmacao in ['s', 'sim', 'yes']:
        try:
            args = shlex.split(comando_str)
            resultado = subprocess.run(args, capture_output=True, text=True, timeout=CONFIG["command_timeout"], shell=False)
            saida = resultado.stdout if resultado.stdout else resultado.stderr
            return saida[:CONFIG["max_output_chars"]] if saida else "Executado com sucesso."
        except Exception as e: return f"Erro: {str(e)}"
    return "Operação recusada."

def main():
    print("--- SISTEMAS C.H.A.R.L.E.S. ONLINE (v3.1 Automation) ---")
    historico = carregar_memoria()
    while True:
        try:
            usuario = input("\nVocê: ").strip()
            if not usuario or usuario.lower() in ["sair", "exit"]: break
            
            resposta = perguntar_ao_gemma(usuario, historico)
            
            # 1. Verifica se é um COMANDO de terminal
            match_cmd = re.search(r"\[COMMAND\](.*?)\[/COMMAND\]", resposta, re.DOTALL)
            # 2. Verifica se é uma AÇÃO de automação
            match_act = re.search(r"\[ACTION\](.*?)\[/ACTION\]", resposta, re.DOTALL)
            
            if match_cmd:
                comando = match_cmd.group(1).strip()
                resultado = executar_comando(comando)
                resposta_final = perguntar_ao_gemma(f"O comando {comando} retornou: {resultado}. Responda ao usuário.", historico)
                print(f"\nC.H.A.R.L.E.S.: {resposta_final}")
                historico.append({"role": "user", "content": usuario})
                historico.append({"role": "assistant", "content": resposta_final})
            
            elif match_act:
                acao = match_act.group(1).strip()
                resultado = processar_acao(acao)
                resposta_final = perguntar_ao_gemma(f"A ação {acao} resultou em: {resultado}. Responda ao usuário.", historico)
                print(f"\nC.H.A.R.L.E.S.: {resposta_final}")
                historico.append({"role": "user", "content": usuario})
                historico.append({"role": "assistant", "content": resposta_final})
            
            else:
                print(f"\nC.H.A.R.L.E.S.: {resposta}")
                historico.append({"role": "user", "content": usuario})
                historico.append({"role": "assistant", "content": resposta})
            
            salvar_memoria(historico)
        except KeyboardInterrupt: break

if __name__ == "__main__":
    main()
