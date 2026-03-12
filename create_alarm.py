import wave
import math
import struct
import os


def generate_beep():

    # Ensure sounds folder exists
    os.makedirs("sounds", exist_ok=True)

    sample_rate = 44100
    duration = 1.0
    frequency = 800.0

    wav_file = wave.open("sounds/alarm.wav", "w")

    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)

    for i in range(int(sample_rate * duration)):

        value = int(
            32767.0 * math.sin(2 * math.pi * frequency * i / sample_rate)
        )

        data = struct.pack('<h', value)
        wav_file.writeframesraw(data)

    wav_file.close()

    print("✅ Alarm sound created at sounds/alarm.wav")


if __name__ == "__main__":
    generate_beep()