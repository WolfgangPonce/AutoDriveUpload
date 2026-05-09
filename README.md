# AutoDrive Uploader

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/WolfgangPonce)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-green?style=for-the-badge&logo=python&logoColor=white)

App pra Windows que monitora uma pasta e faz upload automatico de videos pro Google Drive. Util pra renders longos do Media Encoder ou qualquer outro fluxo onde voce quer ir dormir e o computador resolve.

## Download

Baixe a versao mais recente em [Releases](https://github.com/WolfgangPonce/AutoDriveUploader/releases) e rode o `AutoDriveUploader.exe`. Sem instalacao, sem configuracao manual de OAuth.

## Funcionalidades

**Principais:**
- Monitora uma pasta esperando videos novos (`.mp4`, `.mov`, `.mkv`, `.avi`)
- Detecta quando o render terminou (tamanho do arquivo estavel por 30s)
- Faz upload pra pasta especifica do Google Drive
- Filtro por nome exato OU padrao glob (ex: `*.mp4`, `render_*.mov`)
- Move arquivo pra outra pasta apos upload (opcional)
- Desliga o PC quando termina (opcional)
- Toca som quando termina (opcional, configuravel)
- Mostra qual conta Google esta conectada

**Configuracoes:**
- Idioma: Portugues / Ingles (autodetecta no primeiro uso)
- Tema: Claro / Escuro
- Som ao terminar: beep, notificacao Windows, ou arquivo .wav/.mp3 customizado
- Apagar todo o historico

**Historico e logs:**
- Historico de todos os uploads (data, arquivo, tamanho, status)
- Log de erros separado pra debug

## Como usar

1. **Conecta a conta do Google Drive**
   - Clica em "Conectar"
   - Vai abrir o navegador pedindo pra logar e autorizar
   - Confirma e fecha o navegador
   - Status muda pra "Conectado: seu@email.com"

2. **Cola o link da pasta destino do Drive**
   - Abre a pasta no Drive pelo navegador
   - Copia a URL completa
   - Cola no campo

3. **Seleciona a pasta a monitorar** (onde o Media Encoder/Premiere/etc renderiza)

4. **Define o filtro de arquivo**
   - **Padrao**: aceita varios. Ex: `*.mp4`, `render_*.mov`
   - **Nome exato**: so aceita um. Ex: `video_final.mp4`

5. **(Opcional) Marca "mover apos upload"** e escolhe a pasta destino

6. **(Opcional) Marca "desligar PC apos terminar"** ou "tocar som ao terminar"

7. **Clica em "Iniciar monitoramento"** e pode ir dormir

## Buildar do source

### Pre-requisitos

- **Python 3.11+** com "Add Python to PATH" marcado
- **rclone.exe** baixado de https://rclone.org/downloads/ e colocado em `bin/rclone.exe`

### Build

```cmd
build.bat
```

O script le a versao do arquivo `VERSION`, compila e organiza tudo em:

```
C:\Users\<voce>\OneDrive\Documents\Apps\Autodrive Uploader\<versao>\
├── AutoDriveUploader.exe
├── CHANGELOG.md
└── source\
```

### Versionamento

Esquema usado: `1.X.Y` (semver simplificado)
- **X** sobe em mudancas grandes (feature nova, refactor, breaking change)
- **Y** sobe em mudancas pequenas (bugfix, ajuste de UI, polimento)

## Estrutura

```
AutoDriveUploader/
├── main.py              # GUI principal (Tkinter)
├── uploader.py          # Logica de monitoramento
├── rclone_manager.py    # Wrapper do rclone
├── config_store.py      # Persistencia de configs
├── history_store.py     # Historico de uploads e log de erros
├── sound_player.py      # Player de sons (winsound + mciSendString)
├── i18n.py              # Sistema de traducoes (PT/EN)
├── version.py           # Le arquivo VERSION
├── bin/
│   └── rclone.exe       # Voce baixa e coloca aqui
├── VERSION              # 1.0.0
├── CHANGELOG.md
├── build.bat
├── build.spec
└── requirements.txt
```

## Onde os dados ficam salvos

`%APPDATA%\AutoDriveUploader\`

- `config.json` - preferencias (idioma, tema, paths, etc)
- `rclone.conf` - token OAuth do Google Drive
- `upload_history.jsonl` - historico de uploads
- `errors.log` - log de erros

Pra resetar tudo, deleta a pasta inteira.

## Limitacoes conhecidas

- **Windows only** (mciSendString, shutdown, winsound sao especificos do Windows)
- **Rate limit do rclone**: o app usa o client_id padrao do rclone, compartilhado entre usuarios. Pra uso pessoal e poucos amigos funciona bem.
- **Email da conta** pode demorar 1-2s pra carregar apos conectar
- **mp3 customizado**: alguns codecs raros podem nao tocar. Use `.wav` se der problema.

## Troubleshooting

**"rclone.exe nao encontrado"**: baixa em https://rclone.org/downloads/ e coloca em `bin/`.

**App abre em ingles mas quero portugues**: vai em Configuracoes > Idioma > Portugues.

**Som nao toca**: testa primeiro com "Testar som" na aba Configuracoes.

## Suporte

Se o AutoDrive Uploader te ajudou, voce pode [me pagar um cafe](https://www.buymeacoffee.com/WolfgangPonce) ☕. Ajuda a manter projetos como esse.

## Licenca

Uso pessoal e livre.
