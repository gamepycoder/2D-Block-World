from constants import *
import pygame
import inputs
import ui
import world

CAM_MOVEMENT_SPEED = 64


class Game:
    def __init__(self, title, window_size, world_config: dict):
        self.title = title
        self.window_size = window_size
        self.FPS = world_config["fps"]

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        self.window_rect = pygame.Rect((0, 0), self.window_size)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.title)

        self.running = True

        self.frame_counter = 0

        self.world = world.World(world_config)
        self.init_gen = world_config["init_gen"]
        self.cam_x = 0
        self.cam_y = 0
        self.draw_area = (
            int(self.window_size[0] // CHUNK_TOTAL_SIZE) + 2,
            int(self.window_size[1] // CHUNK_TOTAL_SIZE) + 2,
        )

        self.player = self.world.entitys[0]

        self.cam_on_player = True

        self.draw_offset_x = self.cam_x + self.window_rect.centerx
        self.draw_offset_y = self.cam_y + self.window_rect.centery

        self.place_image = ui.Image(
            (0, 0),
            (BLOCK_SIZE, BLOCK_SIZE),
            image=self.world.textures.place_block,
        )
        self.edit_image = ui.Image(
            (0, 0),
            (BLOCK_SIZE, BLOCK_SIZE),
            image=self.world.textures.edit_block,
        )
        self.hotbar = ui.Image(
            (0, 0),
            self.world.textures.hotbar.get_size(),
            image=self.world.textures.hotbar,
        )
        self.hotbar_cover = ui.Image(
            (0, 0),
            self.world.textures.hotbar_cover.get_size(),
            image=self.world.textures.hotbar_cover,
        )
        self.pause_text = ui.Text(
            ((window_size[0] / 2) - 64, 2),
            (128, 32),
            "PAUSED",
            TEXT_COLOR,
            BACKGROUND_UI_COLOR,
        )
        self.temp_pause_text = ui.Text(
            ((window_size[0] / 2) - 128, 2),
            (256, 32),
            "LOADING",
            TEXT_COLOR,
            BACKGROUND_UI_COLOR,
        )

        self.pos_text = ui.Text(
            ((window_size[0]) - 258, 2),
            (256, 32),
            "",
            TEXT_COLOR,
            BACKGROUND_UI_COLOR,
        )

        self.hotbar_data = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.number_key = 0

        for i in range(0, 10):
            self.hotbar.image.blit(
                self.world.textures.get_big_block_texture(self.hotbar_data[i]),
                pygame.Vector2(((i * 32) + ((i * 2) + 2), 2)),
            )

        self.paused = False
        self.temp_paused = False
        self.temp_pause_time = 60 * 5

    def run(self):
        print("pre-gen, seed:", self.world.seed)
        if self.cam_on_player:
            self.cam_x = -int((self.player.pos.x + (self.player.size[0] / 2)))
            self.cam_y = -int((self.player.pos.y + (self.player.size[1] / 2)))
        self.world.load_pos = (
            int(-self.cam_x // CHUNK_TOTAL_SIZE),
            int(-self.cam_y // CHUNK_TOTAL_SIZE),
        )

        for i in range(self.init_gen):
            self.world.load_nearest_chunk(fast=True)
        
        pos_found = False
        self.player.test()
        pos_found = 1 in self.player.collide_data
        while not pos_found:
            self.player.pos += pygame.Vector2(0, BLOCK_SIZE)
            self.player.test()
            pos_found = 1 in self.player.collide_data
            pos_found = pos_found or (tuple(self.player.pos // CHUNK_TOTAL_SIZE) not in self.world.chunks)
        
        self.player.pos -= pygame.Vector2(0, BLOCK_SIZE)

        while self.running:
            self.do_frame()

        self.quit_pygame()

    def do_frame(self):
        self.handle_events()

        if self.paused or self.temp_paused:
            self.frame_counter += self.temp_paused
            if self.frame_counter > self.temp_pause_time:
                self.frame_counter = 0
                self.temp_paused = False
            self.world.load_nearest_chunk(fast=True)
        else:
            self.game_logic()

        self.draw()
        pygame.display.update(self.window_rect)

        self.clock.tick(self.FPS)

    def quit_pygame(self):
        pygame.quit()

    def handle_events(self):
        (
            quit_game,
            print_debug,
            jump,
            camera_toggle,
            teleport,
            clone,
            save,
            mouse_button,
            mouse_button_down,
            mouse_pos,
            cam_left,
            cam_right,
            cam_up,
            cam_down,
            left,
            right,
            fast,
            slow,
            number_key,
            pause,
            fly_toggle,
        ) = inputs.handle_keys()

        if pause:
            self.paused = not self.paused

        self.running = not quit_game

        if print_debug:
            print(
                self.clock.get_fps(),
                len(self.world.chunks),
                len(self.world.entitys),
                self.FPS,
            )

        if save:
            self.world.save()

        if not (self.paused or self.temp_paused):
            if camera_toggle:
                self.cam_on_player = not self.cam_on_player
            if teleport:
                self.player.pos.x = -int((self.cam_x + (self.player.size[0] / 2)))
                self.player.pos.y = -int((self.cam_y + (self.player.size[1] / 2)))
            if clone:
                self.world.create_entity(
                    0, self.player.pos.copy(), self.player.vel.copy()
                )
            if fly_toggle:
                self.player.fly_physics = not self.player.fly_physics

            if number_key != -1:
                self.number_key = number_key
            self.player.block_to_place = self.hotbar_data[self.number_key]

            world_mouse_pos = pygame.Vector2(
                (mouse_pos[0] - self.draw_offset_x),
                (mouse_pos[1] - self.draw_offset_y),
            )

            self.edit_pos, self.place_pos = self.player.block_editing(
                world_mouse_pos,
                mouse_button=mouse_button,
                mouse_button_down=mouse_button_down,
            )

            if not self.cam_on_player:
                self.cam_x += CAM_MOVEMENT_SPEED * cam_left
                self.cam_x -= CAM_MOVEMENT_SPEED * cam_right
                self.cam_y += CAM_MOVEMENT_SPEED * cam_up
                self.cam_y -= CAM_MOVEMENT_SPEED * cam_down

            self.player.movement(left, right, jump, fast, slow)

            self.world.load_pos = (
                int(-self.cam_x // CHUNK_TOTAL_SIZE),
                int(-self.cam_y // CHUNK_TOTAL_SIZE),
            )

    def draw(self):
        self.draw_offset_x = self.cam_x + self.window_rect.centerx
        self.draw_offset_y = self.cam_y + self.window_rect.centery
        self.draw_offset = pygame.Vector2(self.draw_offset_x, self.draw_offset_y)

        start_chunk_x = int((-self.draw_offset_x) // CHUNK_TOTAL_SIZE)
        start_chunk_y = int((-self.draw_offset_y) // CHUNK_TOTAL_SIZE)

        chunk_poses = [
            (x, y)
            for x in range(start_chunk_x, start_chunk_x + self.draw_area[0])
            for y in range(start_chunk_y, start_chunk_y + self.draw_area[1])
        ]

        chunk_textures, temp_pause = self.world.get_chunk_textures(chunk_poses)
        if temp_pause:
            self.temp_paused = True

        self.screen.fill((255, 255, 255))
        for i, chunk_texture in enumerate(chunk_textures):
            chunk_pos = chunk_poses[i]
            self.screen.blit(
                chunk_texture,
                (
                    (chunk_pos[0] * CHUNK_TOTAL_SIZE) + self.draw_offset_x,
                    (chunk_pos[1] * CHUNK_TOTAL_SIZE) + self.draw_offset_y,
                ),
            )

        for entity in self.world.entitys:
            entity.draw(
                self.screen,
                (
                    int(entity.pos.x) + self.draw_offset_x,
                    int(entity.pos.y) + self.draw_offset_y,
                ),
            )

        self.edit_image.draw(self.screen)
        self.place_image.draw(self.screen)
        self.hotbar.draw(self.screen)
        self.hotbar_cover.draw(self.screen)
        self.pos_text.change_text(str(self.player.pos / BLOCK_SIZE), TEXT_COLOR)
        self.pos_text.draw(self.screen)
        if self.paused:
            self.pause_text.draw(self.screen)
        if self.temp_paused:
            self.temp_pause_text.change_text(
                "LOADING: " + str(self.temp_pause_time - self.frame_counter), TEXT_COLOR
            )
            self.temp_pause_text.draw(self.screen)

    def game_logic(self):
        self.world.load_nearest_chunk()
        self.world.update_entitys()
        if self.cam_on_player:
            self.cam_x = -int((self.player.pos.x + (self.player.size[0] / 2)))
            self.cam_y = -int((self.player.pos.y + (self.player.size[1] / 2)))
        if self.edit_pos is not None:
            self.edit_image.rect.topleft = (
                (self.edit_pos[0] * BLOCK_SIZE) + self.draw_offset_x,
                (self.edit_pos[1] * BLOCK_SIZE) + self.draw_offset_y,
            )
        if self.place_pos is not None:
            self.place_image.rect.topleft = (
                (self.place_pos[0] * BLOCK_SIZE) + self.draw_offset_x,
                (self.place_pos[1] * BLOCK_SIZE) + self.draw_offset_y,
            )
        self.hotbar_cover.rect.topleft = (
            self.number_key * (self.hotbar_cover.rect.width - 2),
            0,
        )
        
