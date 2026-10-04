import streamlit as st
st.title("Guitar Practice Tracker")

# Starting with creating a class for each practice session
if "practice_session" not in st.session_state:
    st.session_state.practice_sessions = []
class PracticeSession: 
    def __init__(self, length, date, index, songs):
        self.length = length
        self.date = date
        self.index = index
        self.songs = songs
class Song:
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp

# storing songs
if "songs" not in st.session_state:
    st.session_state.songs = []

def display_songs(songs):
    for song in songs: 
        st.write(song.name)

song_name = st.text_input("", placeholder="Add a song")

if st.button("+") and song_name: 
    st.session_state.songs.append(Song(song_name, 0))
    display_songs(st.session_state.songs)
    song_name = ""

if st.button("Save Songs"):
    current_songs = st.session_state.songs
    index = len(st.session_state.practice_sessions) + 1
    st.session_state.practice_sessions.append(PracticeSession(0, index, 0, current_songs))
    st.session_state.songs = []
    display_songs(st.session_state.songs)

