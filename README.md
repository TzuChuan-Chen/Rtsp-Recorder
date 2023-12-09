# RTSP Recorder

RTSP Recorder is a PyQt5-based application for recording video streams from RTSP cameras. It provides a user-friendly interface to start and stop recordings, preview camera streams, and configure various camera settings.

## Features

- Record video streams from RTSP cameras.
- Preview camera streams before starting recording.
- Configurable settings for different camera sets.
- Choose recording format (e.g., mkv, mp4, mov).
- Display recording duration in real-time.

## Prerequisites

Before running the application, make sure you have the following dependencies installed:

- Python 3.x
- PyQt5
- FFmpeg

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/rtsp-recorder.git
    cd rtsp-recorder
    ```

2. Install dependencies:

    ```bash
    altgraph==0.17.4
    ffmpeg-python==0.2.0
    future==0.18.3
    numpy==1.24.1
    packaging==23.2
    pefile==2023.2.7
    pyinstaller==6.2.0
    pyinstaller-hooks-contrib==2023.10
    PyQt5==5.15.10
    PyQt5-Qt5==5.15.2
    PyQt5-sip==12.13.0
    pywin32-ctypes==0.2.2

    ```

## Usage

1. Run the application:

    ```bash
    python main.py
    ```

2. Select the camera set, recording format, and camera preview.
3. Click "Start Recording" to begin recording from selected cameras.
4. Click "Stop Recording" to stop all ongoing recordings.
5. Use the "Preview" button to preview camera streams.

## Configuration

Modify the `camera_settings.txt` file to configure different camera sets and their settings. Each set includes a list of dictionaries specifying the RTSP stream URL, save name, and save path for each camera.

Example configuration:

```json
{
  "Set1": [{"URL": "rtsp://example.com/stream0", "Save_name": "Cs_1", "Save_path": "./data"}, 
           {"URL": "rtsp://example.com/stream1", "Save_name": "Cz_2", "Save_path": "./data"}, 
           {"URL": "rtsp://example.com/stream2", "Save_name": "Cf_3", "Save_path": "./data"}],
  // ... (other sets)
}
