import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ARENA_MARGIN = 40  # gap between screen edge and the arena boundary


class View:
    def __init__(self):
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sim Lab - Milestone 0")
        self.screen = pygame.display.get_surface()

        self.arena_rect = pygame.Rect(
            ARENA_MARGIN,
            ARENA_MARGIN,
            SCREEN_WIDTH - 2 * ARENA_MARGIN,
            SCREEN_HEIGHT - 2 * ARENA_MARGIN,
        )
        
    def draw(self, vehicle_state):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.arena_rect, width=2)

        # vehicle center dot
        pygame.draw.circle(
            self.screen,
            WHITE,
            (int(vehicle_state.x), int(vehicle_state.y)),
            6,
        )

        pygame.display.flip()