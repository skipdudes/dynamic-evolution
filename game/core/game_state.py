import logging

log = logging.getLogger(__name__)

class GameState:
    """
    Persists data across level transitions.
    Stores NPC chat histories, global inventory, and quest data.
    """
    def __init__(self):
        # Dictionary mapping npc_id to a list of message dicts
        # e.g., {"king": [{"role": "user", "content": "Hello!"}]}
        self.npc_chat_history: dict[str, list[dict]] = {}

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
