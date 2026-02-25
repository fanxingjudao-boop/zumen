# QUICKSTART（最短実行フロー）

## 0. 前提

- 場所: `zumen-main` または `zumen-main/nearby_map`
- Windows では `run.bat` 系を使うと Python コマンド差異を吸収できます。

## 1. 設定検証

### Windows
```powershell
# repo直下でも nearby_map 配下でも可
.\run_validate.bat
```

### macOS/Linux
```bash
cd nearby_map
python3 validate_config.py
```

## 2. ダウンロード枚数の確認（必須）

### Windows
```powershell
.\run_dryrun.bat
```

### macOS/Linux
```bash
cd nearby_map
python3 download_tiles.py --dry-run
```

## 3. タイル収集

### Windows
```powershell
cd nearby_map
.\run.bat download --yes
```

### macOS/Linux
```bash
cd nearby_map
python3 download_tiles.py --yes
```

## 4. 起動

### Windows
```powershell
.\run_server.bat
```

### macOS/Linux
```bash
cd nearby_map
python3 -m http.server 8000
```

## 5. 画面確認

- 地図: `http://localhost:8000/app/`
- 図面: `http://localhost:8000/blueprint_map/app/`
- オンライン確認: `http://localhost:8000/app/?mode=online`

## 6. Windows向け補足

- 1つに統一したランチャー: `nearby_map/run.bat`
- サブコマンド:
  - `run.bat validate`
  - `run.bat dryrun`
  - `run.bat server`
  - `run.bat download --yes`
