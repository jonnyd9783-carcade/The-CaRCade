import pygame

# Edit this dictionary to remap keys - grouped however feels
# ergonomic to you. Nothing else in the codebase needs to change.
KEY_BINDINGS = {
    "throttle_up": pygame.K_UP,
    "throttle_down": pygame.K_DOWN,
    "steer_left": pygame.K_LEFT,
    "steer_right": pygame.K_RIGHT,
}


class KeyboardController:
    def __init__(self):
        print("No controller detected - falling back to keyboard input.")

    def read_raw(self):
        keys = pygame.key.get_pressed()

        throttle = 0.0
        if keys[KEY_BINDINGS["throttle_up"]]:
            throttle -= 1.0
        if keys[KEY_BINDINGS["throttle_down"]]:
            throttle += 1.0

        steering = 0.0
        if keys[KEY_BINDINGS["steer_left"]]:
            steering -= 1.0
        if keys[KEY_BINDINGS["steer_right"]]:
            steering += 1.0

        return {"throttle": throttle, "steering": steering}