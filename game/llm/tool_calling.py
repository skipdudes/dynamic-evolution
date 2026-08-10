import logging
from game.entities.item_data import ITEMS_DB
from game.entities.quest_data import QUESTS_DB
from game.core.settings import STRING_NOTIFY_ITEM, STRING_NOTIFY_QUEST

log = logging.getLogger(__name__)


def clean_llm_text(text: str) -> str:
    """
    Cleans fancy typography from LLM output to prevent pixel font rendering crashes.
    """
    if not text:
        return ""

    text = text.replace('\x00', '').replace('\xa0', ' ')
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '‑': '-', '…': '...'
    }
    for fancy_char, normal_char in replacements.items():
        text = text.replace(fancy_char, normal_char)

    return text.strip()


def execute_tool_calls(tools: list[dict], play_state, game_state, current_npc_id: str):
    """
    Translates the structured JSON output from the LLM into game state changes.
    """
    for args in tools:

        # 1. Check for item giving
        item_id = args.get("give_item_id")
        qty = args.get("give_item_qty", 0)

        if item_id and item_id.strip() and item_id != "none" and qty > 0:
            play_state.player.inventory.add_item(item_id, qty)
            item_name = ITEMS_DB.get(item_id, {}).get("name", item_id)
            play_state.hud.add_notification(f"{STRING_NOTIFY_ITEM}{item_name} x{qty}")
            log.info(f"Tool Executed [give_item]: {qty}x {item_id}")

        # 2. Check for quest updates (Now handles multiple quests at once!)
        quest_updates = args.get("quest_updates", [])
        for q_update in quest_updates:
            quest_id = q_update.get("quest_id")
            action = q_update.get("quest_action")

            # Clean the entry text BEFORE adding it to the journal
            entry = clean_llm_text(q_update.get("quest_entry", ""))

            if quest_id and quest_id.strip() and quest_id != "none" and action in ["start", "progress", "complete"]:
                quest_name = QUESTS_DB.get(quest_id, {}).get("title", quest_id)

                if action == "start":
                    play_state.player.journal.add_quest(quest_id)
                    if entry:
                        play_state.player.journal.add_entry(quest_id, entry)

                elif action == "progress":
                    if not play_state.player.journal.has_quest(quest_id):
                        play_state.player.journal.add_quest(quest_id)
                    if entry:
                        play_state.player.journal.add_entry(quest_id, entry)

                elif action == "complete":
                    if entry:
                        play_state.player.journal.add_entry(quest_id, entry)
                    play_state.player.journal.complete_quest(quest_id)

                play_state.hud.add_notification(f"{STRING_NOTIFY_QUEST}{quest_name}")
                log.info(f"Tool Executed [update_quest]: {quest_id} ({action})")

        # 3. Check for stagnant state updates
        stagnant_state = args.get("stagnant_state")
        if stagnant_state and stagnant_state.strip() and stagnant_state != "none":
            game_state.set_stagnant_state(current_npc_id, stagnant_state)
            log.info(f"Tool Executed [stagnant_state]: {stagnant_state}")

        # 4. Check for item removing
        remove_item_id = args.get("remove_item_id")
        remove_qty = args.get("remove_item_qty", 0)

        if remove_item_id and remove_item_id.strip() and remove_item_id != "none" and remove_qty > 0:
            # Assuming your inventory class has a remove_item method!
            if hasattr(play_state.player.inventory, 'remove_item'):
                play_state.player.inventory.remove_item(remove_item_id, remove_qty)
                item_name = ITEMS_DB.get(remove_item_id, {}).get("name", remove_item_id)
                play_state.hud.add_notification(f"Lost item: {item_name} x{remove_qty}")
                log.info(f"Tool Executed [remove_item]: {remove_qty}x {remove_item_id}")
            else:
                log.warning("Inventory class is missing 'remove_item' method!")

        # 5. Check for NPC location updates (spawning / despawning)
        npc_updates = args.get("npc_location_updates", [])
        for n_update in npc_updates:
            n_id = n_update.get("npc_id")
            s_id = n_update.get("spawn_id")

            if s_id and s_id.lower() == "none":
                s_id = None

            if n_id:
                game_state.set_npc_spawn(n_id, s_id)
                log.info(f"Tool Executed [update_npc_location]: {n_id} -> {s_id}")

        # 6. Check for teleportation
        teleport_dest = args.get("teleport_destination")
        if teleport_dest and teleport_dest.strip() and teleport_dest != "none":
            if hasattr(play_state, 'teleport_player'):
                play_state.teleport_player(teleport_dest)
            else:
                log.warning(
                    f"Teleport requested to '{teleport_dest}', but 'teleport_player' method is missing in PlayState!")
            log.info(f"Tool Executed [teleport]: {teleport_dest}")

        # 7. Check for night mode toggle
        if "set_night_mode" in args:
            night_mode_val = args.get("set_night_mode")
            if night_mode_val == "true":
                play_state.is_night = True
                log.info("Tool Executed [set_night_mode]: True")
            elif night_mode_val == "false":
                play_state.is_night = False
                log.info("Tool Executed [set_night_mode]: False")
            # If it's "" (empty string) or anything else, do nothing!

        # 8. Check for endgame trigger
        if "trigger_ending" in args:
            ending_val = args.get("trigger_ending")
            if ending_val in ["good", "bad"]:
                play_state.pending_ending = ending_val
                log.info(f"Tool Executed [trigger_ending]: {ending_val}")
