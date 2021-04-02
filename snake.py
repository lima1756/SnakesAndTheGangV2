import pygame
import math as m
import random
from easyAI import TwoPlayersGame, Human_Player, AI_Player, Negamax


class COLORS:
    white = (255, 255, 255)
    black = (0, 0, 0)
    yellow = (255, 255, 102)
    red = (213, 50, 80)
    green = (0, 255, 0)
    blue = (50, 153, 213)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Snake:
    def __init__(self, x, y):
        self.body = [Point(x, y)]
        self.length = 1
        self.speed = 15
        self.direction = [0, 0]
        self.directionKey = 0
        self.alive = True
        self.growing = False

    def grow(self):
        self.length += 1
        self.growing = True
        self.body.append(Point(self.body[0].x, self.body[0].y))

    def move(self, limitX, limitY, block_size):
        self.growing = False
        for i in range(self.length-1, 0, -1):
            self.body[i] = self.body[i-1]
        self.body[0] = Point(self.body[0].x + self.direction[0],
                             self.body[0].y + self.direction[1])
        if self.body[0].x >= limitX:
            self.body[0].x = 0
        if self.body[0].x < 0:
            self.body[0].x = limitX-block_size
        if self.body[0].y < 0:
            self.body[0].y = limitY-block_size
        if self.body[0].y >= limitY:
            self.body[0].y = 0


class Game(TwoPlayersGame):
    WIDTH = 600
    HEIGHT = 400
    BLOCK_SIZE = 10
    FOOD_QTY = 5
    display = None
    clock = None
    font_style = None
    DIRECTIONS = {
        pygame.K_LEFT: [-BLOCK_SIZE, 0],
        pygame.K_RIGHT: [BLOCK_SIZE, 0],
        pygame.K_UP: [0, -BLOCK_SIZE],
        pygame.K_DOWN: [0, BLOCK_SIZE]
    }

    OPPOSITE_MOVE = {pygame.K_RIGHT: pygame.K_LEFT, pygame.K_UP: pygame.K_DOWN,
                    pygame.K_LEFT: pygame.K_RIGHT, pygame.K_DOWN: pygame.K_UP}


    def __init__(self, players):
        pygame.init()
        Game.display = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT))
        Game.clock = pygame.time.Clock()
        Game.font_style = pygame.font.SysFont("verdana", 25)

        # Define the players
        self.players = players
        # Define who starts the game
        self.nplayer = 1

        pygame.display.set_caption('Snakes')
        self.game_over = False
        self.game_close = False
        self.initGame()

    def initGame(self):
        self.food = []
        for _ in range(self.FOOD_QTY):
            self.addFood()
        self.snakes = [Snake(self.WIDTH//2, self.HEIGHT//2)]
        self.snakes.append(Snake(round(random.randrange(0, self.WIDTH - self.BLOCK_SIZE) / self.BLOCK_SIZE) *
                                 self.BLOCK_SIZE, round(random.randrange(0, self.HEIGHT - self.BLOCK_SIZE) / self.BLOCK_SIZE) * self.BLOCK_SIZE))

    def message(self, msg, color, posx=0, posy=0):
        if posx == None:
            posx = self.WIDTH / 3
        if posy == None:
            posy = self.HEIGHT / 3
        text = Game.font_style.render(msg, True, color)
        posx -= text.get_rect().width/2
        posy -= text.get_rect().height/2
        Game.display.blit(text, [posx, posy])

    def drawSnakes(self):
        for i in range(len(self.snakes)):
            for point in self.snakes[i].body:
                pygame.draw.rect(Game.display, COLORS.white if i == 0 else COLORS.red, [
                    point.x, point.y, self.BLOCK_SIZE, self.BLOCK_SIZE])

    def drawFood(self):
        for point in self.food:
            pygame.draw.rect(Game.display, COLORS.green, [
                point.x, point.y, self.BLOCK_SIZE, self.BLOCK_SIZE])

    def addFood(self, i=None):
        f = Point(round(random.randrange(0, self.WIDTH - self.BLOCK_SIZE) / self.BLOCK_SIZE) *
                  self.BLOCK_SIZE, round(random.randrange(0, self.HEIGHT - self.BLOCK_SIZE) / self.BLOCK_SIZE) * self.BLOCK_SIZE)
        if i != None:
            self.food[i] = f
        else:
            self.food.append(f)

    def collision_food(self):
        for snake in self.snakes:
            for i in range(len(self.food)):
                if self.food[i].x == snake.body[0].x and self.food[i].y == snake.body[0].y:
                    snake.grow()
                    self.addFood(i)

    def check_collision(self, i, j):
        start = 1 if i == j else 0 # avoid head check herself.
        for b in range(start, len(self.snakes[j].body)):
            if (not (i == j and self.snakes[i].growing)) and self.snakes[i].body[0].x == self.snakes[j].body[b].x \
                    and self.snakes[i].body[0].y == self.snakes[j].body[b].y:
                    return True
        return False

    def collision_snakes(self):
        total = len(self.snakes)
        death = []
        for i in range(total):
            for j in range(total):
                if self.check_collision(i, j):
                        death.append(i)
        for i in death:
            self.snakes[i].alive = False

    def is_over(self):
        return not all([snake.alive for snake in self.snakes])

    def points_over_diamonds(self, indexPlayer, weight=0.3):
        scores = []
        for f in self.food:
            dy = abs(self.snakes[indexPlayer].body[0].y - f.y)
            dx = abs(self.snakes[indexPlayer].body[0].x - f.x)
            dy = self.HEIGHT - dy if dy > self.HEIGHT / 2 else dy
            dx = self.WIDTH - dx if dx > self.WIDTH / 2 else dx

            distance = (dy/self.HEIGHT) + (dx/self.WIDTH)
            score = 1 - distance

            scores.append(score)
        scores = sorted(scores, reverse=True)

        return (scores[0] + scores[1] *.5 + scores[2] *.125) *weight

    def points_over_enemy(self, indexPlayer, weight=.1):
        score = 0
        opponent = (indexPlayer + 1) % 2
        weight_due_lenght = 3 / (len(self.snakes[indexPlayer].body)**(0.8))
        for b in self.snakes[indexPlayer].body:

            dx = abs(b.x - self.snakes[opponent].body[0].x)
            dx = self.WIDTH - dx  if dx > self.WIDTH /2 else dx

            dy = abs(b.y - self.snakes[opponent].body[0].y)
            dy = self.HEIGHT - dy  if dy > self.HEIGHT /2 else dy
            distance = (dy / self.HEIGHT) + (dx / self.WIDTH)

            score += m.log1p(m.e**(2 - distance))
        return score*weight * weight_due_lenght

    def scoring(self):
        if not self.snakes[0].alive:
            score = -100
        elif not self.snakes[1].alive:
            score = 100
        else:
            score = 0
            score += self.points_over_diamonds(0, weight=1)
            score -= self.points_over_diamonds(1, weight=1)
            score += self.points_over_enemy(0, weight=.2)
            score -= self.points_over_enemy(1, weight=.2)
            print(score)
        return score

    def check_avoid_auto_collision(self, move):
        snake = self.snakes[self.nplayer - 1]
        for b in range(1, len(snake.body)):
            if (not snake.growing) and \
                    snake.body[0].x + self.DIRECTIONS[move][0] == snake.body[b].x and \
                    snake.body[0].y + self.DIRECTIONS[move][1] == snake.body[b].y:
                    return False
        return True

    def possible_moves(self):
        direction = self.snakes[self.nplayer - 1].directionKey
        possible_moves = [self.OPPOSITE_MOVE[d] for d in self.OPPOSITE_MOVE if direction != d]
        possible_moves = [mm for mm in possible_moves if self.check_avoid_auto_collision(mm)]
        if len(possible_moves) == 0:
            possible_moves = [self.OPPOSITE_MOVE[d] for d in self.OPPOSITE_MOVE if direction != d]
            # doesn't matter this case, is dead already, only avoiding bug on negamax.
        return possible_moves

    def make_move(self, move):
        snake = self.snakes[self.nplayer-1]
        if move in self.OPPOSITE_MOVE and snake.directionKey != self.OPPOSITE_MOVE[move]:
            snake.direction = self.DIRECTIONS[move]
            snake.directionKey = move
        snake.move(self.WIDTH, self.HEIGHT, self.BLOCK_SIZE)

    def gameLoop(self):
        while not self.game_over:
            while self.is_over():
                Game.display.fill(COLORS.black)
                self.message("Game over", COLORS.blue,
                             self.WIDTH / 2, self.HEIGHT/4)
                if self.snakes[0].alive:
                    self.message("You win", COLORS.green,
                                 self.WIDTH / 2, self.HEIGHT/4 * 2)
                else:
                    self.message("You lose", COLORS.red,
                                 self.WIDTH / 2, self.HEIGHT/4*2)
                self.message("Press any key to play again",
                             COLORS.blue, self.WIDTH / 2, self.HEIGHT/4*3)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_over = True
                    if event.type == pygame.KEYDOWN:
                        self.initGame()
                        self.gameLoop()

            humanMove = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_over = True
                    else:
                        humanMove = event.key
            self.play_move(humanMove)

            Game.display.fill(COLORS.black)

            # MOVING THE DUMMY ENEMY
            ai_move = self.get_move()
            self.play_move(ai_move) # self.make_move(self.possible_moves()[random.randrange(0, 3)])

            self.collision_food()
            self.collision_snakes()
            self.drawSnakes()
            self.drawFood()

            pygame.display.update()
            Game.clock.tick(self.snakes[0].speed)
        pygame.quit()
        quit()


def main():
    Game([ Human_Player(), AI_Player(Negamax(1, win_score=100)) ]).gameLoop()


if __name__ == '__main__':
    main()
