import os
import threading
import logging
from dotenv import load_dotenv
from groq import Groq
from game.core.settings import LLM_NAME

log = logging.getLogger(__name__)

class GroqClient:
    """
    Handles asynchronous communication with the Groq API using the official SDK.
    """

    def __init__(self):
        load_dotenv()  # load environment variables from the .env file securely

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            log.error("GROQ_API_KEY not found in .env file! Please check the configuration.")

        self.client = Groq(api_key=api_key)
        self.model = LLM_NAME  # read model name from settings.py

    def generate_response_async(self, messages: list[dict], callback):
        """
        Starts a background thread to fetch the response.
        This ensures the main Pygame loop continues running smoothly.
        """
        thread = threading.Thread(target=self._fetch_response, args=(messages, callback))
        thread.daemon = True
        thread.start()

    def _fetch_response(self, messages: list[dict], callback):
        """
        Internal method executed by the background thread.
        Communicates with Groq and returns the result via the callback.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
            )
            reply_text = chat_completion.choices[0].message.content
            callback(reply_text, None)

        except Exception as e:
            log.error(f"Groq API Request failed: {e}")
            callback(None, str(e))
