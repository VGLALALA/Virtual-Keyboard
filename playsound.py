from pydub import AudioSegment
import simpleaudio as sa

def playsound(music_file):
    try:
        # Load the music file
        song = AudioSegment.from_file(music_file, format="mp3")
        # Convert to raw audio data for simpleaudio
        play_obj = sa.play_buffer(
            song.raw_data,
            num_channels=song.channels,
            bytes_per_sample=song.sample_width,
            sample_rate=song.frame_rate
        )
        play_obj.wait_done()  # Block until playback is finished
    except Exception as e:
        print(f"Error playing sound: {e}")
