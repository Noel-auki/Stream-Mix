import subprocess

def stream_to_nginx(video_stream_url, audio_stream_url, output_stream_url):
    command = [
        'ffmpeg',
        '-i', video_stream_url,  # Video stream URL from Nginx
        '-i', audio_stream_url,  # Audio stream URL from Nginx
        '-c:v', 'copy',          # Copy video codec
        '-c:a', 'aac',           # Encode audio to AAC
        '-map', '0:v:0',         # Map the video stream
        '-map', '1:a:0',         # Map the audio stream
        '-tune', 'zerolatency',  # Tune for low latency
        '-preset', 'ultrafast',  # Set encoding preset
        '-shortest',             # Finish when the shortest input ends
        '-f', 'flv',             # Output format
        output_stream_url        # Output stream URL
    ]

    print(f'Running FFmpeg command: {" ".join(command)}')

    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

if __name__ == "__main__":
    video_stream_url = 'rtmp://192.168.1.50:1940/extraction/stream'  # Video stream URL from Larix Broadcaster
    audio_stream_url = 'rtmp://127.0.0.1:2940/secure-extraction/test'  # Audio stream URL from OBS
    output_stream_url = 'rtmp://192.168.1.50:1940/extraction/combined_stream'  # URL to output the combined stream to Nginx

    stream_to_nginx(video_stream_url, audio_stream_url, output_stream_url)
