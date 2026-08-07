import logging
from game.llm.client import GroqClient

log = logging.getLogger(__name__)

class GameState:
    """
    Persists data across level transitions.
    Stores NPC chat histories, global inventory, and quest data, and the LLM client.
    """

    def __init__(self):
        self.npc_chat_history: dict[str, list[dict]] = {}  # dictionary mapping npc_id to a list of message dicts
        self.groq_client = GroqClient()  # init LLM client only once

        # Dictionary tracking the active spawn_id for specific NPCs.
        # If an NPC's ID is mapped to None, they won't spawn anywhere.
        # If an NPC is NOT in this dictionary, the game automatically assumes their active spawn is '{npc_id}_start'.
        self.active_npc_spawns: dict[str, str | None] = {
            "elara": None,      # Hidden
            "deserter": None,   # Hidden
            "courier": None     # Hidden
        }

        # Dictionary to track the 'Stagnant State' - a one-sentence summary of how the NPC feels about the player.
        self.stagnant_states: dict[str, str] = {}

    def get_npc_history(self, npc_id: str) -> list[dict]:
        """Returns the chat history for a specific NPC. Initializes if empty."""
        if npc_id not in self.npc_chat_history:
            self.npc_chat_history[npc_id] = []
        return self.npc_chat_history[npc_id]

    def add_dialogue_message(self, npc_id: str, role: str, content: str):
        """Appends a new message to the NPC's history."""
        history = self.get_npc_history(npc_id)
        history.append({"role": role, "content": content})
        log.debug(f"Added message to {npc_id}'s history | Role: {role}")

    def clear_history(self, npc_id: str):
        """Clears the history for a specific NPC."""
        if npc_id in self.npc_chat_history:
            self.npc_chat_history[npc_id] = []

    def is_npc_spawn_active(self, npc_id: str, spawn_id: str) -> bool:
        """
        Checks if the provided spawn_id is the currently active one for the given npc_id.
        Automatically defaults to '{npc_id}_start' if the NPC is not explicitly listed in active_npc_spawns.
        """
        if npc_id in self.active_npc_spawns:
            return self.active_npc_spawns[npc_id] == spawn_id

        # Fallback based on naming convention
        default_spawn_id = f"{npc_id}_start"
        return spawn_id == default_spawn_id

    def set_npc_spawn(self, npc_id: str, spawn_id: str | None):
        """
        Updates the active spawn location for an NPC.
        Pass None to completely hide the NPC from the world.
        """
        self.active_npc_spawns[npc_id] = spawn_id
        log.info(f"Updated NPC '{npc_id}' active spawn to: {spawn_id}")

    def get_stagnant_state(self, npc_id: str) -> str:
        """Returns the current relationship status/thought of the NPC regarding the player."""
        # Default state if no interaction has happened yet
        return self.stagnant_states.get(
            npc_id,
            "You don't know this person well yet. Form your opinion based on this conversation."
        )

    def set_stagnant_state(self, npc_id: str, state: str):
        """Updates the relationship summary for an NPC."""
        self.stagnant_states[npc_id] = state
        log.info(f"Updated Stagnant State for '{npc_id}': {state}")
