# C.H.A.R.L.E.S.

Assistente de IA local para interação conversacional, automações no sistema operacional e memória persistente. O projeto foi desenvolvido em Python com integração ao [Ollama](https://ollama.com/) e foi pensado como um laboratório prático de agentes, comandos estruturados e automação assistida por LLM.

> Projeto experimental de portfólio. Execute somente em um ambiente de testes e revise o código antes de permitir ações no sistema.

## O que o projeto demonstra

- Integração de uma aplicação Python com um modelo local servido pelo Ollama.
- Uso de instruções estruturadas para separar respostas conversacionais, comandos de terminal e ações de automação.
- Memória persistente das últimas interações em arquivo JSON.
- Automação de arquivos, pastas, sites e aplicativos.
- Confirmação explícita antes da execução de comandos de terminal.
- Lista inicial de comandos bloqueados para reduzir ações potencialmente destrutivas.
- Limitação do tamanho da saída retornada pelo terminal e tempo máximo de execução.

## Como funciona

O arquivo `charles_core.py` mantém um loop de conversa no terminal. Cada mensagem é enviada ao Ollama junto com o contexto recente e um prompt de sistema. A resposta pode conter uma destas estruturas:

- `[COMMAND] ... [/COMMAND]`: solicita um comando de terminal e exige confirmação do usuário.
- `[ACTION] ... [/ACTION]`: solicita uma ação nativa, como abrir uma URL, criar uma pasta, listar arquivos ou pesquisar um arquivo.
- Texto comum: é exibido diretamente como resposta conversacional.

A memória é salva em `charles_memory.json`, mantendo as últimas 20 mensagens do histórico.

## Requisitos

- Python 3.10 ou superior.
- Ollama instalado e em execução.
- Um modelo compatível disponível no Ollama. A configuração atual usa `gemma4:31b-cloud`; altere `CONFIG["modelo"]` em `charles_core.py` se necessário.
- Sistema operacional Windows para as ações de abertura de aplicativos atualmente implementadas com `start`.

## Instalação

```bash
git clone https://github.com/LucianoNeto0/C.H.A.R.L.E.S-AI.git
cd C.H.A.R.L.E.S-AI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Inicie o Ollama e confirme que a API está disponível em `http://localhost:11434`. Depois execute:

```bash
python charles_core.py
```

Digite `sair` ou `exit` para encerrar.

## Configuração principal

As opções ficam no dicionário `CONFIG` em `charles_core.py`:

- `ollama_url`: endereço da API do Ollama.
- `modelo`: modelo utilizado para gerar as respostas.
- `memory_file`: arquivo local de memória.
- `request_timeout`: tempo máximo de espera pela resposta do modelo.
- `command_timeout`: tempo máximo de execução de um comando confirmado.
- `max_output_chars`: limite de caracteres retornados pelo terminal.
- `blacklist`: termos bloqueados antes da execução.

## Segurança e limitações conhecidas

O C.H.A.R.L.E.S. executa ações reais no computador quando o usuário confirma um comando ou quando o modelo solicita uma ação permitida. A blacklist é uma camada inicial de proteção, não um sandbox e não deve ser tratada como uma barreira completa contra comandos perigosos. Antes de usar o projeto fora de um ambiente de testes, recomenda-se substituir a blacklist por uma allowlist de comandos, restringir diretórios autorizados, validar argumentos, registrar auditoria e executar o agente com permissões mínimas.

Nunca coloque chaves, senhas ou dados pessoais no repositório. O arquivo de memória pode conter conversas e deve ser tratado como dado local sensível.

## Tecnologias

- Python
- Requests
- Ollama
- Gemma
- JSON
- `subprocess`, `pathlib`, `webbrowser` e `shlex`

## Status

Protótipo funcional em evolução. O próximo passo natural é separar o núcleo conversacional das ferramentas, adicionar testes automatizados e criar uma camada de permissões mais granular.

## Autor

Luciano Cardoso do Rêgo Neto
GitHub: [@LucianoNeto0](https://github.com/LucianoNeto0)

## Licença

Este projeto não possui uma licença open source. O código é disponibilizado para demonstração e avaliação de portfólio; todos os direitos são reservados ao autor. Qualquer reutilização depende de autorização prévia.
