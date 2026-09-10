import pygame
import math
from vehicle.state import PIXELS_PER_FOOT, REFLEX_14_LENGTH_INCHES, REFLEX_14_WIDTH_INCHES

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)  # direction-of-travel line color, distinct from heading (white)
MAGENTA = (255, 0, 255)  # simulated sensor reading marker, distinct from vehicle dot
GREEN = (50, 255, 50)  # estimated position marker, distinct from measured/truth

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ARENA_MARGIN = 40

DOT_RADIUS_PIXELS = round(PIXELS_PER_FOOT * (REFLEX_14_LENGTH_INCHES / 12) * 0.5)
VEHICLE_HALF_LENGTH_PIXELS = (PIXELS_PER_FOOT * (REFLEX_14_LENGTH_INCHES / 12)) / 2
VEHICLE_HALF_WIDTH_PIXELS = (PIXELS_PER_FOOT * (REFLEX_14_WIDTH_INCHES / 12)) / 2


class View:
    def __init__(self):
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sim Lab - Milestone 6")
        self.screen = pygame.display.get_surface()
        self.arena_rect = pygame.Rect(ARENA_MARGIN, ARENA_MARGIN, SCREEN_WIDTH - 2 * ARENA_MARGIN, SCREEN_HEIGHT - 2 * ARENA_MARGIN)

    def draw(self, vehicle_state, sensor_reading=None, estimated_state=None):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.arena_rect, width=2)

        center_x = vehicle_state.x
        center_y = vehicle_state.y
        dot_radius = DOT_RADIUS_PIXELS
        line_length = 25

        heading_rad = math.radians(vehicle_state.heading)
        heading_dir_x = math.sin(heading_rad)
        heading_dir_y = -math.cos(heading_rad)

        heading_start = (center_x + heading_dir_x * dot_radius, center_y + heading_dir_y * dot_radius)
        heading_end = (center_x + heading_dir_x * (dot_radius + line_length),
                        center_y + heading_dir_y * (dot_radius + line_length))
        pygame.draw.line(self.screen, WHITE, heading_start, heading_end, width=2)

        travel_rad = math.radians(vehicle_state.direction_of_travel)
        travel_dir_x = math.sin(travel_rad)
        travel_dir_y = -math.cos(travel_rad)

        travel_start = (center_x + travel_dir_x * dot_radius, center_y + travel_dir_y * dot_radius)
        travel_end = (center_x + travel_dir_x * (dot_radius + line_length),
                      center_y + travel_dir_y * (dot_radius + line_length))
        pygame.draw.line(self.screen, YELLOW, travel_start, travel_end, width=2)

        sin_h = math.sin(heading_rad)
        cos_h = math.cos(heading_rad)
        hl = VEHICLE_HALF_LENGTH_PIXELS
        hw = VEHICLE_HALF_WIDTH_PIXELS

        corners_local = [
            (hl, -hw),
            (hl, hw),
            (-hl, hw),
            (-hl, -hw),
        ]
        corners_world = [
            (center_x + f * sin_h + r * cos_h, center_y - f * cos_h + r * sin_h)
            for (f, r) in corners_local
        ]
        pygame.draw.polygon(self.screen, WHITE, corners_world)

        if sensor_reading is not None:
            reading_point = (int(sensor_reading.x), int(sensor_reading.y))
            pygame.draw.circle(self.screen, MAGENTA, reading_point, dot_radius - 1, width=2)

        # --- NEW (Milestone 6): estimated position, hollow green circle ---
        if estimated_state is not None:
            estimate_point = (int(estimated_state.x), int(estimated_state.y))
            pygame.draw.circle(self.screen, GREEN, estimate_point, dot_radius - 1, width=2)

        pygame.display.flip()