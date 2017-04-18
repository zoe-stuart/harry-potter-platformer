import pygame
import random

pygame.init()

# Window settings
WIDTH = 960
HEIGHT = 640
FPS = 60

# Colors
TRANSPARENT = (0, 0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Fonts
font_sm = pygame.font.Font(None, 32)
font_md = pygame.font.Font(None, 64)
font_lg = pygame.font.Font(None, 72)

# Images
hero_img_right = pygame.image.load("assets/harry_adorable_right.png")
hero_img_right = pygame.transform.scale(hero_img_right, (64, 64))
hero_img_left = pygame.image.load("assets/harry_adorable_left.png")
hero_img_left = pygame.transform.scale(hero_img_left, (64, 64))
hero_images = [hero_img_right, hero_img_left]

block_img = pygame.image.load("assets/medievalTile_064.png")
block_img = pygame.transform.scale(block_img, (64, 64))

diadem_img = pygame.image.load("assets/horcruxes/diadem.png")
diadem_img = pygame.transform.scale(diadem_img, (32, 32))
diary_img = pygame.image.load("assets/horcruxes/diary.png")
diary_img = pygame.transform.scale(diary_img, (32, 32))
goblet_img = pygame.image.load("assets/horcruxes/goblet.png")
goblet_img = pygame.transform.scale(goblet_img, (32, 32))
harry_img = pygame.image.load("assets/horcruxes/harry.png")
harry_img = pygame.transform.scale(harry_img, (32, 32))
locket_img = pygame.image.load("assets/horcruxes/locket.png")
locket_img = pygame.transform.scale(locket_img, (32, 32))
nagini_img = pygame.image.load("assets/horcruxes/nagini.png")
nagini_img = pygame.transform.scale(nagini_img, (32, 32))
ring_img = pygame.image.load("assets/horcruxes/ring.png")
ring_img = pygame.transform.scale(ring_img, (32, 32))

background_img = pygame.image.load("assets/background.png")
h = background_img.get_height()
w = int(background_img.get_width() * HEIGHT / h)
background_img = pygame.transform.scale(background_img, (w, HEIGHT))

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_UP


class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super(Entity, self).__init__()

        self.image = pygame.Surface([64, 64], pygame.SRCALPHA, 32)
        self.image.blit(image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        
class Block(Entity):
    
    def __init__(self, x, y, image):
        super(Block, self).__init__(x, y, image)


class Character(Entity):

    def __init__(self, x, y, images):
        super(Character, self).__init__(x, y, images[0])
        
        self.images = images

        self.speed = 10
        self.jump_power = 20
        
        self.vx = 0
        self.vy = 0
        
        self.score = 0

    def apply_gravity(self, level):
        self.vy += level.gravity

    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width
        
    def process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_horcruxes(self, horcruxes):
        hit_list = pygame.sprite.spritecollide(self, horcruxes, True)
        
        for horcrux in hit_list:
            self.score += horcrux.value     
    
    def move_left(self):
        self.vx = -1 * self.speed
        self.image.blit(self.images[1], [0, 0])
        
    def move_right(self):
        self.vx = self.speed
        self.image.blit(self.images[0], [0, 0])
        
    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power

        self.rect.y -= 1
        
        
    def update(self, level):
        self.apply_gravity(level)
        self.check_world_edges(level)
        self.process_blocks(level.blocks)
        
        self.process_horcruxes(level.horcruxes)



class Horcrux(Entity):
    
    def __init__(self, x, y, image):
        super(Horcrux, self).__init__(x, y, image)
        
        self.value = 1

class Enemy():
    pass

class Level():
    def __init__(self, blocks, horcruxes):
        self.blocks = blocks
        self.horcruxes = horcruxes
        
        self.active_sprites = pygame.sprite.Group()
        self.active_sprites.add(self.horcruxes)
        
        self.inactive_sprites = pygame.sprite.Group()
        self.inactive_sprites.add(blocks)

        self.width = 2048
        self.height = 640
        self.completed = False
        self.gravity = 1
        
class Game():


    def __init__(self, hero):
        self.hero = hero
        
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption("My Platform Game")
        self.clock = pygame.time.Clock()
        
        self.running = True
        
    def start(self, level):
        self.level = level
        
        self.background_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)

        for i in range(0, level.width, background_img.get_width()):
            self.background_layer.blit(background_img, [i, 0])
            
        self.level.inactive_sprites.draw(self.inactive_layer)


    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH
            
        return x, 0
    
    def play(self):
        
        while self.running:
            
            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == JUMP:
                        self.hero.jump(self.level.blocks)
                        
            pressed = pygame.key.get_pressed()
            
            # game logic
            if pressed[LEFT]:
                self.hero.move_left()
            elif pressed[RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()

            self.hero.update(self.level)
            
            #Drawing

            offset_x, offset_y = self.calculate_offset()
                        
            self.active_layer.fill(TRANSPARENT)
            self.level.active_sprites.draw(self.active_layer)
            
            self.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])
            
            self.window.blit(self.background_layer, [offset_x / 2, offset_y])
            self.window.blit(self.inactive_layer, [offset_x, offset_y])
            self.window.blit(self.active_layer, [offset_x, offset_y])
            
            # Update window
            pygame.display.update()
            self.clock.tick(FPS)

        # Close window on quit
        pygame.quit ()

def main():
    # Make sprites
    hero = Character(500, 512, hero_images)

    blocks = pygame.sprite.Group()
     
    for i in range(0, WIDTH * 10, 64):
        b = Block(i, 576, block_img)
        blocks.add(b)

    blocks.add(Block(192, 448, block_img))
    blocks.add(Block(256, 448, block_img))
    blocks.add(Block(320, 448, block_img))

    blocks.add(Block(448, 320, block_img))
    blocks.add(Block(512, 320, block_img))

    horcruxes = pygame.sprite.Group()
    horcruxes.add(Horcrux(768, 416, diadem_img))
    horcruxes.add(Horcrux(256, 352, ring_img))

    # Make a level
    level = Level(blocks, horcruxes)

    # Start game
    game = Game(hero)
    game.start(level)
    game.play()

if __name__ == "__main__":
    main()
    
