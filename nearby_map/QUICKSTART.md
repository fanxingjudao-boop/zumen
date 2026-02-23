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


## 公開URLで確認する場合

- `.../app/?mode=online` でオンラインタイル表示

- 公開前に `config.json` の `tiles.terms_url` から利用規約を確認


## Windowsで `python3` が使えない場合

PowerShell では次を使ってください。

```powershell
py -3 validate_config.py
py -3 download_tiles.py --dry-run
py -3 -m http.server 8000
```

`py` がない場合はPythonをインストールし、`Add python.exe to PATH` を有効にしてください。


## ズーム別の収集範囲を確認

```bash
python3 download_tiles.py --dry-run
```

`z12までは全国、z13以上は名古屋` の方針で枚数が表示されます。
