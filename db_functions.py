import psycopg2
import hashlib
from contextlib import closing
import streamlit as st
import os

# Update this with your PostgreSQL connection details
DB_CONFIG = {
    'dbname': 'echo_db',
    'user': 'postgres',
    'password': 'Family@04',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    user_id SERIAL PRIMARY KEY,
                    email TEXT,
                    password TEXT
                );
                CREATE TABLE IF NOT EXISTS Transcripts (
                    transcript_id SERIAL PRIMARY KEY,
                    file_name TEXT,
                    transcription TEXT,
                    transcription_summary TEXT,
                    sentiment_label TEXT,
                    sentiment_report TEXT,
                    prev_ai_research TEXT,
                    fact_check TEXT,
                    user_id INTEGER REFERENCES Users(user_id)
                );
                CREATE TABLE IF NOT EXISTS AudioFiles (
                    audio_id SERIAL PRIMARY KEY,
                    file_name TEXT,
                    audio_data BYTEA,
                    transcript_id INTEGER REFERENCES Transcripts(transcript_id)
                );
                CREATE TABLE IF NOT EXISTS Messages (
                    message_id SERIAL PRIMARY KEY,
                    role TEXT,
                    message TEXT,
                    transcript_id INTEGER REFERENCES Transcripts(transcript_id),
                    user_id INTEGER REFERENCES Users(user_id)
                );
            """)

def add_user_to_db(email, password):
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Users (email, password)
                VALUES (%s, %s)
            """, (email, password_hash))

def authenticate_user(email, password):
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT email FROM Users WHERE email = %s AND password = %s
            """, (email, password_hash))
            user = cur.fetchone()
    return bool(user)

def get_user_id(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
            result = cur.fetchone()
            return result[0] if result else None

def insert_into_transcripts(user_id, file_name, transcription, transcription_summary, sentiment_label, sentiment_report, prev_ai_research, fact_check):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Transcripts (user_id, file_name, transcription, transcription_summary, sentiment_label, sentiment_report, prev_ai_research, fact_check) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, file_name, transcription, transcription_summary, sentiment_label, sentiment_report, prev_ai_research, fact_check))

def get_transcript_ids_and_names():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT transcript_id, file_name FROM Transcripts")
            results = cur.fetchall()
            return [f"{row[0]} - {row[1]}" for row in results]

def get_transcript_by_id(selection):
    id = int(selection.split(' - ')[0])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT transcription FROM Transcripts WHERE transcript_id = %s", (id,))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                return "No transcript found for the given id"

def get_sentiment_by_id(selection):
    id = int(selection.split(' - ')[0])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT sentiment_label FROM Transcripts WHERE transcript_id = %s", (id,))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                return "No transcript found for the given id"

def get_sentiment_report_by_id(selection):
    id = int(selection.split(' - ')[0])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT sentiment_report FROM Transcripts WHERE transcript_id = %s", (id,))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                return "No transcript found for the given id"

def get_fact_check_by_id(selection):
    id = int(selection.split(' - ')[0])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT fact_check FROM Transcripts WHERE transcript_id = %s", (id,))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                return "No transcript found for the given id"

def get_summary_by_id(selection):
    id = int(selection.split(' - ')[0])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT transcription_summary FROM Transcripts WHERE transcript_id = %s AND user_id = %s", 
                        (id, st.session_state.user_id))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                return "No transcript found for the given id"

def insert_audio(file_path, transcript_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            cur.execute("""
                INSERT INTO AudioFiles (file_name, audio_data, transcript_id) VALUES (%s, %s, %s)
            """, (os.path.basename(file_path), psycopg2.Binary(audio_data), transcript_id))

def get_transcript_id(file_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT transcript_id FROM Transcripts WHERE file_name = %s", (file_name,))
            result = cur.fetchone()
            return result[0] if result else None