import pathlib
import subprocess
import tempfile
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI()

INSTRUCTIONS = """
Speak the text as if delivering a sermon to a Reformed Baptist congregation.
Use a clear, reverent, and pastoral tone.
Emphasize key theological points naturally, with slight pauses.
Speak slowly and clearly, suitable for reading aloud.
Maintain warmth and authority in the voice.
"""
AUDIO_DIR = pathlib.Path("./audio")
TRANSLATIONS_DIR = pathlib.Path("./translations")
AUDIO_DIR.mkdir(exist_ok=True)
MAX_CHUNK_SIZE = 4000


def get_sections(text: str) -> list[str]:
    """Split text into <= MAX_CHUNK_SIZE sections, keeping line breaks."""
    sections = []
    next_section = []
    for phrase in text.split("\n"):
        if len("\n".join(next_section)) + len(phrase) > MAX_CHUNK_SIZE:
            sections.append("\n".join(next_section))
            next_section = [phrase]
            continue
        next_section.append(phrase)
    if next_section:
        sections.append("\n".join(next_section))
    return sections


def tts_file_for_language(lang: str):
    """Generate a single mp3 file for the translated text of a given language."""
    input_path = TRANSLATIONS_DIR / f"{lang}.txt"
    output_path = AUDIO_DIR / f"{lang}.mp3"

    if not input_path.exists():
        print(f"⚠️  Skipping {lang}: translation file not found.")
        return

    print(f"🔊 Generating audio for {lang}...")

    text = input_path.read_text(encoding="utf-8").strip()
    sections = get_sections(text)

    temp_files = []

    for i, section in enumerate(sections):
        tmp = pathlib.Path(tempfile.gettempdir()) / f"{lang}_{i}.mp3"
        print(f"  ▶️  Converting section {i + 1}/{len(sections)}...")

        # Stream TTS to a temporary file
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="ash",  # you can change to "verse", "soft", "bright", etc.
            input=section,
            instructions=INSTRUCTIONS,
        ) as response:
            response.stream_to_file(tmp)
        temp_files.append(tmp)

    print(f"  🔗 Merging {len(temp_files)} sections...")

    merge_mp3s(temp_files, output_path)

    print(f"✅ Saved: {output_path}")


def merge_mp3s(temp_files: list[pathlib.Path], output_path: pathlib.Path):
    # Create a temporary text file listing the inputs for ffmpeg
    list_file = pathlib.Path("/tmp/ffmpeg_inputs.txt")
    list_file.write_text("\n".join(f"file '{tmp}'" for tmp in temp_files))

    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",  # just copies the mp3 frames — no re-encoding
            str(output_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    list_file.unlink(missing_ok=True)
    for tmp in temp_files:
        tmp.unlink(missing_ok=True)


def main():
    LANGUAGES = os.environ["LANGUAGES"].split(",")
    for lang in LANGUAGES:
        tts_file_for_language(lang)


if __name__ == "__main__":
    main()
