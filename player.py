import pygame
from laser import Laser

boost = 0

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, constraint, speed):
        super().__init__()
        self.image = pygame.image.load('graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        #Speed
        self.speed = speed
        #Screen constraint
        self.max_x_constraint = constraint
        #Laser
        self.ready = True
        self.laser_time  = 0
        self.laser_cooldown = 600
        self.lasers = pygame.sprite.Group()

        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.2)

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    def recharge(self):
        if not self.ready:
            currnt_time = pygame.time.get_ticks()
            if currnt_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def shoot_laser(self):
        self.shoot = self.lasers.add(Laser(self.rect.center,-8, self.rect.bottom))
        self.extra_laser()

    def extra_laser(self):
        if(boost == 1):
            x,y = self.rect.center
            a = (x, y + 100)
            self.lasers.add(Laser(a,-8, self.rect.bottom))

    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()