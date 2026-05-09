# AutoDrive Uploader

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/WolfgangPonce)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-green?style=for-the-badge&logo=python&logoColor=white)

Windows app that watches a folder and automatically uploads videos to Google Drive. Useful for long renders in Media Encoder, or any workflow where you want to go to bed and let the computer handle it.

## Download

Grab the latest version from [Releases](https://github.com/WolfgangPonce/AutoDriveUploader/releases) and run `AutoDriveUploader.exe`. No install, no manual OAuth setup.

## Features

**Core:**
- Watches a folder for new videos (`.mp4`, `.mov`, `.mkv`, `.avi`)
- Detects when render finished (file size stable for 30s)
- Uploads to a specific Google Drive folder
- Filter by exact name OR glob pattern (e.g. `*.mp4`, `render_*.mov`)
- Move file to another folder after upload (optional)
- Shut down PC when done (optional)
- Play sound when done (optional, configurable)
- Shows which Google account is connected

**Settings:**
- Language: Portuguese / English (autodetects on first run)
- Theme: Light / Dark
- Finish sound: beep, Windows notification, or custom `.wav`/`.mp3` file
- Clear all history

**History and logs:**
- Upload history (date, file, size, status)
- Separate error log for debugging

## How to use

1. **Connect your Google Drive account**
   - Click "Connect"
   - Browser opens asking you to log in and authorize
   - Confirm and close the browser
   - Status changes to "Connected: your@email.com"

2. **Paste the destination Drive folder link**
   - Open the folder in Drive in your browser
   - Copy the full URL
   - Paste it in the field

3. **Pick the folder to watch** (where Media Encoder/Premiere/etc renders)

4. **Set the file filter**
   - **Pattern**: matches multiple files. E.g. `*.mp4`, `render_*.mov`
   - **Exact name**: matches one file only. E.g. `final_video.mp4`

5. **(Optional) Check "move after upload"** and pick a destination folder

6. **(Optional) Check "shut down PC after finishing"** or "play sound when done"

7. **Click "Start monitoring"** and you can go to sleep

## Build from source

### Prerequisites

- **Python 3.11+** with "Add Python to PATH" checked
- **rclone.exe** downloaded from https://rclone.org/downloads/ and placed in `bin/rclone.exe`

### Build

```cmd
build.bat
```

The script reads the version from the `VERSION` file, compiles, and organizes everything in:

```
C:\Users\<you>\OneDrive\Documents\Apps\Autodrive Uploader\<version>\
├── AutoDriveUploader.exe
├── CHANGELOG.md
└── source\
```

### Versioning

Scheme used: `1.X.Y` (simplified semver)
- **X** bumps for big changes (new feature, refactor, breaking change)
- **Y** bumps for small changes (bugfix, UI tweak, polish)

## Project structure

```
AutoDriveUploader/
├── main.py              # Main GUI (Tkinter)
├── uploader.py          # Folder monitoring logic
├── rclone_manager.py    # rclone wrapper
├── config_store.py      # Config persistence
├── history_store.py     # Upload history and error log
├── sound_player.py      # Sound player (winsound + mciSendString)
├── i18n.py              # Translation system (PT/EN)
├── version.py           # Reads VERSION file
├── bin/
│   └── rclone.exe       # You download and place this here
├── VERSION              # 1.0.0
├── CHANGELOG.md
├── build.bat
├── build.spec
└── requirements.txt
```

## Where data is stored

`%APPDATA%\AutoDriveUploader\`

- `config.json` - user preferences (language, theme, paths, etc)
- `rclone.conf` - Google Drive OAuth token
- `upload_history.jsonl` - upload history
- `errors.log` - error log

To reset everything, delete that folder.

## Known limitations

- **Windows only** (mciSendString, shutdown, winsound are Windows-specific)
- **rclone rate limit**: the app uses rclone's default client_id, which is shared across users. Fine for personal use and a few friends.
- **Account email** may take 1-2s to load after connecting
- **Custom mp3**: some uncommon codecs might not play. Use `.wav` if you run into issues.

## Troubleshooting

**"rclone.exe not found"**: download from https://rclone.org/downloads/ and put it in `bin/`.

**App opens in Portuguese but I want English**: go to Settings > Language > English.

**Sound not playing**: test it first with "Test sound" in the Settings tab.

## Support

If AutoDrive Uploader is useful to you, you can [buy me a coffee](https://www.buymeacoffee.com/WolfgangPonce) ☕. Helps keep projects like this going.

## License

Free for personal use.
