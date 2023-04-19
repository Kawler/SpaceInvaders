import sys
import json
import pygame
from player import Player
from sys import exit
import obstacle
from alien import Alien
from random import choice, randint
from laser import Laser
from alien import Extra

class Game:
    def __init__(self):
        #Player setup
        player_sprite = Player((screen_width / 2, screen_height), screen_width,5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        self.level = 1
        self.game_is_work = False
        self.high_score = {
            'high_score': 0,
        }
        with open('data.txt') as score_file:
            self.high_score = json.load(score_file)

        self.safe_high_score = False

        # Health and score setup
        self.lives = 4
        self.live_surf = pygame.image.load('graphics/player.png').convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 3 + 30)
        self.score = 0
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)
        self.main_menu_font = pygame.font.Font('font/Pixeled.ttf', 36)

        #obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        #self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)

        # Alien setup
        self.aliens = pygame.sprite.Group()
        #self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1
        self.alien_speed = 1
        self.alien_lasers = pygame.sprite.Group()

        #Extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)

        #Audio
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.2)
        music.play(loops= -1)
        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.2)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.3)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (241,79,80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance = 60 ,y_distance = 48, x_offset = 70, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0: alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2: alien_sprite = Alien('green',x ,y)
                else: alien_sprite = Alien('red',x, y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = (-1)*self.alien_speed
                self.alien_move_down(1)
            if alien.rect.left <= 0:
                self.alien_direction = self.alien_speed
                self.alien_move_down(1)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right','left']), screen_width))
            self.extra_spawn_time = randint(400, 800)

    def collision_checks(self):
        #player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacel collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                     laser.kill()
                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()
                    self.new_level_check = pygame.time.get_ticks()
                #extra collisions
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += 500
                    laser.kill()
        #alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                     laser.kill()
                if pygame.sprite.spritecollide(laser, self.player, False):
                     laser.kill()
                     self.lives -= 1
                     if self.lives <= 0:
                        for alien in self.aliens:
                            alien.kill()
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    self.lives -= 1
                    if self.lives <= 0:
                        for alien in self.aliens:
                            alien.kill()

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft = (10,-6))
        screen.blit(score_surf, score_rect)

    def display_level(self):
        level_surf = self.font.render(f'Level: {self.level}', False, 'white')
        level_rect = level_surf.get_rect(center=(screen_width / 2, 22))
        screen.blit(level_surf, level_rect)

    def victory_message(self):
        if not self.aliens.sprites() and self.lives > 0:
            victory_surf = self.font.render(f'Level: {self.level} complete!', False, 'white')
            victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)
            currnt_time = pygame.time.get_ticks()
            if currnt_time >= self.new_level_check + 8000:
                self.new_level()

    def new_level(self):
        self.alien_speed += 0.25
        self.level += 1
        if (self.lives < 4): self.lives += 1
        self.alien_setup(rows=6, cols=8)

    def end_game(self):
        if(self.lives <= 0):
            if (not self.safe_high_score and self.high_score['high_score'] < self.score):
                self.high_score['high_score'] = self.score
                with open('data.txt', 'w') as high_score:
                    json.dump(self.high_score, high_score)
                self.safe_high_score = True
            score = self.high_score['high_score']
            end_game_surf = self.font.render(f'Game over! Score: {self.score}', False, 'white')
            end_game_rect = end_game_surf.get_rect(center=(screen_width / 2, screen_height / 2))
            record_surf = self.font.render(f'Your record: {score}', False, 'white')
            record_surf_rect = record_surf.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
            end_game_restart = self.font.render('Press `Space` to restart!', False, 'white')
            end_game_restart_rect = end_game_restart.get_rect(center=(screen_width / 2, screen_height / 2 + 100))
            screen.blit(end_game_surf, end_game_rect)
            screen.blit(end_game_restart, end_game_restart_rect)
            screen.blit(record_surf, record_surf_rect)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.safe_high_score = False
                self.level = 1
                self.alien_speed = 1
                self.lives = 4
                self.score = 0
                self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)
                self.alien_setup(rows=6, cols=8)

    def main_menu(self):
        score = self.high_score['high_score']
        title = self.main_menu_font.render('Space Invaders', False, 'green')
        title_rect = title.get_rect(center=(screen_width / 2, screen_height / 2))
        record_surf = self.font.render(f'Your record: {score}', False, 'white')
        record_surf_rect = record_surf.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
        game_start = self.font.render('Press `Space` to start!', False, 'white')
        game_start_rect = game_start.get_rect(center=(screen_width / 2, screen_height / 2 + 80))
        screen.blit(title, title_rect)
        screen.blit(record_surf, record_surf_rect)
        screen.blit(game_start, game_start_rect)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.game_is_work = True
            self.safe_high_score = False
            self.level = 1
            self.alien_speed = 1
            self.lives = 4
            self.score = 0
            self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=480)
            self.alien_setup(rows=6, cols=8)

    def run(self):
        if(not self.game_is_work):
            self.main_menu()
        else:
            self.player.update()
            self.alien_lasers.update()
            self.extra.update()

            self.aliens.update(self.alien_direction)
            self.alien_position_checker()
            self.extra_alien_timer()
            self.collision_checks()

            self.player.sprite.lasers.draw(screen)
            self.player.draw(screen)
            self.blocks.draw(screen)
            self.aliens.draw(screen)
            self.alien_lasers.draw(screen)
            self.extra.draw(screen)
            self.display_lives()
            self.display_score()
            self.display_level()
            self.end_game()
            self.victory_message()


        # Обновим все группы спрайтов
        # Нарисуем все группы спрайтов



if __name__ == '__main__':
    pygame.init()
    screen_width = 600;
    screen_height = 600;

    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption('Space invaders')
    clock = pygame.time.Clock()
    game = Game()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
        screen.fill((30, 30, 30))
        game.run()

        pygame.display.update()
        clock.tick(60)