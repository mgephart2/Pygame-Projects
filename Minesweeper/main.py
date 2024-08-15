import pygame, sys, math, random, asyncio


class Block(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

class Board(Block):
    def __init__(self, values, cell_visibility, font):
        self.values = values
        self.cell_visibility = cell_visibility
        self.font = font
        self.sqrt_len = int(math.sqrt(len(self.values)))
        self.grid_size = screen_width//self.sqrt_len
    
    #Sets up the game board
    def populate_array(self, difficulty):
        #Initialize 1D game array on easy
        if difficulty == 1:
            self.values = [0] * 13
            self.cell_visibility = [False] * 16
            for i in range(3):
                self.values.append(9)
            self.font = pygame.font.SysFont("Arial", 88)
        #Initialize 1D game array on medium
        elif difficulty == 2:
            self.values = [0] * 54
            self.cell_visibility = [False] * 64
            for i in range(10):
                self.values.append(9)
            self.font = pygame.font.SysFont("Arial", 35)
        #Initialize 1D game array on hard
        elif difficulty == 3:
            self.values = [0] * 80
            self.cell_visibility = [False] * 100
            for i in range(20):
                self.values.append(9)
            self.font = pygame.font.SysFont("Arial", 35)
        #Randomize bomb locations and initialize helpful variables
        random.shuffle(self.values)
        self.sqrt_len = int(math.sqrt(len(self.values)))
        self.grid_size = screen_width//self.sqrt_len
        rows = []
        #Converts 1D game array to 2D game array
        for i in range(self.sqrt_len+2):
            row = [0] * (self.sqrt_len+2)
            rows.append(row)

        for i in range(len(self.values)):
            rows[i//self.sqrt_len+1][i%self.sqrt_len+1] = self.values[i]

        #Populates the game array with the appropriate values next to bombs
        for i in range(len(self.values)):
            x = i//self.sqrt_len
            y = i%self.sqrt_len
            if rows[x+1][y+1] != 9:
                if rows[x][y] == 9:
                    rows[x+1][y+1] += 1
                if rows[x][y+1] == 9:
                    rows[x+1][y+1] += 1
                if rows[x][y+2] == 9:
                    rows[x+1][y+1] += 1
                if rows[x+1][y] == 9:
                    rows[x+1][y+1] += 1
                if rows[x+1][y+2] == 9:
                    rows[x+1][y+1] += 1
                if rows[x+2][y] == 9:
                    rows[x+1][y+1] += 1
                if rows[x+2][y+1] == 9:
                    rows[x+1][y+1] += 1
                if rows[x+2][y+2] == 9:
                    rows[x+1][y+1] += 1
        
        #Convert back from 2D array to 1D array
        for i in range(len(self.values)):
            self.values[i] = rows[i//self.sqrt_len+1][i%self.sqrt_len+1]

class Bomb(Block):
    def __init__(self, path, x_pos, y_pos):
        super().__init__(path, x_pos, y_pos)

class GameManager:
    def __init__(self, bomb_sprite):
        self.bomb_sprite = bomb_sprite
        self.state = 'start_menu'

    def run_game(self):
        # Drawing the game board
        self.draw_board()

    def check_array(self, mouse_pos, button):
        x = screen_width/board.sqrt_len
        y = screen_height/board.sqrt_len
        for i in range(len(board.values)):
            #Identifies which cell is being clicked
            if mouse_pos[0] < x and mouse_pos[0] > x-(screen_width/board.sqrt_len):
                if mouse_pos[1] < y and mouse_pos[1] > y-(screen_height/board.sqrt_len):
                    #Left click not on a bomb or flag
                    if button == 1 and board.values[i] < 10:
                        board.cell_visibility[i] = True
                    #Right click to place flag
                    elif button == 3 and board.values[i] < 10 and board.cell_visibility[i] == False:
                        board.values[i] += 10
                        board.cell_visibility[i] = True
                    #Right click to remove flag
                    elif button == 3 and board.values[i] >= 10:
                        board.cell_visibility[i] = False
                        board.values[i] -= 10
            x += screen_width/board.sqrt_len
            if i % board.sqrt_len == (board.sqrt_len-1):
                y += screen_height/board.sqrt_len
                x = screen_width/board.sqrt_len
                    
    def draw_board(self):
        #Draws grid
        for x in range(0, screen_width, board.grid_size):
            pygame.draw.line(screen, line_color, (x, 0), (x, screen_height))
        for y in range(0, screen_height, board.grid_size):
            pygame.draw.line(screen, line_color, (0, y), (screen_width, y))
        
        x = (screen_width/board.sqrt_len)/2
        y = (screen_height/board.sqrt_len)/2
        lose = False
        #Draws values on revealed cells
        for i in range(len(board.cell_visibility)):
            if board.cell_visibility[i]:
                #Draws numbers
                if board.values[i] < 9:
                    cell_value = board.font.render(str(board.values[i]), True, text_color)
                    cell_value_rect = cell_value.get_rect(center = (x, y))
                    screen.blit(cell_value, cell_value_rect)
                #Draws bomb
                if board.values[i] == 9:
                    bomb = Bomb('./assets/bomb.png', x, y)
                    bomb_sprite.add(bomb)
                    self.bomb_sprite.draw(screen)
                    if self.state != 'game_over':
                        self.state = 'game_over'
                #Draws flag
                if board.values[i] > 9:
                    cell_value = board.font.render(str("F"), True, flag_color)
                    cell_value_rect = cell_value.get_rect(center = (x, y))
                    screen.blit(cell_value, cell_value_rect)

            x += (screen_width/board.sqrt_len)
            if x >= screen_width:
                x = (screen_width/board.sqrt_len)/2
                y += (screen_height/board.sqrt_len)
            if y >= screen_height:
                y = (screen_height/board.sqrt_len)/2
        
        #Checks if win condition is reached
        if self.state != 'game_over':
            self.check_win()

    def start_game(self):
        #Displays start menu
        screen.fill('grey81')

        title = title_font.render(str('Minesweeper'), True, text_color)
        title_rect = title.get_rect(center = (screen_width/2, 150))
        screen.blit(title, title_rect)
        
        start_menu = menu_font.render(str('Choose a difficulty'), True, text_color)
        start_menu_rect = start_menu.get_rect(center = (screen_width/2, screen_height/2 + 40))
        screen.blit(start_menu, start_menu_rect)

        easy_option = option_font.render(str('Easy (1)'), True, text_color)
        easy_option_rect = easy_option.get_rect(center = (screen_width/2 - 200, screen_height/2 + 150))
        screen.blit(easy_option, easy_option_rect)

        medium_option = option_font.render(str('Medium (2)'), True, text_color)
        medium_option_rect = medium_option.get_rect(center = (screen_width/2, screen_height/2 + 150))
        screen.blit(medium_option, medium_option_rect)

        hard_option = option_font.render(str('Hard (3)'), True, text_color)
        hard_option_rect = hard_option.get_rect(center = (screen_width/2 + 200, screen_height/2 + 150))
        screen.blit(hard_option, hard_option_rect)

        pygame.display.update()

    def handle_start_menu(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = 1
                board.populate_array(difficulty)
                self.state = 'game_running'
            if event.key == pygame.K_2:
                difficulty = 2
                board.populate_array(difficulty)
                self.state = 'game_running'
            if event.key == pygame.K_3:
                difficulty = 3
                board.populate_array(difficulty)
                self.state = 'game_running'
    
    def game_over(self):
        #Displays lose menu
        lose_text = menu_font.render(str('You blew up!'), True, lose_color)
        lose_text_rect = lose_text.get_rect(center = (screen_width/2, 75))
        screen.blit(lose_text, lose_text_rect)

        try_again = menu_font.render(str('Would you like to play again?'), True, lose_color)
        try_again_rect = try_again.get_rect(center = (screen_width/2, 150))
        screen.blit(try_again, try_again_rect)

        yes_option = option_font.render(str('Yes (Enter)'), True, lose_color)
        yes_option_rect = yes_option.get_rect(center = (screen_width/4 + 20, screen_height/2 + 40))
        screen.blit(yes_option, yes_option_rect)

        no_option = option_font.render(str('No (Esc)'), True, lose_color)
        no_option_rect = no_option.get_rect(center = (screen_width/1.5 + 20, screen_height/2 + 40))
        screen.blit(no_option, no_option_rect)

        pygame.display.update()

    def handle_game_over(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = 'start_menu'
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    
    def check_win(self):
        #Win condition: All cells have been revealed with flags on all bombs
        for i in range(len(board.values)):
            if board.cell_visibility[i] == False:
                return False
            if board.values[i] > 8 and board.values[i] != 19:
                return False
        self.state = 'win'

    def win(self):
        #Displays win menu
        win_text = menu_font.render(str('You won!'), True, win_color)
        win_text_rect = win_text.get_rect(center = (screen_width/2, 75))
        screen.blit(win_text, win_text_rect)

        try_again = menu_font.render(str('Would you like to play again?'), True, win_color)
        try_again_rect = try_again.get_rect(center = (screen_width/2, 150))
        screen.blit(try_again, try_again_rect)

        yes_option = option_font.render(str('Yes (Enter)'), True, win_color)
        yes_option_rect = yes_option.get_rect(center = (screen_width/4 + 20, screen_height/2 + 40))
        screen.blit(yes_option, yes_option_rect)

        no_option = option_font.render(str('No (Esc)'), True, win_color)
        no_option_rect = no_option.get_rect(center = (screen_width/1.5 + 20, screen_height/2 + 40))
        screen.blit(no_option, no_option_rect)

        pygame.display.update()

    def handle_win(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = 'start_menu'
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()


# General Setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Minesweeper')

# Global Variables
bg_color = pygame.Color('grey81')
line_color = pygame.Color('white')
text_color = pygame.Color('black')
flag_color = pygame.Color('red')
lose_color = pygame.Color('blue')
win_color = pygame.Color('yellow')

# Game fonts
title_font = pygame.font.SysFont("Arial", 84)
menu_font = pygame.font.SysFont("Arial", 48)
option_font = pygame.font.SysFont("Arial", 40)

bomb_sprite = pygame.sprite.GroupSingle()

board = Board([0], [0], pygame.font.SysFont("Arial", 88))
game_manager = GameManager(bomb_sprite)

game_manager.start_game()

async def main():
    # Event Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif game_manager.state == 'start_menu':
                game_manager.handle_start_menu(event)
            elif game_manager.state == 'game_running':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game_manager.check_array(pygame.mouse.get_pos(), event.button)
            elif game_manager.state == 'game_over':
                game_manager.handle_game_over(event)
            elif game_manager.state == 'win':
                game_manager.handle_win(event)

        
        # Background
        screen.fill(bg_color)

        # Run the appropriate game state
        if game_manager.state == 'start_menu':
            game_manager.start_game()
        elif game_manager.state in ['game_running', 'game_over', 'win']:
            game_manager.run_game()
            if game_manager.state == 'game_over':
                game_manager.game_over()
            elif game_manager.state == 'win':
                game_manager.win()

        # Rendering
        pygame.display.flip()
        clock.tick(120)
        await asyncio.sleep(0)
        
asyncio.run(main())
