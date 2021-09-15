import os
import random
import sys

import pygame
from pygame.locals import *

# Initialise pygame sounds
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()


def load_image(name, colorkey=None, only_image=False, size=(25, 20)):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image', name)
        raise SystemExit(message)
    # image = image.convert()
    image = pygame.transform.scale(image, size)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    if not only_image:
        return image, image.get_rect()
    else:
        return image


class Text(object):

    def __init__(self, screen, text='Pygame', pos=(0, 0), bold=False, size=24, clr=(119, 136, 153)):
        self.font = pygame.font.Font('font/unifont.ttf', size)
        self.font.set_bold(bold)
        self.color = clr

        self.render(text)
        self.draw(screen, pos)

    def render(self, txt):
        self.img = self.font.render(txt, True, self.color)
        self.rect = self.img.get_rect()

    def draw(self, scrn, pos):
        self.rect.center = pos
        scrn.blit(self.img, self.rect)


class Button(object):
    """This is displays all the buttons in this game"""

    def __init__(self, pos, text='pygame'):
        """Initialises the button object"""
        self.text = text
        self.pos = pos
        self.color = (88, 139, 174)
        self.hover_color = (106, 90, 205)
        self.rect = pygame.Rect(pos, (100, 50))
        self.draw()
        self.check_hover()

    def draw(self):
        pygame.draw.rect(App.screen, self.color, self.rect)
        pygame.draw.rect(App.screen, (250, 218, 94), self.rect, 2)
        Text(App.screen, self.text, self.rect.center, clr=Color('yellow'))

    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            pygame.draw.rect(App.screen, self.hover_color, self.rect)
            pygame.draw.rect(App.screen, Color('green'), self.rect, 2)
            Text(App.screen, self.text, self.rect.center, clr=Color('green'))

    def get_rect(self):
        return self.rect


class Ship(pygame.sprite.Sprite):
    speed = 4
    lives = [load_image('ship.png', -1, True) for i in range(3)]

    def __init__(self, margin):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('ship.png', -1)
        self.screen = App.screen.get_rect()
        self.rect.midbottom = (self.screen.midbottom[0], self.screen.midbottom[1] - margin)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, left=False, right=False):
        """move the ship in left and right direction"""
        move = True
        if right:
            Ship.speed = abs(Ship.speed)
        if left:
            Ship.speed = abs(Ship.speed) * -1
        if not left and not right:
            move = False
        if self.rect.left <= 0:
            move = False
            self.rect.x = 1
        if self.rect.right >= self.screen.right:
            move = False
            self.rect.x = self.rect.x - 1

        if move:
            self.rect.move_ip(Ship.speed, 0)

    def get_pos(self):
        return self.rect.center


class Bullet(pygame.sprite.Sprite):
    speed = 7

    def __init__(self, pos, direction='up', img=None):
        pygame.sprite.Sprite.__init__(self)

        self.direction = direction

        if img is None:
            self.image = pygame.Surface([3, 6])
            self.image.fill(Color('white'))
            self.image.set_colorkey(Color('white'))
        else:
            self.image = img
        if img is None:
            pygame.draw.rect(self.image, Color('green'), [0, 0, 3, 6])

        self.rect = self.image.get_rect()

        self.rect.center = pos

    def update(self):
        """update and move the bullet"""
        if self.direction == 'up':
            self.rect.y -= Bullet.speed
        if self.direction == 'down':
            self.rect.y += Bullet.speed

        if self.rect.y <= 0 or self.rect.y >= 576:
            self.kill()


class BulletBlocker(pygame.sprite.Sprite):

    # CONSTRUCTOR
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.index = 0
        self.image = pygame.Surface([60, 100])
        self.pos = (x, y)
        self.image.fill(Color('white'))
        self.image.set_colorkey((Color('white')))

        self.image_list = [
            pygame.image.load('images/bullet-blocker/1.png'),
            pygame.image.load('images/bullet-blocker/2.png'),
            pygame.image.load('images/bullet-blocker/3.png'),
            pygame.image.load('images/bullet-blocker/4.png'),
            pygame.image.load('images/bullet-blocker/5.png'),
            pygame.image.load('images/bullet-blocker/6.png'),
            pygame.image.load('images/bullet-blocker/7.png'),
            pygame.image.load('images/bullet-blocker/8.png'),
            pygame.image.load('images/bullet-blocker/9.png'),
            pygame.image.load('images/bullet-blocker/10.png'),
            pygame.image.load('images/bullet-blocker/11.png'),
            pygame.image.load('images/bullet-blocker/12.png'),
            pygame.image.load('images/bullet-blocker/13.png'),
            pygame.image.load('images/bullet-blocker/14.png'),
            pygame.image.load('images/bullet-blocker/15.png'),
            pygame.image.load('images/bullet-blocker/16.png'),
            pygame.image.load('images/bullet-blocker/17.png')]

        # TRANSFORM THE BLOCKER IMAGE
        for i in range(len(self.image_list)):
            self.image_list[i] = pygame.transform.scale(self.image_list[i], (100, 50))

        self.image = self.image_list[0]

        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def draw(self):
        App.screen.blit(self.image, self.rect)

    def update(self):
        self.index += 1
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.check_index()

    def check_index(self):

        if self.index >= 16:
            self.kill()


class Alien(pygame.sprite.Sprite):
    frames = 0

    def __init__(self, x, y, alien_type=1):
        pygame.sprite.Sprite.__init__(self)
        self.alien_type = alien_type
        alien_type1 = [load_image('aliens/InvaderC1.png', -1, True), load_image('aliens/InvaderC2.png', -1, True)]
        alien_type2 = [load_image('aliens/InvaderB1.png', -1, True), load_image('aliens/InvaderB2.png', -1, True)]
        alien_type3 = [load_image('aliens/InvaderA1.png', -1, True), load_image('aliens/InvaderA2.png', -1, True)]

        if self.alien_type == 1:
            self.aliens = alien_type1
        if self.alien_type == 2:
            self.aliens = alien_type2
        if self.alien_type == 3:
            self.aliens = alien_type3

        self.index = 0
        self.image = self.aliens[self.index]

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = self.rect.x
        self.speed = 0.2

    def update(self):

        self.image = self.aliens[self.index]
        self.x += self.speed
        self.rect.x = int(self.x)
        Alien.frames += 1
        if Alien.frames > 30:
            self.index += 1
            Alien.frames = 0
            if self.index > 1:
                self.index = 0

    def update_speed(self):
        self.speed += 0.25

    def shift_down(self):
        self.speed *= -1
        self.rect.y += 20

    def get_alien_type(self):
        return self.alien_type


class MasterAlien(Alien):

    def __init__(self):
        super(MasterAlien, self).__init__(-50, 0)
        self.image, self.rect = load_image('aliens/EnemyMaster.png', -1, size=(50, 25))
        self.rect.y = 55
        self.snd = pygame.mixer.Sound('sounds/ufo_lowpitch.wav')
        self.snd.play()

    def update(self):
        self.rect.x += 5
        if self.rect.x > 1024:
            self.kill()


class App(object):
    screen = None
    running = True
    fps = 40
    fps_offset = 0
    clock = pygame.time.Clock()
    bullets = pygame.sprite.Group()
    ship = None
    aliens = pygame.sprite.Group()
    alien_drops = pygame.sprite.Group()
    blocker = pygame.sprite.Group()
    lives = [load_image('ship.png', -1, True) for i in range(3)]
    starfield = []
    score_file = open('score.txt', 'r+')

    def __init__(self):
        pygame.init()
        self.size = self.w, self.h = 1024, 576
        pygame.display.set_caption('Space Invaders')
        App.screen = pygame.display.set_mode(self.size, 0, 32)
        App.ship = Ship(25)

        # STARFIELD LIST
        for i in range(241):
            App.starfield.append(load_image('StarField/{0}.png'.format(i), -1, True, size=(1024, 576)))

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()

    @staticmethod
    def game_over():
        terminate = Text(App.screen, 'Quit', pos=(512, 288), bold=True, size=48, clr=Color('green'))

        new_game = False

        while not new_game:

            for event in pygame.event.get():

                if event.type == QUIT:
                    App().quit()
                if event.type == MOUSEMOTION:
                    if terminate.rect.collidepoint(event.pos[0], event.pos[1]):
                        Text(App.screen, 'Quit', pos=(512, 288), bold=True, size=48, clr=(255, 245, 238))
                    else:
                        Text(App.screen, 'Quit', pos=(512, 288), bold=True, size=48, clr=Color('green'))

                if event.type == MOUSEBUTTONDOWN:
                    if event.button == BUTTON_LEFT:
                        if terminate.rect.collidepoint(event.pos[0], event.pos[1]):
                            App().quit()

            Text(App.screen, 'Game Over..!!', pos=(512, 188), bold=True, size=100, clr=(255, 245, 238))

            pygame.display.update()
        if new_game:
            App().startup_screen()

    @staticmethod
    def startup_screen():

        # LOAD LOGO IMAGE
        logo, logo_rect = load_image('logo.png', -1, size=(650, 250))
        logo_rect.center = (670, 150)

        invader, invader_rect = load_image('game station.png', -1, size=(300, 270))
        invader_rect.center = (200, 140)

        boundary_rect = pygame.Rect(0, 0, 900, 290)
        boundary_rect.center = (512, 425)

        sbg_rect = pygame.Rect(0, 0, 1024, 576)
        sbg_index = 0

        # aliens images
        a1, a1rect = load_image('aliens/InvaderA1.png')
        a1rect.center = (300, 340)
        a2, a2rect = load_image('aliens/InvaderB1.png')
        a2rect.center = (300, 380)
        a3, a3rect = load_image('aliens/InvaderC1.png')
        a3rect.center = (300, 420)
        a4, a4rect = load_image('aliens/EnemyMaster.png')
        a4rect.center = (300, 460)

        ships, ships_rect = load_image('ships.png', -1, size=(100, 80))
        ships_rect.center = (750, 350)
        ships1, ships_rect1 = load_image('ships.png', -1, size=(100, 80))
        ships_rect1.center = (650, 450)
        ships2, ships_rect2 = load_image('ships.png', -1, size=(100, 80))
        ships_rect2.center = (850, 400)

        # BUTTONS
        b1 = None
        b2 = None

        # MUSICS
        pygame.mixer.music.load('sounds/Title_bg.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        while True:

            sbg = App.starfield[sbg_index]

            sbg_index += 1
            if sbg_index > 240:
                sbg_index = 0

            for event in pygame.event.get():

                if event.type == QUIT:
                    App().quit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == BUTTON_LEFT:
                        if b1.get_rect().collidepoint(event.pos[0], event.pos[1]):
                            return False
                        if b2.get_rect().collidepoint(event.pos[0], event.pos[1]):
                            App().quit()

            # FILL THE BACKGROUND
            App.screen.fill(Color('black'))
            App.screen.blit(sbg, sbg_rect)
            App.screen.blit(invader, invader_rect)
            App.screen.blit(ships, ships_rect)
            App.screen.blit(ships1, ships_rect1)
            App.screen.blit(ships2, ships_rect2)

            # BLIT THE LOGO
            App.screen.blit(logo, logo_rect)

            # DRAW THE BOX
            pygame.draw.rect(App.screen, Color('green'), boundary_rect, 2)

            # DRAW THE BUTTONS
            b1 = Button((185, 510), text='START')
            b2 = Button((740, 510), text='QUIT')

            # DRAW THE BOX CONTENT
            App.screen.blit(a1, a1rect)
            Text(App.screen, ' = 10 points', (390, 340), size=24, clr=Color('green'))
            App.screen.blit(a2, a2rect)
            Text(App.screen, ' = 20 points', (390, 380), size=24, clr=Color('green'))
            App.screen.blit(a3, a3rect)
            Text(App.screen, ' = 30 points', (390, 420), size=24, clr=Color('green'))
            App.screen.blit(a4, a4rect)
            Text(App.screen, ' = ?? Points', (390, 460), size=24, clr=Color('green'))

            pygame.display.update()
            App.clock.tick(60)

    @staticmethod
    def create_aliens():
        y = 70
        for i in range(2):
            for j in range(15):
                App.aliens.add(Alien((j * 50 + 50), y, alien_type=1))
            y += 40

        for i in range(2):
            for j in range(15):
                App.aliens.add(Alien((j * 50 + 50), y, alien_type=2))
            y += 40

        for i in range(2):
            for j in range(15):
                App.aliens.add(Alien((j * 50 + 50), y, alien_type=3))
            y += 40

    @staticmethod
    def run():

        # crashed ship displaying/control variables
        cimg, crect = load_image('crashed-ship.png', -1, size=(40, 25))
        # image for alien drops
        alien_bullet = load_image('alien_bullet.png', -1, True, size=(20, 10))

        # ship bullet image
        ship_bullet = load_image('ship_bullet.png', -1, True, size=(20, 20))

        coffset = 0
        drop_offset = 0.9998
        show_cimg = False

        ship_dir = {'left': False, 'right': False}

        top_margin = 15

        score = 0
        high_score = int(App.score_file.readline(1))
        credit = 0

        abg_rect = pygame.Rect(0, 0, 1024, 576)
        abg_index = 0

        App.startup_screen()
        pygame.mixer.music.stop()

        App.create_aliens()

        for bl in range(4):
            App.blocker.add(BulletBlocker(((bl * 250 - 100) + 250), 500))

        # SOUNDS
        shoot = pygame.mixer.Sound('sounds/shoot.wav')
        shoot.set_volume(0.2)
        alien_shoot = pygame.mixer.Sound('sounds/InvaderBullet.wav')
        alien_shoot.set_volume(0.2)
        ship_hitsnd = pygame.mixer.Sound('sounds/ShipHit.wav')
        invader_hitsnd = pygame.mixer.Sound('sounds/InvaderHit.wav')

        snd1 = pygame.mixer.Sound('sounds/fastinvader1.wav')
        snd1.set_volume(0.8)
        sound_offset = 90

        # Master Alien
        master_alien = pygame.sprite.Group()
        respawn_time = random.randint(900, 1000)

        while App.running:
            respawn_time -= 1

            if sound_offset < 0:
                snd1.play()
                sound_offset = 30

            sound_offset -= 1

            if len(App.aliens) == 0:
                App.create_aliens()
                drop_offset = 0.9999

            abg = App.starfield[abg_index]

            abg_index += 1
            if abg_index > 240:
                abg_index = 0

            App.fps_offset += 1
            if App.fps_offset > 100:
                App.fps_offset = 0
                drop_offset -= 0.00001
                App.fps += 1.2
                # INCREASE ALIENS SPEED
                for a in App.aliens:
                    a.update_speed()

            for event in pygame.event.get():
                if event.type == QUIT:
                    App.running = False

                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        ship_dir['left'] = True
                    if event.key == K_RIGHT:
                        ship_dir['right'] = True
                    if event.key == K_SPACE:
                        if len(App.bullets) < 2:
                            App.bullets.add(Bullet(App.ship.get_pos(), img=ship_bullet))
                            shoot.play()

                if event.type == KEYUP:
                    if event.key == K_LEFT:
                        ship_dir['left'] = False
                    if event.key == K_RIGHT:
                        ship_dir['right'] = False

            # update sprites
            App.ship.update(ship_dir['left'], ship_dir['right'])
            App.bullets.update()
            App.aliens.update()
            App.alien_drops.update()
            master_alien.update()

            edge = False

            for alien in App.aliens:
                if alien.rect.right > 1024 or alien.rect.left <= 0:
                    edge = True

            if edge:
                for alien in App.aliens:
                    alien.shift_down()

            for alien in App.aliens:
                drop_prob = random.random()
                if drop_prob >= drop_offset and len(App.alien_drops) < 5:
                    alien_shoot.play()
                    App.alien_drops.add(Bullet(alien.rect.center, direction='down', img=alien_bullet, ))

            # check collisions
            alien_hit = pygame.sprite.groupcollide(App.aliens, App.bullets, True, True)
            ship_hit = pygame.sprite.spritecollide(App.ship, App.alien_drops, True)
            pygame.sprite.groupcollide(App.alien_drops, App.bullets, True, True)
            blocker_hit = pygame.sprite.groupcollide(App.blocker, App.alien_drops, False, True)
            pygame.sprite.groupcollide(App.aliens, App.blocker, True, True)

            # SHIP BULLET AND BULLET BLOCKER HIT
            ship_bullet_hit = pygame.sprite.groupcollide(App.blocker, App.bullets, False, True)

            # fill the screen with background color
            App.screen.fill(Color('black'))
            App.screen.blit(abg, abg_rect)

            # Draw the lives
            if len(App.lives) > 0:
                for i in range(len(App.lives)):
                    App.screen.blit(App.lives[i], (0 + (i * 30), 552))

            # Check for game over
            if len(App.lives) == 0:
                App().game_over()

            if len(ship_hit) > 0:
                ship_hitsnd.play()
                show_cimg = True
                App.lives.pop(-1)

            if coffset > 25:
                show_cimg = False
                coffset = 0

            # TRACKING SCORE
            if len(alien_hit) > 0:
                invader_hitsnd.play()
                for a in alien_hit:
                    if a.get_alien_type() == 1:
                        score += 40
                    elif a.get_alien_type() == 2:
                        score += 20
                    elif a.get_alien_type() == 3:
                        score += 10
                    else:
                        score += random.randint(100, 500)

            # UPDATE BLOCKER FOR BLOCKER AND ALIENS BULLET HIT
            if len(blocker_hit) > 0:
                for b in blocker_hit:
                    b.update()

            # UPDATE BLOCKER FOR BLOCKER AND SHIP BULLET HIT
            if len(ship_bullet_hit) > 0:
                for blocker in ship_bullet_hit:
                    blocker.update()

            # draw sprite objects
            # draw ship
            if show_cimg:
                crect.center = App.ship.get_pos()
                App.screen.blit(cimg, crect)
                coffset += 1
            else:
                App.ship.draw(App.screen)

            App.bullets.draw(App.screen)
            App.aliens.draw(App.screen)
            App.alien_drops.draw(App.screen)
            App.blocker.draw(App.screen)
            master_alien.draw(App.screen)

            if respawn_time <= 0:
                master_alien.add(MasterAlien())
                respawn_time = random.randint(900, 1500)

            if score > high_score:
                high_score = score
                App.score_file.seek(0)
                App.score_file.write(str(high_score) + '\n')

            # SCORE
            Text(App.screen, '< Score >', pos=(950, top_margin), bold=False, clr=Color('green'))
            Text(App.screen, ('000' + str(score)), pos=(950, top_margin * 3), bold=False, clr=Color('green'))
            # HIGH SCORE
            Text(App.screen, '< High Score >', pos=(100, top_margin), bold=False, clr=Color('green'))
            Text(App.screen, ('000' + str(high_score)), pos=(100, top_margin * 3), bold=False, clr=Color('green'))
            # GAME TITLE
            Text(App.screen, 'SpaceInvaders', pos=(512, top_margin), clr=Color('green'))
            # CREDITS
            Text(App.screen, '< Credits >', pos=(850, 560), clr=Color('green'))
            Text(App.screen, ('000' + str(credit)), pos=(950, 560), clr=Color('green'))

            # DRAW THE BOTTOM LINE
            pygame.draw.line(App.screen, Color('green'), (0, 551), (1024, 551))

            # update the main screen
            pygame.display.update()
            App.clock.tick(int(App.fps))  # 60 frames per second
        App().quit()


if __name__ == '__main__':
    App().run()
