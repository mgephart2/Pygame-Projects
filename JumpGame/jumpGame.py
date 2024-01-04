import pygame, sys, random

class Block(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

class Player(Block):
    def __init__(self, path, x_pos, y_pos):
        super().__init__(path, x_pos, y_pos)
        self.gravity = 0
        self.inAir = False
    
    def constrain(self):
        if self.rect.bottom > screen_height/1.5:
            self.rect.bottom = screen_height/1.5
            self.inAir = False
        else:
            self.inAir = True
    
    def update(self):
        self.rect.y += self.gravity
        self.gravity += 0.3
        self.constrain()

class Spike(Block):
    def __init__(self, path, x_pos, y_pos, x_speed, player):
        super().__init__(path, x_pos, y_pos)
        self.x_speed = -2
        self.player = player
        self.active = False
    
    def update(self):
        if self.rect.bottom > screen_height/1.5:
            self.rect.bottom = screen_height/1.5
        
        self.rect.x += self.x_speed
        self.collisions()

    def collisions(self):
        if pygame.sprite.spritecollide(self, self.player, False):
            collision_player = pygame.sprite.spritecollide(self, self.player, False)[0].rect
            if abs(self.rect.left == collision_player.right) < 10:
                self.x_speed = 0
                player.y_speed = 0
                pygame.mixer.Sound.play(crash_sound)
                game_manager.play_again()
            elif abs(self.rect.top == collision_player.bottom) < 10:
                self.x_speed = 0
                player.y_speed = 0
                pygame.mixer.Sound.play(crash_sound)
                game_manager.play_again()

    def reset_spike(self):
        self.rect.center = (screen_width/1.5, screen_height/1.5)
        self.x_speed = random.choice((-2, -2.5, -3, -3.5, -4))

class GameManager:
    def __init__(self, player_sprite, spike_sprite):
        self.score = 0
        self.high_score = 0
        self.player_sprite = player_sprite
        self.spike_sprite = spike_sprite

    def run_game(self):
        # Drawing the game objects
        self.player_sprite.draw(screen)
        self.spike_sprite.draw(screen)

        # Updating the game objects
        self.player_sprite.update()
        self.spike_sprite.update()
        self.reset_spike()
        self.draw_score()

    def draw_score(self):
        score = basic_font.render(str(self.score), True, text_color)
        score_rect = score.get_rect(midtop = (screen_width/2, 30))
        screen.blit(score, score_rect)

        high_score = high_score_font.render(str('High Score: ') + str(self.high_score), True, text_color)
        high_score_rect = high_score.get_rect(midleft = (8, 20))
        screen.blit(high_score, high_score_rect)
    
    def reset_spike(self):
        if self.spike_sprite.sprite.rect.left <= 0:
            self.score += 1
            self.spike_sprite.sprite.reset_spike()
        
    def play_again(self):
        play_again = play_again_font.render(str('Play Again?'), True, text_color)
        play_again_rect = play_again.get_rect(midtop = (screen_width/2, 75))
        screen.blit(play_again, play_again_rect)

        yes_option = yes_option_font.render(str('Yes (Enter)'), True, text_color)
        yes_option_rect = yes_option.get_rect(midtop = (screen_width/4 + 20, screen_height/2 - 40))
        screen.blit(yes_option, yes_option_rect)

        no_option = no_option_font.render(str('No (Esc)'), True, text_color)
        no_option_rect = no_option.get_rect(midtop = (screen_width/1.5 + 20, screen_height/2 - 40))
        screen.blit(no_option, no_option_rect)

        self.draw_score()
        
        pause = True
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.restart_game()
                        pause = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            pygame.display.update()
            clock.tick(120)

    def restart_game(self):
        player.rect.top = screen_width/4
        player.rect.bottom = screen_height/1.5
        player.gravity = 0

        spike.rect.left = screen_width/1.5
        spike.rect.bottom = screen_height/1.5
        spike.x_speed = -2

        if self.score > self.high_score:
            self.high_score = self.score

        self.score = 0

# General Setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('JumpGame')

# Global Variables
bg_color = pygame.Color('deepskyblue1')
floor_color = pygame.Color('springgreen')
text_color = pygame.Color('black')
jump_sound = pygame.mixer.Sound("jump.wav")
crash_sound = pygame.mixer.Sound("crash.wav")
floor = pygame.Rect(0, screen_height/1.5, screen_width, screen_height)

# Game Fonts
basic_font = pygame.font.SysFont("Arial", 32)
high_score_font = pygame.font.SysFont("Arial", 24)
play_again_font = pygame.font.SysFont("Arial", 48)
yes_option_font = pygame.font.SysFont("Arial", 40)
no_option_font = pygame.font.SysFont("Arial", 40)

# Game Objects
player = Player('bunny.png', screen_width/4, screen_height/1.5)
player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(player)

spike = Spike('spike.png', screen_width/1.5, screen_height/1.5, 1, player_sprite)
spike_sprite = pygame.sprite.GroupSingle()
spike_sprite.add(spike)

game_manager = GameManager(player_sprite, spike_sprite)

# Event Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and player.inAir == False:
                pygame.mixer.Sound.play(jump_sound)
                player.gravity = -13

    # Background
    screen.fill(bg_color)
    pygame.draw.rect(screen, floor_color, floor)

    # Run the Game
    game_manager.run_game()

    # Rendering
    pygame.display.flip()
    clock.tick(120)