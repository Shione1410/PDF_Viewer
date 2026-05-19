# PDF Viewer

## 概要
このプロジェクトは、指定フォルダ下のPDFファイルを閲覧するための簡易PDFビューアです。

## 背景
フォルダのプレビュー欄の読み込みの反応が遅いので作成。
特にページを繰り、戻しを重視し、フォルダ内のPDFを資料群として閲覧しやすいようにしたいことを背景とする。

## 目的
- PDF閲覧機能の学習
- UI構築の練習
- Pythonライブラリの検証

## 主な機能
- PDFファイル読み込み
- ページ表示
- ページ送り / 戻し
- ズーム機能（あれば）
- サムネイル表示（あれば）

## 使用技術
- Python
- 使用ライブラリ:
- sys
- os
- shutil
- tracebac
- fitz # PyMuPDF
- PyQt6.Qtwidgets # QApplication, QMainWindow, QWidget, QVBoxLayout,  QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea, QComboBox
- PyQt6.QtGui # OPixmap, QImage
- PyQt6.QtCore


## フォルダ構成

project/
├ src/
├ data/
├ test/
└ README.md

## 実行方法

### 必要ライブラリインストール

```bash
pip install -r requirements.txt
