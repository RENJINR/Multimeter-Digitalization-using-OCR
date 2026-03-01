# **_MULTIMETER DIGITALIZATION USING OCR_**
The project's main objective is to employ optical character recognition (OCR) technology to digitalize digital multimeter readings and plot a graph from the digits extracted from the images. To accomplish this Using Arduino microcontroller for voltage regulation, then ESP-32 cam module is used to generate the url for live feed images. Developing a system that records the multimeter's display using an ESP-32 camera, extracts numerical values from the image using OCR techniques, and digitally logs the readings is the major objective of the project. This system is made up of data logging, image acquisition, picture preparation, and OCR processing. Image preprocessing enhances the obtained image's clarity and contrast to boost OCR accuracy, while image acquisition captures the multimeter display. The numerical values from the preprocessed image are then retrieved using OCR processing


## **Hardware Requirements:**
* Arduino UNO board
* Fully Functioning Multimeter
* ESP32 board with camera module (supported models listed in camera_pins.h)
* Optional: LED for flash (pin defined in camera_pins.h)
* Wi-Fi network with known SSID and password

## _**Software Requirements:**_

* Arduino IDE (https://www.arduino.cc/en/software) for ESP32 code and Voltage regulation
* Python 3.12 (https://www.python.org/downloads/) for digit recognition script

_**Additional libraries for Python script**_
1. import numpy as np
2. import cv2
3. import matplotlib.pyplot as plt
4. import requests
5. import os
6. from io import BytesIO
7. from PIL import Image

#### **_To install the necessary libraries_**
1. pip install numpy
2. pip install opencv-python
3. pip install opencv-contrib-python
4. pip install matplotlib
5. pip install requests
6. pip install pillow

**Note: The os and io modules are part of the Python standard library and do not require installation.**


##### **_Functions of Python Libraries_**
* NumPy (numpy): Used for numerical operations and array manipulation.
* numpy as np: For general NumPy functions.
* OpenCV (cv2): Used for image processing.
* cv2: Main OpenCV module.
* cv2.ximgproc: For advanced image processing (e.g., thinning).
* cv2.adaptiveThreshold, cv2.getRotationMatrix2D, cv2.warpAffine, cv2.connectedComponentsWithStats, cv2.bitwise_or, cv2.medianBlur, cv2.HoughLines: Specific functions for image processing tasks.
* Matplotlib (matplotlib.pyplot): Used for plotting graphs.
* matplotlib.pyplot as plt: For creating plots and figures.
* Requests (requests): Used for making HTTP requests.
* requests: Main module for making HTTP requests.
* Pillow (PIL): Used for image handling.
* PIL.Image: For opening and converting images.
* OS (os): Used for interacting with the operating system.
* os: Main module for OS operations.
* IO (io): Used for handling byte streams.
* io.BytesIO: For reading byte data from requests.

## **Directory Structure:**

1. Multimeter_Digitalization/
2. ├── esp32_camera_code/          # Core ESP32 code with camera initialization and web server
3. │   ├── camera_pins.h           # Defines camera model and pin assignments
4. │   └── CameraWebServer.ino     # Main program logic for ESP32
5. ├── python_digit_recognition/   # Python script for digit extraction and recognition
6. │   └── Digit_Recognition.py    # Script implementing digit processing logic
7. └── README.md                   # This file (instructions and usage guide)


#### **_ESP32 Camera Code (esp32_camera_code/)_**

**camera_pins.h**: This file defines the camera model being used and assigns pin configurations specific to that model. it is needed to uncomment the appropriate camera model definition based on hardware setup.

**CameraWebServer.ino**: This is the core program for the ESP32. It performs the following tasks:
Initializes serial communication for debugging output.
Configures the camera module using settings in camera_config_t.
Adjusts sensor parameters (optional) for improved image quality or frame rate.
Sets up LED flash if a pin is defined in camera_pins.h.
Establishes Wi-Fi connection using the provided SSID and password.
Starts the web server.
Prints the local IP address to the serial console for access.

#### _**Python Digit Recognition Script (python_digit_recognition/)**_

**Digit_Recognition.py**: This script implements the logic for processing captured images and extracting seven-segment digits. It uses libraries like OpenCV, NumPy, pil.. for image manipulation and character recognition. ,it's expected to perform the following:
* Fetch images from the ESP32 camera's web server using a URL constructed with the ESP32's IP address.
* Preprocess the images (e.g., grayscale conversion, noise reduction, thresholding, morphological operation).
* Apply segmentation techniques to isolate individual digits.
* Extract features from the segmented digits (e.g., segment activation patterns).
* Employ a classification algorithm (Digit lookup) to recognize the digits.

##### **_Usage:_**

**Set Up ESP32:**
Flash the _CameraWebServer.ino_ code to the ESP32 board using the Arduino IDE.
Connect the ESP32 to the Wi-Fi network.

**Run Python Script:**
Navigate to the python_Digit_Recognition directory.
Install any required Python libraries.
Execute the script using python _digit_recognition.py_.

#### _Notes:_

The provided code snippets includes the detailed implementation of the Python digit recognition script.
The hardware setup (camera model, pin assignments) might require adjustments based on specific ESP32 board and camera module.

