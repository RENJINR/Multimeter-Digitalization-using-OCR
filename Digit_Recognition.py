import numpy as np
import cv2
import matplotlib.pyplot as plt
import requests
import os
from io import BytesIO
from PIL import Image

# Show images during processing
show_images = True

# Function to fetch image from ESP32-CAM
def fetch_image_from_esp32_cam(url):
    response = requests.get(url, verify=False)
    img_array = np.array(Image.open(BytesIO(response.content)).convert('L'))
    return img_array

# Function for rotating an image by angles other than 90, 180, or 270
def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

# Trim mean function definition
def trimmean(arr, percent):
    n = len(arr)
    k = int(round(n * (float(percent) / 100) / 2))
    return np.mean(arr[k + 1:n - k])

# Checking active 7-segment DP segments in digit_roi
def search4segments(digit_roi):
    dig_H, dig_W = digit_roi.shape
    seg_short_side = dig_W // 4
    # Define a set of tuples for creating the mask for the 7 segments
    segments = [
        ((0, 0), (seg_short_side, dig_W)),  # top
        ((0, 0), (dig_H // 2, seg_short_side)),  # top-left
        ((0, dig_W - seg_short_side), (dig_H // 2, dig_W)),  # top-right
        ((dig_H // 2 - seg_short_side // 2, 0), (dig_H // 2 + seg_short_side // 2, dig_W)),  # center
        ((dig_H // 2, 0), (dig_H, seg_short_side)),  # bottom-left
        ((dig_H // 2, dig_W - seg_short_side), (dig_H, dig_W)),  # bottom-right
        ((dig_H - seg_short_side, 0), (dig_H, dig_W))  # bottom
    ]
    # Set of activated segments
    on = [0] * len(segments)
    # Loop over the individual segments
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        # Extract the segment ROI, count the total number of thresholded pixels in the segment, and then compute
        # the area of the segment
        segROI = digit_roi[xA:xB, yA:yB]
        total = cv2.countNonZero(segROI)
        area = (xB - xA) * (yB - yA)
        # If the total number of non-zero pixels is greater than 40% of the area, mark the segment as "on"
        if total / float(area + 1e-1) > 0.5:
            on[i] = 1
    return on

# ESP32-CAM's IP address (change this to your camera's IP)
esp32_cam_ip = 'http://192.168.178.89'

# Define the URL for the camera feed
url = f"{esp32_cam_ip}/capture"

# Lists to store time series data
time_series = []
digit_series = []

# Set up the plot
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(time_series, digit_series, 'r-')
ax.set_ylim(0, 10)  # Assuming the digits are between 0 and 9

# Function to update the plot
def update_plot(new_digit):
    time_series.append(len(time_series))  # Use index as time for simplicity
    digit_series.append(new_digit)
    line.set_xdata(time_series)
    line.set_ydata(digit_series)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

# Loop to process images continuously until 'q' is pressed
try:
    while True:
        # Fetch image from the ESP32-CAM
        img = fetch_image_from_esp32_cam(url)

        # Blur the image to get rid of high frequency noise
        img = cv2.medianBlur(img, 5)

        # OPTIONAL: Resize the image, so it can be displayed with cv2.imshow for ROI selection recommended for large images, which would not fit on the display screen
        img = cv2.resize(img, (int(img.shape[1] / 1.2), int(img.shape[0] / 1.2)))

        # Manual selection of ROI
        roi = cv2.selectROI(img)
        cv2.destroyAllWindows()

        # ROI image
        img_roi = img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

        # Kernel size for adaptive thresholding (depending on the size of the ROI ->expected No. of digits in ROI 4-6)
        ksize = max(3, 2 * (roi[2] // 8) + 1)
        if ksize % 2 == 0:
            ksize += 1
        print(f"using ksize: {ksize}")  # print the ksize for debugging

        # Adaptive thresholding
        img_bw = cv2.adaptiveThreshold(img_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, ksize, 3)

        # Getting connected components with stats
        img_bw_CC = cv2.connectedComponentsWithStats(img_bw)
        # Create and populate a matrix with only the relevant information from CC with stats
        CC_stats = np.zeros((len(img_bw_CC[2]), 4), np.uint32)
        CC_stats[:, 0] = range(len(img_bw_CC[2]))
        CC_stats[:, 1] = img_bw_CC[2][:, -1]
        CC_stats[:, 2:] = img_bw_CC[2][:, 2:-1]
        # Remove all CC, which have a bounding box that touches the border of the ROI - probably not a digit
        relevant_cc_stats = np.delete(CC_stats,
                                      np.logical_or(np.logical_or(img_bw_CC[2][:, 0] == 0, img_bw_CC[2][:, 1] == 0),
                                                    np.logical_or(
                                                        img_bw_CC[2][:, 0] + img_bw_CC[2][:, 2] == img_roi.shape[1],
                                                        img_bw_CC[2][:, 1] + img_bw_CC[2][:, 3] == img_roi.shape[0])), 0)
        # Sort the matrix rows according to the pixel count of regions (from largest -> smallest)
        relevant_cc_stats = relevant_cc_stats[np.argsort(-relevant_cc_stats[:, 1])]

        # Trimmed mean of CC sizes (calculated from the middle 40%)
        mean = trimmean(relevant_cc_stats[:, 1], 60)
        # Standard deviation
        stddev = np.std(relevant_cc_stats[1:, 1])
        # Remove all components which are smaller than a third of the mean (NOT QUITE ROBUST)
        relevant_cc_stats = relevant_cc_stats[relevant_cc_stats[:, 1] > (mean / 4)]

        # Creating an empty image to draw the remaining components
        masks = np.zeros((img_bw.shape), dtype=np.uint8)
        for i in range(relevant_cc_stats.shape[0]):
            cv2.bitwise_or(masks, np.array(img_bw_CC[1] == relevant_cc_stats[i, 0], dtype=np.uint8), masks)

        roi_thinned = cv2.ximgproc.thinning(masks)
        lines = cv2.HoughLines(roi_thinned, 1, np.pi / 180, 30)

        if show_images:
            # Display results of preprocessing
            _, axs = plt.subplots(1, 2)
            axs[0].imshow(img_bw, cmap='binary')
            axs[1].imshow(masks, cmap='binary')
            plt.show()

        # Getting the image's projection on the horizontal axis
        ver_proj = np.sum(masks, axis=0)
        # Threshold the vector according to its mean (1/5)
        ver_proj[ver_proj < np.mean(ver_proj) / 5] = 0
        ver_proj[ver_proj >= np.mean(ver_proj)] = 1
        ver_proj = ver_proj.astype(bool)

        # Getting the borders (places where the thresholded projection changes)
        borders = []
        for i in range(1, len(ver_proj)):
            if ver_proj[i - 1] ^ ver_proj[i]:
                borders.append(i)

        # Getting the outermost borders
        lengths = list(np.diff(borders))
        if len(borders) > 2:
            if borders[0] > 2:
                lengths.insert(0, borders[0])
            if sum(lengths) < masks.shape[1]:
                lengths.append(masks.shape[1] - borders[-1])
        else:
            raise RuntimeError

        # Cutting the image to smaller images and storing these in a list
        img_segments = []
        for i in range(1, len(borders)):
            img_segments.append(masks[:, borders[i - 1]:borders[i]])

        if show_images:
            _, axs = plt.subplots(1, len(img_segments))
            for i in range(len(img_segments)):
                axs[i].imshow(img_segments[i], cmap='binary')
            plt.show()

        # Distinguishing the digits from the supposedly empty in-between-digit regions
        digits = []
        for i in range(len(img_segments)):
            if cv2.countNonZero(img_segments[i]) > img_segments[i].size / 5:
                digits.append(img_segments[i])

        if show_images:
            _, axs = plt.subplots(1, len(digits))
            for i in range(len(digits)):
                axs[i].imshow(digits[i], cmap='binary')
            plt.show()

        # Projecting the rows in sub-images to the vertical axis
        digits_hor_proj = [np.sum(digit, axis=1) for digit in digits]
        # Further shrinking the images to get the most tight bounding boxes
        for i in range(len(digits)):
            tmp = np.where(digits_hor_proj[i] > np.mean(digits_hor_proj[i] / 2))
            digits[i] = digits[i][int(tmp[0][0]):int(tmp[0][-1]) + 1, :]

        if show_images:
            _, axs = plt.subplots(1, len(digits))
            for i in range(len(digits)):
                axs[i].imshow(digits[i], cmap='binary')
            plt.show()

        digits_closed = []
        for i in range(len(digits)):
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(digits[i].shape[1] / 5), int(digits[i].shape[1] / 5)))
            digits_closed.append(cv2.morphologyEx(digits[i], cv2.MORPH_DILATE, kernel))

        # Define the dictionary of digit segments
        DIGITS_LOOKUP = {
            (1, 1, 1, 0, 1, 1, 1): 0,
            (1, 0, 1, 1, 1, 0, 1): 2,
            (1, 0, 1, 1, 0, 1, 1): 3,
            (0, 1, 1, 1, 0, 1, 0): 4,
            (1, 1, 0, 1, 0, 1, 1): 5,
            (1, 1, 0, 1, 1, 1, 1): 6,
            (1, 0, 1, 0, 0, 1, 0): 7,
            (1, 1, 1, 1, 1, 1, 1): 8,
            (1, 1, 1, 1, 0, 1, 1): 9
        }

        # Creating an output list for recognised digits
        digit_rec = []
        for digit in digits:
            dig_H, dig_W = digit.shape
            seg_short_side = dig_W // 3
            # Slight rotation in case of not recognising the digit on the first try
            trials = 0
            rot_pos = [-5, -3, 3, 5]
            # For recognising a one
            if dig_H > 3 * dig_W and cv2.countNonZero(digit) > 0.4 * dig_W * dig_H:
                digit_rec.append(1)
                update_plot(1)
            else:
                if cv2.countNonZero(digit) > 0.3 * dig_W * dig_H:
                    pass
                else:
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(digits[i].shape[1] / 5), int(digits[i].shape[1] / 5)))
                    cv2.morphologyEx(digits[i], cv2.MORPH_DILATE, kernel, digits[i])
                while trials < len(rot_pos):
                    if trials == 0:
                        on = search4segments(digit)
                    try:
                        digit_value = DIGITS_LOOKUP[tuple(on)]
                        digit_rec.append(digit_value)
                        update_plot(digit_value)
                        break
                    except KeyError:
                        rot_digit = rotate_image(digit, rot_pos[trials])
                        on = search4segments(rot_digit)
                        trials += 1
                if trials == 4:
                    digit_rec.append(None)
                    update_plot(None)

        if show_images:
            _, axs = plt.subplots(1, len(digits))
            for i in range(len(digits)):
                axs[i].imshow(digits[i], cmap='binary')
                axs[i].title.set_text(digit_rec[i])
            plt.show()

        # Print the result vector
        print(digit_rec)

        # Check for 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
