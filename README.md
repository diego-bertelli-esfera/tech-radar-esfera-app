# Tech Radar Corporativo Esfera — Projeto pronto para GitHub/Amplify

**Este diretório é o projeto de publicação da Fase 1, sem a etapa `bootstrap.sh`.**

## Importante: como a aplicação oficial é obtida

Este pacote inclui **toda a configuração da Esfera e os dados (48 tecnologias)**, mas **não incorpora fisicamente o código-fonte da Thoughtworks**. Como não foi possível transferir esse repositório para o ambiente de criação do arquivo, a etapa `git clone` foi deslocada para o **build do AWS Amplify** (`amplify.yml`), automaticamente e fixada na tag oficial `v1.2.0`. Isso evita qualquer `bootstrap.sh` no computador do usuário; é uma diferença de empacotamento, não de produto publicado.

Ao conectar este repositório privado ao Amplify, o serviço:

1. Valida `files/radar.csv` e os testes locais.
2. Obtém a versão `v1.2.0` do Thoughtworks BYOR no ambiente de build.
3. Executa `npm ci` e `npm run build:prod`.
4. Copia o frontend compilado para `dist/` e o CSV para `dist/files/radar.csv`.
5. Publica `dist/` no Hosting.

**Não é necessário instalar Node, clonar o BYOR nem rodar bootstrap no seu computador.** O ambiente de build precisa conseguir acessar o GitHub e o registro NPM. A base aberta da Thoughtworks utiliza licença AGPL-3.0; mantenha os avisos da distribuição oficial.

## Conteúdo

```text
tech-radar-esfera-app/
├── .github/workflows/
│   ├── sync-radar.yml              # Fase 2: recebe alteração do Power Automate
│   └── validate-radar.yml          # Teste de PR e push
├── .gitignore
├── amplify.yml                    # AWS Amplify: baixa e compila Thoughtworks
├── files/radar.csv                # Dados Esfera: 48 entradas
├── scripts/
│   ├── validate_radar.py          # Checagem de CSV
│   └── import_dispatch.py         # Conversão base64 recebida do workflow
├── tests/test_validator.py
└── docs/
    ├── FASE-1.md                  # Publicação manual inicial
    └── FASE-2.md                  # OneDrive + Power Automate (futuro)
```

## Começar agora (Fase 1)

```bash
cd tech-radar-esfera-app
python3 scripts/validate_radar.py files/radar.csv   # opcional, se tiver Python

git init -b main
git add .
git commit -m "feat: primeira publicacao do tech radar Esfera"
git remote add origin https://github.com/SUA-ORGANIZACAO/tech-radar-esfera.git
git push -u origin main
```

O repositório remoto deve ser **privado**, criado vazio (sem README). No AWS Amplify, use **Create new app > GitHub**, branch `main`, confirme o `amplify.yml` e faça o deploy.

Abra `https://SEU-DOMINIO.amplifyapp.com/files/radar.csv` para testar o CSV. Na interface do radar, informe essa URL e clique em **Build my radar**. O formulário da Thoughtworks não é modificado e o CSV não é carregado automaticamente.

Para o detalhamento, consulte [FASE 1](docs/FASE-1.md) e [FASE 2](docs/FASE-2.md).

## Segurança e limitações

O GitHub privado protege o **repositório**, não o site público. O Amplify Hosting é acessível na internet; configure proteção conforme política corporativa e proteja o acesso direto a `/files/radar.csv`. Basic Auth do Amplify serve apenas como restrição simples de piloto; não é SSO corporativo. Não publique dados sensíveis.

**Verificação efetuada:** conteúdo e validação locais do CSV, testes Python e integridade dos arquivos de automação. **Não realizado:** clone efetivo do upstream, build Node, deploy AWS ou teste integrado do Power Automate neste ambiente. O primeiro deploy no Amplify comprovará essas integrações.
