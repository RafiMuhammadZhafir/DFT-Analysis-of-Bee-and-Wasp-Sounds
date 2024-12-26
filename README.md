# Audio Recorder and Visualizer

## Authors
- **Ishmatu Aulia Rizky Kirana** - 2042231004  
- **Rafi Muhammad Zhafir** - 2042231038  
- **Riska Hidayati Laena** - 2042231054

## Supervisor
**Ir. Dwi Oktavianto Wahyu Nugroho, S.T., M.T.**

## Overview
This project provides an interactive application to record audio in real-time, visualize the waveform, and perform frequency analysis using FFT and DFT. The GUI is implemented with **PyQt5**, and the application offers multiple functionalities including live audio recording, plotting, and saving the recorded data.

## Features
- **Live Audio Recording**: Capture audio in real time with adjustable settings.
- **Signal Visualization**: Display waveform and frequency spectrum using FFT and DFT.
- **Customizable Settings**: Change amplitude, sampling rate, and update interval.
- **Data Saving**: Save recorded audio as a `.wav` file.

## Requirements
Make sure you have the following dependencies installed:
- Python 3.x
- PyQt5
- NumPy
- Matplotlib
- PyAudio
- SciPy

## How to Run
1. Install dependencies using `pip install PyQt5 numpy matplotlib pyaudio scipy`.
2. Run the application: `python wow.py`.
3. Use the interactive GUI to:
   - Start/Stop recording.
   - Visualize signal waveform and frequency analysis.
   - Adjust parameters and save the recorded audio.

## File Contents
- **`wow.py`**: Main script containing the GUI and audio recording functionalities.

## Application Preview
- **Waveform Plot**: Real-time visualization of the audio signal.
- **FFT/DFT Plots**: Frequency spectrum of the recorded signal.

## License
This project is licensed under the MIT License.
