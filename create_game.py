from os import listdir
import random
import pygame
import game
import ui
from constants import *


class Game:
    def __init__(self, title, window_size, fps):
        self.title = title
        self.window_size = window_size
        self.FPS = fps

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        self.window_rect = pygame.Rect((0, 0), self.window_size)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.title)

        self.running = True
        self.finished = False
        
        self.fps_limit = 60
        self.load_file = ""
        self.gen_speed = 8
        self.init_gen = 512
        self.seed = 0
        self.defult_rand_seed = random.randrange(0, 1000000000000)

        self.play_button = ui.Button(
            (2, 2), (200, 32), "Play now", TEXT_COLOR, BACKGROUND_UI_COLOR
        )

        #self.seed_text = ui.Text((132, 2), (128, 32), "", TEXT_COLOR, BACKGROUND_UI_COLOR)

        self.world_text = ui.Text(
            (2, 36), (452, 32), "Load world: ", TEXT_COLOR, BACKGROUND_UI_COLOR
        )

        self.new_button = ui.Button(
            (262, 2), (120, 32), "New world", TEXT_COLOR, BACKGROUND_UI_COLOR
        )

        self.world_names = listdir(SAVE_DIR)
        self.world_buttons = [
            ui.Button(
                (2, 70 + ((i * 32) + (i * 2))),
                (256, 32),
                file_name,
                TEXT_COLOR,
                BACKGROUND_UI_COLOR,
            )
            for i, file_name in enumerate(listdir(SAVE_DIR))
        ]

        self.fps_cap_button = ui.Button(
            (204, 2), (250, 32), "FPS Capped (60)", TEXT_COLOR, BACKGROUND_UI_COLOR
        )

        self.gen_speed_slider = ui.Slider(
            ui.Image((456, 2), (320, 32), BACKGROUND_UI_COLOR),
            ui.Image((456, 2), (10, 32), TEXT_COLOR),
            10,
        )

        self.gen_speed_text = ui.Text(
            (778, 2), (220, 32), "Gen speed: " + str(self.gen_speed), TEXT_COLOR, BACKGROUND_UI_COLOR
        )

        self.gen_speed_slider.set_slider(self.gen_speed)

        self.init_gen_slider = ui.Slider(
            ui.Image((456, 36), (320, 32), BACKGROUND_UI_COLOR),
            ui.Image((456, 36), (2, 32), TEXT_COLOR),
            0.2,
        )

        self.init_gen_text = ui.Text(
            (778, 36), (220, 32), "Init gen: " + str(self.init_gen), TEXT_COLOR, BACKGROUND_UI_COLOR
        )

        self.init_gen_slider.set_slider(self.init_gen)

    def run(self):
        while self.running:
            self.do_frame()

        self.quit_pygame()
        if not self.seed:
            self.seed = self.defult_rand_seed
        return {
            "fps": self.fps_limit,
            "load_file": self.load_file,
            "gen_speed": self.gen_speed,
            "seed": self.seed,
            "init_gen": self.init_gen,
            "load_distance": 32
        }

    def do_frame(self):
        self.handle_events()
        self.game_logic()

        self.draw()
        pygame.display.update(self.window_rect)

        self.clock.tick(self.FPS)

    def quit_pygame(self):
        pygame.quit()

    def handle_events(self):
        mouse_button_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_down = True

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_button = 0

        if mouse_pressed[0]:
            mouse_button = 1
        elif mouse_pressed[2]:
            mouse_button = 2

        if (mouse_button == 1) and self.gen_speed_slider.is_hovered_over(mouse_pos):
            self.gen_speed_slider.set_slider_pos(mouse_pos[0])
            self.gen_speed = self.gen_speed_slider.number + 1
            self.gen_speed_text.change_text(
                "Gen speed: " + str(self.gen_speed), TEXT_COLOR
            )

        if (mouse_button == 1) and self.init_gen_slider.is_hovered_over(mouse_pos):
            self.init_gen_slider.set_slider_pos(mouse_pos[0])
            self.init_gen = self.init_gen_slider.number
            self.init_gen_text.change_text(
                "Init gen: " + str(self.init_gen), TEXT_COLOR
            )

        if self.play_button.is_hovered_over(mouse_pos) and mouse_button_down:
            self.running = False

        if self.new_button.is_hovered_over(mouse_pos) and mouse_button_down:
            self.load_file = ""
            self.world_text.change_text("Load world: ", TEXT_COLOR)

        if self.fps_cap_button.is_hovered_over(mouse_pos) and mouse_button_down:
            if self.fps_limit:
                self.fps_limit = 0
                self.fps_cap_button.change_text("FPS Uncapped", TEXT_COLOR)
            else:
                self.fps_limit = 60
                self.fps_cap_button.change_text("FPS Capped (60)", TEXT_COLOR)

        for i, button in enumerate(self.world_buttons):
            if button.is_hovered_over(mouse_pos) and mouse_button_down:
                self.load_file = self.world_names[i]
                self.world_text.change_text("Load world: " + self.load_file, TEXT_COLOR)

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.play_button.draw(self.screen)
        self.world_text.draw(self.screen)
        self.new_button.draw(self.screen)
        self.fps_cap_button.draw(self.screen)
        self.gen_speed_slider.draw(self.screen)
        self.gen_speed_text.draw(self.screen)
        self.init_gen_slider.draw(self.screen)
        self.init_gen_text.draw(self.screen)
        for button in self.world_buttons:
            button.draw(self.screen)

    def game_logic(self):pass


while 1:
    new_menu = Game("Game", (1000, 600), 30)
    world_config = new_menu.run()
    if new_menu.finished:
        break
    world_game = game.Game("2D Block world", (1280, 640), world_config=world_config)
    world_game.run()
