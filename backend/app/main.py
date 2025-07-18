from fastapi import FastAPI, UploadFile, File, Form, status, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import logging

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
    expose_headers=["Content-Range", "Accept-Ranges"]
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


@app.post("/predict/video")
def predict_video(
    video: UploadFile = File(...),
    max_frames: int = 100
):
    input_video_path = os.path.join(UPLOAD_DIR, video.filename)
    output_video_path = os.path.join(RESULT_DIR, f"result_{video.filename}")
    confs_threshold = [0.5, 0.5, 0.5]

    with open(input_video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    model_paths = [os.path.join(MODELS_DIR, name) for name in os.listdir(MODELS_DIR) if name.endswith('.pt')]

    predict_on_video(
        model_paths=model_paths,
        confs_threshold=confs_threshold,
        input_video_path=input_video_path,
        output_video_path=output_video_path,
        max_frames=max_frames
    )

    return {"result_video_filename": f"result_{video.filename}"}


@app.get("/")
def root():
    return {"message": "Marine Detect API is running."}


@app.get("/results/{filename}")
async def get_result_video(filename: str, request: Request):
    print('Received request for video:', filename)
    file_path = os.path.join(RESULT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = os.path.getsize(file_path)
    # range_header = request.headers.get("range")

    # if range_header:
    #     # Parse Range: bytes=start-end
    #     range_val = range_header.strip().split("=")[-1]
    #     range_start, range_end = range_val.split("-")
    #     range_start = int(range_start) if range_start else 0
    #     range_end = int(range_end) if range_end else file_size - 1

    #     chunk_size = (range_end - range_start) + 1

    #     def range_stream():
    #         try:
    #             with open(file_path, "rb") as f:
    #                 f.seek(range_start)
    #                 yield f.read(chunk_size)
    #         except ConnectionResetError:
    #             print("Client disconnected while streaming (range).")
    #             return

    #     return StreamingResponse(
    #         range_stream(),
    #         status_code=206,
    #         media_type="video/mp4",
    #         headers={
    #             "Content-Range": f"bytes {range_start}-{range_end}/{file_size}",
    #             "Accept-Ranges": "bytes",
    #             "Content-Length": str(chunk_size),
    #             "content-encoding": "identity",
    #             "Content-Type": "video/mp4"
    #         },
    #     )

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
