import pathlib

import os
from openai import OpenAI

from dotenv import load_dotenv

# IMPORTANT: Call this function at the top of your script
load_dotenv()

INSTRUCTIONS = """
Act as an expert translator specializing in Christian theological texts, specifically from a Reformed Baptist perspective.

Source: The following text is an excerpt from a sermon.

Audience: The target audience is an English-speaking congregation familiar with biblical language.

Tone: Preserve the original's formal, pastoral, and reverent tone.

Goal: The final translation must be theologically precise and suitable for being read aloud.

Additional notes
1. When numbers in the format of "8:1-10", they are translated to chapter 8, verses from 1 to 10.
2. When bible cites are included, use NKJV in English when the target language is English. In the rest languages, use the Bible version that is most commonly used in that language.
"""
LANGUAGES = os.environ["LANGUAGES"].split(",")

try:
    client = OpenAI()
except Exception as e:
    if "OPENAI_API_KEY" in str(e):
        print("Error: OpenAI API key not found.")
        print("Please set the OPENAI_API_KEY environment variable.")
    else:
        print(e)

    exit()


def main():
    original_txt = pathlib.Path("./original.txt").read_text()
    for lang in LANGUAGES:
        _translate_text(
            original_txt.strip(),
            lang,
            pathlib.Path(f"./translations/{lang}.txt"),
        )


def _translate_text(
    input_text: str,
    output_lang: str,
    output_path: pathlib.Path,
) -> None:
    """
    Translates a given text to a target language using the gpt-5-nano model.

    Args:
        text_to_translate: The text you want to translate.
        target_language: The language to translate the text into (e.g., "Spanish").
        source_language: The source language of the text (e.g., "English"). Defaults to "auto".

    Returns:
        The translated text as a string, or an error message.
    """
    print(f"Translating to {output_lang}...")

    instructions = (
        f"{INSTRUCTIONS}\nTranslate the following text from Spanish to {output_lang}:"
    )
    with client.responses.stream(
        model="gpt-5-nano",  # Specifically using the cost-effective gpt-5-nano model
        instructions=instructions,
        input=input_text,
    ) as stream:
        with output_path.open("w", encoding="utf-8") as f:
            for event in stream:
                if event.type == "response.output_text.delta":
                    f.write(event.delta)
                    f.flush()  # ✅ ensures live write
                elif event.type == "response.completed":
                    print("\n--- done ---")


if __name__ == "__main__":
    main()
