import pygame
import time
import random


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

    def grow(self):
        self.length += 1
        self.body.append(Point(self.body[0].x, self.body[0].y))

    def move(self, limitX, limitY, block_size):
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


class Game:
    WIDTH = 600
    HEIGHT = 400
    BLOCK_SIZE = 10
    FOOD_QTY = 5

    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Snakes')
        self.clock = pygame.time.Clock()
        self.font_style = pygame.font.SysFont("verdana", 25)
        self.game_over = False
        self.game_close = False
        self.initGame()

    def initGame(self):
        self.food = []
        for i in range(self.FOOD_QTY):
            self.addFood()
        self.snakes = [Snake(self.WIDTH//2, self.HEIGHT//2)]
        self.snakes.append(Snake(round(random.randrange(0, self.WIDTH - self.BLOCK_SIZE) / self.BLOCK_SIZE) *
                                 self.BLOCK_SIZE, round(random.randrange(0, self.HEIGHT - self.BLOCK_SIZE) / self.BLOCK_SIZE) * self.BLOCK_SIZE))

    def message(self, msg, color, posx=0, posy=0):
        if posx == None:
            posx = self.WIDTH / 3
        if posy == None:
            posy = self.HEIGHT / 3
        text = self.font_style.render(msg, True, color)
        posx -= text.get_rect().width/2
        posy -= text.get_rect().height/2
        self.display.blit(text, [posx, posy])

    def drawSnakes(self):
        for i in range(len(self.snakes)):
            for point in self.snakes[i].body:
                pygame.draw.rect(self.display, COLORS.white if i == 0 else COLORS.red, [
                    point.x, point.y, self.BLOCK_SIZE, self.BLOCK_SIZE])

    def drawFood(self):
        for point in self.food:
            pygame.draw.rect(self.display, COLORS.green, [
                point.x, point.y, self.BLOCK_SIZE, self.BLOCK_SIZE])

    def addFood(self, i=None):
        f = Point(round(random.randrange(0, self.WIDTH - self.BLOCK_SIZE) / self.BLOCK_SIZE) *
                  self.BLOCK_SIZE, round(random.randrange(0, self.HEIGHT - self.BLOCK_SIZE) / self.BLOCK_SIZE) * self.BLOCK_SIZE)
        if i != None:
            self.food[i] = f
        else:
            self.food.append(f)

    def collissionFood(self):
        for snake in self.snakes:
            for i in range(len(self.food)):
                if self.food[i].x == snake.body[0].x and self.food[i].y == snake.body[0].y:
                    snake.grow()
                    self.addFood(i)

    def collissionSnakes(self):
        total = len(self.snakes)
        death = []
        for i in range(total):
            for j in range(total):
                if i == j:
                    continue
                for point in self.snakes[j].body:
                    if self.snakes[i].body[0].x == point.x and self.snakes[i].body[0].y == point.y:
                        death.append(i)
                        print(i)
        for i in death:
            self.snakes[i].alive = False

    def check_end_game(self):
        return not all([snake.alive for snake in self.snakes])

    def gameLoop(self):
        while not self.game_over:
            while self.check_end_game():
                self.display.fill(COLORS.black)
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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.snakes[0].directionKey != pygame.K_RIGHT:
                        self.snakes[0].direction[0] = -self.BLOCK_SIZE
                        self.snakes[0].direction[1] = 0
                        self.snakes[0].directionKey = pygame.K_LEFT
                    elif event.key == pygame.K_RIGHT and self.snakes[0].directionKey != pygame.K_LEFT:
                        self.snakes[0].direction[0] = self.BLOCK_SIZE
                        self.snakes[0].direction[1] = 0
                        self.snakes[0].directionKey = pygame.K_RIGHT
                    elif event.key == pygame.K_UP and self.snakes[0].directionKey != pygame.K_DOWN:
                        self.snakes[0].direction[1] = -self.BLOCK_SIZE
                        self.snakes[0].direction[0] = 0
                        self.snakes[0].directionKey = pygame.K_UP
                    elif event.key == pygame.K_DOWN and self.snakes[0].directionKey != pygame.K_UP:
                        self.snakes[0].direction[1] = self.BLOCK_SIZE
                        self.snakes[0].direction[0] = 0
                        self.snakes[0].directionKey = pygame.K_DOWN
                    elif event.key == pygame.K_ESCAPE:
                        self.game_over = True

            self.display.fill(COLORS.black)

            # MOVING THE DUMMY ENEMY
            self.snakes[1].direction[1] = self.BLOCK_SIZE
            self.snakes[1].direction[0] = 0
            self.snakes[1].directionKey = pygame.K_DOWN

            self.collissionFood()

            for snake in self.snakes:
                snake.move(self.WIDTH, self.HEIGHT, self.BLOCK_SIZE)
                self.collissionSnakes()

            self.drawSnakes()
            self.drawFood()

            pygame.display.update()
            self.clock.tick(self.snakes[0].speed)
        pygame.quit()
        quit()


def main():
    Game().gameLoop()


if __name__ == '__main__':
    main()
