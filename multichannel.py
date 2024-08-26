import subprocess
import threading
import time

def stream_to_ivs(video_url, audio_url, output_stream_url):
    command = [
        'ffmpeg',
        # '-re',
        # '-fflags', 'nobuffer',  # Read input at native frame rate
        '-i', video_url,        # Input video URL
        '-i', audio_url,        # Input audio URL
        '-c:v', 'copy',         # Copy the video codec as is
        '-c:a', 'aac',          # Encode audio in AAC format
        '-map', '0:v:0',        # Map video from the first input
        '-map', '1:a:0',        # Map audio from the second input
        '-tune', 'zerolatency',
        '-preset', 'ultrafast',
        '-shortest',          
        '-f', 'flv',            # Use the FLV format for streaming over RTMP(S)
        output_stream_url       # The AWS IVS RTMP stream URL
    ]

    while True:
        try:
            print(f'Running FFmpeg command: {" ".join(command)}')
            result = subprocess.run(command, capture_output=True, text=True)
            print(result.stdout)
            print(result.stderr)
            break  # Exit loop if FFmpeg process completes successfully
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    video_url_1 = 'https://937a5aa6b93e.us-west-2.playback.live-video.net/api/video/v1/us-west-2.730335574547.channel.22fqWlEHEUCc.m3u8'
    video_url_2 = 'https://937a5aa6b93e.us-west-2.playback.live-video.net/api/video/v1/us-west-2.730335574547.channel.sbRWwkwHZkYg.m3u8'
    audio_url = 'https://937a5aa6b93e.us-west-2.playback.live-video.net/api/video/v1/us-west-2.730335574547.channel.3lcLwrlSljEj.m3u8'
    output_stream_url_1 = "rtmps://937a5aa6b93e.global-contribute.live-video.net:443/app/sk_us-west-2_aCxhZGHSwyBx_PTAE4SbAcPWjLep9nxlh7EaJrZpJ17"
    output_stream_url_2 = "rtmps://937a5aa6b93e.global-contribute.live-video.net:443/app/sk_us-west-2_mSiXvssfKEQW_SXedNKxlSN6K6qqiMuWEtX1rdknZim"

    # Create two threads for the two streaming processes
    thread_1 = threading.Thread(target=stream_to_ivs, args=(video_url_1, audio_url, output_stream_url_1))
    thread_2 = threading.Thread(target=stream_to_ivs, args=(video_url_2, audio_url, output_stream_url_2))

    # Start both threads
    thread_1.start()
    thread_2.start()

    # Wait for both threads to finish
    thread_1.join()
    thread_2.join()
