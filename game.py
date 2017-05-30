#!/usr/bin/env python3

import json
import pygame
import sys
import xbox360_controller

pygame.mixer.pre_init()
pygame.init()

# Window settings
TITLE = "Help Harry!"
WIDTH = 960
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Options
sound_on = True

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_UP

# Levels
levels = ["levels/world-1.json",
          "levels/world-2.json",
          "levels/world-3.json"]

# Colors
TRANSPARENT = (0, 0, 0, 0)
T_GREY = (172, 192, 193, 60)
GREY = (172, 192, 193)
WHITE = (255, 255, 255)

# Fonts
FONT_SM = pygame.font.Font("assets/fonts/enchanted_land.otf", 32)
FONT_MD = pygame.font.Font("assets/fonts/enchanted_land.otf", 64)
FONT_LG = pygame.font.Font("assets/fonts/shadowed_black_wide.ttf", 72)

# Helper functions
def load_image(file_path, width=GRID_SIZE, height=GRID_SIZE):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (width, height))

    return img

def play_sound(sound, loops=0, maxtime=0, fade_ms=0):
    if sound_on:
        if maxtime == 0:
            sound.play(loops, maxtime, fade_ms)
        else:
            sound.play(loops, maxtime, fade_ms)

def play_music():
    if sound_on:
        pygame.mixer.music.play(-1)

# Images
hero_walk1_right = load_image("assets/harry/harry_right.png")
hero_walk1_left = load_image("assets/harry/harry_left.png")
hero_walk2_right = load_image("assets/harry/harry_right.png")
hero_walk2_left = load_image("assets/harry/harry_left.png")
hero_jump_right = load_image("assets/harry/harry_right.png")
hero_jump_left = load_image("assets/harry/harry_left.png")
hero_idle = load_image("assets/harry/harry_right.png")
hero_images = {"run_right": [hero_walk1_right, hero_walk2_right],
               "run_left": [hero_walk1_left, hero_walk2_left],
               "jump_right": hero_jump_right,
               "jump_left": hero_jump_left,
               "idle": hero_idle}

block_images = {"SB": load_image("assets/stone_block.png"),
                "WB": load_image("assets/wood_block.png"),
                "EL": load_image("assets/stone_block.png")}

torch_images = {"T1": load_image("assets/torch_1.png"),
                "T2": load_image("assets/torch_2.png"),
                "T3": load_image("assets/torch_3.png"),
                "T4": load_image("assets/torch_4.png")}


horcrux_images = {"diadem": load_image("assets/horcruxes/diadem.png"),
                  "diary": load_image("assets/horcruxes/diary.png"),
                  "goblet": load_image("assets/horcruxes/goblet.png"),
                  "harry": load_image("assets/horcruxes/harry.png"),
                  "locket": load_image("assets/horcruxes/locket.png"),
                  "nagini": load_image("assets/horcruxes/nagini.png"),
                  "ring": load_image("assets/horcruxes/ring.png")}

#stats pictures
empty_heart_img = load_image("assets/heart_empty.png")
full_heart_img = load_image("assets/heart_full.png")
life_img = load_image("assets/life.png")

#powerups
powerup_heart_img = load_image("assets/hedwig_heart_down.png")
powerup_life_img = load_image("assets/hedwig_life_down.png")

#flag
flag_img = load_image("assets/door.png")
flagpole_img = load_image("assets/door.png")

#monsters
dementor_img1 = load_image("assets/dementor.png")
dementor_images = [dementor_img1]

pixie_img1 = load_image("assets/pixie_left.png")
pixie_images = [pixie_img1]

# Sounds
JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
COIN_SOUND = pygame.mixer.Sound("assets/sounds/pickup.wav")
POWERUP_SOUND = pygame.mixer.Sound("assets/sounds/powerup.wav")
HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.wav")
DIE_SOUND = pygame.mixer.Sound("assets/sounds/death.wav")
LEVELUP_SOUND = pygame.mixer.Sound("assets/sounds/level_up.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")
VICTORY_SOUND = pygame.mixer.Sound("assets/sounds/win.wav")

class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vy = 0
        self.vx = 0

    def apply_gravity(self, level):
        self.vy += level.gravity
        self.vy = min(self.vy, level.terminal_velocity)

class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Torch(Entity):

    def __init__(self, x, y, images):
        super().__init__(x, y, images['T1'])

        self.images = images
        
        self.steps = 0
        
    def set_image(self):
        self.steps = (self.steps + 1) % 4# Works well with 2 images, try lower number if more frames are in animation

        self.image = images[steps]

    def update(self):
        self.set_image()
        print(self.image_index)

class Character(Entity):

    def __init__(self, images):
        super().__init__(0, 0, images['idle'])

        self.images_run_right = images['run_right']
        self.images_run_left = images['run_left']
        self.image_jump_right = images['jump_right']
        self.image_jump_left = images['jump_left']
        self.image_idle = images['idle']

        self.running_images = self.images_run_right
        self.image_index = 0
        self.steps = 0

        self.speed = 6
        self.jump_power = 20

        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.on_ground = True

        self.score = 0
        self.coins = 0
        self.lives = 3
        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0

    def move(self, val):
        self.vx = self.speed*val
        if self.vx > 0:
            self.facing_right = False
        else:
            self.facing_right = True

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power
            
        self.rect.y -= 1

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.on_ground = False
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_horcruxes(self, horcruxes):
        hit_list = pygame.sprite.spritecollide(self, horcruxes, True)

        for horcrux in hit_list:
            play_sound(COIN_SOUND)
            self.score += horcrux.value
            self.coins += 1

            if self.coins >= 10:
                self.lives += 1
                self.coins = 0

    def process_enemies(self, enemies):
        
        if self.vy > 0 :
            hit_list = pygame.sprite.spritecollide(self, enemies, False)
            for h in hit_list:
                h.lives -= 1
                self.vy -= 30

                if h.lives <= 0 and h.invincibility == 0:
                    self.score += h.value
                    pygame.sprite.Sprite.kill(h)
                   
                
        elif self.vy <= 0 and self.invincibility == 0:
            hit_list = pygame.sprite.spritecollide(self, enemies, False)

            for h in hit_list:
                
                play_sound(HURT_SOUND)
                self.hearts -= 1
                self.invincibility = int(0.75 * FPS)

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            play_sound(POWERUP_SOUND)
            p.apply(self)

    def check_flag(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.flag, False)

        if len(hit_list) > 0:
            level.completed = True
            play_sound(LEVELUP_SOUND)

    def set_image(self):
        if self.on_ground:
            
            if self.facing_right:
                self.running_images = self.images_run_right
            else:
                self.running_images = self.images_run_left

            self.steps = (self.steps + 1) % self.speed # Works well with 2 images, try lower number if more frames are in animation

            if self.steps == 0:
                self.image_index = (self.image_index + 1) % len(self.running_images)
                self.image = self.running_images[self.image_index]
            
        else:
            if self.facing_right:
                self.image = self.image_jump_right
            else:
                self.image = self.image_jump_left

    def die(self):
        self.lives -= 1
        self.score = 0

        if self.lives > 0:
            play_sound(DIE_SOUND)
        else:
            play_sound(GAMEOVER_SOUND)

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts
        self.invincibility = 0

    def update(self, level):
        self.process_enemies(level.enemies)
        self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)
        self.set_image()

        if self.hearts > 0:
            self.process_horcruxes(level.horcruxes)
            self.process_powerups(level.powerups)
            self.check_flag(level)

            if self.invincibility > 0:
                self.invincibility -= 1
        else:
            self.die()

class Horcrux(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 1


class Enemy(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])
        
        self.images_left = images
        self.images_right = [pygame.transform.flip(img, 1, 0) for img in images]
        self.current_images = self.images_left
        self.image_index = 0
        self.steps = 0

        self.invincibility = 0

    def reverse(self):
        self.vx *= -1

        if self.vx < 0:
            self.current_images = self.images_left
        else:
            self.current_images = self.images_right

        self.image = self.current_images[self.image_index]

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self):
        pass

    def set_images(self):
        if self.steps == 0:
            self.image = self.current_images[self.image_index]
            self.image_index = (self.image_index + 1) % len(self.current_images)

        self.steps = (self.steps + 1) % 20 # Nothing significant about 20. It just seems to work okay.

    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vx = self.start_vx
        self.vy = self.start_vy
        self.image = self.images_left[0]
        self.steps = 0

class Dementor(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.lives = 1
        self.value = 5
        
        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

class Pixie(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.lives = 2
        self.value = 10
        
        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False

            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if reverse:
            self.reverse()

class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.lives += 1

class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        if character.hearts != character.max_hearts:
            character.hearts += 1

class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Level():

    def __init__(self, file_path):
        self.starting_blocks = []
        self.starting_enemies = []
        self.starting_horcruxes = []
        self.starting_powerups = []
        self.starting_flag = []
        self.starting_torches = []

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.horcruxes = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()
        self.torches = pygame.sprite.Group()


        self.active_sprites = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()

        with open(file_path, 'r') as f:
            data = f.read()

        map_data = json.loads(data)

        self.name = map_data['name']
        self.width = map_data['width'] * GRID_SIZE
        self.height = map_data['height'] * GRID_SIZE

        self.start_x = map_data['start'][0] * GRID_SIZE
        self.start_y = map_data['start'][1] * GRID_SIZE

        for item in map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.starting_blocks.append(Block(x, y, img))

        for item in map_data['dementors']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Dementor(x, y, dementor_images))

        for item in map_data['pixies']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Pixie(x, y, pixie_images))

        for item in map_data['horcruxes']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = horcrux_images[item[2]]
            self.starting_horcruxes.append(Horcrux(x, y, img))

        for item in map_data['oneups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(OneUp(x, y, powerup_life_img))

        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, powerup_heart_img))
            
        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, powerup_heart_img))

        for i, item in enumerate(map_data['flag']):
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE

            if i == 0:
                img = flag_img
            else:
                img = flagpole_img

            self.starting_flag.append(Flag(x, y, img))

        self.background_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

        if map_data['background-color'] != "":
            self.background_layer.fill(map_data['background-color'])

        if map_data['background-img'] != "":
            background_img = pygame.image.load(map_data['background-img'])

            if map_data['background-fill-y']:
                h = background_img.get_height()
                w = int(background_img.get_width() * HEIGHT / h)
                background_img = pygame.transform.scale(background_img, (w, HEIGHT))

            if "top" in map_data['background-position']:
                start_y = 0
            elif "bottom" in map_data['background-position']:
                start_y = self.height - background_img.get_height()

            if map_data['background-repeat-x']:
                for x in range(0, self.width, background_img.get_width()):
                    self.background_layer.blit(background_img, [x, start_y])
            else:
                self.background_layer.blit(background_img, [0, start_y])

        if map_data['scenery-img'] != "":
            scenery_img = pygame.image.load(map_data['scenery-img'])

            if map_data['scenery-fill-y']:
                h = scenery_img.get_height()
                w = int(scenery_img.get_width() * HEIGHT / h)
                scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

            if "top" in map_data['scenery-position']:
                start_y = 0
            elif "bottom" in map_data['scenery-position']:
                start_y = self.height - scenery_img.get_height()

            if map_data['scenery-repeat-x']:
                for x in range(0, self.width, scenery_img.get_width()):
                    self.scenery_layer.blit(scenery_img, [x, start_y])
            else:
                self.scenery_layer.blit(scenery_img, [0, start_y])

        pygame.mixer.music.load(map_data['music'])

        self.gravity = map_data['gravity']
        self.terminal_velocity = map_data['terminal-velocity']

        self.completed = False

        self.blocks.add(self.starting_blocks)
        self.enemies.add(self.starting_enemies)
        self.horcruxes.add(self.starting_horcruxes)
        self.powerups.add(self.starting_powerups)
        self.flag.add(self.starting_flag)

        self.active_sprites.add(self.horcruxes, self.enemies, self.powerups)
        self.inactive_sprites.add(self.blocks, self.flag)

        self.inactive_sprites.draw(self.inactive_layer)

    def reset(self):
        self.enemies.add(self.starting_enemies)
        self.horcruxes.add(self.starting_horcruxes)
        self.powerups.add(self.starting_powerups)

        self.active_sprites.add(self.horcruxes, self.enemies, self.powerups)

        for e in self.enemies:
            e.reset()

class Game():

    SPLASH = 0
    START = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETED = 4
    GAME_OVER = 5
    VICTORY = 6

    def __init__(self):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.done = False

        self.reset()

    def start(self):
        self.level = Level(levels[self.current_level])
        self.level.reset()
        self.hero.respawn(self.level)

    def advance(self):
        self.current_level += 1
        self.start()
        self.stage = Game.START

    def reset(self):
        self.hero = Character(hero_images)
        self.current_level = 0
        self.start()
        self.stage = Game.SPLASH

    def display_splash(self, surface):
        line1 = FONT_LG.render(TITLE, 1, GREY)
        line2 = FONT_SM.render("Press start to begin.", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 5 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))
        

    def display_message(self, surface, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;


        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        level_text = FONT_SM.render("Level:  " + self.level.name, 1, WHITE)
        hearts_text = FONT_SM.render("Hearts:  ", 1, WHITE)
        lives_text = FONT_SM.render("Lives:  ", 1, WHITE)
        lives_num_text = FONT_SM.render(" x  " + str(self.hero.lives), 1, WHITE)
        score_text = FONT_SM.render("Score:  " + str(self.hero.score), 1, WHITE)
        coins_text = FONT_SM.render("Coins:  " + str(self.hero.coins), 1, WHITE)


        i = 0
        while i < self.hero.max_hearts:
            if i < self.hero.hearts:
                surface.blit(full_heart_img, (84 + i*32, 36))
            elif i >= self.hero.hearts:
                surface.blit(empty_heart_img, (84 + i*32, 36))
            i += 1
            
            
        surface.blit(score_text, (WIDTH - score_text.get_width() - 32, 16))
        surface.blit(coins_text, (WIDTH - coins_text.get_width() - 32, 64))
        surface.blit(level_text, (32, 16))
        surface.blit(hearts_text, (32, 48))
        
        surface.blit(lives_text, (32, 80))
        surface.blit(life_img, (75, 70))
        surface.blit(lives_num_text, (126, 80))

    def process_events(self):
        controller = xbox360_controller.Controller(0)
        xmodifier = 1
        left_x, left_y = controller.get_left_stick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == xbox360_controller.START:
                    if self.stage == Game.SPLASH or self.stage == Game.START:
                        self.stage = Game.PLAYING
                        play_music()

                    elif self.stage == Game.PLAYING:
                        pass

                    elif self.stage == Game.PAUSED:
                        pass

                    elif self.stage == Game.LEVEL_COMPLETED:
                        self.advance()

                    elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                        if event.joy == controller.get_id():
                            if event.button == xbox360_controller.START:
                                self.reset()

                elif event.button == xbox360_controller.BACK:
                    if self.stage == Game.PLAYING:
                        self.start()

                    elif self.stage == Game.PAUSED:
                        self.start()

                    elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                        if event.joy == controller.get_id():
                            if event.button == xbox360_controller.START:
                                self.reset()

                elif event.button == xbox360_controller.A:
                    self.hero.jump(self.level.blocks)

                elif event.button == xbox360_controller.B:
                    pass#sound on/off: global sound_on, sound_on = False
                
                elif event.button == xbox360_controller.X:
                    pass

            elif left_x != 0:
                pressed = controller.get_buttons()
                if pressed[xbox360_controller.LEFT_STICK_BTN] and self.hero.vy == 0:
                    left_x = left_x*2
                self.hero.move(left_x)

            elif left_x == 0:
                self.hero.stop()
            

    def update(self):
        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)

        if self.level.completed:
            if self.current_level < len(levels) - 1:
                self.stage = Game.LEVEL_COMPLETED
            elif self.current_level == len(levels) - 1 and self.stage != Game.VICTORY:
                self.stage = Game.VICTORY
                play_sound(VICTORY_SOUND)
            pygame.mixer.music.stop()

        elif self.hero.lives == 0:
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()

        elif self.hero.hearts == 0:
            self.level.reset()
            self.hero.respawn(self.level)

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def draw(self):
        offset_x, offset_y = self.calculate_offset()

        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        if self.hero.invincibility % 3 < 2:
            self.level.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        self.window.blit(self.level.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.scenery_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.level.active_layer, [offset_x, offset_y])

        self.display_stats(self.window)

        if self.stage == Game.SPLASH:
            self.display_splash(self.window)
        elif self.stage == Game.START:
            self.display_message(self.window, "Ready?", "Press start to begin.")
        elif self.stage == Game.PAUSED:
            pass
        elif self.stage == Game.LEVEL_COMPLETED:
            self.display_message(self.window, "Level Complete!", "Press start to continue.")
        elif self.stage == Game.VICTORY:
            self.display_message(self.window, "You Win!", "Press back to restart.")
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press back to restart.")

        pygame.display.flip()

    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.start()
    game.loop()
    pygame.quit()
    sys.exit()
