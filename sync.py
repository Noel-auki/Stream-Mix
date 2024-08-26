import subprocess

def get_first_pts(stream_url, stream_type, timeout=10):
    command = [
        'ffmpeg',
        '-i', stream_url,
        '-map', f'0:{stream_type}',
        '-c', 'copy',
        '-f', 'null',
        '-'
    ]
    
    print(f'Running FFmpeg to get first PTS for {stream_type} stream: {" ".join(command)}')
    
    try:
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True, timeout=timeout)
        pts_time = None
        
        for line in result.stderr.splitlines():
            print(f"FFmpeg output: {line}")  # Print FFmpeg output for debugging
            if 'pts_time:' in line:
                pts_time = float(line.split('pts_time:')[1].split()[0])
                break
        
        if pts_time is None:
            print(f"Failed to retrieve PTS for {stream_type} stream.")
        else:
            print(f"First PTS for {stream_type} stream: {pts_time}")
        
        return pts_time
    
    except subprocess.TimeoutExpired:
        print(f"FFmpeg command timed out after {timeout} seconds while trying to get PTS for {stream_type}.")
        return None

def stream_to_nginx(video_stream_url, audio_stream_url, output_stream_url):
    # Get the first PTS of the video and audio streams
    video_pts = get_first_pts(video_stream_url, 'v:0')
    audio_pts = get_first_pts(audio_stream_url, 'a:0')

    if video_pts is None or audio_pts is None:
        print("Failed to retrieve PTS for either video or audio stream. Exiting.")
        return

    # Calculate the delay needed
    audio_delay = video_pts - audio_pts
    print(f"Calculated audio delay: {audio_delay} seconds")

    # Construct the FFmpeg command
    command = [
        'ffmpeg',
        '-i', video_stream_url,  # Video stream URL from Nginx
    ]
    
    if audio_delay > 0:
        command.extend(['-itsoffset', str(audio_delay), '-i', audio_stream_url])  # Apply delay to audio
    else:
        command.extend(['-itsoffset', str(-audio_delay), '-i', video_stream_url])  # Apply delay to video
    
    command.extend([
        '-c:v', 'copy',          # Copy video codec
        '-c:a', 'aac',           # Encode audio to AAC
        '-map', '0:v:0',         # Map the video stream
        '-map', '1:a:0',         # Map the audio stream
        '-tune', 'zerolatency',  # Tune for low latency
        '-preset', 'ultrafast',  # Set encoding preset
        '-shortest',             # Finish when the shortest input ends
        '-f', 'flv',             # Output format
        output_stream_url        # Output stream URL
    ])

    print(f'Running FFmpeg command to stream: {" ".join(command)}')
    
    # Run FFmpeg with the dynamically calculated offset
    result = subprocess.run(command, capture_output=True, text=True)
    print("FFmpeg stdout:")
    print(result.stdout)
    print("FFmpeg stderr:")
    print(result.stderr)

if __name__ == "__main__":
    video_stream_url = 'rtmp://192.168.29.202:1940/extraction/stream'  # Video stream URL from Larix Broadcaster
    audio_stream_url = 'rtmp://127.0.0.1:2940/secure-extraction/test'  # Audio stream URL from OBS
    output_stream_url = 'rtmp://192.168.29.202:1940/extraction/combined_stream'  # URL to output the combined stream to Nginx

    stream_to_nginx(video_stream_url, audio_stream_url, output_stream_url)
