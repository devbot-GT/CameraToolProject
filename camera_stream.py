#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 11:16:41 2023

@author: devbot
"""

import io
import time
import picamera
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import signal
import sys

# Global variable for terminating the camera stream
terminate_signal = False

# Function to start the camera stream
def start_camera_stream(camera_mode, stream_mode):
    print(f'camera_mode: {camera_mode}')
    print(f'stream_mode: {stream_mode}')
    global terminate_signal, camera

    try:
        # Initialize the camera
        camera = picamera.PiCamera()
        camera.resolution = (4056, 3040) if camera_mode == 3 else (2028, 1080)

        if stream_mode == 'HDMI':
            camera.start_preview(fullscreen=False, window=(0, 0, 640, 480))
        elif stream_mode == 'wireless':
            # Start the HTTP streaming server in a separate thread
            server_thread = threading.Thread(target=start_http_server)
            server_thread.start()

            # Enable network streaming (HTTP)
            camera.start_recording('/dev/null', format='h264', splitter_port=2)
            time.sleep(2)  # Wait for the splitter to initialize
            camera.start_recording(HTTPMotionOutput(camera), format='mjpeg', splitter_port=1, resize=(640, 480))
            print('Started streaming wirelessly on port 8000')

        # Register the signal handler for proper termination
        signal.signal(signal.SIGTERM, cleanup)

        # Keep the script running indefinitely
        while not terminate_signal:
            time.sleep(1)

    finally:
        cleanup(None, None)

# Signal handler for KeyboardInterrupt (Ctrl+C)
def cleanup_keyboard_interrupt(signal, frame):
    print("KeyboardInterrupt received. Stopping camera stream.")
    cleanup(signal, frame)

# Signal handler to stop the camera stream
def cleanup(signal, frame):
    global terminate_signal
    terminate_signal = True

    camera.stop_preview()
    camera.close()
    sys.exit(0)

# Function to start the HTTP streaming server
def start_http_server():
    server_address = ('', 8000)  # Use any available port
    http_server = HTTPServer(server_address, HTTPMotionHandler)
    http_server.serve_forever()

# Custom HTTP request handler
class HTTPMotionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=stream_boundary')
            self.end_headers()

            try:
                stream = io.BytesIO()  # Create a new stream for each request
                while not terminate_signal:
                    frame = camera.capture_continuous(stream, format='jpeg', use_video_port=True)
                    self.wfile.write(b'--stream_boundary\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                    self.wfile.flush()
            except Exception as e:
                print(f'Error: {e}')
        else:
            self.send_response(404)

# Custom output for capturing MJPEG stream
class HTTPMotionOutput:
    def __init__(self, camera):
        self.camera = camera

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.stream.seek(0)
            self.stream.truncate()
            self.stream.write(buf)

    def flush(self):
        pass

# Get the camera_mode and stream_mode from command-line arguments
camera_mode = int(sys.argv[1])
stream_mode = sys.argv[2]

# Start the camera stream
start_camera_stream(camera_mode, stream_mode)
