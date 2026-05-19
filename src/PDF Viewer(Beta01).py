import sys
import os
import shutil
import traceback
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea, QComboBox)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class PDFBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Strategic Browser v1.4 - Robust Edition")
        self.setGeometry(100, 100, 1100, 950)

        self.pdf_list = []
        self.current_idx = -1
        self.source_dir = ""
        self.target_dir = ""
        self.current_pixmap = None 

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 上部ツールバー ---
        toolbar_layout = QHBoxLayout()
        self.btn_change_source = QPushButton("📂 閲覧フォルダ変更")
        self.btn_change_target = QPushButton("🎯 保存フォルダ変更")
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["名前順（昇順）", "名前順（降順）", "新しい順", "古い順"])
        self.sort_combo.currentIndexChanged.connect(self.apply_sort)

        toolbar_layout.addWidget(self.btn_change_source)
        toolbar_layout.addWidget(self.btn_change_target)
        toolbar_layout.addWidget(QLabel(" 並び替え:"))
        toolbar_layout.addWidget(self.sort_combo)
        main_layout.addLayout(toolbar_layout)

        # 情報表示
        self.info_label = QLabel("フォルダを選択してください")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #f0f0f0; padding: 5px;")
        main_layout.addWidget(self.info_label)

        # PDF表示エリア
        self.scroll_area = QScrollArea()
        self.pdf_label = QLabel("PDF Not Loaded")
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setStyleSheet("background-color: #222; color: white;") 
        self.scroll_area.setWidget(self.pdf_label)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # 下部操作ボタン
        btn_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ 前へ")
        self.btn_next = QPushButton("次へ ▶")
        self.btn_copy = QPushButton("📁 コピー保存")
        
        btn_style = "padding: 15px; font-size: 14px; font-weight: bold;"
        self.btn_prev.setStyleSheet(btn_style)
        self.btn_next.setStyleSheet(btn_style)
        self.btn_copy.setStyleSheet(btn_style + "background-color: #0078D4; color: white;")

        self.btn_prev.clicked.connect(self.prev_pdf)
        self.btn_next.clicked.connect(self.next_pdf)
        self.btn_copy.clicked.connect(self.copy_current_pdf)
        self.btn_change_source.clicked.connect(self.change_source_dir)
        self.btn_change_target.clicked.connect(self.change_target_dir)

        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_next)
        main_layout.addLayout(btn_layout)

    def change_source_dir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "閲覧するフォルダを選択")
        if new_dir:
            self.source_dir = new_dir
            self.refresh_pdf_list()

    def change_target_dir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "コピー先の保存フォルダを選択")
        if new_dir:
            self.target_dir = new_dir
            self.info_label.setText(f"保存先: {os.path.basename(self.target_dir)}")

    def refresh_pdf_list(self):
        if not self.source_dir: return
        # 隠しファイルや~$で始まる一時ファイルを除外
        files = [f for f in os.listdir(self.source_dir) if f.lower().endswith('.pdf') and not f.startswith('~$')]
        
        sort_type = self.sort_combo.currentText()
        if sort_type == "名前順（昇順）": files.sort()
        elif sort_type == "名前順（降順）": files.sort(reverse=True)
        elif sort_type == "新しい順": files.sort(key=lambda x: os.path.getmtime(os.path.join(self.source_dir, x)), reverse=True)
        elif sort_type == "古い順": files.sort(key=lambda x: os.path.getmtime(os.path.join(self.source_dir, x)))

        self.pdf_list = files
        if self.pdf_list:
            self.current_idx = 0
            self.show_pdf()
        else:
            self.pdf_label.clear()
            self.pdf_label.setText("PDFが見つかりません")
            self.info_label.setText("指定フォルダにPDFファイルがありません。")

    def apply_sort(self):
        if self.source_dir and self.pdf_list:
            current_file = self.pdf_list[self.current_idx]
            self.refresh_pdf_list()
            if current_file in self.pdf_list:
                self.current_idx = self.pdf_list.index(current_file)
                self.show_pdf()

    def show_pdf(self):
        if 0 <= self.current_idx < len(self.pdf_list):
            filename = self.pdf_list[self.current_idx]
            abs_path = os.path.join(self.source_dir, filename)
            path_for_fitz = '\\\\?\\' + os.path.abspath(abs_path) if os.name == 'nt' else abs_path
            
            try:
                # PDFを開く
                doc = fitz.open(path_for_fitz)
                
                # 【修復戦術】構造エラー対策を安全に実行
                if doc.is_pdf:
                    try:
                        # 引数を指定せず、バージョンごとのデフォルトのクリーンアップを実行
                        doc.scrub() 
                    except Exception:
                        # scrub()でエラーが出た場合は無視して描画へ強行
                        pass
                
                if doc.page_count > 0:
                    page = doc.load_page(0)
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), colorspace=fitz.csRGB)
                    
                    # PNGバイト列に変換（メモリ管理の安定化）
                    img_data = pix.tobytes("png") 
                    qimg = QImage.fromData(img_data)
                    
                    self.current_pixmap = QPixmap.fromImage(qimg)
                    self.pdf_label.setPixmap(self.current_pixmap)
                    self.pdf_label.setFixedSize(self.current_pixmap.size())
                    self.info_label.setText(f"[{self.current_idx + 1}/{len(self.pdf_list)}] {filename}")
                else:
                    self.pdf_label.setText("白紙または読み取り不能なPDFです")
                
                doc.close()
            except Exception:
                # 詳細なエラーをターミナルに表示
                print(f"Error reading {filename}:\n{traceback.format_exc()}")
                self.pdf_label.setText(f"表示失敗: {filename}\nPDF構造に重大な欠陥があります")
                self.info_label.setText("読み込みエラー発生")

    def next_pdf(self):
        if self.current_idx < len(self.pdf_list) - 1:
            self.current_idx += 1
            self.show_pdf()

    def prev_pdf(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.show_pdf()

    def copy_current_pdf(self):
        if not self.target_dir:
            self.change_target_dir()
            if not self.target_dir: return

        if 0 <= self.current_idx < len(self.pdf_list):
            src = os.path.join(self.source_dir, self.pdf_list[self.current_idx])
            dst = os.path.join(self.target_dir, self.pdf_list[self.current_idx])
            try:
                shutil.copy2(src, dst)
                self.info_label.setText(f"【コピー完了】: {self.pdf_list[self.current_idx]}")
            except Exception as e:
                self.info_label.setText(f"コピー失敗: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFBrowser()
    window.show()
    sys.exit(app.exec())