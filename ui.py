import sys
import os
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox,
    QGroupBox, QStatusBar, QProgressBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from form import ExcelForm, CSVForm

class FileLoaderWidget(QWidget):
    def __init__(self, title, debug=False):
        super().__init__()
        self.title = title
        self.form = None
        self.debug = debug
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 15, 10, 15)
        main_layout.setSpacing(10)

        # 创建分组框
        group_box = QGroupBox(f"{self.title}文件设置")
        group_box.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout = QVBoxLayout(group_box)
        layout.setSpacing(10)

        # 文件选择部分
        file_layout = QHBoxLayout()
        self.file_label = QLabel(f"文件路径：")
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText(f"选择{self.title}文件...")
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.setStyleSheet("padding: 5px;")
        self.browse_btn.clicked.connect(self.browse_file)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_input, 1)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # 工作表选择容器
        self.sheet_widget = QWidget()
        sheet_layout = QHBoxLayout(self.sheet_widget)
        sheet_layout.setContentsMargins(0, 0, 0, 0)
        self.sheet_label = QLabel("工作表：")
        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(150)
        sheet_layout.addWidget(self.sheet_label)
        sheet_layout.addWidget(self.sheet_combo, 1)
        self.sheet_widget.setVisible(False)
        layout.addWidget(self.sheet_widget)
        self.sheet_combo.currentTextChanged.connect(self.handle_sheet_change)

        # 索引列选择
        self.index_widget = QWidget()
        index_layout = QHBoxLayout(self.index_widget)
        index_layout.setContentsMargins(0, 0, 0, 0)
        self.index_label = QLabel("索引列：")
        self.index_combo = QComboBox()
        self.index_combo.setMinimumWidth(150)
        index_layout.addWidget(self.index_label)
        index_layout.addWidget(self.index_combo, 1)
        self.index_widget.setVisible(False)
        layout.addWidget(self.index_widget)
        self.index_combo.currentTextChanged.connect(self.set_index_col)

        # 更新列选择
        if self.title == "数据源":
            update_layout = QHBoxLayout()
            self.update_col_label = QLabel("更新列：")
            self.update_col_combo = QComboBox()
            self.update_col_combo.setMinimumWidth(150)
            update_layout.addWidget(self.update_col_label)
            update_layout.addWidget(self.update_col_combo, 1)
            layout.addLayout(update_layout)

        # 文件状态指示
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("未加载文件")
        self.status_indicator.setStyleSheet("color: gray; font-style: italic;")
        status_layout.addStretch()
        status_layout.addWidget(self.status_indicator)
        layout.addLayout(status_layout)

        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"选择{self.title}文件", "",
            "表格文件 (*.xlsx *.xls *.csv)"
        )
        if file_path:
            self.file_input.setText(file_path)
            self.status_indicator.setText("正在加载...")
            self.status_indicator.setStyleSheet("color: blue;")
            QApplication.processEvents()
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            if file_path.endswith('.csv'):
                self.form = CSVForm(file_path)
                file_type = "CSV文件"
            elif file_path.endswith(('.xlsx', '.xls')):
                self.form = ExcelForm(file_path)
                file_type = "Excel文件"
                sheet_names = self.form.get_sheet_names()
                if len(sheet_names) > 1:
                    self.sheet_combo.clear()
                    self.sheet_combo.addItems(sheet_names)
                    self.sheet_widget.setVisible(True)
                else:
                    self.form.load_sheet(sheet_names[0])
                    self.sheet_widget.setVisible(False)
            else:
                raise ValueError("不支持的文件格式")

            self.update_index_combo()
            self.status_indicator.setText(f"{file_type}已加载 ✓")
            self.status_indicator.setStyleSheet("color: green; font-weight: bold;")

        except Exception as e:
            self.status_indicator.setText(f"加载失败: {str(e)}")
            self.status_indicator.setStyleSheet("color: red;")
            if self.debug:
                QMessageBox.critical(self, "错误", str(traceback.format_exc()))
            else:
                QMessageBox.critical(self, "错误", str(e))

    def handle_sheet_change(self):
        sheet_name = self.sheet_combo.currentText()
        self.status_indicator.setText(f"加载工作表: {sheet_name}...")
        self.status_indicator.setStyleSheet("color: blue;")
        QApplication.processEvents()
        self.form.load_sheet(sheet_name)
        self.update_index_combo()
        self.status_indicator.setText(f"工作表 '{sheet_name}' 已加载 ✓")
        self.status_indicator.setStyleSheet("color: green; font-weight: bold;")

    def update_index_combo(self):
        if self.form:
            self.index_combo.clear()
            self.index_combo.addItems(self.form.get_col_names())
            self.index_widget.setVisible(True)
            if hasattr(self, 'update_col_combo'):
                self.update_col_combo.clear()
                self.update_col_combo.addItems(self.form.get_col_names())

    def set_index_col(self):
        if self.form:
            index_col = self.index_combo.currentText()
            self.form.set_index_col(index_col)

class MainWindow(QMainWindow):
    def __init__(self, debug=False):
        super().__init__()
        self.sour = None
        self.dest = None
        self.debug = debug
        self.init_ui()
        self.apply_styles()

        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def init_ui(self):
        self.setWindowTitle("表格数据合并工具")
        self.setGeometry(100, 100, 700, 500)

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 顶部标题和说明
        header = QLabel("表格数据合并工具")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        description = QLabel("此工具用于合并两个表格的数据，基于共同的索引列将数据源填入目标表格中")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 使用分割器使两个文件加载器可以调整大小
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 源文件加载
        self.source_loader = FileLoaderWidget("数据源", self.debug)
        splitter.addWidget(self.source_loader)

        # 目标文件加载
        self.dest_loader = FileLoaderWidget("目标", self.debug)
        splitter.addWidget(self.dest_loader)

        layout.addWidget(splitter, 1)  # 分配拉伸空间

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 操作按钮区域
        btn_group = QGroupBox("操作")
        btn_layout = QHBoxLayout(btn_group)

        self.merge_btn = QPushButton("合并数据")
        self.merge_btn.setFixedHeight(40)
        self.merge_btn.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.merge_btn.clicked.connect(self.merge_data)

        btn_layout.addStretch()
        btn_layout.addWidget(self.merge_btn)
        btn_layout.addStretch()

        layout.addWidget(btn_group)

        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")

        self.setCentralWidget(main_widget)

    def apply_styles(self):
        # 设置整体应用样式
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QLabel {
                color: #333333;
            }
        """)

    def merge_data(self):
        try:
            if not self.source_loader.form or not self.dest_loader.form:
                raise ValueError("请先加载源文件和目标文件")

            self.status_bar.showMessage("正在合并数据...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            QApplication.processEvents()

            update_col = self.source_loader.update_col_combo.currentText()
            self.progress_bar.setValue(30)
            QApplication.processEvents()

            self.dest_loader.form.merge_from(self.source_loader.form, update_col)
            self.progress_bar.setValue(70)
            QApplication.processEvents()

            self.status_bar.showMessage("数据合并完成，请选择保存位置")

            path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", "",
                "Excel文件 (*.xlsx);;CSV文件 (*.csv)"
            )

            if path:
                self.status_bar.showMessage("正在保存文件...")
                self.progress_bar.setValue(90)
                QApplication.processEvents()

                self.dest_loader.form.save(path)
                self.progress_bar.setValue(100)
                QApplication.processEvents()

                self.status_bar.showMessage(f"文件已保存至: {os.path.basename(path)}")
                reply = QMessageBox.question(self, "成功", "数据合并和保存已完成！\n是否打开文件？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        os.startfile(path)
                    except Exception as e:
                        if self.debug:
                            QMessageBox.critical(self, "错误", str(traceback.format_exc()))
                        else:
                            QMessageBox.critical(self, "错误", str(e))

            else:
                self.status_bar.showMessage("已取消保存文件")

            self.progress_bar.setVisible(False)

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage(f"错误: {str(e)}")
            if self.debug:
                QMessageBox.critical(self, "错误", str(traceback.format_exc()))
            else:
                QMessageBox.critical(self, "错误", str(e))


if __name__ == "__main__":
    if '--debug' in sys.argv:
        sys.argv.remove('--debug')
        app = QApplication(sys.argv)
        window = MainWindow(debug=True)
    else:
        app = QApplication(sys.argv)
        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        window = MainWindow()
    window.show()
    sys.exit(app.exec())
