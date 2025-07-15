import os
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image
from google import genai
from google.adk.events import Event
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_instruction_from_file(filename: str, default_instruction: str = "Default instruction.") -> str:
    """Reads instruction text from a file relative to this script."""
    instruction = default_instruction
    
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'r', encoding="utf-8") as file:
            instruction = file.read()
        print(f"Successfully loaded instruction from {filename}.")
        
    except FileNotFoundError:
        print(f"WARNING: Instruction file not found {filename}. Using default instruction.")
    except Exception as e:
        print(f"ERROR: {e} loading {filename}. Using default instruction.")
    
    return instruction


def get_client(api_key: Optional[str] = None) -> genai.Client:
    """Initializes and returns a Gemini client."""
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)


def text2event(author: str, text_message: str) -> Event:
    """Creates an ADK Event with a simple text message."""
    return Event(
        author=author,
        content=types.Content(parts=[types.Part(text=text_message)]),
    )


def save_image_from_bytes(image_bytes: bytes, output_filepath: str) -> None:
    """Saves image bytes to a file using Pillow."""
    image = Image.open(BytesIO(image_bytes))
    image.save(output_filepath)
    logger.info(f"Image successfully saved to '{output_filepath}'") 