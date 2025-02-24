import pickle
from time import time
from constants import *
import perlin_noise
import pygame
import numpy
import entity
import textures


ERROR_OFFSET = 0.0000000001

PLAYER_EDIT_DIST = 8

GRAVITY = pygame.Vector2(0, 1)
RESISTANCE = pygame.Vector2(0.8, 0.99)

CHUNK_RANGE = range(CHUNK_SIZE)

EMPTY_CHUNK_DATA = numpy.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=numpy.int32)

SOIL_AMOUNT = 16
FREQUENCY = 250
AMPLITUDE = 200

CAVE_SIZE_TOTAL = 0.1

CAVE_SIZE = 0.02
CAVE_SIZE_INCREASE = 0.01 / 400
BLOB_CAVE_SIZE = 0.4

CAVE_FREQUENCY = 5000
BLOB_CAVE_FREQUENCY = 10


def block_to_chunk(block_pos):
    chunk_x, block_x = divmod(block_pos[0], CHUNK_SIZE)
    chunk_y, block_y = divmod(block_pos[1], CHUNK_SIZE)
    return (chunk_x, chunk_y), (block_x, block_y)


def abs_max(numbers):
    return max([abs(number) for number in numbers])


class Chunk_loader:
    COLUMNS_PER_FRAME = 2

    def __init__(self, world, chunk_pos):
        self.world = world
        self.pos = chunk_pos
        self.data = EMPTY_CHUNK_DATA.copy()
        self.texture = self.world.textures.empty_chunk_surface.copy()

        self.chunk_block_x = self.pos[0] * CHUNK_SIZE
        self.chunk_block_y = self.pos[1] * CHUNK_SIZE
        self.chunk_block_pos = pygame.Vector2(self.chunk_block_x, self.chunk_block_y)
        self.chunk_block_pos_x = pygame.Vector2(
            self.chunk_block_x + CHUNK_SIZE, self.chunk_block_y
        )
        self.chunk_block_pos_y = pygame.Vector2(
            self.chunk_block_x, self.chunk_block_y + CHUNK_SIZE
        )
        self.chunk_block_pos_xy = pygame.Vector2(
            self.chunk_block_x + CHUNK_SIZE, self.chunk_block_y + CHUNK_SIZE
        )
        self.chunk_block_range_x = [x + self.chunk_block_x for x in CHUNK_RANGE]
        self.chunk_block_range_y = [y + self.chunk_block_y for y in CHUNK_RANGE]

        self.sample = self.chunk_block_pos
        self.sample_x = self.chunk_block_pos_x
        self.sample_y = self.chunk_block_pos_y
        self.sample_xy = self.chunk_block_pos_xy

        self.cave = self.world.cave_noise.noise(tuple(self.sample / CAVE_FREQUENCY))
        self.cave_x = self.world.cave_noise.noise(tuple(self.sample_x / CAVE_FREQUENCY))
        self.cave_y = self.world.cave_noise.noise(tuple(self.sample_y / CAVE_FREQUENCY))
        self.cave_xy = self.world.cave_noise.noise(
            tuple(self.sample_xy / CAVE_FREQUENCY)
        )

        self.blob_cave = (
            (self.world.blob_cave_noise.noise(tuple(self.sample / BLOB_CAVE_FREQUENCY)) / BLOB_CAVE_SIZE)
            + 1
        )
        self.blob_cave_x = (
            (self.world.blob_cave_noise.noise(tuple(self.sample_x / BLOB_CAVE_FREQUENCY)) / BLOB_CAVE_SIZE)
            + 1
        )
        self.blob_cave_y = (
            (self.world.blob_cave_noise.noise(tuple(self.sample_y / BLOB_CAVE_FREQUENCY)) / BLOB_CAVE_SIZE)
            + 1
        )
        self.blob_cave_xy = (
            (self.world.blob_cave_noise.noise(
                tuple(self.sample_xy / BLOB_CAVE_FREQUENCY)
            ) / BLOB_CAVE_SIZE)
            + 1
        )

        self.cave_value = self.cave / ((CAVE_SIZE+(self.chunk_block_pos.y*CAVE_SIZE_INCREASE)) + ERROR_OFFSET)
        self.cave_x_value = self.cave_x / ((CAVE_SIZE+(self.chunk_block_pos_x.y*CAVE_SIZE_INCREASE)) + ERROR_OFFSET)
        self.cave_y_value = self.cave_y / ((CAVE_SIZE+(self.chunk_block_pos_y.y*CAVE_SIZE_INCREASE)) + ERROR_OFFSET)
        self.cave_xy_value = self.cave_xy / ((CAVE_SIZE+(self.chunk_block_pos_xy.y*CAVE_SIZE_INCREASE)) + ERROR_OFFSET)
        self.blob_cave_value = self.blob_cave
        self.blob_cave_x_value = self.blob_cave_x
        self.blob_cave_y_value = self.blob_cave_y
        self.blob_cave_xy_value = self.blob_cave_xy

        self.generate_step = 0

    def interpolate_cave_noise(
        self, block_pos: pygame.Vector2, value, x_value, y_value, xy_value
    ):
        dist_xy = (block_pos - self.chunk_block_pos) / 32
        dist = (-(dist_xy.copy())) + pygame.Vector2(1, 1)
        dist_x = pygame.Vector2(dist_xy.copy().x, (-(dist_xy.copy().y)) + 1)
        dist_y = (-(dist_x.copy())) + pygame.Vector2(1, 1)

        return sum(
            (
                (dist.x * dist.y) * value,
                (dist_x.x * dist_x.y) * x_value,
                (dist_y.x * dist_y.y) * y_value,
                (dist_xy.x * dist_xy.y) * xy_value,
            )
        )

    def generate_next(self):
        for x in range(self.generate_step, self.generate_step + self.COLUMNS_PER_FRAME):
            if self.generate_step >= CHUNK_SIZE:
                self.generate_chunk_texture()
                return False
            self.generate_data(x)
            self.generate_step += 1
        return True

    def generate_data(self, x):
        block_x = self.chunk_block_range_x[x]
        surface = int(
            self.world.surface_noise.noise(self.chunk_block_range_x[x] / FREQUENCY)
            * AMPLITUDE
        )
        for y in CHUNK_RANGE:
            block_y = self.chunk_block_range_y[y]
            blob_cave_noise = self.interpolate_cave_noise(
                pygame.Vector2(block_x, block_y),
                self.blob_cave_value,
                self.blob_cave_x_value,
                self.blob_cave_y_value,
                self.blob_cave_xy_value,
            )
            cave_noise = self.interpolate_cave_noise(
                pygame.Vector2(block_x, block_y),
                self.cave_value,
                self.cave_x_value,
                self.cave_y_value,
                self.cave_xy_value,
            )
            cave = (abs(cave_noise/blob_cave_noise) < (CAVE_SIZE_TOTAL))
            if not cave:
                if block_y == surface:
                    block_type = 2
                elif block_y > surface and block_y <= surface + SOIL_AMOUNT:
                    block_type = 3
                elif block_y > surface + SOIL_AMOUNT:
                    block_type = 4
                else:
                    block_type = 1
            else:
                block_type = 1
            self.data[x, y] = block_type

    def generate_all_data(self):
        if self.generate_step >= CHUNK_SIZE:
            self.generate_chunk_texture()
            return

        surface = 0
        for x in CHUNK_RANGE:
            block_x = self.chunk_block_range_x[x]
            if not self.world.flat:
                surface = int(
                    self.world.surface_noise.noise(block_x / FREQUENCY) * AMPLITUDE
                )
            for y in CHUNK_RANGE:
                block_y = self.chunk_block_range_y[y]
                blob_cave_noise = self.interpolate_cave_noise(
                    pygame.Vector2(block_x, block_y),
                    self.blob_cave_value,
                    self.blob_cave_x_value,
                    self.blob_cave_y_value,
                    self.blob_cave_xy_value,
                )
                cave_noise = self.interpolate_cave_noise(
                    pygame.Vector2(block_x, block_y),
                    self.cave_value,
                    self.cave_x_value,
                    self.cave_y_value,
                    self.cave_xy_value,
                )
                cave = (abs(cave_noise/blob_cave_noise) < (CAVE_SIZE_TOTAL))
                if not cave:
                    if block_y == surface:
                        block_type = 2
                    elif block_y > surface and block_y <= surface + SOIL_AMOUNT:
                        block_type = 3
                    elif block_y > surface + SOIL_AMOUNT:
                        block_type = 4
                    else:
                        block_type = 1
                else:
                    block_type = 1
                self.data[x, y] = block_type

        self.generate_chunk_texture()

    def generate_chunk_texture(self):
        for x in CHUNK_RANGE:
            for y in CHUNK_RANGE:
                data = self.data[x, y]
                self.texture.blit(
                    self.world.textures.get_block_texture(data, pygame.Vector2(x, y)),
                    (x * BLOCK_SIZE, y * BLOCK_SIZE),
                )


class World:
    def __init__(self, world_config):
        self.textures = textures.Textures()
        self.entitys = []
        self.unloaded_entitys = []
        self.entitys.append(
            entity.Player(self, 0, PLAYER_EDIT_DIST, pygame.Vector2(0, -512))
        )

        if world_config["load_file"]:
            with open(SAVE_DIR + world_config["load_file"], "rb") as f:
                self.seed, self.changes, entity_data, unloaded_entity_data = (
                    pickle.load(f)
                )
                [
                    self.create_entity(entity_number, pos, vel)
                    for entity_number, pos, vel in (entity_data + unloaded_entity_data)[
                        1:
                    ]
                ]
                self.entitys[0].pos, self.entitys[0].vel = entity_data[0][1:]
        else:
            self.seed = world_config["seed"]
            self.changes = {}

        self.flat = True
        if self.seed:
            self.flat = False

        self.surface_noise = perlin_noise.PerlinNoise(octaves=1, seed=self.seed)
        self.cave_noise = perlin_noise.PerlinNoise(octaves=1, seed=self.seed + 1)
        self.blob_cave_noise = perlin_noise.PerlinNoise(octaves=1, seed=self.seed + 2)

        self.chunks = {}
        self.chunk_textures = {}
        self.load_pos = (0, 0)
        self.last_load_pos = self.load_pos
        self.load_distance = world_config["load_distance"]
        Chunk_loader.COLUMNS_PER_FRAME = world_config["gen_speed"]

        self.chunk_range_x = range(
            self.load_pos[0] - self.load_distance,
            self.load_pos[0] + self.load_distance + 1,
        )
        self.chunk_range_y = range(
            self.load_pos[1] - self.load_distance,
            self.load_pos[1] + self.load_distance + 1,
        )
        self.chunks_in_range = [
            (x, y) for x in self.chunk_range_x for y in self.chunk_range_y
        ]
        self.chunks_in_range.sort(key=abs_max)

        self.chunk_to_load = None

    def create_entity(
        self,
        entity_number,
        init_pos=pygame.Vector2(),
        init_vel=pygame.Vector2(),
        init_force=pygame.Vector2(),
    ):
        new_entity = entity.Entity(
            self,
            entity_number,
            init_pos,
            init_vel,
            init_force,
        )
        self.entitys.append(new_entity)
        return new_entity

    def update_entitys(self):
        to_pop = []
        for i, entity in enumerate(self.unloaded_entitys):
            if not any(
                [
                    not (tuple(chunk_pos) in self.chunks)
                    for chunk_pos in entity.chunks_in
                ]
            ):
                to_pop.insert(0, i)

        for i in to_pop:
            self.entitys.append(self.unloaded_entitys.pop(i))

        to_pop = []
        for i, entity in enumerate(self.entitys):
            if (
                any(
                    [
                        not (tuple(chunk_pos) in self.chunks)
                        for chunk_pos in entity.chunks_in
                    ]
                )
                and i
            ):
                to_pop.insert(0, i)
                continue
            entity.update()

        for i in to_pop:
            self.unloaded_entitys.append(self.entitys.pop(i))

    def load_nearest_chunk(self, fast=False):
        if not self.chunk_to_load:
            for pos in self.chunks_in_range:
                chunk_pos = (pos[0] + self.load_pos[0], pos[1] + self.load_pos[1])
                if chunk_pos not in self.chunks:
                    self.set_chunk_loader(chunk_pos)
                    if chunk_pos in self.changes:
                        self.chunk_to_load.data = self.changes[chunk_pos].copy()
                        self.chunk_to_load.generate_step = CHUNK_SIZE
                    break
        else:
            if fast:
                self.load_chunk_fast()
            else:
                self.load_chunk()

        chunks_to_unload = [
            chunk_pos
            for chunk_pos in self.chunks
            if (chunk_pos[0] - self.load_pos[0]) not in self.chunk_range_x
            or (chunk_pos[1] - self.load_pos[1]) not in self.chunk_range_y
        ]

        for chunk_pos in chunks_to_unload:
            self.chunks.pop(chunk_pos)
            self.chunk_textures.pop(chunk_pos)

    def set_block(self, block_pos, block_type):
        chunk_pos, local_block_pos = block_to_chunk(block_pos)

        if not chunk_pos in self.chunks:
            return False

        self.chunks[chunk_pos][local_block_pos] = block_type
        self.changes[chunk_pos] = self.chunks[chunk_pos].copy()

        blit_pos = (local_block_pos[0] * BLOCK_SIZE, local_block_pos[1] * BLOCK_SIZE)

        self.chunk_textures[chunk_pos].blit(
            self.textures.background_block_surface, blit_pos
        )
        self.chunk_textures[chunk_pos].blit(
            self.textures.get_block_texture(block_type, pygame.Vector2(block_pos)),
            blit_pos,
        )
        return True

    def set_chunk_loader(self, chunk_pos):
        if self.chunk_to_load == None:
            self.chunk_to_load = Chunk_loader(self, chunk_pos)

    def load_chunk(self):
        if not self.chunk_to_load.generate_next():
            self.finish_chunk()

    def load_chunk_fast(self):
        self.chunk_to_load.generate_all_data()
        self.finish_chunk()

    def finish_chunk(self):
        self.chunks[self.chunk_to_load.pos] = self.chunk_to_load.data
        self.chunk_textures[self.chunk_to_load.pos] = self.chunk_to_load.texture
        self.chunk_to_load = None

    def get_blocks(self, block_poses):
        return [self.get_block(block_pos) for block_pos in block_poses]

    def get_block(self, block_pos):
        chunk_pos, local_block_pos = block_to_chunk(block_pos)
        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos][local_block_pos]
        else:
            return 0

    def get_chunk_textures(self, chunk_poses):
        is_empty = False
        chunk_textures = []
        for chunk_pos in chunk_poses:
            if chunk_pos in self.chunk_textures:
                chunk_textures.append(self.chunk_textures[chunk_pos])
            else:
                chunk_textures.append(self.textures.empty_chunk_surface)
                is_empty = True

        return chunk_textures, is_empty

    def save(self):
        with open((SAVE_DIR + SAVE_NAME + str(int(time())) + ".txt"), "wb") as f:
            entity_data = [(e.entity_number, e.pos, e.vel) for e in self.entitys]
            unloaded_entity_data = [
                (e.entity_number, e.pos, e.vel) for e in self.unloaded_entitys
            ]
            pickle.dump(
                (
                    self.surface_noise.seed,
                    self.changes,
                    entity_data,
                    unloaded_entity_data,
                ),
                f,
            )
