from constants import *
import pygame
import math

BLOCK_COLLISION_DATA = [0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 1, 0]
ENTITY_TEXTURE_NAMES = ["textures/player.png"]
ENTITY_SIZES = [(32, 64)]
ENTITY_HITBOX_DATA = [[(pygame.Vector2(10, 0), pygame.Vector2(13, 63))]]
ENTITY_ARM_MID_POS = [pygame.Vector2(16, 18)]

# ENTITY_ARMS_TEXTURE_NAMES

GRAVITY = pygame.Vector2(0, 1)
RESISTANCE = pygame.Vector2(0.8, 0.99)

NEIGHBORS = [
    pygame.Vector2(-1, -1),
    pygame.Vector2(0, -1),
    pygame.Vector2(1, -1),
    pygame.Vector2(-1, 0),
    pygame.Vector2(0, 0),
    pygame.Vector2(1, 0),
    pygame.Vector2(-1, 1),
    pygame.Vector2(0, 1),
    pygame.Vector2(1, 1),
]


def supercover_line(p0, p1, dist=0):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    nx = abs(dx)
    ny = abs(dy)
    sign_x = -1 + (2 * int(dx > 0))
    sign_y = -1 + (2 * int(dy > 0))

    p = (p0[0], p0[1])
    points = [(p[0], p[1])]
    ix = 0
    iy = 0
    while ix < nx or iy < ny:
        x, y = 0, 0
        decision = (1 + 2 * ix) * ny - (1 + 2 * iy) * nx
        if decision == 0:
            x += sign_x
            y += sign_y
            ix += 1
            iy += 1
        elif decision < 0:
            x += sign_x
            ix += 1
        else:
            y += sign_y
            iy += 1
        p = x + p[0], y + p[1]
        if dist:
            if math.dist(p0, p) > dist:
                break

        points.append(p)

    return points


def get_surround(pos):
    return [pos + offset for offset in NEIGHBORS]


class Entity:
    def __init__(
        self,
        world,
        entity_number,
        init_pos=pygame.Vector2(),
        init_vel=pygame.Vector2(),
        init_force=pygame.Vector2(),
    ):
        self.world = world
        self.size = pygame.Vector2(ENTITY_SIZES[entity_number])
        default_image = self.world.textures.entity_textures[entity_number]
        self.images = [default_image, pygame.transform.flip(default_image, True, False)]
        self.hitbox_data = ENTITY_HITBOX_DATA[entity_number]
        self.mid_arm_pos = ENTITY_ARM_MID_POS[entity_number]
        self.entity_number = entity_number

        self.fly_physics = False
        self.climb = 0
        self.pos = init_pos
        self.test_pos = self.pos
        self.vel = init_vel
        self.force = init_force
        self.dir = 0

        self.chunk_pos = self.pos // CHUNK_TOTAL_SIZE
        self.chunks_in = []

        self.collide_x = False
        self.collide_y = False
        self.collide_xy = False
        self.stuck = False
        self.blocks_collide = []
        self.get_blocks_collide()
        self.collide_data = []

    def draw(self, screen, pos):
        if (self.vel.x > 0):
            self.dir = 1
        elif (self.vel.x < 0):
            self.dir = 0
        screen.blit(self.images[self.dir], pos)

    def get_blocks_collide(self):
        blocks = []
        for start_pos, size in self.hitbox_data:
            start_pos_block = (start_pos + self.test_pos) / BLOCK_SIZE
            end_pos_block = (size + start_pos + self.test_pos) / BLOCK_SIZE

            block_range_x = range(
                math.floor(start_pos_block.x), math.floor(end_pos_block.x) + 1
            )
            block_range_y = range(
                math.floor(start_pos_block.y), math.floor(end_pos_block.y) + 1
            )

            blocks += [
                (block_x, block_y)
                for block_x in block_range_x
                for block_y in block_range_y
            ]
        self.blocks_collide = blocks

    def collide(self):
        self.collide_data = [
            BLOCK_COLLISION_DATA[block]
            for block in self.world.get_blocks(self.blocks_collide)
        ]

    def lowest_collide(self):
        return [self.collide_data[i] for i in self.get_lowest_blocks()]

    def test(self):
        self.test_pos = self.pos.copy()
        self.get_blocks_collide()
        self.collide()

    def test_xy(self):
        self.test_pos = self.pos.copy()
        self.test_pos += self.vel
        self.get_blocks_collide()
        self.collide()

    def test_x(self):
        self.test_pos = self.pos.copy()
        self.test_pos.x += self.vel.x
        self.get_blocks_collide()
        self.collide()

    def test_y(self):
        self.test_pos = self.pos.copy()
        self.test_pos.y += self.vel.y
        self.get_blocks_collide()
        self.collide()

    def get_lowest_blocks(self):
        lowest_y = max([block_pos[1] for block_pos in self.blocks_collide])
        return [
            i
            for i, block_pos in enumerate(self.blocks_collide)
            if block_pos[1] == lowest_y
        ]

    def update(self):
        self.chunk_pos = self.pos // CHUNK_TOTAL_SIZE
        self.chunks_in = get_surround(self.chunk_pos)
        if self.fly_physics:
            self.vel += self.force
            self.vel = self.vel * RESISTANCE.y
        else:
            self.vel += self.force + GRAVITY
            self.vel = self.vel.elementwise() * RESISTANCE
        self.force = pygame.Vector2()

        self.collide_x = False
        self.collide_y = False
        self.collide_xy = False
        self.stuck = False

        self.test()
        still_collide_data = self.lowest_collide() + [0]
        if 1 in self.collide_data:
            self.vel = pygame.Vector2()
            self.stuck = True
            return

        self.test_xy()
        lowest_collide = [
            i
            for i, data in enumerate(self.lowest_collide())
            if (data == 2) and (still_collide_data[i] != 2)
        ]
        if (1 in self.collide_data) or (
            (lowest_collide and self.vel.y > 0) and self.climb + 1
        ):
            self.collide_xy = True
            self.test_x()
            if 1 in self.collide_data:
                self.vel.x = 0
                self.collide_x = True
            self.test_y()
            lowest_collide = [
                i
                for i, data in enumerate(self.lowest_collide())
                if (data == 2) and (still_collide_data[i] != 2)
            ]
            if (1 in self.collide_data) or (
                (lowest_collide and self.vel.y > 0) and self.climb + 1
            ):
                self.vel.y = 0
                self.collide_y = True

        if not (self.collide_x or self.collide_y) and self.collide_xy:
            self.vel.y = 0
            self.collide_y = True

        self.pos += self.vel
        self.test_pos = self.pos.copy()
        self.test()


class Player(Entity):
    def __init__(
        self,
        world,
        entity_number,
        edit_dist,
        init_pos=pygame.Vector2(),
        init_vel=pygame.Vector2(),
        init_force=pygame.Vector2(),
    ):
        super().__init__(
            world,
            entity_number,
            init_pos,
            init_vel,
            init_force,
        )
        self.edit_dist = edit_dist
        self.block_to_place = 10

    def block_editing(self, mouse_pos, mouse_button=0, mouse_button_down=False):
        mid_arm_pos = (self.mid_arm_pos) + self.pos

        start_pos = (
            math.floor(mid_arm_pos.x / BLOCK_SIZE),
            math.floor(mid_arm_pos.y / BLOCK_SIZE),
        )
        end_pos = (
            math.floor(mouse_pos.x / BLOCK_SIZE),
            math.floor(mouse_pos.y / BLOCK_SIZE),
        )

        line = supercover_line(start_pos, end_pos, dist=self.edit_dist)
        line_collide_data = [
            BLOCK_COLLISION_DATA[block] for block in self.world.get_blocks(line)
        ]

        if len(line) < 2:
            line_index = None
            return None, None

        only_place = False
        try:
            line_index = next(
                i for i, collide_data in enumerate(line_collide_data) if collide_data
            )
        except StopIteration:
            line_index = -1
            only_place = True

        if mouse_button_down and (not only_place):
            place_pos = line[line_index - 1]
        else:
            place_pos = line[line_index]

        edit_pos = line[line_index]

        if mouse_button == 1:
            self.world.set_block(edit_pos, 1)

        elif mouse_button == 2:
            place_surround_poses = [
                (place_pos[0] - 1, place_pos[1]),
                (place_pos[0] + 1, place_pos[1]),
                (place_pos[0], place_pos[1] - 1),
                (place_pos[0], place_pos[1] + 1),
            ]
            all_entity_blocks = [
                block_pos
                for entity in self.world.entitys
                for block_pos in entity.blocks_collide
                if self.chunk_pos in entity.chunks_in
            ]
            if (
                not BLOCK_COLLISION_DATA[self.world.get_block(place_pos)]
                and (place_pos not in all_entity_blocks)
                and not all(
                    [
                        not BLOCK_COLLISION_DATA[self.world.get_block(pos)]
                        for pos in place_surround_poses
                    ]
                )
            ):
                self.world.set_block(place_pos, self.block_to_place)

        if only_place:
            return edit_pos, line[line_index]
        return (
            edit_pos,
            line[line_index - 1],
        )

    def movement(
        self, left_walk=False, right_walk=False, jump=False, fast=False, slow=False
    ):
        self.climb = (not slow)-1
        fast_speed = (1 * int(fast)) - (0.5 * int(slow))
        self.force -= pygame.Vector2((1 + fast_speed) * int(left_walk), 0)
        self.force += pygame.Vector2((1 + fast_speed) * int(right_walk), 0)

        self.force += pygame.Vector2(0, (-10) * (int(jump and (self.collide_y or self.fly_physics)) - (int(slow and self.fly_physics)/5)))
