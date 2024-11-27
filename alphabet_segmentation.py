import math
import subprocess
import cv2
from matplotlib import pyplot as plt
import numpy as np
import os

def sort_contours(contours_info, row_threshold=100):
    """
    Organizes contours into a matrix based on their positions.

    Parameters:
        contours_info (list): List of contour dictionaries.
        row_threshold (int): Vertical distance threshold to group contours into the same row.

    Returns:
        List[List[dict]]: Matrix of contours organized as rows and columns.
    """
    # Sort contours by their top coordinate (extTop[1])
    contours_info_sorted = sorted(contours_info, key=lambda c: c['extTop'][1])

    rows = []
    current_row = []
    last_top = None

    for info in contours_info_sorted:
        current_top = info['extTop'][1]
        if last_top is None:
            last_top = current_top
            current_row.append(info)
        elif abs(current_top - last_top) < row_threshold:
            current_row.append(info)
        else:
            # Sort current row left to right based on extLeft[0]
            current_row.sort(key=lambda c: c['extLeft'][0])
            rows.append(current_row)
            current_row = [info]
            last_top = current_top

    # Add the last row
    if current_row:
        current_row.sort(key=lambda c: c['extLeft'][0])
        rows.append(current_row)

    result = []
    for row in rows:
        result.extend(row)

    return result

def segment_characters(image_path, output_folder):
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Unable to load image.")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)


    # Apply Otsu's Thresholding after Gaussian filtering
    _, thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_TRIANGLE
    )
    # cv2.imshow('Dilated Image', thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Find contours on the dilated image
    contours, hierarchy = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Calculate bounding boxes and extreme points
    contours_info = []
    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < 40:  # Adjust area threshold as needed
            continue
        info = {
            'index': idx,
            'contour': cnt,
            'area': area,
            'extLeft': tuple(cnt[cnt[:, :, 0].argmin()][0]),
            'extRight': tuple(cnt[cnt[:, :, 0].argmax()][0]),
            'extTop': tuple(cnt[cnt[:, :, 1].argmin()][0]),
            'extBot': tuple(cnt[cnt[:, :, 1].argmax()][0]),
        }
        contours_info.append(info)
        roi = thresh[
            info['extTop'][1]:info['extBot'][1],
            info['extLeft'][0]:info['extRight'][0]
        ]
        x = info['extLeft'][0]
        y = info['extLeft'][1]
        cv2.imwrite(os.path.join("mediate_res", f'letter_{x}_{y}_{area}.png'), roi)

    dot_threshold = 500
    dot_dist_threshold = 100

    # Merge small contours (dots) with nearby larger contours (letters)
    merged_contours = []
    skip_indices = set()
    for i, info in enumerate(contours_info):
        if i in skip_indices:
            continue
        cnt = info['contour']
        if info['area'] < dot_threshold:  # Adjust area threshold as needed
            # Possible dot, find nearby larger contour
            for j in range(len(contours_info)):
                if i == j:
                    continue
                other = contours_info[j]
                if other['area'] > dot_threshold:
                    # Calculate distance between dot bottom and letter top
                    distance = math.dist(info['extBot'], other['extTop'])
                    if distance < dot_dist_threshold:
                        # Merge contours
                        merged = np.concatenate((cnt, other['contour']))

                        # if the countour was already merged, we need to remove the previous one
                        if j in skip_indices:
                            for cnt_i, cnt in enumerate(merged_contours):
                                if cnt['index'] == j:
                                    merged_contours.pop(cnt_i)
                        info['index'] = j
                        info['contour'] = merged
                        info['area'] += other['area']
                        info['extBot'] = other['extBot']
                        info['extLeft'] = other['extLeft'] if other['extLeft'][0] < info['extLeft'][0] else info['extLeft']
                        info['extRight'] = other['extRight'] if other['extRight'][0] > info['extRight'][0] else info['extRight']
                        merged_contours.append(info)
                        skip_indices.add(j)
                        skip_indices.add(i)
                        break

            skip_indices.add(i)

    for i, info in enumerate(contours_info):
        if i not in skip_indices:
            merged_contours.append(info)

    # Sort contours from left to right and from top to bottom
    merged_contours = sort_contours(merged_contours)
    # Extract and save each letter
    for idx, info in enumerate(merged_contours):
        roi = thresh[
            info['extTop'][1]:info['extBot'][1],
            info['extLeft'][0]:info['extRight'][0]
        ]
        roi = cv2.bitwise_not(roi)
        if roi.shape[0] > 0 and roi.shape[1] > 0:
            cv2.imwrite(os.path.join(output_folder, f'letter_{idx}.png'), roi)

    print(f"Extracted {len(merged_contours)} letters.")


if __name__ == "__main__":
    image_path = "input_ukr_2.jpg"
    output_folder = "result"
    segment_characters(image_path, output_folder)
    subprocess.run(
        ["./png_to_svg.sh", "result"],
    )