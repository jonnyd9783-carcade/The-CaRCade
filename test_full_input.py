import pygame
import time

pygame.init()
pygame.display.set_mode((100, 100))
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found.")
else:
    j = pygame.joystick.Joystick(0)
    j.init()
    print(f"Found: {j.get_name()}")
    print(f"Axes: {j.get_numaxes()}  Buttons: {j.get_numbuttons()}  Hats: {j.get_numhats()}")
    print("Press buttons, move sticks/triggers, and tap the D-pad.")
    print("Only CHANGED values will print. Ctrl+C to stop.\n")

    import time as _t
    pygame.event.pump()
    _t.sleep(0.3)
    pygame.event.pump()
    last_axes = [round(j.get_axis(i), 2) for i in range(j.get_numaxes())]
    last_buttons = [0] * j.get_numbuttons()
    last_hats = [(0, 0)] * j.get_numhats()

    while True:
        pygame.event.pump()

        axes = [round(j.get_axis(i), 2) for i in range(j.get_numaxes())]
        buttons = [j.get_button(i) for i in range(j.get_numbuttons())]
        hats = [j.get_hat(i) for i in range(j.get_numhats())]

        for i, (old, new) in enumerate(zip(last_axes, axes)):
            if abs(old - new) > 0.15:
                print(f"AXIS {i}: {old} -> {new}")

        for i, (old, new) in enumerate(zip(last_buttons, buttons)):
            if old != new:
                state = "PRESSED" if new else "released"
                print(f"BUTTON {i}: {state}")

        for i, (old, new) in enumerate(zip(last_hats, hats)):
            if old != new:
                print(f"HAT {i} (D-pad): {new}")

        last_axes, last_buttons, last_hats = axes, buttons, hats
        time.sleep(0.05)