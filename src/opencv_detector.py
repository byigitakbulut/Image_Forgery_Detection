import cv2
import numpy as np
import base64


def detect_copy_move_in_memory(image_bytes, algorithm="SIFT", min_distance=50):
    """
    Detects copy-move forgery in an image directly from memory using feature matching.

    Parameters
    ----------
    image_bytes : bytes
        The raw image data received from the API endpoint.
    algorithm : str
        The feature detection algorithm to use ("SIFT", "AKAZE", "ORB").
    min_distance : int
        The minimum pixel distance between matched keypoints to be considered a forgery.

    Returns
    -------
    dict
        A dictionary containing the match count, a boolean indicating forgery,
        and the base64 encoded result image.
    """

    # Convert bytes to numpy array, then decode into an OpenCV image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Image could not be decoded.")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Algorithm Selection
    if algorithm == "SIFT":
        detector = cv2.SIFT_create()
        norm_type = cv2.NORM_L2
    elif algorithm == "AKAZE":
        detector = cv2.AKAZE_create()
        norm_type = cv2.NORM_HAMMING
    elif algorithm == "ORB":
        detector = cv2.ORB_create()
        norm_type = cv2.NORM_HAMMING
    else:
        raise ValueError(
            "Invalid algorithm. Please use 'SIFT', 'AKAZE', or 'ORB'. SURF is excluded due to patent restrictions.")

    # 2. Extract Keypoints and Descriptors
    keypoints, descriptors = detector.detectAndCompute(gray, None)

    if descriptors is None or len(descriptors) < 2:
        return {
            "algorithm": algorithm,
            "match_count": 0,
            "is_tampered": False,
            "result_image_base64": None,
            "message": "Not enough keypoints found."
        }

    # 3. Setup Matcher
    bf = cv2.BFMatcher(norm_type)

    # We need at least 3 descriptors to run knnMatch with k=3
    if len(descriptors) < 3:
        return {
            "algorithm": algorithm,
            "match_count": 0,
            "is_tampered": False,
            "result_image_base64": None,
            "message": "Not enough descriptors for knnMatch."
        }

    matches = bf.knnMatch(descriptors, descriptors, k=3)

    good_matches = []

    # 4. Filter Matches (Lowe's Ratio Test)
    for match in matches:
        if len(match) == 3:
            m1, m2, m3 = match

            # Ratio test (0.75 - 0.80 is generally optimal)
            if m2.distance < 0.75 * m3.distance:
                pt1 = np.array(keypoints[m1.queryIdx].pt)
                pt2 = np.array(keypoints[m2.trainIdx].pt)

                distance = np.linalg.norm(pt1 - pt2)

                if distance > min_distance:
                    good_matches.append(cv2.DMatch(m1.queryIdx, m2.trainIdx, m2.distance))

    match_count = len(good_matches)
    is_tampered = match_count > 10  # Threshold: if more than 10 strong matches, flag as tampered

    # 5. Draw Matches on Image
    result_img = cv2.drawMatches(
        img_rgb, keypoints, img_rgb, keypoints, good_matches, None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        matchColor=(255, 0, 0)
    )

    # 6. Convert Result Image to Base64 for Frontend
    # Convert RGB back to BGR for correct OpenCV encoding
    result_img_bgr = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', result_img_bgr)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return {
        "algorithm": algorithm,
        "match_count": match_count,
        "is_tampered": is_tampered,
        "result_image_base64": img_base64,
        "message": "Processing complete."
    }