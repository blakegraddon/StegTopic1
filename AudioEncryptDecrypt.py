import wave

def encode_message_to_sound(input_audio, message, output_audio):

    with wave.open(input_audio, 'rb') as audio:

        params, frames = audio.getparams(), bytearray(audio.readframes(audio.getnframes()))

    #Binary section
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'

    # File too small
    if len(binary_message) > len(frames):
        raise ValueError("Audio file too small for the message.")

    for i, bit in enumerate(binary_message):
        frames[i] = (frames[i] & ~1) | int(bit)

    #Output wave
    with wave.open(output_audio, 'wb') as output:
        output.setparams(params)
        output.writeframes(frames)

    print(f"Message encoded in {output_audio}")

def decode_message_from_sound(input_audio):

    with wave.open(input_audio, 'rb') as audio:

        frames = bytearray(audio.readframes(audio.getnframes()))

    binary_message = ''.join(str(frame & 1) for frame in frames)

    decoded_message = ''.join(
        chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)
    )

    # Decoding finished
    return decoded_message.split('\x00', 1)[0]

def main():
    print("WAV Encryption & Decryption")
    choice = input("To encode, type 'encode'\nTo decode, type 'decode'\nPlease enter selectiion here: ")

    if choice == "encode":
        encode_message_to_sound(
            input("Input WAV file name: "),
            input("Message to encode: "),
            input("Output WAV file name: ")
        )
    elif choice == "decode":
        print("Decoded message:", decode_message_from_sound(input("Encoded WAV file: ")))
    else:
        print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
