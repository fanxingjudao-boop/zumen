# 名古屋オフライン地図システム

国土地理院の地理院タイル（XYZ）を利用した、スタンドアロン前提のオフライン地図システムです。

## 構成

- `config.json`: 中心座標、ズーム、bbox、タイル設定
- `validate_config.py`: 設定検証
- `download_tiles.py`: タイルダウンローダー（再試行・進捗・推定付き）
- `app/index.html`: 周辺地図UI（オフラインタイル表示）
- `blueprint_map/app/index.html`: 図面マップUI（周辺地図への導線）

## セットアップ

```bash
cd nearby_map
python3 validate_config.py
python3 download_tiles.py --yes
```

> 大量ダウンロードの前に `--dry-run` でタイル枚数確認を推奨します。

## 実行

ローカルファイル直開きでは `fetch` 制限が出るため HTTP サーバーで起動してください。

```bash
cd nearby_map
python3 -m http.server 8000
```

- 周辺地図: `http://localhost:8000/app/`
- 図面UI: `http://localhost:8000/blueprint_map/app/`

## 重要事項

- 出典表示: `出典：地理院タイル（国土地理院）`
- `tiles.local_template` は相対パスのみ（`..` 禁止）
- 失敗タイルがある場合は `download_tiles.py` の再実行で再取得できます（既存ファイルはスキップ）。
