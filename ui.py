import math
import pygame


class Image:
    def __init__(self, pos, size, color=(0, 0, 0, 0), image=False):
        self.rect = pygame.Rect(pos, size)
        self.image = pygame.Surface(size).convert_alpha()
        self.image.fill(color)
        if image:
            self.image.blit(image, ((0, 0), size))

    def draw(self, win):
        win.blit(self.image, self.rect)


class Text(Image):
    def __init__(self, pos, size, text, text_color, color=(0, 0, 0, 0), image=False):
        super().__init__(pos, size, color=color, image=image)
        self.original_image = self.image.copy()
        self.font = pygame.font.SysFont("monospace", 20, True)
        text_image = self.font.render(text, 1, text_color).convert_alpha()
        text_rect = text_image.get_rect(
            center=pygame.math.Vector2(self.image.get_size()) / 2
        )
        self.image.blit(text_image, text_rect)

    def change_text(self, text, text_color):
        self.image = self.original_image.copy()
        text_image = self.font.render(text, 1, text_color).convert_alpha()
        text_rect = text_image.get_rect(
            center=pygame.math.Vector2(self.image.get_size()) / 2
        )
        self.image.blit(text_image, text_rect)


class Button(Text):
    def __init__(self, pos, size, text, text_color, color=(0, 0, 0, 0), image=False):
        super().__init__(pos, size, text, text_color, color=color, image=image)

    def is_hovered_over(self, point):
        return self.rect.collidepoint(point)


class Slider:
    def __init__(self, image_bar: Image, image_slider, increment):
        self.image_bar = image_bar
        self.image_slider = image_slider
        self.increment = increment
        self.image_slider.rect.topleft = self.image_bar.rect.topleft
        self.number = 0
        self.max_num = int(self.image_bar.rect.width / self.increment)

    def is_hovered_over(self, point):
        return self.image_bar.rect.collidepoint(point)

    def set_slider_pos(self, pos_x):
        self.number = int(
            max(
                (
                    min(
                        (
                            ((pos_x - self.image_bar.rect.left) / self.increment),
                            self.max_num,
                        )
                    ),
                    0,
                )
            )
        )
        self.image_slider.rect.left = (
            self.number * self.increment
        ) + self.image_bar.rect.left

    def set_slider(self, number):
        self.number = number
        self.image_slider.rect.left = (
            self.number * self.increment
        ) + self.image_bar.rect.left

    def draw(self, win):
        self.image_bar.draw(win)
        self.image_slider.draw(win)
