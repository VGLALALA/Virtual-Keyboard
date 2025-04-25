import json
import os
import time
import webbrowser
from playsound import playsound
from arduino import ArduinoSpeaker

def play_song(song_name, playlist_json_path, arduino_port=None, baudrate=9600):
    # Load playlist
    with open(playlist_json_path, 'r') as f:
        playlist = json.load(f)

    if song_name not in playlist:
        print(f"Song '{song_name}' not found in playlist.")
        return

    song_info = playlist[song_name]

    if arduino_port:
        try:
            speaker = ArduinoSpeaker(arduino_port, baudrate)
            if 'music_sheet' in song_info:
                print(f"Playing '{song_name}' on Arduino speaker...")
                speaker.play_music_sheet(song_info['music_sheet'])
                speaker.close()
                return
            else:
                print(f"No music sheet available for '{song_name}'. Cannot play on speaker.")
                speaker.close()
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")

    # Fallback to playing audio file if Arduino is not used or failed
    if 'audio_file' in song_info and os.path.exists(song_info['audio_file']):
        print(f"Playing '{song_name}' audio file...")
        playsound(song_info['audio_file'])
    else:
        print(f"No audio file found for '{song_name}'. Opening YouTube search...")
        query = song_name.replace(' ', '+')
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

def add_song(song_name, audio_file_path, playlist_json_path, music_sheet=None):
    # Load existing playlist
    if os.path.exists(playlist_json_path):
        with open(playlist_json_path, 'r') as f:
            playlist = json.load(f)
    else:
        playlist = {}

    # Add new song
    playlist[song_name] = {'audio_file': audio_file_path}
    if music_sheet:
        playlist[song_name]['music_sheet'] = music_sheet

    # Save updated playlist
    with open(playlist_json_path, 'w') as f:
        json.dump(playlist, f, indent=4)

    print(f"Song '{song_name}' added to playlist.")

# Example Usage:
# play_song('Twinkle Twinkle', 'playlist.json', arduino_port='COM3')
# play_song('Twinkle Twinkle', 'playlist.json')  # without Arduino
# add_song('New Song', 'new_song.mp3', 'playlist.json', [440, 440, 440, 0, 440, 440, 440])