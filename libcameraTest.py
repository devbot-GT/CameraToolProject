import time
import libcamera
import libcamera.apps

# Initialize the libcamera system
libcamera.init()

# Create a CameraManager object to manage cameras
manager = libcamera.CameraManager()

# Get the first available camera
camera = manager.get()

# Acquire the camera to start capturing
camera.acquire()

# Create an ImageEncoder to encode captured frames
encoder = libcamera.ImageEncoder()

# Create a CaptureRequest to request frames
request = camera.create_capture_request()

# Configure the CaptureRequest to capture an image
request.output_buffers = [encoder.allocate()]
request.metadata = True

# Queue the CaptureRequest for capturing
camera.queue_request(request)

# Wait for the capture to complete
camera.wait()

# Get the captured image from the encoder
image = encoder.frame(0)

# Save the image to a file
image.save("captured_image.jpg")

# Release the resources
encoder.release(image)
camera.release()
manager.release()

# Clean up the libcamera system
libcamera.exit()
