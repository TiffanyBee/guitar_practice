import streamlit as st
import time
import datetime
import pandas as pd
import db
import csv

## WORKING ON DATABASE FOR SONGS
# Classes
class PracticeSession: 
    def __init__(self, length, date, index, songs):
        self.length = length
        self.date = date
        self.index = index
        self.songs = songs
        self.total_songs = len(songs)
class Song:
    def __init__(self, name, duration, start):
        self.name = name
        self.duration = duration
        self.start = start
        

# State


def update_dataframe():
    practice_sessions = st.session_state.practice_sessions
    st.session_state.sessions_df = pd.DataFrame([vars(s) for s in practice_sessions])

    total_songs = st.session_state.total_songs
    st.session_state.total_songs_df = pd.DataFrame([vars(s) for s in total_songs])


def load_db():
    sessions = []
    total_songs = []
    for row in db.load_sessions():
        current_songs = [Song(name, duration, 0,) for name, duration in row["songs"]]
        sessions.append(
            PracticeSession(
                length=row["length"],
                date=row["date"],
                index=len(sessions) + 1,
                songs=current_songs,
            )
        )
        total_songs.extend(current_songs)
    return [sessions, total_songs]


def init_state():
    st.session_state.setdefault("running", False)
    st.session_state.setdefault("start_time", 0.0)
    st.session_state.setdefault("elapsed", 0.0)

    st.session_state.setdefault("practice_sessions", [])
    st.session_state.practice_sessions = load_db()[0]
    st.session_state.setdefault("total_songs", [])
    st.session_state.total_songs = load_db()[1]
    st.session_state.setdefault("current_songs", [])


    st.session_state.setdefault("sessions_df", pd.DataFrame())
    st.session_state.setdefault("total_songs_df", pd.DataFrame())
    update_dataframe()



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
    songs = st.session_state.current_songs
    if songs:
        songs[-1].duration = current_elapsed() - songs[-1].start

def add_song(name):
    close_current_song()
    st.session_state.current_songs.append(Song(name, 0, current_elapsed()))

def save_session():
    close_current_song()
    songs = st.session_state.current_songs
    practice_sessions = st.session_state.practice_sessions
    index = len(practice_sessions) + 1
    length = current_elapsed()
    
    db.save_session(
        date = datetime.date.today(),
        length = length,
        songs = [(s.name, s.duration) for s in songs]
    )

    st.session_state.practice_sessions = load_db()[0]
    update_dataframe()

    _ = """
    st.session_state.practice_sessions.append(
        PracticeSession(
            length=length, 
            date=datetime.date.today(),
            index=index,
            songs=songs
        )
    )
    """
    #songs_df = st.sessions_state.songs_df
    #current_songs_df = pd.DataFrame([vars(s) for s in songs])
    #st.sessions_state.songs_df = pd.concat([songs_df, current_songs_df], ignore_index=True])
    st.session_state.current_songs = []
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
    songs = st.session_state.current_songs
    for i, song in enumerate(songs):
        is_current = i == len(songs) - 1
        seconds = current_elapsed() - song.start if is_current else song.duration

        # rendering button and column
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"{i + 1}. {song.name}: {format_time(seconds)}")
        with col2:
            st.button("x", key=i)


def delete_song():
    songs = st.session_state.current_songs
    song_todelete = [for i in range(len(songs)) if st.session_state[i]]
    st.session_state["clicked"] = True

def render_history():
    st.subheader("History")
    for session in reversed(st.session_state.practice_sessions):
        with st.expander(f"Session {session.index} ({session.date}): {format_time(session.length)} ({session.total_songs} songs)"):
            for song in session.songs:
                st.write(f"{song.name}: {format_time(song.duration)}")

## data visualization
def render_dataframe():
    session_df = st.session_state.sessions_df
    st.write(session_df)
    songs_df = st.session_state.total_songs_df
    
    st.write(songs_df)


def session_length_overtime():
    sessions = st.session_state.sessions_df
    st.line_chart(data=sessions, x="index", y="length")

def ranked_songs_chart():
    songs = st.session_state.total_songs_df
    songs["minutes"] = songs["duration"] / 60
    st.bar_chart(data=songs, x="name", y="minutes", horizontal=True)

# ---------- Main ----------
st.title("Guitar Practice Tracker")

render_stopwatch_display()
render_stopwatch_controls()
render_add_song_form()
render_song_list()
st.button("Save Session", on_click=save_session)
render_history()
render_dataframe()
session_length_overtime()
ranked_songs_chart()

#update_dataframe()
