# engine module stub 
import pygame
from SuperStudent import welcome_screen, level_menu, game_loop


def run_game():
    pygame.init()
    welcome_screen()
    while True:
        mode = level_menu()
        if mode is None:
            break
        restart_level = game_loop(mode)
        while restart_level and mode in ("shapes", "colors"):
            restart_level = game_loop(mode)
    pygame.quit()


if __name__ == '__main__':
    run_game() 