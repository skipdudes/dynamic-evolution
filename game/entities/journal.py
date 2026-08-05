class Journal:
    """
    Manages the player's quest log.
    Quests have a title, a status ('active' or 'completed'), and a list of text entries.
    """
    def __init__(self):
        # Dictionary to store quests.
        # Key: quest_id (string), Value: dictionary with quest data
        self.quests = {}

    def add_quest(self, quest_id: str, title: str):
        """Adds a new active quest to the journal."""
        if quest_id not in self.quests:
            self.quests[quest_id] = {
                "title": title,
                "status": "active",
                "entries": []
            }

    def add_entry(self, quest_id: str, entry_text: str):
        """Adds a new progress entry to an existing quest."""
        if quest_id in self.quests:
            self.quests[quest_id]["entries"].append(entry_text)

    def complete_quest(self, quest_id: str):
        """Marks an existing quest as completed."""
        if quest_id in self.quests:
            self.quests[quest_id]["status"] = "completed"

    def has_quest(self, quest_id: str) -> bool:
        """Checks if a quest is currently in the journal."""
        return quest_id in self.quests

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the journal for LLM prompt injection.
        Example output: {"quest_missing_shipment": {"status": "active", "entries": [...]}}
        """
        return self.quests

    def get_llm_string(self) -> str:
        """
        Formats the journal into a readable string for the LLM prompt.
        Separates active and completed quests.
        """
        if not self.quests:
            return "No quests."

        active_quests = []
        completed_quests = []

        for q_id, q_data in self.quests.items():
            if q_data["status"] == "active":
                # Send the title and the most recent entry as the "current objective"
                last_entry = q_data["entries"][-1] if q_data["entries"] else "No details yet."
                active_quests.append(f"[{q_data['title']}] - Current state: {last_entry}")
            else:
                completed_quests.append(q_data["title"])

        result = ""
        if active_quests:
            result += "ACTIVE QUESTS:\n" + "\n".join(f"- {q}" for q in active_quests) + "\n"
        if completed_quests:
            result += f"COMPLETED QUESTS: {', '.join(completed_quests)}\n"

        return result.strip() if result else "No quests."
