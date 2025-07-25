import os
import time
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Config
load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = 'gemini-1.5-flash'
CHUNK_SIZE = 10000
OVERLAP = 200
MAX_RETRIES = 5
RETRY_DELAY = 15

# Utilities
def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(text, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def get_model():
    if not API_KEY:
        raise ValueError("Missing GEMINI_API_KEY.")
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)

# Gemini Call
def summarize_chunk(text, model):
    prompt = f"Summarize this:\n\n{text}"
    retries = 0
    while retries < MAX_RETRIES:
        try:
            res = model.generate_content(prompt)
            if res.text:
                return res.text
            raise ValueError("Empty response.")
        except Exception as e:
            logging.warning(f"Retry {retries+1}/{MAX_RETRIES}: {e}")
            time.sleep(RETRY_DELAY * (2 ** retries))
            retries += 1
    raise RuntimeError("All retries failed.")

# Chunk Logic
def split_text(text):
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        chunk = text[start:end]
        if end < len(text):
            split = text.rfind('.', start, end)
            if split != -1:
                end = split + 1
        chunks.append(text[start:end].strip())
        start = end
    return chunks

def summarize(text):
    model = get_model()
    if len(text) <= CHUNK_SIZE:
        return summarize_chunk(text, model)
    chunks = split_text(text)
    summaries = [summarize_chunk(chunk, model) for chunk in chunks]
    return summarize_chunk("\n\n".join(summaries), model)

# Main
def main():
    inputs = {
        "sipri": {
            "in": os.path.join(DATA_DIR, "processed", "defence", "sipri_summary_cleaned.txt"),
            "out": os.path.join(DATA_DIR, "processed", "defence", "sipri_summary_gemini.txt"),
        },
        "opec": {
            "in": os.path.join(DATA_DIR, "processed", "energy", "opec_summary_cleaned.txt"),
            "out": os.path.join(DATA_DIR, "processed", "energy", "opec_summary_gemini.txt"),
        }
    }

    for name, paths in inputs.items():
        logging.info(f"Summarizing {name.upper()}...")
        try:
            text = read_file(paths["in"])
            summary = summarize(text)
            save_file(summary, paths["out"])
            logging.info(f"{name.upper()} summary saved.")
        except Exception as e:
            logging.error(f"Failed to summarize {name.upper()}: {e}")

if __name__ == "__main__":
    main()
