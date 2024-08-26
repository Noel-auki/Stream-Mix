import subprocess
import time

def get_stream_start_time(stream_url, stream_type):
    print(f"Getting {stream_type} PTS")
    """Get the start time of the stream."""
    while True:
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=start_time', '-of', 'default=nw=1:nk=1', stream_url],
                capture_output=True, text=True
            )
            print(result.stdout)
            print(result.stderr)
            if result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e:
            print(f"Error fetching {stream_type} PTS: {e}")
        
        print(f"Waiting for {stream_type} stream to start...")
        time.sleep(2)

def stream_to_ivs(video_url, audio_url, output_stream_url):
    # Wait for the audio and video streams to become available
    video_start_time = get_stream_start_time(video_url, "video")
    audio_start_time = get_stream_start_time(audio_url, "audio")
   


    # Calculate the offset required for synchronization
    video_offset =  audio_start_time - video_start_time
    print(f'Calculated video offset: {video_offset}')
   
    # applied_offset =-(video_offset/1000)
    # print(f'Applied Offset: {applied_offset}')

        
    command = [
        'ffmpeg',
        # '-itsoffset', str(video_offset),  # Apply delay to the audio stream
        '-i', audio_url,                 # Input audio URL
        '-itsoffset', str(video_offset),
        '-i', video_url,                 # Input video URL
        '-c:v', 'copy',                  # Copy the video codec as is
        '-c:a', 'aac',                   # Encode audio in AAC format
        '-map', '1:v:0',                 # Map video from the second input
        '-map', '0:a:0',                 # Map audio from the first input (with delay)
        '-tune', 'zerolatency',
        '-preset', 'ultrafast',
        '-shortest',                     # Stop encoding when the shortest stream ends
        '-f', 'flv',                     # Use the FLV format for streaming over RTMP(S)
        output_stream_url                # The AWS IVS RTMP stream URL
    ]


    print(f'Running FFmpeg command: {" ".join(command)}')

    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

if __name__ == "__main__":
    video_url = 'rtmp://192.168.1.50:1940/extraction/stream'
    audio_url = 'rtmp://127.0.0.1:2940/secure-extraction/test'
    output_stream_url = "rtmp://192.168.1.50:1940/extraction/combined_stream"
    
    stream_to_ivs(video_url, audio_url, output_stream_url)