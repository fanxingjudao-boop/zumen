# 名古屋オフライン地図システム 実運用手順書（再作成版）

この手順書は、**壊れた状態から再確認**し、誰でも同じ手順で起動できるように整理したものです。

---

## 1. 目的

- 図面検索UI（ルート `/index.html`）と地図UI（`nearby_map/app`）を連携して運用する
- オフライン運用できるようタイルを事前収集する
- 収集方針は次の通り
  - 低ズーム（`nationwide_until_zoom` まで）は全国収集
  - それ以上の高ズームは名古屋のみ収集

---

## 2. 事前確認

### Linux / macOS

```bash
python3 --version
```

### Windows PowerShell

```powershell
py -3 --version
# だめなら
python --version
```

`python3` が見つからない場合は `run_*.bat` を利用してください。

---

## 3. 設定検証

```bash
cd nearby_map
python3 validate_config.py
```

Windows:

```powershell
cd nearby_map
.\run_validate.bat
```

成功条件:
- `Validation PASSED` が表示される

---

## 4. 収集計画の確認（必須）

```bash
python3 download_tiles.py --dry-run
```

Windows:

```powershell
.\run_dryrun.bat
```

確認ポイント:
- `Scope mode: mixed`
- `z11, z12: nationwide`
- `z13以上: nagoya`

---

## 5. タイル収集実行

```bash
python3 download_tiles.py --yes
```

Windows:

```powershell
py -3 download_tiles.py --yes
```

### 小さく動作確認したい場合（推奨）

```bash
python3 download_tiles.py --yes --scope nagoya --zmin 11 --zmax 11
```

---

## 6. 起動プロセス

### A. 地図アプリのみ起動

```bash
cd nearby_map
python3 -m http.server 8000
```

表示:
- `http://localhost:8000/app/`（オフライン）
- `http://localhost:8000/app/?mode=online`（確認用）

### B. 図面検索UIと連携して起動（実運用）

```bash
cd <repo-root>
python3 -m http.server 8000
```

表示:
- `http://localhost:8000/`（図面検索UI）

運用フロー:
1. 設備を検索
2. 検索結果をクリック
3. 図面セルと地図中心・マーカーが同期


### C. 図面と地図を往復する運用フロー（今回追加）

1. `http://localhost:8000/` を開く
2. 設備を1件選ぶ
3. `地図を新規タブで開く` を押す
4. 地図で位置確認後、`図面へ戻る` を押す
5. 図面一覧に戻ったら `この図面の地点を地図で開く` で再遷移

上記で、図面・検索・地図の往復が切れずに行えることを確認します。

---

## 7. 操作性（改善済み）

- 図面/地図/並列の表示切替
- ハザードレイヤー個別ON/OFF
- ハザード `全ON` / `全OFF`
- 地図方向パッド（↑↓←→）で一定量パン移動
- `◎` で名古屋中心へ、`📍` で選択地点へ復帰
- ズームスライダー、ダブルクリック拡大、`Shift + ダブルクリック`縮小、ピンチズーム
- キーボード: `+` / `-` / `r`
- スマホでパネル折りたたみ

---

## 8. この再検証で実施したチェック

1. `node --check app.js`
2. `python3 validate_config.py`
3. `python3 download_tiles.py --dry-run`
4. `python3 download_tiles.py --yes --scope nagoya --zmin 11 --zmax 11`
   - この環境では外部タイル取得が `403 Tunnel connection failed` で失敗（ネットワーク制限）

> したがって、**収集ロジック自体は正常**で、最終的な取得成功可否は実運用ネットワークで確認してください。

---

## 9. トラブルシューティング

### `python3` が無い（Windows）

- `py -3` を使う
- もしくは `run_validate.bat / run_dryrun.bat / run_server.bat`

### 地図が空白

- オフラインモードでタイル未収集の可能性
- `?mode=online` で表示確認
- その後オフラインタイル収集を実施

### 収集が失敗する

- プロキシ/ファイアウォール制限を確認
- 別ネットワークで再実行

