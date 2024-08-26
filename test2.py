import av

# Stream URLs
video_stream_url = 'rtmp://192.168.1.50:1940/extraction/stream'
audio_stream_url = 'rtmp://127.0.0.1:2940/secure-extraction/test'
output_stream_url = 'rtmp://192.168.1.50:1940/extraction/combined_stream'

# Open the input streams
print("Opening video stream...")
video_input = av.open(video_stream_url)
print("Opening audio stream...")
audio_input = av.open(audio_stream_url)

# Open the output stream with the correct format
print("Opening output stream...")
output_format = av.open(output_stream_url, 'w', format='flv')

# Get the video and audio streams
video_stream = video_input.streams.video[0]
audio_stream = audio_input.streams.audio[0]

# Create video and audio streams for the output
output_video_stream = output_format.add_stream(template=video_stream)
output_audio_stream = output_format.add_stream(template=audio_stream)

# Initialize packet reading for the video and audio streams
video_packet_gen = video_input.demux(video_stream)
audio_packet_gen = audio_input.demux(audio_stream)

# Synchronization
first_audio_pts = None
first_video_pts = None
audio_offset = None

print("Starting to mux video and audio packets...")

while True:
    video_packet = next(video_packet_gen, None)
    audio_packet = next(audio_packet_gen, None)

    # Sync video to the first PTS encountered
    if video_packet and first_video_pts is None:
        first_video_pts = video_packet.pts
        print(f"First video PTS: {first_video_pts}")

    # Adjust audio PTS based on video PTS
    if audio_packet and first_video_pts is not None:
        if first_audio_pts is None:
            first_audio_pts = audio_packet.pts
            audio_offset = first_video_pts - first_audio_pts
            print(f"First audio PTS: {first_audio_pts}, Audio Offset: {audio_offset}")

        # Adjust the audio PTS to match the video PTS
        adjusted_audio_pts = audio_packet.pts + audio_offset
        audio_packet.pts = adjusted_audio_pts
        audio_packet.dts = adjusted_audio_pts
        audio_packet.stream = output_audio_stream
        output_format.mux(audio_packet)
        print(f"Original Audio PTS: {audio_packet.pts - audio_offset}, Adjusted PTS: {adjusted_audio_pts}")

    if video_packet:
        # Pass video packets without adjustment
        video_packet.stream = output_video_stream
        output_format.mux(video_packet)
        print(f"Muxed Video Packet - PTS: {video_packet.pts}")

    # Break if both streams have finished
    if video_packet is None and audio_packet is None:
        print("Both streams ended.")
        break

# Flush the output container
print("Flushing output container...")
output_format.close()

# Close the input streams
print("Closing input streams...")
video_input.close()
audio_input.close()

print("Streaming completed successfully.")