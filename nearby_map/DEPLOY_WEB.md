# Web公開手順（実際にネットで視認する）

このプロジェクトは静的ファイルのみなので、GitHub Pages / Netlify / Vercel などで公開できます。

## 最短: GitHub Pages

1. このリポジトリを GitHub に push
2. GitHub の `Settings` → `Pages`
3. `Deploy from a branch` を選択
4. Branch: `work`（または main） / Folder: `/nearby_map`
5. 保存後に発行される URL を開く

## 公開URLでの表示

- オフライン前提 UI: `/app/`
- ネット公開向け（オンラインタイル取得）: `/app/?mode=online`
- 図面UI: `/blueprint_map/app/`

## 補足

- `?mode=online` は `config.json` の `source_template`（地理院タイルURL）から直接読み込みます。
- `?mode=offline`（デフォルト）は `tiles/std/...` を参照するため、タイル未配置時は空白になります。

## 利用規約チェック（公開前に必須）

1. 地理院タイルの利用規約ページ（`tiles.terms_url`）を確認する
2. 画面上に出典表示（`出典：地理院タイル（国土地理院）`）が常時あることを確認する
3. 大量アクセスを避ける（`download_tiles.py` は sleep/retry 付き）
4. 利用目的・配布形態が利用規約に反しないか最終確認する

> 規約に抵触する可能性がある場合は、公開を一旦停止してください。
