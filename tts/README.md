# Translation and TTS

## Environment variables

```
OPENAI_API_KEY=...
LANGUAGES=english,russian
```

## Set the original text

```bash
vim ./original.txt
```

## Translate

```bash
docker compose up --build translator
```

Output:
- translations/english.txt
- translations/russian.txt

## Convert to speech

```bash
docker compose up --build tts
```

Output:
- translations/english.txt
- translations/russian.txt

## Stream

```bash
docker compose up --build streamer
```
