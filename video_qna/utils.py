import re
import assemblyai as aai
import openai
import yt_dlp
from django.conf import settings
import os


def yt_title(link):
    ydl_opts = {
        "quiet": True,
        "format": "bestaudio/best",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        title = info_dict.get("title", None)
    return title


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def download_audio(youtube_url, output_path=settings.MEDIA_ROOT):
    title = yt_title(youtube_url)
    sanitized_title = sanitize_filename(title)

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": f"{output_path}/{sanitized_title}.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        ext = info_dict.get("ext", None)

    sanitized_file = f"{output_path}/{sanitized_title}.{ext}"

    return sanitized_file


def delete_audio(directory=settings.MEDIA_ROOT):
    if os.path.exists(directory) and os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        print(f"Directory '{directory}' does not exist or is not a valid directory.")


def get_transcription(link):
    audio_file = download_audio(link)

    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.nano, language_detection=True
    )
    transcriber = aai.Transcriber(config=config)

    transcript = transcriber.transcribe(audio_file)

    delete_audio()

    if transcript.status == aai.TranscriptStatus.error:
        return transcript.error
    else:
        return transcript.text


def get_answer(transcript, question):

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = f'Use the provided video transcript delimited by triple quotes to answer questions. If the answer cannot be found in the transcript, write "I could not find an answer in the provide video."'
    user_prompt = f'"""{transcript}""" Question: {question}'

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        max_tokens=1000,
    )

    return completion.choices[0].message.content
