# CameraToolProject

## *This repository is for the automation of a hybrid DED and CNC camera tool for porosity analysis.*

### pi_controller.py is run on a host computer to SSH into the Raspberry Pi and command it for testing.
    There is a psudo terminal with log and command inputs to navigate directories and run python scripts.
    There are buttons to quickly run scripts like starting and stopping the camera feed automatically.
    
### camera_stream.py will need to be stored on the Raspberry Pi and will be responsible for starting and stopping the camera stream.
    For now, this is for a Raspberry Pi HQ Camera Module and streams the camera feed through the micro HDMI port.
    Working on finishing the functionality for streaming the camera feed wirelessly.
    The buttons on the GUI from the host computer for "Start Camera Stream" and "End Camera Stream" run and kill this script on the Raspberry Pi.
    
### spin_to_win.py will have the Raspberry Pi idle, waiting for input from a gyroscope to pass a threshold that will start or kill a camera stream python script.
    This file has not been created yet.
    This will be used for automating when the camera toll should be recording or idle.
    When the camera tool gets selected from the CNC tool changing carousel, it will spin before following the tool path to indicate the Raspberry Pi should start streaming.
    The camera tool will spin again once it is done with its tool path to stop streaming before being placed back on the carousel.
