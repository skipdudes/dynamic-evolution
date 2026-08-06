import logging
from game.entities.item_data import ITEMS_DB
from game.entities.quest_data import QUESTS_DB
from game.core.settings import STRING_NOTIFY_ITEM, STRING_NOTIFY_QUEST

log = logging.getLogger(__name__)


def execute_tool_calls(tools: list[dict], play_state, game_state, current_npc_id: str):
    """
    Translates the structured JSON output from the LLM into game state changes.
    """
    for args in tools:  # 'tools' is now a list of the 'npc_response' dictionaries

        # 1. Check for item giving
        item_id = args.get("give_item_id")
        qty = args.get("give_item_qty", 0)

        if item_id and item_id.strip() and item_id != "none" and qty > 0:
            play_state.player.inventory.add_item(item_id, qty)
            item_name = ITEMS_DB.get(item_id, {}).get("name", item_id)
            play_state.hud.add_notification(f"{STRING_NOTIFY_ITEM}{item_name} x{qty}")
            log.info(f"Tool Executed [give_item]: {qty}x {item_id}")

        # 2. Check for quest updates
        quest_id = args.get("quest_id")
        action = args.get("quest_action")
        entry = args.get("quest_entry", "")

        if quest_id and quest_id.strip() and quest_id != "none" and action in ["start", "progress", "complete"]:
            quest_name = QUESTS_DB.get(quest_id, {}).get("title", quest_id)

            if action == "start":
                play_state.player.journal.add_quest(quest_id)
                if entry:
                    play_state.player.journal.add_entry(quest_id, entry)
                play_state.hud.add_notification(f"{STRING_NOTIFY_QUEST}New Quest: {quest_name}")

            elif action == "progress":
                if not play_state.player.journal.has_quest(quest_id):
                    play_state.player.journal.add_quest(quest_id)
                play_state.player.journal.add_entry(quest_id, entry)
                play_state.hud.add_notification(f"{STRING_NOTIFY_QUEST}Updated: {quest_name}")

            elif action == "complete":
                play_state.player.journal.complete_quest(quest_id)
                play_state.hud.add_notification(f"{STRING_NOTIFY_QUEST}Completed: {quest_name}")

            log.info(f"Tool Executed [update_quest]: {quest_id} ({action})")

        # 3. Check for stagnant state updates
        stagnant_state = args.get("stagnant_state")
        if stagnant_state and stagnant_state.strip() and stagnant_state != "none":
            game_state.set_stagnant_state(current_npc_id, stagnant_state)
            log.info(f"Tool Executed [stagnant_state]: {stagnant_state}")
