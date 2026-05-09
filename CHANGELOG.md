# AutoDrive Uploader v1.0.0

Primeira versao publica.

## Funcionalidades

### Principais
- Monitora uma pasta esperando videos novos (.mp4, .mov, .mkv, .avi)
- Detecta quando o render terminou via tamanho de arquivo estavel (30s)
- Faz upload pra pasta especifica do Google Drive
- Filtro por nome exato OU padrao glob (ex: `*.mp4`, `render_*.mov`)
- Move arquivo apos upload (opcional)
- Desliga PC ao terminar (opcional)
- Toca som ao terminar (opcional)

### Configuracoes
- Idioma: Portugues / Ingles (autodetecta no primeiro uso)
- Tema: Claro / Escuro
- Som: beep / notificacao Windows / arquivo .wav ou .mp3 customizado
- Apagar historico de uploads

### Conta Google Drive
- Conexao via OAuth (rclone authorize)
- Mostra email da conta conectada
- Botao desconectar

### Historico e logs
- Historico em JSONL com data, arquivo, tamanho, status
- Log de erros separado em texto plano
- Botao "Ver historico" abre janela com tabela
- Acesso direto ao log de erros pela mesma janela

## Arquitetura

### Modulos
- `main.py` - GUI Tkinter com tabs Principal/Configuracoes
- `uploader.py` - Logica de monitoramento (thread-based, polling)
- `rclone_manager.py` - Wrapper do rclone (auth, upload, account info)
- `config_store.py` - Persistencia de configs em `%APPDATA%\AutoDriveUploader\config.json`
- `history_store.py` - Historico (JSONL) e error log
- `sound_player.py` - winsound + mciSendString (mp3 nativo Windows)
- `i18n.py` - Sistema de traducoes PT/EN
- `version.py` - Le arquivo VERSION

### Onde os dados ficam
`%APPDATA%\AutoDriveUploader\`
- `config.json` - preferencias do usuario
- `rclone.conf` - token OAuth Google Drive
- `upload_history.jsonl` - historico de uploads
- `errors.log` - log de erros

## Limitacoes conhecidas
- Rate limit do rclone (client_id padrao compartilhado)
- Windows only (mciSendString, shutdown, winsound)
- Email da conta pode demorar 1-2s pra carregar apos conectar

## TODO pra proximas versoes
- Auto-download do rclone.exe no build.bat (se nao existir em bin\, baixa automaticamente)
