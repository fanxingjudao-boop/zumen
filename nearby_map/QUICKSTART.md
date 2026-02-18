# QUICKSTART

## 1) 設定検証

```bash
cd nearby_map
python3 validate_config.py
```

## 2) ダウンロード計画確認

```bash
python3 download_tiles.py --dry-run
```

## 3) タイル取得

```bash
python3 download_tiles.py --yes
```

## 4) サーバー起動

```bash
python3 -m http.server 8000
```

## 5) ブラウザで確認

- `http://localhost:8000/app/`
- `http://localhost:8000/blueprint_map/app/`
