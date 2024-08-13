import pygame, sys, random, asyncio

class Block(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect(center = (x_pos, y_pos))
        

class Player(Block):
    def __init__(self, path, x_pos, y_pos):
        super().__init__(path, x_pos, y_pos)
        self.gravity = 0
        self.inAir = False
        self.mask = pygame.mask.from_surface(self.image)
    
    def constrain(self):
        if self.rect.bottom > asset_height:
            self.rect.bottom = asset_height
            self.inAir = False
        else:
            self.inAir = True
    
    def update(self):
        self.rect.y += self.gravity
        self.gravity += GRAVITY
        self.constrain()

class Spike(Block):
    def __init__(self, path, x_pos, y_pos, x_speed, player):
        super().__init__(path, x_pos, y_pos)
        self.x_speed = -2
        self.player = player
        self.active = False
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        if self.rect.bottom > asset_height:
            self.rect.bottom = asset_height
        
        self.rect.x += self.x_speed
        if game_manager.game_state == 'playing':
            self.collisions()

    def collisions(self):
        rect_collide = pygame.sprite.spritecollide(self, self.player, False)
        mask_collide = pygame.sprite.spritecollide(self, self.player, False, pygame.sprite.collide_mask)
        if rect_collide:
            if mask_collide:
                self.x_speed = 0
                player.y_speed = 0
                pygame.mixer.Sound.play(crash_sound)
                game_manager.game_over()

    def reset_spike(self):
        self.rect.center = (spike_width, asset_height)
        self.x_speed = random.choice(SPIKE_SPEEDS)

class GameManager:
    def __init__(self, player_sprite, spike_sprite):
        self.score = 0
        self.high_score = 0
        self.player_sprite = player_sprite
        self.spike_sprite = spike_sprite
        self.game_state = 'playing'

    def run_game(self):
        # Drawing the game objects
        self.player_sprite.draw(screen)
        self.spike_sprite.draw(screen)

        # Updating the game objects
        if self.game_state == 'playing':
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
        if self.spike_sprite.sprite.rect.right <= 0:
            self.score += 1
            self.spike_sprite.sprite.reset_spike()
        
    def game_over(self):
        self.game_state = 'game_over'

    def play_again_prompt(self):
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

    def restart_game(self):
        player.rect.top = player_width
        player.rect.bottom = asset_height
        player.gravity = 0

        spike.rect.left = spike_width
        spike.rect.bottom = asset_height
        spike.x_speed = -2

        if self.score > self.high_score:
            self.high_score = self.score

        self.score = 0
        self.game_state = 'playing'

# General Setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Bunny Hop')

# Global Variables
background = pygame.image.load('./assets/background.png').convert_alpha()
background = pygame.transform.scale(background, (screen_width, screen_height))
floor_color = pygame.Color('springgreen')
text_color = pygame.Color('black')
jump_sound = pygame.mixer.Sound("./assets/jump.wav")
crash_sound = pygame.mixer.Sound("./assets/crash.wav")
player_width = (screen_width/4)+50
spike_width = (screen_width/1.5)+50
asset_height = (screen_height/1.5)+19

# Game Fonts
basic_font = pygame.font.SysFont("Arial", 32)
high_score_font = pygame.font.SysFont("Arial", 24)
play_again_font = pygame.font.SysFont("Arial", 48)
yes_option_font = pygame.font.SysFont("Arial", 40)
no_option_font = pygame.font.SysFont("Arial", 40)

# Game Objects
player = Player('./assets/bunny.png', player_width, asset_height)
player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(player)
GRAVITY = 0.3

spike = Spike('./assets/spike.png', spike_width, asset_height, 1, player_sprite)
spike_sprite = pygame.sprite.GroupSingle()
spike_sprite.add(spike)
SPIKE_SPEEDS = (-2, -2.5, -3, -3.5, -4)

game_manager = GameManager(player_sprite, spike_sprite)

async def main():
    # Event Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_manager.game_state == 'playing':
                    if event.key == pygame.K_UP and player.inAir == False:
                        pygame.mixer.Sound.play(jump_sound)
                        player.gravity = -13
                elif game_manager.game_state == 'game_over':
                    if event.key == pygame.K_RETURN:
                        game_manager.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        # Background
        #screen.fill(bg_color)
        screen.blit(background, (0, 0))

        # Run the game logic
        game_manager.run_game()
        if game_manager.game_state == 'game_over':
            game_manager.play_again_prompt()


        # Rendering
        pygame.display.flip()
        clock.tick(120)
        await asyncio.sleep(0)
        
asyncio.run(main())