<div align="center">

# 🦅 OpenHawk IA

### SO Global AI Intelligence para a Era dos Agentes

Desde documentos e lançamentos de modelos de fronteira até mercados de capitais, políticas e ecossistemas OSS:
buscar, desduplicar, analisar, assinar e enviar por push em uma plataforma, com interfaces MCP + CLI para fluxos de trabalho de agentes.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#docker-start)
[![MCP](https://img.shields.io/badge/MCP-Enabled-111827?style=for-the-badge)](#mcp-service)
[![CLI](https://img.shields.io/badge/Agent_CLI-Ready-0ea5e9?style=for-the-badge)](#agent-cli-new)
[![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)](LICENSE)

**📣 Canais push de assinatura**

![Feishu](https://img.shields.io/badge/Feishu-Notify-00C95A?style=flat-square)
![WeCom](https://img.shields.io/badge/WeCom-Notify-00A1FF?style=flat-square)
![WeChat](https://img.shields.io/badge/WeChat-Notify-05C160?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-Notify-2AABEE?style=flat-square)
![DingTalk](https://img.shields.io/badge/DingTalk-Notify-1677FF?style=flat-square)
![ntfy](https://img.shields.io/badge/ntfy-Notify-5B7FFF?style=flat-square)
![Bark](https://img.shields.io/badge/Bark-Notify-FF7A59?style=flat-square)
![Slack](https://img.shields.io/badge/Slack-Notify-4A154B?style=flat-square)
![Email](https://img.shields.io/badge/Email-Notify-6366F1?style=flat-square)

**🏷️ Tags importantes**

![AI Paper Radar](https://img.shields.io/badge/AI%20Paper%20Radar-Research%20Tracking-2563EB?style=flat-square)
![AI Frontier Radar](https://img.shields.io/badge/AI%20Frontier%20Radar-Model%20Releases-0EA5E9?style=flat-square)
![AI Finance](https://img.shields.io/badge/AI%20Finance-Global%20Markets-0891B2?style=flat-square)
![AI Industry Reports](https://img.shields.io/badge/AI%20Industry%20Reports-Institutional%20Insights-14B8A6?style=flat-square)
![AI Policy and Safety](https://img.shields.io/badge/AI%20Policy%20%26%20Safety-Regulation%20%26%20Risk-7C3AED?style=flat-square)
![AI OSS Signals](https://img.shields.io/badge/AI%20OSS%20Signals-Developer%20Ecosystem-1D4ED8?style=flat-square)
![Subscription Push](https://img.shields.io/badge/Subscription%20Push-Multi%20Channel-0F766E?style=flat-square)

<p align="center">
  <img src="image.png" alt="OpenHawk project banner" width="920" />
</p>

[中文](README.md) | [English](README-EN.md) | [हिन्दी](README-HI.md) | [Español](README-ES.md) | [العربية](README-AR.md) | [Français](README-FR.md) | **Português** | [বাংলা](README-BN.md) | [日本語](README-JA.md) | [한국어](README-KO.md)

</div>

## 🚀 Por que este projeto existe
Os sinais de IA são altamente fragmentados e se movem rapidamente. O rastreamento manual geralmente falha devido a:

- Canais fragmentados: documentos, anúncios de fornecedores, ganhos, atualizações de políticas e tendências de OSS estão desconectados.
- Ruído recente: notícias obsoletas continuam ressurgindo e eliminam novos sinais.
- Dor de desduplicação: repostagens distribuídas acionam ingestão repetida e notificações repetidas.
- Lacuna de automação: difícil integrar a "busca de inteligência" diretamente nos pipelines dos agentes.

O `OpenHawk` transforma isso em uma camada de inteligência extensível e sempre ativa que os agentes podem chamar diretamente.

## 👥 Para quem se destina
- Pesquisadores de IA: acompanhem continuamente a evolução de artigos e métodos.
- Equipes de produto e engenharia: rastreiam lançamentos, ferramentas e sinais do desenvolvedor.
- Equipes de investimento e estratégia: acompanhem ganhos, investimentos, financiamento e movimentos de mercado.
- Equipes de política e conformidade: rastreiam incidentes de regulamentação e segurança de IA em todas as regiões.
- Construtores de agentes: usam ferramentas MCP/CLI como recursos programáveis.

## 🧭 Seis páginas independentes (paralelas, não aninhadas)
| Página | Uso principal | Fontes Típicas |
| --- | --- | --- |
| Radar de papel AI | Acompanhamento acadêmico e análise profunda de artigos | arXiv e feeds de pesquisa |
| Fronteira de IA | Atualizações de modelo, produto e tecnologia | sites oficiais, blogs de fornecedores, laboratórios |
| Finanças de IA | Mercado de capitais e inteligência empresarial | ganhos, transcrições de chamadas, feeds de mercado, financiamento/M&A |
| Relatórios da indústria de IA | Pesquisa industrial e institucional | think tanks globais, instituições, whitepapers |
| Política e segurança de IA | Regulamentação e monitoramento de riscos | reguladores, órgãos políticos, fontes de incidentes de segurança |
| AI OSS e sinais de desenvolvimento | Ferramentas de código aberto e tendências do ecossistema de desenvolvimento | Tendências do GitHub + filtragem semântica README |

> Todas as seis páginas são independentes. Cada página possui configurações, assinaturas e regras de push isoladas.

## ⚙️ Capacidades essenciais
- Ingestão de múltiplas fontes com organização de origem orientada para a região.
- Histórico persistente + índices de desduplicação para evitar buscas/envios repetidos.
- Controle de atualidade (por exemplo, uma janela de 90 dias) para suprimir itens obsoletos.
- Pipeline de tradução unificado (qualquer idioma de destino) para títulos, análise LLM e conteúdo push.
- Notificações multicanal: `feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`.
- Estratégias de push inteligentes: `daily` / `incremental` / `realtime`.
- Busca agendada e trabalhos opcionais de assinatura automática.
- Interface da ferramenta MCP para integração de agentes baseada em protocolo.
- CLI do agente (novo) para invocação direta e programável de ferramentas locais.

## 🌐 Pipeline de tradução unificado (qualquer idioma de destino)
- Um pipeline em todas as camadas: `título`, `resumo/análise LLM` e `carga útil de notificação`.
- Suporte ao idioma de destino: `Inglês`, `Coreano`, `Japonês`, `Francês`, `Chinês`, `Chinês Tradicional`, além de idiomas de destino personalizados.
- Controle de custos: tradução em lote, preenchimento incremental de campos e reutilização persistente para evitar chamadas repetidas de API.
- Comportamento consistente: Web, MCP e CLI compartilham a mesma semântica `output_linguagem`, para que a interface do usuário e as saídas push permaneçam sincronizadas.

Exemplo (CLI):
```bash
# Set AI Finance page output language to Japanese
openhawk-ai-cli call save_scope_settings --args '{"scope":"market_finance","output_language":"Japanese"}'

# Fetch using this scope and language policy
openhawk-ai-cli call fetch_scope_items --args '{"scope":"market_finance","max_per_source":20}'
```

## 🧠 Estratégia de push inteligente
| Estratégia | Acionar | Melhor para | Característica |
| --- | --- | --- | --- |
| `diariamente` | Resumo agendado diariamente | Resumo executivo/equipe | Agregação completa de tópicos em cadência fixa |
| `incremental` | Janela agendada, somente novo | Monitoramento de rotina | Entrega incremental sem duplicação |
| `tempo real` | Push imediato acionado por evento | Principais lançamentos de modelos, quebras de políticas, alertas de financiamento | Sem espera pelo cronograma, maior pontualidade |

Notas:
- A estratégia é configurada por regra de assinatura e pode diferir nas 6 páginas.
- Pode ser combinado com filtros (origem, região, tipo de evento, palavras-chave) para roteamento preciso de alertas.

## 🧱 Arquitetura do Sistema
```text
             +---------------------------+
             |      Data Sources         |
             | papers / frontier / ...   |
             +-------------+-------------+
                           |
                           v
+----------------+   +------------+   +-------------------+
| Fetch & Dedupe |-->| Persistence|-->| Analysis & Routing|
+----------------+   +------------+   +-------------------+
                           |                    |
                           v                    v
                    +-------------+     +------------------+
                    | Web Console |     | Notification Push |
                    +------+------+     +------------------+
                           |
                +----------+----------+
                | MCP Server / CLI    |
                | (agent automation)  |
                +---------------------+
```

---

## ⚡ Início rápido
### 1) 🧩 Requisitos
-Python `>= 3.12`
- `uv` é recomendado
- Usuários do Docker: `Docker` + `Docker Compose`

### 2) 🖥️ Startup Local (Desenvolvimento)
```bash
uv sync --locked
```

1. Execute a busca/tempo de execução principal uma vez:
```bash
openhawk-ai
```

2. Execute o console da Web interativo (IU de 6 páginas):
```bash
python -m openhawk_ai.web.panel_server --port 8080 --output-dir output
```

3. Inicie o serviço MCP (HTTP):
```bash
openhawk-ai-mcp --transport http --host 0.0.0.0 --port 3333
```

### 3) 🐳 Início do Docker
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Portas padrão:
- Serviço Web: `WEBSERVER_PORT` (padrão: `8080`)
- Ponto de extremidade MCP: `http://127.0.0.1:3333/mcp`

Parar:
```bash
docker compose -f docker/docker-compose.yml down
```

Ver registros:
```bash
docker compose -f docker/docker-compose.yml logs -f
```

---

## 🤖 Agente CLI (Novo)
Para permitir que agentes/scripts chamem ferramentas OpenHawk diretamente sem transporte MCP, este repositório adiciona `openhawk-ai-cli`.

### 🎯 Metas de design
- Mesma superfície de capacidade das ferramentas MCP (mesmos nomes de ferramentas e semântica de argumentos).
- Entrada JSON e saída JSON para integração fácil de automação.
- Funciona bem com scripts de shell, pipelines de CI e executores de agentes.

### 🧪 Comando Básico
```bash
openhawk-ai-cli tools
```

### 📌 Exemplos comuns
1. Liste todas as ferramentas e parâmetros disponíveis:
```bash
openhawk-ai-cli tools
```

2. Chame uma ferramenta com JSON embutido:
```bash
openhawk-ai-cli call list_scope_items --args '{"scope":"market_finance","limit":20}'
```

3. Chame uma ferramenta com arquivo args:
```bash
openhawk-ai-cli call upsert_scope_subscription --args-file ./payload.json
```

4. Substitua a raiz do projeto e o diretório de saída:
```bash
openhawk-ai-cli --project-root . --output-dir ./output call get_project_overview
```

5. Saída JSON compacta (compatível com pipeline):
```bash
openhawk-ai-cli call list_scopes --compact
```

### Exemplos do Windows PowerShell (recomendado)
1. Use `ConvertTo-Json` com `--args-file` (mais confiável):
```powershell
$payload = @{ scope = "market_finance"; limit = 20 } | ConvertTo-Json -Compress
$payload | Set-Content -Encoding utf8 .\payload.json
openhawk-ai-cli call list_scope_items --args-file .\payload.json --compact
```

2. Use um arquivo aqui-string args:
```powershell
@'
{
  "scope": "frontier",
  "max_per_source": 20,
  "source_ids": ["openai-news", "anthropic-news"]
}
'@ | Set-Content -Encoding utf8 .\payload.json

openhawk-ai-cli call fetch_scope_items --args-file .\payload.json --compact
```

3. Ferramentas que não precisam de argumentos podem ser chamadas diretamente:
```powershell
openhawk-ai-cli call get_project_overview --compact
```

### 🧾 Códigos de saída
- `0`: sucesso
- `1`: erro de execução de tempo de execução/ferramenta
- `2`: parâmetros inválidos, ferramenta desconhecida ou JSON malformado

### 🛠️ Parâmetros CLI e cobertura
Argumentos fixos da CLI:

| Nível | Parâmetro | Descrição |
| --- | --- | --- |
| Global | `--projeto-raiz` | Substituir raiz do projeto |
| Global | `--output-dir` | Substituir diretório de saída |
| Global | `--compacto` | Emitir JSON compacto |
| Subcomando | `ferramentas` | Listar ferramentas disponíveis |
| Subcomando | `chamar <ferramenta>` | Invocar uma ferramenta |
| opção `ligar` | `--args` | Argumentos JSON embutidos |
| opção `ligar` | `--args-file` | Carregar argumentos JSON do arquivo |

Os argumentos de negócios da ferramenta são definidos por ferramenta. Usar:

```bash
openhawk-ai-cli tools --compact
```

Limite de cobertura:
- Abrange todos os recursos da ferramenta MCP atualmente expostos (22 ferramentas), incluindo visão geral, busca/lista/configurações/assinaturas de escopo e inteligência/assinaturas em papel.
- Não gerencia diretamente o ciclo de vida do processo/contêiner (por exemplo, iniciar/interromper processos do Docker ou do servidor Web).
- Não realiza interações de interface do usuário diretamente do navegador, mas cobre operações equivalentes da camada de dados (configurações, busca, assinaturas, push).

---

## 🔌 Serviço MCP
### Começar
```bash
# stdio
python -m mcp_server.server --transport stdio

# http
python -m mcp_server.server --transport http --host 0.0.0.0 --port 3333
```

Ponto de extremidade HTTP:

`http://127.0.0.1:3333/mcp`

### Grupos de ferramentas MCP
1. Visão geral do projeto
- `get_project_overview`
- `lista_páginas`
- `lista_escopos`

2. Configurações globais
- `get_global_settings`
- `save_global_settings`

3. Escopo de dados e busca
- `list_scope_sources`
- `list_scope_items`
- `fetch_scope_items`
- `get_scope_settings`
- `save_scope_settings`

4. Assinaturas de escopo
- `list_scope_subscriptions`
- `upsert_scope_subscription`
- `delete_scope_subscription`
- `run_scope_subscriptions`

5. Inteligência em papel
- `lista_papéis`
- `get_paper_detail`
- `deep_analyze_paper`
- `set_paper_action`

6. Assinaturas em papel
- `list_paper_subscriptions`
- `upsert_paper_subscription`
- `delete_paper_subscription`
- `run_paper_subscriptions`

---

## 🧠 Configuração
Diretório de configuração principal: `config/`

Arquivos principais:
- `config/config.yaml`: configuração principal do tempo de execução (busca, IA, push, armazenamento)
- `config/timeline.yaml`: predefinições de agendamento e regras de tempo
- `config/frequency_words.txt`: regras de frequência de palavras-chave
- `config/ai_interests.txt`: interesses do tópico
- `config/ai_análise_prompt.txt`: modelo de prompt de análise
- `config/ai_translation_prompt.txt`: modelo de prompt de tradução

Diretório de saída do tempo de execução: `output/`

Arquivos persistentes comuns:
- `output/ai_progress_items.json`
- `output/ai_progress_seen.json`
- `output/panel_settings.json`
- `output/progress_page_settings.json`
- `output/panel_subscriptions.json`
- `output/progress_subscriptions.json`
- `output/notícias/*.db`
- `saída/rss/*.db`

---

## 📣 Canais de notificação
Implementado de forma consistente em backend + frontend + MCP + CLI:
- `feishu`
- `trabalhamos`
- `wechat` (WeChat pessoal via modo de texto WeCom)
- `telegrama`
- `dingtalk`
- `ntfy`
- `latir`
- `folga`
- `e-mail`

---

## 🗂️ Estrutura do Projeto
```text
.
├─ openhawk_ai/                # Core runtime (fetch/analyze/push/web)
│  ├─ __main__.py             # Main entry
│  ├─ agent_cli.py            # Agent CLI entry (new)
│  └─ web/panel_server.py     # Interactive console server
├─ mcp_server/                # MCP server
├─ config/                    # Configuration and prompt templates
├─ docker/                    # Dockerfile / compose / entry scripts
├─ docs/assets/               # README visual assets (including OpenHawk SVG)
├─ output/                    # Runtime persistent data
├─ README.md
└─ README-EN.md
```

---

## ❓Perguntas frequentes
### Q1: Qual é a relação entre CLI e MCP?
A CLI chama diretamente as mesmas funções da ferramenta compatível com MCP. Use MCP para integração de protocolo e CLI para script/automação local.

### Q2: A CLI pode cobrir todos os recursos?
CLI cobre todos os recursos atualmente expostos pelo MCP (22 ferramentas). Se uma ação na UI for mapeada para operações da camada de dados (busca, consulta, configurações, assinaturas, push), ela normalmente será automatizável via CLI.

### Q3: Por que estou vendo mensagens duplicadas?
Verificar:
- se `output/ai_progress_seen.json` é persistido/montado corretamente
- se as regras de assinatura duplicadas estão configuradas
- se as assinaturas `timeline` e em nível de página estão acionando janelas sobrepostas

### Q4: Qual é o caminho mínimo de integração do agente?
Comece com:
```bash
openhawk-ai-cli call get_project_overview
```
Em seguida, chame `list_scope_items` / `list_papers` / `run_*_subscriptions` conforme necessário.

---

## 🙏 Agradecimentos e Referência
- Este projeto faz referência e é inspirado no [TrendRadar](https://github.com/sansan0/TrendRadar).
- OpenHawk estende a arquitetura de forma independente com seis páginas paralelas, estratégia de origem regionalizada, assinaturas multicanais e fluxos de trabalho integrados de MCP + Agent CLI.

---

## 📄 Licença
Este projeto está licenciado sob [Licença MIT](LICENSE).
