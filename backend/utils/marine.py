"""
This module is used for inference functions.

Software Name : marine-detect
SPDX-FileCopyrightText: Copyright (c) Orange Business Services SA
SPDX-License-Identifier: AGPL-3.0-only.

This software is distributed under the GNU Affero General Public License v3.0,
the text of which is available at https://spdx.org/licenses/AGPL-3.0-only.html <https://spdx.org/licenses/AGPL-3.0-only.html>
or see the "LICENSE" file for more details.

Authors: Eléonore Charles
Software description: Object detection models for identifying species in marine environments.
"""

import os

import cv2
import numpy as np
from PIL import ExifTags, Image
from tqdm import tqdm
from ultralytics import YOLO


def save_combined_image(
    images_input_folder_path: str,
    image_name: str,
    output_folder_pred_images: str,
    combined_results: list,
) -> None:
    """
    Saves the results of multiple detections on an image using specified parameters.

    Args:
        images_input_folder_path (str): Path to the folder containing input images.
        image_name (str): Name of the input image.
        output_folder_pred_images (str): Path to the folder where the combined images will be saved.
        combined_results (list): List of detection results.

    Returns:
        None
    """
    # Open the image and check its orientation
    img_path = os.path.join(images_input_folder_path, image_name)
    original_image = Image.open(img_path)

    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = dict(original_image._getexif().items())

        if exif[orientation] == 3:
            original_image = original_image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            original_image = original_image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            original_image = original_image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

    output_path = os.path.join(output_folder_pred_images, image_name)
    combined_image = combine_results(np.array(original_image), combined_results)
    combined_image = cv2.cvtColor(combined_image, cv2.COLOR_BGR2RGB)
    combined_image = combined_image[..., ::-1]
    combined_image = Image.fromarray(combined_image)
    combined_image.save(output_path)


def combine_results(original_image: np.ndarray, results_list: list) -> np.ndarray:
    """
    Combines results from a list of detection outcomes.

    It uses the original image and returns the resulting combined image array.

    Args:
        original_image (np.ndarray): Array representing the original image.
        results_list (list): List of detection results.

    Returns:
        np.ndarray: Combined image array.
    """
    combined_image = original_image

    for results in results_list:
        for result in results:
            combined_image = result.plot(img=combined_image)

    return combined_image


def predict_on_images(
    model_paths: list[str],
    confs_threshold: list[float],
    images_input_folder_path: str,
    images_output_folder_path: str,
    save_txt: bool = False,
    save_conf: bool = False,
) -> None:
    """
    Utilizes a list of YOLO models to predict detections on a set of images.
    Model files should be stored in the 'models' folder for best practice.

    Args:
        model_paths (list[str]): List of paths to YOLO model files.
        confs_threshold (list[float]): List of confidence thresholds corresponding to each model.
        images_input_folder_path (str): Path to the folder containing input images.
        images_output_folder_path (str): Path to the folder where annotated images will be saved.
        save_txt (bool): Whether to save bounding box coordinates in text files.
        save_conf (bool): Whether to save confidence scores in text files.

    Returns:
        None
    """
    models = [YOLO(model_path) for model_path in model_paths]

    if images_output_folder_path:
        os.makedirs(f"{images_output_folder_path}", exist_ok=True)

    for image_name in tqdm(os.listdir(images_input_folder_path)):
        combined_results = []
        for i, model in enumerate(models):
            results = model(
                os.path.join(images_input_folder_path, image_name),
                conf=confs_threshold[i],
                save_txt=save_txt,
                save_conf=save_conf,
            )
            combined_results.extend(results)

        if images_output_folder_path:
            save_combined_image(
                images_input_folder_path,
                image_name,
                images_output_folder_path,
                combined_results,
            )


def predict_on_video(
    model_paths: list[str],
    confs_threshold: list[float],
    input_video_path: str,
    output_video_path: str,
    max_frames: int = None,  # Optional: Set a frame limit for testing
) -> None:
    """
    Processes a video using YOLO models to predict and annotate detections on frames.
    Model files should be stored in the 'models' folder for best practice.

    Args:
        model_paths (list[str]): Paths to YOLO model files.
        confs_threshold (list[float]): Confidence thresholds for each model.
        input_video_path (str): Path to input video.
        output_video_path (str): Path to save annotated output video.
        max_frames (int, optional): Max frames to process (for debugging). Default is None.

    Returns:
        None
    """

    # Load models dynamically from provided paths
    models = [YOLO(path) for path in model_paths]

    # Open input video
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video file: {input_video_path}")
        return

    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Fallback if FPS is 0
    if frame_rate == 0:
        print("⚠️ Warning: FPS is 0. Defaulting to 30 FPS.")
        frame_rate = 30

    print(f"📹 Processing video: {input_video_path}")
    print(f"Resolution: {frame_width}x{frame_height}, FPS: {frame_rate}, Total Frames: {total_frames}")

    # Define output video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (frame_width, frame_height))

    processed_frames = 0
    pbar = tqdm(total=total_frames if max_frames is None else min(max_frames, total_frames))

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("✅ End of video or failed to read frame.")
            break

        combined_results = []
        try:
            for i, model in enumerate(models):
                results = model(frame, conf=confs_threshold[i])
                
                combined_results.extend(results)
        except Exception as e:
            print(f"⚠️ Error during model prediction: {e}")
            continue

        # Combine detections and write annotated frame
        try:
            annotated_frame = combine_results(frame, combined_results)
            out.write(annotated_frame)
        except Exception as e:
            print(f"⚠️ Error during frame annotation: {e}")
            continue

        processed_frames += 1
        pbar.update(1)

        if max_frames and processed_frames >= max_frames:
            print(f"🛑 Frame limit ({max_frames}) reached. Exiting.")
            break

    cap.release()
    out.release()
    pbar.close()
    # Uncomment if you want to display the video in a windows/ GUI enabled machine
    # cv2.destroyAllWindows()
    print(f"✅ Output video saved to: {output_video_path}")
    

## Script execution removed for FastAPI integration