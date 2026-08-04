import os
import pygame
import pytmx
import logging
from game.core.settings import LEVELS_DIR

log = logging.getLogger(__name__)

class Level:
    def __init__(self, filename: str):
        self.filename = filename
        self.path = os.path.join(LEVELS_DIR, filename)

        log.info(f"Loading map: {self.filename}")
        self.tmx_data = pytmx.load_pygame(self.path)

        # Get level type ('indoor' or 'outdoor', default to 'outdoor')
        level_type_raw = str(self.tmx_data.properties.get("level_type", "outdoor")).strip().lower()
        if level_type_raw == "indoor":
            self.level_type = "indoor"
        else:
            if level_type_raw != "outdoor":
                log.warning(f"Invalid level_type '{level_type_raw}' in map. Defaulting to 'outdoor'.")
            self.level_type = "outdoor"

        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        self.collision_rects: list[pygame.Rect] = []
        self.renderables: list[dict] = []
        self.spawns: list[dict] = []
        self.npc_spawns: list[dict] = []
        self.level_triggers: list[dict] = []
        self.lights: list[dict] = []

        self._parse_layers()

    def _parse_layers(self):
        """
        Parses object layers (collisions, triggers, renderables, objects)
        and merges overlapping vertical tiles.
        """
        layer_objects_dict = {
            "renderables": [],
            "objects": []
        }

        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                # 1. Triggers layer
                if layer.name == "triggers":
                    for obj in layer:
                        if obj.name == "player_spawn":
                            # Extract custom property 'level' if defined
                            target_level = getattr(obj, "properties", {}).get("level", "unknown")
                            self.spawns.append({
                                "x": obj.x,
                                "y": obj.y,
                                "level": target_level
                            })
                        elif obj.name == "npc_spawn":
                            npc_id = getattr(obj, "properties", {}).get("npc_id", "default_npc")
                            direction_str = getattr(obj, "properties", {}).get("direction", "down").strip().lower()

                            # Extract spawn_id. If missing, assume the {npc_id}_start convention
                            default_spawn = f"{npc_id}_start"
                            spawn_id = getattr(obj, "properties", {}).get("spawn_id", default_spawn).strip()

                            self.npc_spawns.append({
                                "x": obj.x,
                                "y": obj.y,
                                "npc_id": npc_id,
                                "spawn_id": spawn_id,
                                "direction": direction_str,
                                "width": getattr(obj, "width", 48),
                                "height": getattr(obj, "height", 72)
                            })
                        elif obj.name == "level_trigger":
                            target_level = getattr(obj, "properties", {}).get("level", "")
                            rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                            self.level_triggers.append({
                                "rect": rect,
                                "target_level": target_level
                            })

                # 2. Collision layer
                elif layer.name == "collision":
                    for obj in layer:
                        rect = pygame.Rect(
                            int(obj.x), int(obj.y),
                            int(obj.width), int(obj.height)
                        )
                        self.collision_rects.append(rect)

                # 3. Renderables and Objects layers
                elif layer.name in ["renderables", "objects"]:
                    raw_list = []
                    for obj in layer:
                        if hasattr(obj, "gid") and obj.gid:
                            image = self.tmx_data.get_tile_image_by_gid(obj.gid)
                            if image:
                                raw_list.append({
                                    "image": image,
                                    "x": obj.x,
                                    "y": obj.y,
                                    "w": image.get_width(),
                                    "h": image.get_height()
                                })

                    # Vertical auto-merging logic
                    for r1 in raw_list:
                        true_bottom = r1["y"] + r1["h"]
                        current_y = true_bottom

                        while True:
                            found_next = False
                            for r2 in raw_list:
                                if r2["x"] == r1["x"] and abs(r2["y"] - current_y) < 1:
                                    current_y += r2["h"]
                                    true_bottom = current_y
                                    found_next = True
                                    break
                            if not found_next:
                                break

                        r1["bottom"] = true_bottom
                        r1["z_index"] = 0 if layer.name == "renderables" else 2
                        layer_objects_dict[layer.name].append(r1)

                # 4. Lights layer
                elif layer.name == "lights":
                    glow_radius = 5  # How many pixels the light spills outside the rectangle
                    for obj in layer:
                        rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
                        mask = self._create_light_mask(rect.width, rect.height, glow_radius)
                        self.lights.append({
                            "rect": rect,                       # Original rectangle
                            "draw_x": rect.x - glow_radius,     # Shift left by glow amount
                            "draw_y": rect.y - glow_radius,     # Shift up by glow amount
                            "mask": mask
                        })

        # Depth inheritance for items placed on tables ("objects" on "renderables")
        for obj in layer_objects_dict.get("objects", []):
            best_bottom = obj["bottom"]
            obj_center_x = obj["x"] + obj["w"] / 2

            for rnd in layer_objects_dict.get("renderables", []):
                if rnd["x"] <= obj_center_x <= rnd["x"] + rnd["w"]:
                    if rnd["y"] - obj["h"] <= obj["y"] <= rnd["bottom"]:
                        best_bottom = rnd["bottom"]
                        break

            obj["bottom"] = best_bottom

        # Combine into main list
        self.renderables.extend(layer_objects_dict.get("renderables", []))
        self.renderables.extend(layer_objects_dict.get("objects", []))

    def get_spawn_position(self, previous_level_name: str) -> tuple[float, float]:
        """
        Finds the matching player_spawn point based on the previous level's name.
        Falls back to 'unknown' or the first spawn point.
        """
        # Strip extension if passed (e.g. "woods.tmx" -> "woods")
        clean_prev_name = os.path.splitext(previous_level_name)[0]

        # 1. Search for exact match
        for spawn in self.spawns:
            if spawn["level"] == clean_prev_name:
                log.info(f"Found spawn matching previous level '{clean_prev_name}': ({spawn['x']}, {spawn['y']})")
                return spawn["x"], spawn["y"]

        # 2. Search for 'unknown' fallback
        for spawn in self.spawns:
            if spawn["level"] == "unknown":
                log.info(f"Matching spawn not found. Using 'unknown' spawn: ({spawn['x']}, {spawn['y']})")
                return spawn["x"], spawn["y"]

        # 3. Ultimate fallback: first spawn or (100, 100)
        if self.spawns:
            log.warning("Fallback to first available spawn point.")
            return self.spawns[0]["x"], self.spawns[0]["y"]

        log.warning("No spawn points found in map. Defaulting to (100, 100).")
        return 100.0, 100.0

    def check_level_triggers(self, player_hitbox: pygame.Rect) -> str | None:
        """
        Checks if player's hitbox collides with any level transition trigger.
        Returns target level name or None.
        """
        for trigger in self.level_triggers:
            if player_hitbox.colliderect(trigger["rect"]):
                return trigger["target_level"]
        return None

    def draw_tile_layers(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Renders all visible Tiled tile layers."""
        tile_w = self.tmx_data.tilewidth
        tile_h = self.tmx_data.tileheight

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(
                            tile,
                            (x * tile_w - camera_x, y * tile_h - camera_y)
                        )

    def draw_sorted_objects(self, screen: pygame.Surface, camera_x: float, camera_y: float, entities: list):
        """
        Draws objects and the player together using multi-level Y-Sorting.
        """
        objects_to_draw = []

        # 1. Add map objects
        for obj in self.renderables:
            objects_to_draw.append({
                "image": obj["image"],
                "x": obj["x"],
                "y": obj["y"],
                "bottom": obj["bottom"],
                "z_index": obj["z_index"]
            })

        # Add all living objects (Player, NPCs, Z-index = 1)
        for entity in entities:
            objects_to_draw.append({
                "image": entity.current_sprite,
                "x": entity.x,
                "y": entity.y,
                "bottom": entity.bottom,
                "z_index": 1
            })

        # 3. Sort by Y-bottom first, then Z-index
        sorted_objs = sorted(
            objects_to_draw,
            key=lambda o: (o["bottom"], o["z_index"])
        )

        # 4. Render
        for obj in sorted_objs:
            screen.blit(
                obj["image"],
                (obj["x"] - camera_x, obj["y"] - camera_y)
            )

    def _create_light_mask(self, width: int, height: int, glow: int) -> pygame.Surface:
        """
        Generates a rectangular light mask that exactly fits the dimensions defined in Tiled,
        and expands outward with a soft, rounded glowing gradient.
        """
        surf_w = width + glow * 2
        surf_h = height + glow * 2
        surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        # Draw the gradient from the widest (weakest) to the closest to the core (brightest)
        for d in range(glow, 0, -1):
            progress = 1.0 - (d / glow)
            # Non-linear light intensity falloff for realism
            alpha = int(255 * (progress ** 1.5))

            r_x = glow - d
            r_y = glow - d
            r_w = width + 2 * d
            r_h = height + 2 * d

            # The border_radius=d makes the outer edges of the glow smooth and round,
            # but as it gets closer to the core, it becomes sharper.
            pygame.draw.rect(surf, (255, 255, 255, alpha), (r_x, r_y, r_w, r_h), border_radius=d)

        # Finally, draw the core in the center - a perfect rectangle (e.g., the window pane)
        pygame.draw.rect(surf, (255, 255, 255, 255), (glow, glow, width, height))

        return surf
