import math
import cv2
import numpy as np
import os

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
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Find contours on the dilated image
    contours, hierarchy = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    # thresh = cv2.erode(thresh, None, iterations=2)
    # thresh = cv2.dilate(thresh, None, iterations=2)

# Calculate bounding boxes and centroids
    contours_info = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        # M = cv2.moments(cnt)
        # if M["m00"] != 0:
        #     cx = int(M["m10"] / M["m00"])
        #     cy = int(M["m01"] / M["m00"])
        # else:
        #     cx, cy = x + w // 2, y + h // 2
        contours_info.append({
            'contour': cnt,
            'x': x,
            'y': y,
            'w': w,
            'h': h,
            'area': area,
            'extLeft': tuple(cnt[cnt[:, :, 0].argmin()][0]),
            'extRight': tuple(cnt[cnt[:, :, 0].argmax()][0]),
            'extTop': tuple(cnt[cnt[:, :, 1].argmin()][0]),
            'extBot': tuple(cnt[cnt[:, :, 1].argmax()][0]),
            # 'cx': cx,
            # 'cy': cy
        })

    # Sort contours from left to right
    contours_info = sorted(contours_info, key=lambda c: c['x'])

    # Merge small contours (dots) with nearby larger contours (letters)
    merged_contours = []
    skip_indices = set()
    for i, info in enumerate(contours_info):
        if i in skip_indices:
            continue
        x, y, w, h, area = info['x'], info['y'], info['w'], info['h'], info['area']
        cnt = info['contour']
        if area < 1000:  # Adjust area threshold as needed
            # Possible dot, find nearby larger contour
            for j in range(len(contours_info)):
                if i == j or j in skip_indices:
                    continue
                other = contours_info[j]
                if other['area'] > area:
                    # Calculate distance between centroids
                    # distance = math.hypot(info['cx'] - other['cx'], info['cy'] - other['cy'])

                    distance = math.dist(info['extBot'], other['extTop'])
                    if distance < 100:  # Adjust distance threshold as needed
                        # Merge contours
                        merged = np.concatenate((cnt, other['contour']))
                        merged_contours.append(merged)
                        skip_indices.update([i, j])
                        break
        #     else:
        #         # No nearby larger contour found, keep as is
        #         merged_contours.append(cnt)
        # else:
        #     # Larger contour, check if already merged
        #     if i not in skip_indices:
        #         merged_contours.append(cnt)

    for i, info in enumerate(contours_info):
        if i not in skip_indices:
            merged_contours.append(info['contour'])

    # Extract and save each letter
    for idx, cnt in enumerate(merged_contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 10 and h > 10:
            roi = thresh[y:y+h, x:x+w]
            cv2.imwrite(os.path.join(output_folder, f'letter_{idx}.png'), roi)

    print(f"Extracted {len(merged_contours)} letters.")


if __name__ == "__main__":
    image_path = "input.jpeg"
    # image_path = "inpu_i.jpeg"
    output_folder = "result"
    segment_characters(image_path, output_folder)