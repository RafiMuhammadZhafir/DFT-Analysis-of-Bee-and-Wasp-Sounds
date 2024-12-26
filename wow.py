import sys
import os
import pyaudio
import threading
import numpy as np
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.io.wavfile import write

class LivePlotWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(facecolor='black')
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        # Set dark theme
        self.ax.set_facecolor('#1e1e1e')  # Plot background
        self.ax.tick_params(colors='white')  # Tick color
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 1000, 900)

        # Widgets
        self.plot1 = LivePlotWidget(self)
        self.plot2 = LivePlotWidget(self)
        self.plot3 = LivePlotWidget(self)
        self.time_label = QtWidgets.QLabel("Recording Duration: 0.00 seconds", self)
        self.time_label.setStyleSheet("color: black;")

        # Dropdowns and Labels
        self.amplitude_label = QtWidgets.QLabel("Amplitude")
        self.amplitude_label.setStyleSheet("color: black;")
        self.amplitude_dropdown = QtWidgets.QComboBox()
        self.amplitude_dropdown.addItems(["50", "75", "99"])

        self.sampling_rate_label = QtWidgets.QLabel("Sampling Rate (>1000 Hz)")
        self.sampling_rate_label.setStyleSheet("color: black;")
        self.sampling_rate_dropdown = QtWidgets.QComboBox()
        self.sampling_rate_dropdown.addItems(["8000", "16000", "44100"])

        self.update_interval_label = QtWidgets.QLabel("Update Interval (1 to 100 ms)")
        self.update_interval_label.setStyleSheet("color: black;")
        self.update_interval_dropdown = QtWidgets.QComboBox()
        self.update_interval_dropdown.addItems(["10", "20", "30", "50", "100"])

        # Buttons
        self.start_button = QtWidgets.QPushButton("Start Record")
        self.stop_button = QtWidgets.QPushButton("Stop Record")
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.save_button = QtWidgets.QPushButton("Save")

        # Layouts
        main_layout = QtWidgets.QVBoxLayout()
        dropdown_layout = QtWidgets.QGridLayout()
        button_layout = QtWidgets.QHBoxLayout()
        plot_layout = QtWidgets.QVBoxLayout()

        # Arrange Dropdowns
        dropdown_layout.addWidget(self.amplitude_label, 0, 0)
        dropdown_layout.addWidget(self.amplitude_dropdown, 0, 1)
        dropdown_layout.addWidget(self.sampling_rate_label, 0, 2)
        dropdown_layout.addWidget(self.sampling_rate_dropdown, 0, 3)
        dropdown_layout.addWidget(self.update_interval_label, 0, 4)
        dropdown_layout.addWidget(self.update_interval_dropdown, 0, 5)

        # Arrange Buttons
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)

        # Arrange Plots
        plot_layout.addWidget(self.plot1)
        plot_layout.addWidget(self.plot2)
        plot_layout.addWidget(self.plot3)

        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(plot_layout)
        main_layout.addWidget(self.time_label)

        # Central Widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Audio Setup
        self.stream = None
        self.audio_data = []
        self.running = False
        self.p = pyaudio.PyAudio()  # Initialize PyAudio
        self.chunk_size = 2048
        self.rate = 44100

        # Connect Buttons
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.reset_button.clicked.connect(self.reset_data)
        self.save_button.clicked.connect(self.save_data)

        # Timer for live update
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_plots)

        # Timer for elapsed time display
        self.elapsed_time_timer = QtCore.QTimer(self)
        self.elapsed_time_timer.timeout.connect(self.update_elapsed_time)
        self.elapsed_time = 0  # Time in seconds

        # Initialize plots
        self.initialize_plots()

    def initialize_plots(self):
        self.plot1.ax.clear()
        self.plot1.ax.set_title("Original Signal", fontsize=12, fontweight='bold')
        self.plot1.ax.set_xlabel("Time (s)")
        self.plot1.ax.set_ylabel("Amplitude")
        self.plot1.ax.grid(True, linestyle='--', alpha=0.5)
        self.plot1.draw()

    def start_recording(self):
        self.running = True
        self.audio_data.clear()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)
        threading.Thread(target=self.record_audio, daemon=True).start()
        self.timer.start(100)  # Update every 100 ms
        self.elapsed_time = 0  # Reset elapsed time
        self.elapsed_time_timer.start(1000)  # Update every second

    def stop_recording(self):
        self.running = False
        self.timer.stop()
        self.elapsed_time_timer.stop()

        if self.stream is not None:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"Error stopping stream: {e}")
            finally:
                self.stream = None

    def reset_data(self):
        self.running = False
        if self.stream is not None:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"Error resetting stream: {e}")
            finally:
                self.stream = None
        self.audio_data.clear()
        self.initialize_plots()

    def save_data(self):
        if self.audio_data:
            options = QtWidgets.QFileDialog.Options()
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Audio File", "", "WAV Files (*.wav)", options=options)
            if file_path:
                write(file_path, self.rate, np.array(self.audio_data).astype(np.int16))
                QtWidgets.QMessageBox.information(self, "Save Data", f"Audio data saved successfully to {file_path}!")
        else:
            QtWidgets.QMessageBox.warning(self, "Save Data", "No data to save!")

    def record_audio(self):
        while self.running:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.extend(np.frombuffer(data, dtype=np.int16))
            except Exception as e:
                print(f"Error during recording: {e}")
                self.running = False

    def update_elapsed_time(self):
        self.elapsed_time += 1
        self.time_label.setText(f"Recording Duration: {self.elapsed_time:.2f} seconds")
    
    def update_plots(self):
        """Update the plots with the recorded audio data."""
        if not self.audio_data:
            return

        signal = np.array(self.audio_data)
        normalized_signal = signal / (np.max(np.abs(signal)) + 1e-6)
        time = np.linspace(0, len(normalized_signal) / self.rate, len(normalized_signal))

        # Update Original Signal Plot
        self.plot1.ax.clear()
        self.plot1.ax.plot(time, normalized_signal, color='#39c0ed', alpha=0.8, linewidth=2)
        self.plot1.ax.set_title("Original Signal", fontsize=12, fontweight='bold', color='white')
        self.plot1.ax.set_xlabel("Time (s)", color='white')
        self.plot1.ax.set_ylabel("Amplitude", color='white')
        self.plot1.ax.margins(x=0.05)  # Add small margin
        self.plot1.ax.tick_params(axis='x', labelrotation=15, colors='white')  # Rotate and color ticks
        self.plot1.ax.tick_params(axis='y', colors='white')
        self.plot1.figure.tight_layout()  # Adjust layout
        self.plot1.draw()

        # Update DFT Plot
        hz = np.fft.rfftfreq(len(normalized_signal), 1 / self.rate)
        amplitude = np.abs(np.fft.rfft(normalized_signal))
        self.plot2.ax.clear()
        self.plot2.ax.plot(hz, amplitude, color='#8bda92', alpha=0.8, linewidth=2)
        self.plot2.ax.set_title("DFT of Signal", fontsize=12, fontweight='bold', color='white')
        self.plot2.ax.set_xlabel("Frequency (Hz)", color='white')
        self.plot2.ax.set_ylabel("Amplitude", color='white')
        self.plot2.ax.margins(x=0.05)
        self.plot2.ax.tick_params(axis='x', labelrotation=15, colors='white')
        self.plot2.ax.tick_params(axis='y', colors='white')
        self.plot2.figure.tight_layout()  # Adjust layout
        self.plot2.draw()

        # Update FFT Plot
        self.plot3.ax.clear()
        self.plot3.ax.plot(hz, amplitude, color='#f39c12', alpha=0.8, linewidth=2)
        self.plot3.ax.set_title("FFT of Signal", fontsize=12, fontweight='bold', color='white')
        self.plot3.ax.set_xlabel("Frequency (Hz)", color='white')
        self.plot3.ax.set_ylabel("Magnitude", color='white')
        self.plot3.ax.margins(x=0.05)
        self.plot3.ax.tick_params(axis='x', labelrotation=15, colors='white')
        self.plot3.ax.tick_params(axis='y', colors='white')
        self.plot3.figure.tight_layout()  # Adjust layout
        self.plot3.draw()

    def closeEvent(self, event):
        self.running = False
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
