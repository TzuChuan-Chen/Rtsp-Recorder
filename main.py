from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter
from UI import Ui_Recorder

import ffmpeg
import json, os, sys, time, subprocess
from datetime import datetime


class VideoRecorderThread(QThread):
    def __init__(self, input_file, output_filename):
        super().__init__()
        self.input_file = input_file
        self.output_filename = output_filename
        self.ffmpeg_cmd = None
        self.probe = ffmpeg.probe(self.input_file)
        self.video_stream = next((stream for stream in self.probe['streams'] if stream['codec_type'] == 'video'), None)
        self.width = int(self.video_stream['width'])
        self.height = int(self.video_stream['height'])
        self.frame_rate = self.video_stream['r_frame_rate']
        self.frame_rate = self.frame_rate.split('/')
        self.frame_rate = int(self.frame_rate[0]) / int(self.frame_rate[1])

    def run(self):
        self.ffmpeg_cmd = (
            ffmpeg.input(self.input_file, rtsp_transport="tcp", use_wallclock_as_timestamps=1, hwaccel="auto")
            .output(self.output_filename, vcodec='copy')
            .global_args("-hide_banner", "-loglevel", "error")
            .run_async(pipe_stdin=True)
        )
        # print(self.input_file)
        self.ffmpeg_cmd.wait()

    def stop(self):
        if self.ffmpeg_cmd:
            self.ffmpeg_cmd.stdin.write(b'q')
            self.ffmpeg_cmd.stdin.close()
            self.ffmpeg_cmd.wait()
            self.ffmpeg_cmd = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Recorder()
        self.ui.setupUi(self)
        self.setWindowTitle("RTSP-Recorder")
        self.recording_threads = []
        self.setup_ui_elements()
        self.camera_settings = {}
        #self.load_camera_settings()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_display)

    def update_timer_display(self):
        if self.start_time is None:
            self.ui.label_timer.setText("00:00:00")
        else:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.ui.label_timer.setText(self.time_str)

    def setup_ui_elements(self):
        self.ui.pushButton_startRec.clicked.connect(self.start_recording)
        self.ui.pushButton_stopRec.clicked.connect(self.stop_recording)
        self.ui.pushButton_viewer.clicked.connect(self.display_stream)
        self.ui.pushButton_camSetting.clicked.connect(self.load_camera_settings_on_button_press)

    def message(self, message):
        self.ui.plainTextEdit_logInfo.appendPlainText(message)

    def start_recording(self):
        file_container = self.ui.comboBox_container.currentText()
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("./data", current_time)
        os.makedirs(folder_path, exist_ok=True)

        for setting in self.camera_settings[self.ui.comboBox_cameraSet.currentText()]:
            input_file = setting["URL"]
            output_filename = os.path.join(folder_path, setting["Save_name"] + "." + file_container)
            recording_thread = VideoRecorderThread(input_file, output_filename)

            recording_thread.start()
            self.recording_threads.append(recording_thread)

        self.message(
            f'Recording {self.ui.comboBox_cameraSet.currentText()} started at {current_time} save in {folder_path[2:]} folder')

        self.start_time = time.time()
        self.timer.start(1000)
        self.ui.pushButton_startRec.setEnabled(False)
        self.ui.pushButton_stopRec.setEnabled(True)

    def stop_recording(self):
        for recording_thread in self.recording_threads:
            recording_thread.stop()

        self.timer.stop()
        self.update_timer_display()
        self.on_recording_finished()
        self.recording_threads = []
        self.ui.pushButton_startRec.setEnabled(True)
        self.ui.pushButton_stopRec.setEnabled(False)

    def on_recording_finished(self):
        self.message('Recording finished\n')
        self.timer.stop()
        self.update_timer_display()
        self.recording_threads = []
        self.ui.pushButton_startRec.setEnabled(True)
        self.ui.pushButton_stopRec.setEnabled(False)

    def load_camera_settings_on_button_press(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Camera Settings File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            self.load_camera_settings(file_name)

    def load_camera_settings(self, file_name=None):
        try:
            if file_name is None:
                file_name, _ = QFileDialog.getOpenFileName(self, "Select Camera Settings File", "", "Text Files (*.txt);;All Files (*)")
                if not file_name:
                    return  # User canceled file selection

            with open(file_name, 'r') as file:
                file_content = file.read()
                self.camera_settings = json.loads(file_content)
                self.ui.comboBox_cameraSet.clear()
                for camera_set in self.camera_settings:
                    self.ui.comboBox_cameraSet.addItem(camera_set)
                self.ui.comboBox_cameraPreview.clear()
                for setting in self.camera_settings[self.ui.comboBox_cameraSet.currentText()]:
                    self.ui.comboBox_cameraPreview.addItem(setting["Save_name"])

        except FileNotFoundError:
            self.message("Error loading camera settings file")
            pass

        self.ui.plainTextEdit_logInfo.clear()

    def display_stream(self):
        setting = next(
            (item for item in self.camera_settings[self.ui.comboBox_cameraSet.currentText()] if
             item["Save_name"] == self.ui.comboBox_cameraPreview.currentText()), None)
        # print(setting["URL"])
        ffplay = [
            "ffplay",
            "-hide_banner",
            "-loglevel", "error",
            "-rtsp_transport", "tcp",
            "-i", setting["URL"],
            "-an",
            "-vf", "fps=30,scale=640:480"
        ]
        subprocess.Popen(ffplay, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
