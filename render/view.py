import pygame
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ARENA_MARGIN = 40


class View:
    def __init__(self):
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sim Lab - Milestone 1")
        self.screen = pygame.display.get_surface()
        self.arena_rect = pygame.Rect(ARENA_MARGIN, ARENA_MARGIN, SCREEN_WIDTH - 2 * ARENA_MARGIN, SCREEN_HEIGHT - 2 * ARENA_MARGIN)

    def draw(self, vehicle_state):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.arena_rect, width=2)

        center_x = vehicle_state.x
        center_y = vehicle_state.y
        dot_radius = 6

        heading_rad = math.radians(vehicle_state.heading)
        direction_x = math.sin(heading_rad)
        direction_y = -math.cos(heading_rad)

        start_x = center_x + direction_x * dot_radius
        start_y = center_y + direction_y * dot_radius

        line_length = 25
        end_x = center_x + direction_x * (dot_radius + line_length)
        end_y = center_y + direction_y * (dot_radius + line_length)

        start_point = (start_x, start_y)
        end_point = (end_x, end_y)
        pygame.draw.line(self.screen, WHITE, start_point, end_point, width=2)

        center_point = (int(center_x), int(center_y))
        pygame.draw.circle(self.screen, WHITE, center_point, dot_radius)

        pygame.display.flip()