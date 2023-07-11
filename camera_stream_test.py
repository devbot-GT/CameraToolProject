import libcamera

def start_camera_stream():
    with libcamera.CameraManager() as manager:
        camera = manager.get()  # Get the first available camera

        # Configure camera properties
        camera.configuration.sensorMode = 0  # Set the desired sensor mode
        camera.configuration.pixelFormat = libcamera.PixelFormat('BGR888')
        camera.configuration.size = libcamera.Size(640, 480)  # Set the desired resolution

        # Open the camera and start the stream
        camera.open()
        camera.start()

        # Capture and process frames
        while True:
            frame = camera.capture()
            # Process the frame, e.g., display it, save it, etc.

if __name__ == '__main__':
    start_camera_stream()
