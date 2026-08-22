import pygame
import time
import sys

pygame.init()
pygame.display.set_mode((100, 100))
pygame.joystick.init()

j = pygame.joystick.Joystick(0)
j.init()
print(f"Found: {j.get_name()}")
print(f"Buttons: {j.get_numbuttons()}  Hats: {j.get_numhats()}\n")

controls_to_test = [
    "A", "B", "X", "Y",
    "L (left shoulder)", "R (right shoulder)",
    "ZL (left trigger, press fully)", "ZR (right trigger, press fully)",
    "Select / -", "Start / +",
    "Left stick click (press straight down)",
    "Right stick click (press straight down)",
    "D-pad UP", "D-pad DOWN", "D-pad LEFT", "D-pad RIGHT",
    "Home / circular button",
    "Capture / screenshot button (if it exists)",
]

results = {}

for control_name in controls_to_test:
    print(f"--> Press: {control_name}", flush=True)
    print("    (waiting up to 8 seconds...)", flush=True)

    pygame.event.pump()
    baseline_buttons = [j.get_button(i) for i in range(j.get_numbuttons())]
    baseline_hats = [j.get_hat(i) for i in range(j.get_numhats())]

    found = None
    start = time.time()
    while time.time() - start < 8 and found is None:
        pygame.event.pump()
        for i in range(j.get_numbuttons()):
            if j.get_button(i) and not baseline_buttons[i]:
                found = f"BUTTON {i}"
        for i in range(j.get_numhats()):
            h = j.get_hat(i)
            if h != baseline_hats[i]:
                found = f"HAT {i} -> {h}"
        time.sleep(0.02)

    if found:
        print(f"    Detected: {found}\n", flush=True)
        results[control_name] = found
    else:
        print(f"    Nothing detected (timed out) — skipping\n", flush=True)
        results[control_name] = "NOT DETECTED"

print("\n===== SUMMARY =====", flush=True)
for control_name, result in results.items():
    print(f"{control_name:45s} -> {result}", flush=True)