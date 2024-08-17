import sys
import os
import subprocess
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QProgressBar, QMessageBox, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QLocale

# 设置日志记录
logging.basicConfig(
    filename='conversion.log',  # 日志文件路径
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 定义多语言支持
languages = {
    'zh_cn': {
        'title': '视频到 MP3 批量转换器',
        'source_folder': '来源文件夹：未选择',
        'select_source': '选择来源文件夹',
        'destination_folder': '目标文件夹：未选择',
        'select_destination': '选择目标文件夹',
        'start_conversion': '开始转换',
        'converting': '转换中...',
        'conversion_complete': '转换完成！',
        'select_source_folder': '请选择来源文件夹',
        'select_destination_folder': '请选择目标文件夹',
        'conversion_finished': '转换完成！',
        'language_label': '语言 (Language):'
    },
    'en_us': {
        'title': 'Video to MP3 Converter',
        'source_folder': 'Source Folder: Not Selected',
        'select_source': 'Select Source Folder',
        'destination_folder': 'Destination Folder: Not Selected',
        'select_destination': 'Select Destination Folder',
        'start_conversion': 'Start Conversion',
        'converting': 'Converting...',
        'conversion_complete': 'Conversion Complete!',
        'select_source_folder': 'Please select a source folder',
        'select_destination_folder': 'Please select a destination folder',
        'conversion_finished': 'Conversion Finished!',
        'language_label': 'Language:'
    },
    'zh_tw': {
        'title': '影片到 MP3 批量轉換器',
        'source_folder': '來源資料夾：未選擇',
        'select_source': '選擇來源資料夾',
        'destination_folder': '目標資料夾：未選擇',
        'select_destination': '選擇目標資料夾',
        'start_conversion': '開始轉換',
        'converting': '轉換中...',
        'conversion_complete': '轉換完成！',
        'select_source_folder': '請選擇來源資料夾',
        'select_destination_folder': '請選擇目標資料夾',
        'conversion_finished': '轉換完成！',
        'language_label': '語言 (Language):'
    }
}

class VideoToMp3Converter(QWidget):
    def __init__(self):
        super().__init__()

        # 根据系统语言设置默认语言
        self.system_language = QLocale.system().name()
        if self.system_language.startswith('zh_TW'):
            self.current_language = 'zh_tw'
        elif self.system_language.startswith('zh'):
            self.current_language = 'zh_cn'
        else:
            self.current_language = 'en_us'  # 默认设置为英语

        self.language = languages[self.current_language]

        # 设置窗口标题
        self.setWindowTitle(self.language['title'])
        self.resize(400, 250)

        self.style = """
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QProgressBar {
                height: 20px;
                text-align: center;
                color: #4CAF50;
            }
            QProgressBar::chunk {
                background-color: #007acc;  /* 改为蓝色 */
            }
        """
        self.setStyleSheet(self.style)

        # 初始化界面元素
        self.language_label = QLabel(self.language['language_label'], self)
        self.language_combo = QComboBox(self)
        self.language_combo.addItems(['中文（中国）', 'English (US)', '中文（台灣）'])
        self.language_combo.setCurrentIndex(self._get_language_index())
        self.language_combo.currentIndexChanged.connect(self.change_language)

        self.source_label = QLabel(self.language['source_folder'], self)
        self.destination_label = QLabel(self.language['destination_folder'], self)

        self.source_button = QPushButton(self.language['select_source'], self)
        self.source_button.clicked.connect(self.select_source_folder)

        self.destination_button = QPushButton(self.language['select_destination'], self)
        self.destination_button.clicked.connect(self.select_destination_folder)

        self.convert_button = QPushButton(self.language['start_conversion'], self)
        self.convert_button.clicked.connect(self.start_conversion)

        self.status_label = QLabel('', self)
        self.status_label.setWordWrap(True)  # 启用自动换行

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combo)
        layout.addWidget(self.source_label)
        layout.addWidget(self.source_button)
        layout.addWidget(self.destination_label)
        layout.addWidget(self.destination_button)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def _get_language_index(self):
        if self.current_language == 'zh_cn':
            return 0
        elif self.current_language == 'en_us':
            return 1
        elif self.current_language == 'zh_tw':
            return 2

    def change_language(self, index):
        if index == 0:
            self.current_language = 'zh_cn'
        elif index == 1:
            self.current_language = 'en_us'
        elif index == 2:
            self.current_language = 'zh_tw'

        self.language = languages[self.current_language]
        self.update_ui_text()

    def update_ui_text(self):
        self.setWindowTitle(self.language['title'])
        self.language_label.setText(self.language['language_label'])
        self.source_label.setText(self.language['source_folder'])
        self.destination_label.setText(self.language['destination_folder'])
        self.source_button.setText(self.language['select_source'])
        self.destination_button.setText(self.language['select_destination'])
        self.convert_button.setText(self.language['start_conversion'])

    def select_source_folder(self):
        self.source_folder = QFileDialog.getExistingDirectory(self, self.language['select_source_folder'])
        if self.source_folder:
            self.source_label.setText(f"{self.language['source_folder']}: {self.source_folder}")

    def select_destination_folder(self):
        self.destination_folder = QFileDialog.getExistingDirectory(self, self.language['select_destination_folder'])
        if self.destination_folder:
            self.destination_label.setText(f"{self.language['destination_folder']}: {self.destination_folder}")

    def start_conversion(self):
        if not hasattr(self, 'source_folder') or not self.source_folder:
            QMessageBox.warning(self, 'Error', self.language['select_source_folder'])
            return

        if not hasattr(self, 'destination_folder') or not self.destination_folder:
            QMessageBox.warning(self, 'Error', self.language['select_destination_folder'])
            return

        self.thread = ConversionThread(self.source_folder, self.destination_folder)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.status_signal.connect(self.update_status)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def update_status(self, status):
        self.status_label.setText(status)

    def conversion_finished(self):
        QMessageBox.information(self, 'Info', self.language['conversion_finished'])

class ConversionThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)

    def __init__(self, source_folder, destination_folder):
        super().__init__()
        self.source_folder = source_folder
        self.destination_folder = destination_folder

    def run(self):
        files = os.listdir(self.source_folder)
        total_files = len(files)
        current_file = 0

        for filename in files:
            file_path = os.path.join(self.source_folder, filename)
            if os.path.isdir(file_path):
                continue

            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_type', '-of', 'default=nw=1:nk=1', file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as e:
                error_message = f"检查文件类型时发生错误：{filename}：{e}"
                self.status_signal.emit(self.wrap_text(error_message))
                logging.error(error_message)  # 记录错误信息
                continue

            if result.stdout.strip() == b'video':
                output_file_name = os.path.splitext(filename)[0] + ".mp3"
                output_file_path = os.path.join(self.destination_folder, output_file_name)

                try:
                    subprocess.run(
                        [
                            'ffmpeg',
                            '-i', file_path,
                            '-vn',
                            '-ar', '44100',
                            '-ac', '2',
                            '-ab', '320k',
                            '-f', 'mp3',
                            output_file_path, '-y'
                        ],
                        check=True
                    )

                    current_file += 1
                    progress = int((current_file / total_files) * 100)
                    self.progress_signal.emit(progress)

                    success_message = f"已将 {filename} 转换为 {output_file_name}"
                    self.status_signal.emit(self.wrap_text(success_message))
                    logging.info(success_message)  # 记录成功转换的消息
                except subprocess.CalledProcessError as e:
                    error_message = f"转换文件时发生错误：{filename}：{e}"
                    self.status_signal.emit(self.wrap_text(error_message))
                    logging.error(error_message)  # 记录错误信息
                    continue

    def wrap_text(self, text, max_length=80):
        """将长文本分行，以适应界面宽度"""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 > max_length:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += ' '
                current_line += word
        
        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    converter = VideoToMp3Converter()
    converter.show()
    sys.exit(app.exec_())
