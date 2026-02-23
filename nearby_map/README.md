# 名古屋オフライン地図システム

国土地理院の地理院タイル（XYZ）を利用した、スタンドアロン前提のオフライン地図システムです。

## 構成

- `config.json`: 中心座標、ズーム、bbox、タイル設定
- `validate_config.py`: 設定検証
- `download_tiles.py`: タイルダウンローダー（再試行・進捗・推定付き）
- `app/index.html`: 周辺地図UI（オフラインタイル表示 + ハザードマップ可視化）
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
- `tiles.terms_url` で規約参照先を管理し、公開前に確認する
- 規約に抵触する可能性がある場合は公開を停止する

## Web公開（インターネットでの視認）

`DEPLOY_WEB.md` の手順で公開できます。公開後は以下を利用してください。

- 通常（ローカルタイル）: `/app/`
- ネット公開向け（オンラインタイル）: `/app/?mode=online`


## ハザード可視化

- デモ円ではなく、公的ハザードタイルレイヤー（重ねるハザードマップ）を重畳表示します。
- レイヤー選択は右上パネルで切り替え可能です（洪水・高潮・土砂など）。
- ネットワーク制限環境ではハザードタイルが表示されない場合があります。
- 正式な訓練運用時は、自治体が指定する最新レイヤー構成に合わせて `config.json` の `hazard_layers` を更新してください。


## スマホ表示対応

- 画面幅が狭い場合、上部操作バーは2段表示になります。
- ハザードパネルは初期で折りたたみ、必要時に展開できます。
- ボタンサイズを拡大し、タッチ操作しやすくしています。


## Windows（PowerShell）での実行

`python3` が見つからない場合は、Windows では `py` ランチャーを使ってください。

```powershell
cd nearby_map
py -3 validate_config.py
py -3 download_tiles.py --dry-run
py -3 -m http.server 8000
```

### `py` も使えない場合

1. Python公式サイトからPython 3.10+ をインストール
2. インストーラの `Add python.exe to PATH` を有効化
3. PowerShell を再起動して確認

```powershell
py -3 --version
# または
python --version
```

Microsoft Store のエイリアスが邪魔する場合は、
`設定 > アプリ > アプリ実行エイリアス` で `python.exe` / `python3.exe` をオフにしてください。


## 全国+名古屋のハイブリッド収集方針

- `offline_collection_policy.nationwide_until_zoom` まで（既定: z12）は全国bboxを収集
- それより詳細ズーム（z13以上）は名古屋bboxのみ収集
- `download_tiles.py --dry-run` でズーム別枚数を確認できます


## 操作性向上ポイント

- ハザードレイヤーを `全ON` / `全OFF` で一括切替可能
- キーボード操作: `+`/`-` でズーム、`r` で中心リセット
