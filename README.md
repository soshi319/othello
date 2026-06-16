# オセロアプリ (Othello App)

Flet (Python) で制作した、AI対戦・観戦モード付きの本格的なオセロアプリです。
手元のPCで動かすための環境構築と起動手順を説明します。

## 📥 必要な環境・ダウンロードするもの

このアプリを動かすには、**Python** と、以下の **外部ライブラリ（パッケージ）** が必要です。

### 1. 必須ソフトウェア
* **Python 3.7 以上**（推奨）
    * ダウンロード先: [Python公式サイト](https://www.python.org/)
    * ※ インストール時、Windowsの場合は「Add Python.exe to PATH」に必ずチェックを入れてください。

### 2. 必要な外部ライブラリ
このアプリの画面（GUI）は以下のライブラリを使用して構築されています。
* **Flet (バージョン 0.21.2)**

---

## 🚀 インストールと起動手順

Git Bashやターミナルを開き、以下の手順で実行してください。

### 1. リポジトリのクローンと移動
```bash
git clone [https://github.com/soshi319/othello.git](https://github.com/soshi319/othello.git)
cd othello
```

### 2. 必須ライブラリのインストール
このアプリに必須である `flet` をインストールします。
```bash
pip install flet==0.21.2
```

### 3. アプリの起動
準備が完了したら、以下のコマンドでオセロアプリが全画面で起動します。
```bash
python main.py
```

### ② `KMP_DUPLICATE_LIB_OK` に関するエラーについて
Macや一部のWindows環境において、バックグラウンドの計算ライブラリが重複して強制終了するのを防ぐため、コード内で自動的に環境変数を制御する対策（`os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'`）を組み込んでいます。安心してお使いください。

---

## 📦 アプリの配布（Windows用 .exeファイルの作成）

PythonやFletがインストールされていないPCでも、すぐにオセロアプリを遊べるように「実行ファイル（.exe）」を作成することができます。

### 1. ビルドの実行
ターミナルまたはコマンドプロンプトで、プロジェクトのルートディレクトリ（一番上の階層）を開き、以下のコマンドを実行します。

```bash
flet pack src/main.py --add-data "src/assets;assets" --icon "src/assets/icon.ico"
```
