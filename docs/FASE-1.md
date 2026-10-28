# FASE 1 — Publicação inicial manual, sem bootstrap local

## Pré-requisitos

- Conta GitHub com permissão de criar um repositório privado.
- AWS Amplify Hosting com permissão de conectar o GitHub.
- Git local (Git Bash/WSL no Windows). Python é opcional para teste local.
- Aprovação de Segurança para hospedar radar e CSV via HTTPS no Amplify.

## Passo 1 — Projeto pronto

**Já executado no pacote entregue:** os arquivos de configuração e os 48 itens estão dentro de `tech-radar-esfera-app/`. **Não rode `bootstrap.sh`**; esse arquivo nem está incluído. A fonte oficial da Thoughtworks será obtida pelo próprio Amplify durante o build, conforme `amplify.yml`.

Confira:

```text
tech-radar-esfera-app/amplify.yml
tech-radar-esfera-app/files/radar.csv
tech-radar-esfera-app/.github/workflows/sync-radar.yml
```

Se desejar validar localmente, execute `python3 scripts/validate_radar.py files/radar.csv` na pasta do projeto.

## Passo 2 — Subir os arquivos ao GitHub

1. Em https://github.com/new, crie um repositório **privado, vazio** chamado `tech-radar-esfera` (não marque README, .gitignore ou licença).
2. Abra terminal no diretório **tech-radar-esfera-app** e execute:

```bash
git init -b main
git add .
git commit -m "feat: primeira publicacao Tech Radar Esfera"
git remote add origin https://github.com/SUA-ORGANIZACAO/tech-radar-esfera.git
git push -u origin main
```

Substitua a organização. Se Git pedir seu nome/e-mail, configure usando suas credenciais corporativas. Não coloque tokens em arquivos.

## Passo 3 — Publicar no Amplify

1. Acesse https://console.aws.amazon.com/amplify/ e clique **Create new app**.
2. Escolha **GitHub**. Autorize apenas o repositório `tech-radar-esfera`.
3. Selecione a branch `main`.
4. Confirme que o Amplify reconheceu o arquivo **`amplify.yml`** da raiz.
5. Salve e publique.
6. Nos logs, o Amplify deverá mostrar a obtenção de `thoughtworks/build-your-own-radar` na tag `v1.2.0`, instalação `npm ci`, build `npm run build:prod` e upload do `dist`.

**Atenção:** o ambiente do Amplify precisa ter acesso a `github.com` e a `npmjs.org` para compilar. Não é necessário instalar Node.js localmente. A tag oficial é usada como base imutável para o piloto.

## Passo 4 — Testar

Substitua o domínio ilustrativo abaixo pelo URL que o Amplify lhe fornecer:

```text
https://main.SEU-ID.amplifyapp.com/files/radar.csv
```

Deve abrir um CSV cujo cabeçalho é `name,ring,quadrant,isNew,description`.

Abra `https://main.SEU-ID.amplifyapp.com`, cole o URL acima no campo inicial e clique **Build my radar**. Verifique 48 itens e Bedrock (IA Corp)/Snowflake em **Platforms → Adopt**.

## Passo 5 — Proteger a aplicação

No AWS Amplify Hosting, configure **Access control** para o piloto, se aprovado. Teste a home e a URL `/files/radar.csv` em janela anônima. Proteção de leitura por senha simples não substitui SSO Entra ID. Certifique-se de que a documentação pode ser exibida através de uma aplicação com endpoint público.

## Passo 6 — Atualizações manuais, enquanto a automação não está ativa

Edite `files/radar.csv`, valide e faça push:

```bash
python3 scripts/validate_radar.py files/radar.csv
git add files/radar.csv
git commit -m "data: atualizar classificacoes do radar"
git push
```

Um push dispara um novo build do Amplify. A versão do Excel no OneDrive **não** sincroniza ainda. Depois de configurar a fase 2, as edições passam a ocorrer somente no Excel.

### Teste de aceite

- [ ] `amplify.yml` reconhecido no Console Amplify.
- [ ] Build oficial Thoughtworks compilado.
- [ ] CSV publicado em `/files/radar.csv`.
- [ ] 48 itens renderizados, incluindo Bedrock/Snowflake em Adopt.
- [ ] Política de acesso ao site e CSV confirmada.
