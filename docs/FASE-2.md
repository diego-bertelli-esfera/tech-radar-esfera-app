# FASE 2 — Sincronização automática OneDrive → Power Automate → GitHub → Amplify

A primeira fase deve estar funcionando antes desta configuração. Não crie outro aplicativo Amplify e não mude o repositório.

## 1. Publicar Excel oficial no OneDrive

Use a planilha `Tech_Radar_Esfera_OneDrive_Piloto.xlsx` entregue separadamente junto com o ZIP. Ele contém uma **Tabela Excel** chamada **Radar** (não apenas cinco colunas soltas) e 48 entradas. Envie ao OneDrive for Business autorizado. Abra no Excel e confirme em **Design da Tabela > Nome da Tabela: Radar**.

Cabeçalhos, nessa ordem: `name`, `ring`, `quadrant`, `isNew`, `description`. As novas linhas devem ser **adicionadas dentro da Tabela**. `isNew` é texto `TRUE`/`FALSE`. Se o Excel estiver em SharePoint, use o gatilho SharePoint para alteração, mas mantenha a ação Excel Online (Business) de leitura da tabela.

## 2. Conferir workflow GitHub

O arquivo `.github/workflows/sync-radar.yml` já está no projeto. Ele recebe `repository_dispatch` do tipo `radar_csv_updated` e espera `client_payload.csv_base64`. Em GitHub > **Actions**, confirme que o workflow **Sincronizar radar a partir do OneDrive** aparece. Em GitHub > Settings > Actions > General, permita que workflows tenham `contents: write` se a política corporativa autorizar. Proteção de branch que impeça o commit automático exigirá exceção controlada ou mudança para PR/approval.

## 3. Montar o fluxo Power Automate

Acesse https://make.powerautomate.com → **Create > Automated cloud flow**. Nome: `Sincronizar Tech Radar Esfera`.

| Ordem | Conector/ação | Configuração |
|---|---|---|
| 1 | OneDrive for Business / **When a file is modified (properties only)** | Selecione a pasta do arquivo no OneDrive |
| 2 | **Condition** | Prossiga só quando `Name` for `Tech_Radar_Esfera_OneDrive.xlsx` |
| 3 | **Delay** | 30 segundos (reduz leitura durante salvamento) |
| 4 | Excel Online (Business) / **List rows present in a table** | Location: OneDrive for Business; biblioteca: OneDrive; arquivo: o Excel; tabela: `Radar` |
| 5 | Data Operations / **Select** | Projetar somente as cinco colunas na ordem correta |
| 6 | Data Operations / **Create CSV table** | From: saída de `Select`; Columns: Automatic |
| 7 | Data Operations / **Compose** (renomear para `CSV_BASE64`) | Converter o CSV em base64 |
| 8 | GitHub / **Create a repository dispatch event (Preview)** | Enviar `radar_csv_updated` com `client_payload.csv_base64` |

No gatilho, ative **concurrency=1** para evitar duas execuções simultâneas e configure retry quando necessário. No Excel Online, habilite **Pagination** com threshold de 1000, caso a lista cresça (o padrão lista até 256 linhas). O gatilho OneDrive pode disparar duplicado, e o workflow GitHub não faz commit quando o CSV não muda.

### 3.1 — Data Operations / Select

**From:** selecione o conteúdo dinâmico `value` da ação `List rows present in a table` (ou a expressão `body('List_rows_present_in_a_table')?['value']`, substituindo pelo nome interno correto da sua ação).

Mapeie as chaves **literalmente**, com os seguintes valores pela aba Expression:

| Chave (texto) | Value (expressão) |
|---|---|
| `name` | `item()?['name']` |
| `ring` | `item()?['ring']` |
| `quadrant` | `item()?['quadrant']` |
| `isNew` | `if(equals(toLower(string(item()?['isNew'])),'true'),'TRUE','FALSE')` |
| `description` | `item()?['description']` |

Observação: configure as cinco chaves como texto e os valores como **Expression**, não texto fixo. O conector retorna outras colunas internas do Excel; `Select` evita publicá-las no CSV.

### 3.2 — Data Operations / Create CSV table

**From:** `Body` da ação `Select`. **Columns:** `Automatic`. A saída é um CSV textual com cabeçalhos. Confira a prévia no histórico de execução.

### 3.3 — Data Operations / Compose

Renomeie a ação para `CSV_BASE64`. Use expressão:

```text
base64(body('Create_CSV_table'))
```

Substitua `Create_CSV_table` pelo nome interno exibido no seu fluxo se for diferente.

### 3.4 — GitHub / Create a repository dispatch event (Preview)

- Repository Owner: `SUA-ORGANIZACAO`
- Repository Name: `tech-radar-esfera`
- Event Name: `radar_csv_updated`
- Event Payload: na aba **Expression**, cole:

```text
json(concat('{"csv_base64":"', outputs('CSV_BASE64'), '"}'))
```

O campo deve representar um **objeto JSON**, não uma string literal. Estrutura final: `{"csv_base64":"<texto_base64>"}`. A ação é **Preview**, mesmo que o conector GitHub seja Standard; confirme no tenant a disponibilidade e a permissão de usar o GitHub.

## 4. Conferir a execução ponta a ponta

1. Salve e habilite o fluxo no Power Automate.
2. Edite a descrição de um item no Excel, salve e abra o histórico do fluxo.
3. Abra **GitHub > Actions > Sincronizar radar...** e verifique se houve uma execução bem-sucedida.
4. Confirme um novo commit `data: sincronizar radar a partir do OneDrive` na branch main.
5. Acesse **Amplify > Deployments** e confirme um novo build com estado **Deployed**.
6. Reabra o radar, carregue `/files/radar.csv` e confira a descrição alterada.

O Python (`scripts/import_dispatch.py`) decodifica/valida os dados antes de escrever `files/radar.csv`. Em erro de CSV, a última versão permanece publicada. O workflow ignora CSV idêntico, evitando deploys desnecessários.

## 5. Garantir deploy após commit do bot — alternativa de webhook

**Teste o comportamento real da integração GitHub → Amplify.** O commit feito com o `GITHUB_TOKEN` não cria outros workflows GitHub, e **não é garantido por isso que sua integração Amplify terá o comportamento desejado**. Se o CSV for commitado, mas o Amplify não iniciar um deploy:

1. Amplify > **Hosting > Build settings > Incoming webhooks > Create webhook**. Nome: `radar-sync`, branch `main`.
2. Copie a URL secreta do webhook.
3. GitHub > **Settings > Secrets and variables > Actions > New repository secret**: Nome `AMPLIFY_WEBHOOK_URL`, valor a URL copiada.
4. O workflow `sync-radar.yml` já contém o passo **Acionar Amplify por webhook (opcional)**, que executa POST após commit somente se o segredo existir.
5. Se o push já disparar automaticamente o Amplify, **não configure** o webhook (evita builds duplicados). Se for usar webhook e ambos dispararem, desabilite o auto-build no branch ou remova o webhook.

A URL do webhook é segredo; não a grave no OneDrive, CSV ou Git. Ela permite iniciar builds.

## 6. Falhas, reversão e limites

- Falha no Power Automate: consultar histórico, credenciais dos conectores, nome da tabela `Radar` e paginação.
- GitHub Actions falhou: olhar log da validação. Não há substituição do CSV inválido no Git.
- Amplify falhou: investigar logs do build; a versão anterior permanece hospedada se o deploy não finalizar.
- **Rollback**: `git revert <SHA>` e push. Também **corrija o Excel** para que a próxima sincronização não restaure o conteúdo revertido.
- GitHub `repository_dispatch` limita payload a aproximadamente 64 KB; o CSV inicial possui ~8 KB, e o validador limita a 48 KB.
- GitHub repo privado e website protegido são **dois controles diferentes**. O CSV integra a publicação do site e pode ser lido por quem acessar a aplicação.

## Checklist de aceite

- [ ] Excel no OneDrive, Tabela `Radar` reconhecida no Power Automate.
- [ ] `Select` produz apenas os cinco cabeçalhos esperados.
- [ ] Evento `repository_dispatch` executa o workflow.
- [ ] GitHub commit ocorre apenas após alteração válida.
- [ ] Amplify constrói nova versão após o commit (ou webhook habilitado).
- [ ] Site e CSV protegidos conforme Segurança Corporativa.
