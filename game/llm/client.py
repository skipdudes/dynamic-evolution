import os
import json
import threading
import logging
from dotenv import load_dotenv
from groq import Groq
from game.core.settings import LLM_NAME, ENV_FILE_PATH

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
                    "remove_item_id": {
                        "type": "string",
                        "description": "ID of item to remove from player (e.g., 'special_herbs'). Leave empty if none."
                    },
                    "remove_item_qty": {
                        "type": "integer",
                        "description": "Quantity to remove. Set to 0 if none."
                    },
                    "quest_updates": {
                        "type": "array",
                        "description": "List of quests to update. Can be used to complete one quest and start another simultaneously.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "quest_id": {"type": "string", "description": "ID of the quest"},
                                "quest_action": {"type": "string", "enum": ["start", "progress", "complete"]},
                                "quest_entry": {"type": "string", "description": "Journal entry text. Leave empty if none."}
                            }
                        }
                    },
                    "npc_location_updates": {
                        "type": "array",
                        "description": "List of NPC movements (spawning/despawning).",
                        "items": {
                            "type": "object",
                            "properties": {
                                "npc_id": {"type": "string", "description": "ID of the NPC (e.g., 'elara')."},
                                "spawn_id": {"type": "string", "description": "ID of the spawn point. Use 'none' to despawn/remove them."}
                            }
                        }
                    },
                    "stagnant_state": {
                        "type": "string",
                        "description": "One sentence summary updating your internal relationship state with the player."
                    },
                    "teleport_destination": {
                        "type": "string",
                        "description": "The map name to teleport the player to (e.g., 'meadow'). Leave empty string if no teleport."
                    },
                    "set_night_mode": {
                        "type": "string",
                        "description": "Pass 'true' to enable night, 'false' to enable day, or '' (empty string) to leave time unchanged."
                    },
                    "trigger_ending": {
                        "type": "string",
                        "description": "Pass 'good' to trigger the good ending, 'bad' for the bad ending, or '' (empty string) to do nothing."
                    }
                },
                "required": ["dialogue"]
            }
        }
    }
]


class GroqClient:
    def __init__(self):
        load_dotenv(ENV_FILE_PATH)
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
            # Set tool_choice to "auto".
            # The LLM will use standard text for casual replies,
            # and the JSON tool ONLY when it needs to update the game state.
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                tools=LLM_TOOLS,
                tool_choice="auto",
            )

            response_message = chat_completion.choices[0].message

            # Default to standard text response if the model just wanted to talk
            reply_text = response_message.content if response_message.content else ""
            parsed_tools = []

            if response_message.tool_calls:
                # If the model decided to use the tool, extract the JSON
                tool_call = response_message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)

                # The dialogue is now inside the JSON argument
                tool_dialogue = args.get("dialogue", "")
                if tool_dialogue:
                    reply_text = tool_dialogue

                parsed_tools = [args]

            callback(reply_text, parsed_tools, None)

        except Exception as e:
            log.error(f"Groq API Request failed: {e}")
            callback(None, None, str(e))
