# ai_engine.py
import openai, google.generativeai as genai
from config import OPENAI_API_KEY, GEMINI_API_KEY, DEFAULT_AI

openai.api_key = OPENAI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

async def get_ai_reply(prompt: str, history: list, model: str = DEFAULT_AI) -> str:
    messages = [{"role": "system", "content": "You are a helpful AI."}] + history + [{"role": "user", "content": prompt}]
    try:
        if model == "gemini":
            full = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            resp = genai.GenerativeModel("gemini-pro").generate_content(full)
            return resp.text
        else:
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages, max_tokens=500)
            return resp.choices[0].message.content.strip()
    except Exception as e: return f"AI Error: {e}"

async def transcribe_voice(file_path: str) -> str:
    with open(file_path, "rb") as f: transcript = openai.Audio.transcribe("whisper-1", f)
    return transcript["text"]

async def generate_image(prompt: str) -> str:
    resp = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    return resp.data[0].url