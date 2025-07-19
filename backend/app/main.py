from fastapi import FastAPI, UploadFile, File, Form, status, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import logging,subprocess

from utils.marine import predict_on_images, predict_on_video
from .config import MODELS_DIR, UPLOAD_DIR, RESULT_DIR

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges","Content-Length", "Content-Type"]
)

# Serve static video results
app.mount("/results", StaticFiles(directory="results"), name="results")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


@app.post("/predict/images")
def predict_images(
    confs_threshold: list[float] = Form(...),
    images: list[UploadFile] = File(...)
):
    input_folder = os.path.join(UPLOAD_DIR, "images")
    output_folder = os.path.join(RESULT_DIR, "images")
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    for image in images:
        with open(os.path.join(input_folder, image.filename), "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    model_paths = [os.path.join(MODELS_DIR, name) for name in os.listdir(MODELS_DIR) if name.endswith('.pt')]

    predict_on_images(
        model_paths=model_paths,
        confs_threshold=confs_threshold,
        images_input_folder_path=input_folder,
        images_output_folder_path=output_folder
    )

    return JSONResponse({"result_folder": output_folder})


import subprocess

@app.post("/predict/video")
def predict_video(
    video: UploadFile = File(...),
    max_frames: int = 100
):
    input_video_path = os.path.join(UPLOAD_DIR, video.filename)
    output_video_path = os.path.join(RESULT_DIR, f"result_{video.filename}")
    output_hls_dir = os.path.join(RESULT_DIR, f"hls_{video.filename}")
    os.makedirs(output_hls_dir, exist_ok=True)
    
    confs_threshold = [0.5, 0.5, 0.5]

    # Save uploaded video
    with open(input_video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # Run prediction
    model_paths = [os.path.join(MODELS_DIR, name) for name in os.listdir(MODELS_DIR) if name.endswith('.pt')]
    predict_on_video(
        model_paths=model_paths,
        confs_threshold=confs_threshold,
        input_video_path=input_video_path,
        output_video_path=output_video_path,
        max_frames=max_frames
    )

    # Convert to HLS using ffmpeg
    hls_playlist_path = os.path.join(output_hls_dir, "index.m3u8")
    ffmpeg_command = [
        "ffmpeg",
        "-i", output_video_path,
        "-codec:V", "libx264",
        "-codec:a", "aac",
        "-flags", "+cgop",
        "-g", "30",
        "-hls_time", "4",
        "-hls_list_size", "0",
        "-f", "hls",
        hls_playlist_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"HLS conversion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert video to HLS")

    # Return path to HLS playlist (relative to /results)
    hls_relative_path = f"hls_{video.filename}/index.m3u8"
    return {"hls_url": f"/results/{hls_relative_path}"}


@app.get("/")
def root():
    return {"message": "Marine Detect API is running."}


@app.get("/results/{filename}")
async def get_result_video(filename: str, request: Request):
    file_path = os.path.join(RESULT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("range")

    headers = {
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Cache-Control": "no-cache",
    }

    if range_header:
        try:
            range_val = range_header.strip().split("=")[-1]
            range_start, range_end = range_val.split("-")
            range_start = int(range_start) if range_start else 0
            range_end = int(range_end) if range_end else file_size - 1
            range_end = min(range_end, file_size - 1)
            chunk_size = (range_end - range_start) + 1

            async def range_stream():
                try:
                    with open(file_path, "rb") as f:
                        f.seek(range_start)
                        remaining = chunk_size
                        while remaining > 0:
                            chunk = f.read(min(4096, remaining))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk
                except (ConnectionResetError, BrokenPipeError):
                    logging.info("Client disconnected during streaming")
                except Exception as e:
                    logging.error(f"Streaming error: {str(e)}")

            headers["Content-Range"] = f"bytes {range_start}-{range_end}/{file_size}"
            return StreamingResponse(
                range_stream(),
                status_code=206,
                headers=headers,
                media_type="video/mp4"
            )
        except Exception as e:
            logging.error(f"Range header processing error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid range header")

    # return FileResponse(
    #     file_path,
    #     headers=headers,
    #     media_type="video/mp4"
    # )
    # Full video stream (no Range header)

    def full_stream():
        try:
            with open(file_path, "rb") as f:
                yield from f
        except ConnectionResetError:
            print("Client disconnected while streaming (full).")
            return

    return StreamingResponse(
        full_stream(),
        media_type="video/mp4",
        headers={
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "content-encoding": "identity",
            "Content-Type": "video/mp4"
        }
    )
