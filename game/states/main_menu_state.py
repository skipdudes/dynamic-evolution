import os
import pygame
from game.core.state import BaseState
from game.core.settings import (
    FONT_UI, IMAGE_MAIN_MENU_BG, IMAGE_LOGO, KEY_UP, KEY_DOWN, KEY_INTERACT,
    MENU_OPTION_START, MENU_OPTION_OPTIONS, MENU_OPTION_ABOUT, MENU_OPTION_END,
    COLOR_TEXT_SELECTED, COLOR_TEXT_MAIN, LEVEL_START, WINDOW_WIDTH, WINDOW_HEIGHT,
    STRING_PROLOGUE_HEADER, STRING_PROLOGUE_TEXT, STRING_FIRST_LOG_ENTRY
)
from game.states.transition_state import TransitionState
from game.states.play_state import PlayState
from game.states.options_state import OptionsState
from game.states.about_state import AboutState
from game.entities.player import Player
from game.core.game_state import GameState

class MainMenuState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.font = pygame.font.Font(*FONT_UI)
        self.selected_index = 0

        self.bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        if os.path.exists(IMAGE_MAIN_MENU_BG):
            self.bg_surface = pygame.image.load(IMAGE_MAIN_MENU_BG).convert()
        else:
            self.bg_surface.fill((20, 20, 20))

        self.logo_surface = None
        if os.path.exists(IMAGE_LOGO):
            self.logo_surface = pygame.image.load(IMAGE_LOGO).convert_alpha()

        self.menu_options = [
            MENU_OPTION_START,
            MENU_OPTION_OPTIONS,
            MENU_OPTION_ABOUT,
            MENU_OPTION_END
        ]

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                elif event.key in KEY_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                elif event.key in KEY_INTERACT:
                    self._handle_selection()

    def _handle_selection(self):
        selected = self.menu_options[self.selected_index]

        if selected == MENU_OPTION_START:
            # Delay creating GameState, Groq API etc.
            def load_game():
                from game.states.story_board_state import StoryBoardState
                game_state = GameState()
                player = Player(x=0, y=0)

                # Initialize the first quest right at the start of the game
                player.journal.add_quest("quest_echoes_rebellion")
                player.journal.add_entry("quest_echoes_rebellion", STRING_FIRST_LOG_ENTRY)

                # # test epilogue
                # player.inventory.add_item("ferret_amulet")
                # player.journal.complete_quest("quest_echoes_rebellion")
                # player.journal.add_quest("quest_stranger_tarnstead")
                # player.journal.add_entry("quest_stranger_tarnstead", "The teleportation was successful. I am in a meadow somewhere in Tarnstead. I should head east into the settlement and find a local tavern. A bartender is always the best source of rumors.")
                # player.journal.complete_quest("quest_stranger_tarnstead")
                # player.inventory.add_item("gold", 80)  # Elara tavern
                # player.journal.add_quest("quest_bouncers_test")
                # player.journal.add_entry("quest_bouncers_test", "Grizzly sent me to the bandit hideout in the north-east. It looks like a normal house. I need to talk to a bouncer named Brunt inside.")
                # player.journal.add_entry("quest_bouncers_test", "I convinced Brunt to let me pass.")
                # player.journal.complete_quest("quest_bouncers_test")
                # game_state.set_npc_spawn("brunt", "brunt_rest")
                # player.journal.add_quest("quest_test_loyalty")
                # player.journal.add_entry("quest_test_loyalty", "Cedric ordered me to retrieve a confiscated rebel ledger from Captain Thorne at the Guard Station in the south-west.")
                # player.journal.add_entry("quest_test_loyalty", "I delivered the ledger. Cedric officially accepted me into the Shadows of the Crown.")
                # player.journal.complete_quest("quest_test_loyalty")
                # player.journal.add_quest("quest_midnight_drop")
                # player.journal.add_entry("quest_midnight_drop", "Silas told me to meet a Courier at the Meadow at night. Password: The blind eye sees.")
                # player.journal.add_entry("quest_midnight_drop", "I got the sealed letter. The wax seal has the crest of the Prime Minister! Should I open it or give it to Silas intact?")
                # player.journal.add_entry("quest_midnight_drop", "I delivered the sealed letter intact. Silas trusts me a bit more.")
                # player.journal.complete_quest("quest_midnight_drop")
                # player.journal.add_quest("quest_whispers_dark")
                # player.journal.add_entry("quest_whispers_dark", "Cedric ordered me to rest and await further orders. I need to rent a room at Grizzly's tavern.")
                # player.journal.add_entry("quest_whispers_dark", "I got the room key from Grizzly. It is the third room on the right.")
                # player.inventory.add_item("tavern_key")
                # player.journal.add_entry("quest_whispers_dark", "I paid Elara to escape. She warned me Silas senses my teleportation magic and will lay a trap. I went to sleep; she was gone by morning. I should return to Cedric now.")
                # player.journal.add_entry("quest_whispers_dark", "I survived the night and returned to Cedric.")
                # player.journal.complete_quest("quest_whispers_dark")
                # player.journal.add_quest("quest_point_no_return")
                # player.journal.add_entry("quest_point_no_return", "Cedric is the King's brother! He ordered me to kill Mage Aldous and bring back his staff. I must speak to Silas for the teleport spell.")
                # player.journal.add_entry("quest_point_no_return", "Silas teleported me to Aldous's house. It is time to make my final choice.")
                #
                # # Good Ending
                # player.journal.add_entry("quest_point_no_return", "I stayed loyal to the Crown. Aldous gave me his staff to fake his death and teleported me back to the hideout. He went to warn the capital so we can ambush the rebels.")
                #
                # # Bad Ending
                # #player.journal.add_entry("quest_point_no_return", "I betrayed the Crown. I killed Aldous and took his staff, using its magic to teleport myself back to the hideout. The rebellion marches on.")
                #
                # player.journal.complete_quest("quest_point_no_return")
                # player.journal.add_quest("quest_checkmate")
                # player.journal.add_entry("quest_checkmate", "I returned to Cedric. He revealed my father is a traitor!")
                # player.journal.add_entry("quest_checkmate", "We teleported to the castle gates. The final showdown begins.")

                play_state = PlayState(
                    self.state_machine,
                    level_filename=LEVEL_START,
                    player_instance=player,
                    game_state=game_state
                )
                # Return StoryBoardState, which has loaded game inside
                #return StoryBoardState(self.state_machine, STRING_PROLOGUE_HEADER, STRING_PROLOGUE_TEXT, play_state)
                return StoryBoardState(self.state_machine, STRING_PROLOGUE_HEADER, STRING_PROLOGUE_TEXT, play_state, hold_time=0.5)  # reduce hold time for developing project

            transition = TransitionState(self.state_machine, self, next_state_func=load_game, duration=1.0)
            self.state_machine.change(transition)

        elif selected == MENU_OPTION_OPTIONS:
            self.state_machine.push(OptionsState(self.state_machine))
        elif selected == MENU_OPTION_ABOUT:
            self.state_machine.push(AboutState(self.state_machine))
        elif selected == MENU_OPTION_END:
            transition = TransitionState(self.state_machine, self, None, duration=1.0, is_quit=True)
            self.state_machine.change(transition)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.bg_surface, (0, 0))

        if self.logo_surface:
            logo_x = (screen.get_width() - self.logo_surface.get_width()) // 2
            screen.blit(self.logo_surface, (logo_x, 72))

        # Semi-transparent background for menu options
        menu_bg_rect = pygame.Rect(0, 0, 300, 250)
        menu_bg_rect.centerx = screen.get_width() // 2
        menu_bg_rect.y = 302

        ui_surface = pygame.Surface((menu_bg_rect.width, menu_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 180), ui_surface.get_rect(), border_radius=12)
        screen.blit(ui_surface, (menu_bg_rect.x, menu_bg_rect.y))

        # Draw options
        start_y = 332
        for i, option in enumerate(self.menu_options):
            color = COLOR_TEXT_SELECTED if i == self.selected_index else COLOR_TEXT_MAIN
            text_surf = self.font.render(option, True, color)

            x = (screen.get_width() - text_surf.get_width()) // 2
            y = start_y + (i * 50)
            screen.blit(text_surf, (x, y))
