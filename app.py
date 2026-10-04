import streamlit as st
import time
import datetime

# Classes
class PracticeSession: 
    def __init__(self, length, date, index, songs):
        self.length = length
        self.date = date
        self.index = index
        self.songs = songs
class Song:
    def __init__(self, name, duration, start):
        self.name = name
        self.duration = duration
        self.start = start

# State
def init_state():
    st.session_state.setdefault("running", False)
    st.session_state.setdefault("start_time", 0.0)
    st.session_state.setdefault("elapsed", 0.0)

    st.session_state.setdefault("practice_sessions", [])
    st.session_state.setdefault("songs", [])

init_state()

# State: accumulated time, whether it's running, and when the current run began

#Logical functions

#Timer
def current_elapsed():
    if st.session_state.running:
        return st.session_state.elapsed + (time.time() - st.session_state.start_time)
    return st.session_state.elapsed

def format_time(total):
    h, rem = divmod(int(total), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def start_stopwatch():
    st.session_state.running = True
    st.session_state.start_time = time.time()

def stop_stopwatch():
    st.session_state.elapsed = current_elapsed()
    st.session_state.running = False

def reset_stopwatch():
    st.session_state.running = False
    st.session_state.elapsed = 0.0

# song/session updates
def close_current_song():
    songs = st.session_state.songs
    if songs:
        songs[-1].duration = current_elapsed() - songs[-1].start

def add_song(name):
    close_current_song()
    st.session_state.songs.append(Song(name, 0, current_elapsed()))
def save_session():
    songs = st.session_state.songs
    index = len(songs) + 1
    st.session_state.practice_sessions.append(
        PracticeSession(
            length=current_elapsed(), 
            date=datetime.date.today(),
            index=index,
            songs=songs
        )
    )
    st.session_state.songs = []
    reset_stopwatch()


#  UI
def refresh_rate():
    return 1 if st.session_state.running else None


@st.fragment(run_every=refresh_rate())
def render_stopwatch_display():
    st.header(format_time(current_elapsed()))


def render_stopwatch_controls():
    col1, col2 = st.columns(2)
    if st.session_state.running:
        col1.button("Stop", on_click=stop_stopwatch, use_container_width=True)
    else:
        col1.button("Start", on_click=start_stopwatch, use_container_width=True)
    col2.button("Reset", on_click=reset_stopwatch, use_container_width=True)


def render_add_song_form():
    with st.form("add_song_form", clear_on_submit=True):
        name = st.text_input("Song", placeholder="Add a song", label_visibility="collapsed")
        submitted = st.form_submit_button("+")
    if submitted and name.strip() and st.session_state.running:
        add_song(name.strip())
        st.rerun()


@st.fragment(run_every=refresh_rate())
def render_song_list():
    songs = st.session_state.songs
    for i, song in enumerate(songs):
        is_current = i == len(songs) - 1
        seconds = current_elapsed() - song.start if is_current else song.duration
        st.write(f"{i + 1}. {song.name}: {format_time(seconds)}")


def render_history():
    st.subheader("History")
    for session in reversed(st.session_state.practice_sessions):
        with st.expander(f"Session {session.index} ({session.date}): {format_time(session.length)}"):
            for song in session.songs:
                st.write(f"{song.name}: {format_time(song.duration)}")


# ---------- Main ----------
st.title("Guitar Practice Tracker")

render_stopwatch_display()
render_stopwatch_controls()
render_add_song_form()
render_song_list()
st.button("Save Session", on_click=save_session)
render_history()


