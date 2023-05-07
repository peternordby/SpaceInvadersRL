import os
import random

import numpy as np
import pygame

WIDTH = 400
HEIGHT = 300
FRAME_RATE = 20

ACTIONS = [0,1,2,3] # left, right, shoot, noop

class Invader(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("figures/invader.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1

    def update(self):
        self.rect.x += self.speed

    def change_direction(self):
        self.speed = -self.speed
        self.update()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, lives=3):
        super().__init__()
        self.image = pygame.image.load("figures/player.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.lives = lives

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if self.rect.x + self.rect.width > WIDTH:
            self.rect.x = WIDTH - self.rect.width
        if self.rect.x < 0:
            self.rect.x = 0

    def loose_life(self):
        self.lives -= 1
        if self.lives == 2:
            self.image = pygame.image.load("figures/player_scratched.png")
        elif self.lives == 1:
            self.image = pygame.image.load("figures/player_dented.png")
        elif self.lives == 0:
            self.image = pygame.image.load("figures/player_damaged.png")

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed = 5, hostile=False):
        super().__init__()
        self.image = pygame.image.load("figures/bullet.png") if not hostile else pygame.image.load("figures/bomb.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class SpaceInvaders:
    def __init__(self, agent=False):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Invaders")
        self.clock = pygame.time.Clock()
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((0, 0, 0))
        self.player = Player(200, 250)
        self.invaders = pygame.sprite.Group()
        for i in range(5):
            for j in range(4):
                invader = Invader(10 + 50 * i, 5 + 35 * j)
                self.invaders.add(invader)
        
        self.bullets = pygame.sprite.Group()
        self.COOLDOWN = 15
        self.last_shot = 0

        self.invader_bullets = pygame.sprite.Group()
        self.invader_last_shot = 0

        self.players = pygame.sprite.Group()
        self.players.add(self.player)

        self.points = 0

        self.agent = agent
        
        self.game_over = False

    def update(self, action=None):
        if not self.agent:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.last_shot > self.COOLDOWN:
                    bullet = Bullet(self.player.rect.x + self.player.rect.width / 2, self.player.rect.y)
                    self.bullets.add(bullet)
                    self.last_shot = 0
                if event.type == pygame.QUIT:
                    pygame.quit()

        if self.agent and action is not None:
            if action == 0:
                self.player.rect.x -= self.player.speed
            elif action == 1:
                self.player.rect.x += self.player.speed
            elif action == 2 and self.last_shot > self.COOLDOWN:
                bullet = Bullet(self.player.rect.x + self.player.rect.width / 2, self.player.rect.y)
                self.bullets.add(bullet)
                self.last_shot = 0

        # Check if any invader touches the wall
        for invader in self.invaders:
            if invader.rect.x + invader.rect.width > WIDTH or invader.rect.x < 0:
                for invader in self.invaders:
                    invader.change_direction()
                    invader.rect.y += 20
                    if invader.rect.y >= HEIGHT - 70:
                        self.game_over = True
                break

        # Check for collisions
        for bullet in self.bullets:
            hit = pygame.sprite.spritecollide(bullet, self.invaders, True)
            if hit:
                self.points += 10
                bullet.kill()

        for bullet in self.invader_bullets:
            hit = pygame.sprite.spritecollide(bullet, self.players, False)
            if hit:
                bullet.kill()
                for player in hit:
                    player.loose_life()
                    self.points -= 20

        # Make invaders shoot
        for invader in self.invaders:
            if self.player.rect.x - 20 < invader.rect.x < self.player.rect.x + 20 and random.randint(0, 70) == 0 and self.invader_last_shot > self.COOLDOWN:
                bullet = Bullet(invader.rect.x + invader.rect.width / 2, invader.rect.y, -3, hostile=True)
                self.invader_bullets.add(bullet)
                self.invader_last_shot = 0

        self.screen.blit(self.background, (0, 0))
        self.invaders.update()
        self.players.update()
        self.bullets.update()
        self.invader_bullets.update()
        self.last_shot += 1
        self.invader_last_shot += 1
        self.invaders.draw(self.screen)
        self.players.draw(self.screen)
        self.bullets.draw(self.screen)
        self.invader_bullets.draw(self.screen)

        # Print points and lives
        font = pygame.font.Font(None, 36)
        text = font.render(str(self.player.lives), 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.x = WIDTH - 20
        textpos.y = 10
        self.screen.blit(text, textpos)

        text = font.render(str(self.points), 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.x = 10
        textpos.y = 10
        self.screen.blit(text, textpos)


        # Check if the game is over
        if len(self.invaders) == 0:
            self.game_over = True
            font = pygame.font.Font(None, 36)
            text = font.render("You win!", 1, (255, 255, 255))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            textpos.centery = self.background.get_rect().centery
            self.screen.blit(text, textpos)
            return self.points + self.player.lives * 100     

        if self.player.lives == 0 or self.game_over:
            self.game_over = True
            font = pygame.font.Font(None, 36)
            text = font.render("You loose!", 1, (255, 255, 255))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            textpos.centery = self.background.get_rect().centery
            self.screen.blit(text, textpos)
            return self.points

        pygame.display.flip()

    def play(self):
        while True:
            self.clock.tick(FRAME_RATE)
            action = np.random.choice(4)
            points = self.update(action=action)
            if points:
                pygame.quit()
                return points

    def get_state(self):
        pixels = pygame.surfarray.array3d(self.screen)
        #pixels = np.dot(pixels[..., :3], [0.299, 0.587, 0.114])
        #pixels = pixels.flatten()
        return pixels

    def step(self, action: int):
        prev_points = self.points
        self.update(action)
        return self.get_state(), self.points-prev_points, self.game_over, {0: 0}
    
    def reset(self):
        self.__init__(self.agent)
        return self.get_state()

    def render(self):
        pygame.display.flip()

