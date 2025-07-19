# 🌊 Marine Life Detection App

A full-stack AI-powered application to detect marine species in uploaded videos. Built with **FastAPI**, **YOLOv8**, and **Next.js**. Easily upload, analyze, and view marine life detections directly in your browser.

![alt text](image-1.png)

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-FF4088?style=flat&logo=python&logoColor=white" />
</p>

---
## 🐠 Supported Species

<details>
<summary><strong>📦 Fish.pt</strong></summary>

- fish  
- serranidae  
- urchin  
- scaridae  
- chaetodontidae  
- giant_clam  
- lutjanidae  
- muraenidae  
- sea_cucumber  
- haemulidae  
- lobster  
- crown_of_thorns  
- bolbometopon_muricatum  
- cheilinus_undulatus  
- cromileptes_altivelis  

</details>

<details>
<summary><strong>🐋 Marine.pt</strong></summary>

- ray  
- shark  
- turtle  

</details>

<details>
<summary><strong>🌐 best.pt</strong></summary>

- jellyfish  

</details>

---

## 🧭 Project Structure
```
Marine-Detect/
├── backend/            # ⚙️ FastAPI backend (AI inference, video processing)
│   ├── app/            #   Main backend app (API, logic)
│   ├── models/         #   YOLO model files
│   ├── results/        #   Processed/annotated videos (output)
│   └── uploads/        #   Uploaded videos (input)
├── frontend/           # 💻 Next.js frontend (React UI)
│   ├── src/            #   Source code (pages, components)
│   └── public/         #   Static assets (images, icons)
├── docker-compose.yml  # 🐳 Multi-service orchestration
└── README.md           # 📄 Project documentation
```

---

## ✨ Features

- 🎥 Upload marine life videos for detection  
- 🐬 View annotated video results in-browser  
- 🔄 Stream results using HLS format  
- 🐳 Run locally or with Docker Compose  

---



## ⚙️ Backend

- **Framework:** FastAPI (Python)
- **Libraries:** Ultralytics, OpenCV, ffmpeg
- **API Endpoints:**
  - `POST /predict/video` — Upload a video for detection
  - `GET /results/{filename}` — Stream/download processed video
  - `GET /results` — List all available processed videos

---

## 🎯 Frontend

- **Framework:** Next.js (React)
- **Key Features:** Upload form, progress indicator, video player with HLS support
- **Environment Config:** Uses `NEXT_PUBLIC_BACKEND_URL` to connect to backend

---

## 🚀 Getting Started

### 🐳 Run with Docker (Recommended)

```
docker-compose up --build
```

Then visit:
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 🔧 Local Development

<details>
<summary><strong>1️⃣ Backend</strong></summary>

```
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Install ffmpeg:  
- Ubuntu: `sudo apt-get install ffmpeg`  
- Windows: [Download](https://ffmpeg.org/download.html) and add to PATH

Run FastAPI server:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

</details>

<details>
<summary><strong>2️⃣ Frontend</strong></summary>

```
cd frontend
npm install
```

Set backend URL for development:

```
# .env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Run Next.js dev server:

```
npm run dev
```

Access the frontend in your browser:  
[http://localhost:3000](http://localhost:3000)

</details>

---

## 📹 Usage

1. Open the app in your browser  
2. Upload a marine life video (MP4 recommended)  
3. Wait while the video is processed  
4. Watch the annotated result directly in the app  

---

## 📁 Notes

- Results are saved in `backend/app/results/`
- Uploads are stored in `backend/app/uploads/`
- Place model files inside `backend/models/`
- Videos must be converted to HLS format for streaming

### 🔄 Convert MP4 to HLS using ffmpeg

```
ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8
```

---

## 🛠️ Troubleshooting

| Issue                | Solution                                         |
|---------------------|--------------------------------------------------|
| \`Failed to fetch\`   | Ensure backend is running and URL is correct     |
| Docker connection   | Use \`backend\` as hostname inside Docker Compose |
| ffmpeg not found    | Make sure ffmpeg is installed and in your PATH   |

---

## 🧪 Training for Other Species

If you want to train for a specific species here's the example notebook for training the yolov8 model.(You need the data in annotated format for yolo model to be trained)

👉 [Kaggle Notebook Example](https://www.kaggle.com/code/adityalad1234/notebook5f94400af7)

---
## 🏷️ Annotation Platform

Annotations were created using [Labelbox](https://labelbox.com/).  
You can use any annotation tool that exports in YOLO-compatible format.

---

## 📜 License

**MIT License**

---

## 👤 Author

- **Aditya Lad**

---

## Datasets

- [FishEnv Dataset](https://stpubtenakanclyw.blob.core.windows.net/marine-detect/FishInv-dataset.zip?sv=2022-11-02&ss=bf&srt=co&sp=rltf&se=2099-12-31T18:55:46Z&st=2025-02-03T10:55:46Z&spr=https,http&sig=w%2FTQzrECsYsjtkBXNnnuFtn%2BC06PkjgLxDgRw%2FaUUKI%3D
)
- [MegaFauna Dataset](https://stpubtenakanclyw.blob.core.windows.net/marine-detect/MegaFauna-dataset.zip?sv=2022-11-02&ss=bf&srt=co&sp=rltf&se=2099-12-31T18:55:46Z&st=2025-02-03T10:55:46Z&spr=https,http&sig=w%2FTQzrECsYsjtkBXNnnuFtn%2BC06PkjgLxDgRw%2FaUUKI%3D)

## 🙏 Acknowledgements

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)

