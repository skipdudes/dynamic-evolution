import os
import json
import threading
import logging
from dotenv import load_dotenv
from groq import Groq
from game.core.settings import LLM_NAME

log = logging.getLogger(__name__)

# --- THE MASTER TOOL (STRUCTURED OUTPUT) ---
LLM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "npc_response",
            "description": "Generates the NPC's spoken dialogue and optionally triggers game events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dialogue": {
                        "type": "string",
                        "description": "Your spoken dialogue to the player. ALWAYS write this in character. NEVER leave this empty."
                    },
                    "give_item_id": {
                        "type": "string",
                        "description": "ID of item to give (e.g., 'ferret_amulet', 'gold'). Leave empty string if none."
                    },
                    "give_item_qty": {
                        "type": "integer",
                        "description": "Quantity to give. Set to 0 if none."
                    },
                    "quest_id": {
                        "type": "string",
                        "description": "ID of quest (e.g., 'quest_echoes_rebellion'). Leave empty string if none."
                    },
                    "quest_action": {
                        "type": "string",
                        "enum": ["start", "progress", "complete", "none"],
                        "description": "Action to perform on the quest."
                    },
                    "quest_entry": {
                        "type": "string",
                        "description": "Journal entry text. Leave empty string if none."
                    },
                    "stagnant_state": {
                        "type": "string",
                        "description": "One sentence summary updating your internal relationship state with the player."
                    }
                },
                "required": ["dialogue"]
            }
        }
    }
]


class GroqClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            log.error("GROQ_API_KEY not found in .env file!")

        self.client = Groq(api_key=api_key)
        self.model = LLM_NAME

    def generate_response_async(self, messages: list[dict], callback):
        thread = threading.Thread(target=self._fetch_response, args=(messages, callback))
        thread.daemon = True
        thread.start()

    def _fetch_response(self, messages: list[dict], callback):
        try:
            # We FORCE the model to always use our master tool!
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                tools=LLM_TOOLS,
                tool_choice={"type": "function", "function": {"name": "npc_response"}},
            )

            response_message = chat_completion.choices[0].message
            reply_text = ""
            parsed_tools = []

            if response_message.tool_calls:
                # Extract the forced tool JSON
                tool_call = response_message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)

                # We pull the actual dialogue text straight from the JSON parameters
                reply_text = args.get("dialogue", "")

                # We pass the rest of the arguments to our state updater
                parsed_tools = [args]

            callback(reply_text, parsed_tools, None)

        except Exception as e:
            log.error(f"Groq API Request failed: {e}")
            callback(None, None, str(e))
