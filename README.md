# Case técnico — Automação reCAPTCHA v2 (RPA em Python)

Projeto de demonstração para o case: abrir a [página de demo do reCAPTCHA v2](https://www.google.com/recaptcha/api2/demo) várias vezes, interagir com o **checkbox** e tratar o **desafio de imagens** quando aparecer, com **logs estruturados**, **retry com backoff** e execução em **modo headless** ou **com janela**.

> **Importante (limitações técnicas)**  
> O reCAPTCHA foi criado justamente para dificultar automações. Sem serviços pagos de resolução (proibidos no case), **não há forma simples e confiável** de classificar as imagens do grid só com Selenium.  
> Por isso, a abordagem adotada neste projeto foi manter a automação no que é viável e, quando o desafio de imagens aparece, tratar esse cenário de forma controlada e bem documentada:
> - **Checkbox**: automação com Selenium + [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) (Chrome) para reduzir bloqueios comuns.
> - **Desafio de imagens**: detecção + logs no formato pedido; **resolução assistida manualmente**, o script **aguarda o token** `g-recaptcha-response` enquanto você (ou um operador) resolve o desafio no navegador **visível**.  
> Em **headless** com `ALLOW_MANUAL_SOLVE=false` (padrão no Docker), se o Google exibir o grid, a tentativa tende a **falhar**, isso está documentado e registrado em log.

## Estrutura de pastas

```
case-rpa/
├── src/
│   ├── __init__.py
│   ├── __main__.py          # python -m src
│   ├── principal.py         # CLI, loop de tentativas, backoff
│   ├── config.py            # variáveis de ambiente / .env
│   ├── logging_setup.py     # logs em console + logs/automacao.log
│   ├── navegador.py         # Chrome (undetected ou Selenium) / Firefox
│   └── recaptcha_fluxo.py   # iframes, checkbox, desafio, polling do token
├── logs/                    # arquivos .log (gitignore)
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Pré-requisitos (execução local)

- Python **3.11+**
- **Google Chrome** instalado (recomendado para a demo) **ou** Firefox + GeckoDriver (via `webdriver-manager`)

## Execução local

1. Clone/copie o projeto e entre na pasta:

   ```bash
   cd case-rpa
   ```

2. Crie o ambiente virtual e instale dependências:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   ```

3. Copie o exemplo de variáveis:

   ```bash
   copy .env.example .env        # Windows
   ```

4. Rode a automação:

   ```bash
   python -m src
   ```

   Com argumentos (sobrescrevem o `.env`):

   ```bash
   python -m src --browser chrome --headless false
   ```

### Headless x non-headless

| Objetivo | Configuração |
|----------|----------------|
| **Depurar**  | `.env`: `HEADLESS=false` ou `--headless false` |
| **Execução silenciosa** | `HEADLESS=true` ou `--headless true` |

Para **concluir o desafio de imagens**, use **`HEADLESS=false`** e `ALLOW_MANUAL_SOLVE=true` (padrão quando não é headless). Quando o log pedir, selecione as imagens e confirme no próprio Chrome; o script detecta o token e segue.

### Variáveis úteis (`.env`)

- `ATTEMPTS` — número de vezes que a página é aberta (case: **10**).
- `INTERVAL_SECONDS` — pausa entre tentativas (case: **~4**).
- `CHALLENGE_WAIT_SECONDS` — tempo máximo aguardando você resolver o grid.
- `BROWSER` — `chrome` ou `firefox`.

Logs também são gravados em `logs/automacao.log`.

## Docker

A imagem instala **Google Chrome** (Linux **amd64**). Em Mac **Apple Silicon**, pode ser necessário `--platform linux/amd64`.

Na pasta `docker`:

```bash
cd docker
docker compose up --build
```

No container, o padrão é `HEADLESS=true` e `ALLOW_MANUAL_SOLVE=false` (sem como interagir com o desafio visual). Use Docker para validar **fluxo, logs e checkbox**; para **desafio completo de imagens**, prefira execução **local com janela**.

### Trocar headless via Docker

Edite `docker-compose.yml` em `environment:` (por exemplo `HEADLESS: "false"`, ainda assim, sem display o navegador não aparece para você. Para depuração real use máquina local).

## Boas práticas implementadas

- Funções pequenas por responsabilidade (`config`, `navegador`, `fluxo reCAPTCHA`, `principal`).
- **Retry** com **backoff exponencial** após falhas.
- **Logs** em níveis INFO / WARNING / ERROR conforme o enunciado.
- **Sem** integração com 2Captcha, AntiCaptcha, etc.

## Publicação no GitHub

1. `git init` na pasta do projeto.
2. `git add .` e `git commit -m "Case RPA reCAPTCHA"`.
3. Crie um repositório no GitHub e faça `git remote add` + `git push`.

(Inclua `.env` apenas localmente — não commite segredos; use `.env.example`.)

## Licença de uso

Este código é para **estudo e avaliação técnica**. Respeite os [Termos de Serviço](https://policies.google.com/terms) do Google e políticas de sites alvo. Não use para contornar proteções em produção sem autorização.

# rpa_recaptcha
Projeto de automação em Python para o case técnico de reCAPTCHA v2, com Selenium, tratamento de falhas, logs e execução local ou via Docker.
