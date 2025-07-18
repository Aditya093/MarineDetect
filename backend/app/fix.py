import ffmpeg

def remux_video(input_path, output_path):
    ffmpeg.input(input_path).output(output_path, c='copy', movflags='+faststart').run(overwrite_output=True)
remux_video("C:\\Users\\Lenovo\\Downloads\\Marine Detect\\backend\\results\\result_1151284-hd_1920_1080_30fps.mp4", "fixed.mp4")
