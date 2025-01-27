from moviepy import VideoFileClip, AudioFileClip
import wave
import numpy as np

# This function encodes the message into the least significant bits of the audio samples
def encode_message_to_audio(input_audio_path, message, output_audio_path):
    # Open the input audio file (16-bit PCM expected)
    with wave.open(input_audio_path, 'rb') as audio:
        params = audio.getparams()
        frames = bytearray(audio.readframes(audio.getnframes()))

    # Convert the message to binary and add a stop byte '00000000' at the end
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'

    # Debugging: Print the first few binary bits of the message
    print(f"Binary message (first 64 bits): {binary_message[:64]}")

    # Check if the message can fit in the audio file
    if len(binary_message) > len(frames):
        raise ValueError("Message is too long to fit in the audio file.")

    # Encode the message into the LSB of each audio frame (assuming 16-bit audio)
    binary_index = 0
    for i in range(0, len(frames), 2):  # Process 2 bytes (16 bits) at a time
        if binary_index < len(binary_message):
            # Get the current 16-bit frame (2 bytes)
            sample = frames[i] | (frames[i + 1] << 8)
            # Replace the least significant bit with the message bit
            sample = (sample & 0xFFFE) | int(binary_message[binary_index])  # Modify LSB
            # Save the modified sample back to the frame
            frames[i] = sample & 0xFF
            frames[i + 1] = (sample >> 8) & 0xFF
            binary_index += 1

    # Save the encoded audio to the output path
    with wave.open(output_audio_path, 'wb') as encoded_audio:
        encoded_audio.setparams(params)
        encoded_audio.writeframes(frames)

    print(f"Message encoded and saved to {output_audio_path}")

# This function decodes the hidden message from the audio of the video
def decode_message_from_audio(input_audio_path):
    # Open the audio file and read the frames
    with wave.open(input_audio_path, 'rb') as audio:
        frames = bytearray(audio.readframes(audio.getnframes()))

    # Extract the LSBs of each frame to build the binary message
    binary_message = ''
    for i in range(0, len(frames), 2):  # Process 2 bytes (16 bits) at a time
        # Get the current 16-bit frame
        sample = frames[i] | (frames[i + 1] << 8)
        # Extract the LSB
        binary_message += str(sample & 1)

    # Debugging: Print the first few binary bits extracted from the audio
    print(f"Binary message (first 64 bits extracted): {binary_message[:64]}")

    # Convert the binary message into characters
    decoded_message = ''
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        if byte == '00000000':  # Stop at the stop byte
            break
        decoded_message += chr(int(byte, 2))

    return decoded_message

# This function hides a message in the audio of a video
def encode_message_to_video(input_video_path, message, output_video_path):
    # Extract audio from the video
    input_audio_path = '/tmp/temp_audio.wav'
    video_clip = VideoFileClip(input_video_path)
    video_clip.audio.write_audiofile(input_audio_path, codec='pcm_s16le')

    # Encode the message into the extracted audio
    encoded_audio_path = '/tmp/encoded_audio.wav'
    encode_message_to_audio(input_audio_path, message, encoded_audio_path)

    # Replace the original audio with the encoded audio
    encoded_audio_clip = AudioFileClip(encoded_audio_path)
    final_video = video_clip.with_audio(encoded_audio_clip)

    # Save the final video with the encoded audio
    final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

    print(f"Video with encoded message saved to {output_video_path}")

# This function extracts the hidden message from the audio of a video
def decode_message_from_video(input_video_path):
    # Extract audio from the video
    input_audio_path = '/tmp/extracted_audio.wav'
    video_clip = VideoFileClip(input_video_path)
    video_clip.audio.write_audiofile(input_audio_path, codec='pcm_s16le')

    # Decode the hidden message from the audio
    decoded_message = decode_message_from_audio('/tmp/encoded_audio.wav')
    return decoded_message

def main():
    print("1. Encode a message in video")
    print("2. Decode a message from video")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        input_video_path = input("Enter the path to the input video file (MP4 format): ")
        message = input("Enter the message to encode: ")
        output_video_path = input("Enter the path for the output video file: ")
        try:
            encode_message_to_video(input_video_path, message, output_video_path)
        except Exception as e:
            print(f"Error: {e}")

    elif choice == "2":
        input_video_path = input("Enter the path to the encoded video file (MP4 format): ")
        try:
            decoded_message = decode_message_from_video(input_video_path)
            print(f"Decoded message: {decoded_message}")
        except Exception as e:
            print(f"Error: {e}")

    elif choice == "3":
        print("Exiting.")
        return  # Terminate the program explicitly when exiting.
    else:
        print("Invalid choice. Exiting.")
        return  # Exit program when invalid choice is given.

if __name__ == "__main__":
    main()
