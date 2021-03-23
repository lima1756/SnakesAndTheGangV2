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


class Game(TwoPlayersGame):
    WIDTH = 600
    HEIGHT = 400
    BLOCK_SIZE = 10
    FOOD_QTY = 5
    display = None
    clock = None
    font_style = None


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
        for i in death:
            self.snakes[i].alive = False

    def is_over(self):
        return not all([snake.alive for snake in self.snakes])

    def points_over_diamonds(self, indexPlayer, weight=0.3):
        scores = []
        for f in self.food:
            scores.append((1 - (abs(self.snakes[indexPlayer].body[0].y - f.y) / self.HEIGHT)) +
                          (1 - (abs(self.snakes[indexPlayer].body[0].x - f.x) / self.WIDTH)))
        scores = sorted(scores, reverse=True)

        return (scores[0] + scores[1]*.606 +  scores[2] * .13)  * weight * self.FOOD_QTY

    def points_over_enemy(self, indexPlayer, weight=.5):
        score = 0
        opponent = (indexPlayer + 1) % 2
        weight_due_lenght = 3 # TODO
        for b in self.snakes[indexPlayer].body:
            distance = (1 - (abs(self.snakes[opponent].body[0].y - b.y) / self.HEIGHT)) + \
                     (1 - (abs(self.snakes[opponent].body[0].x - b.x) / self.WIDTH))
            score += m.log1p(m.e**(-distance*distance/2))
        return score*weight * weight_due_lenght

    def scoring(self):
        if not self.snakes[0].alive:
            score = -100
        elif not self.snakes[1].alive:
            score = 100
        else:
            score = 0
            score += self.points_over_diamonds(0)
            score -= self.points_over_diamonds(1)
            score += self.points_over_enemy(0)
            score -= self.points_over_enemy(1)
        return score

    def possible_moves(self):
        """TODO cosas raras pasan aqui.
            Ademas de considerar el añadir restricciones de movimientos
            como dice Ivan, ( que no estoy de acuerdo, porque las colisiones
            se consideran en el scoring).
            El modelo que ofrezco actualmente es defectuoso, o al menos negamax
            toma mal los movimientos, en el sentido de que, si se añade la direccion
            hacia adelante ( o no hacer nada, lo cual es equivalente), decide ir en
            linea recta.
            Si no se le añade esa opcion nula intercala entre movimientos arriba y derecha.
        """
        moves = [pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN]
        return [m for m in moves if self.snakes[self.nplayer - 1].directionKey != m ]
        # return [m if self.snakes[self.nplayer - 1].directionKey != m else 0 for m in moves]

    def make_move(self, move):
        if move == pygame.K_LEFT and self.snakes[self.nplayer-1].directionKey != pygame.K_RIGHT:
            self.snakes[self.nplayer-1].direction = [-self.BLOCK_SIZE, 0]
            self.snakes[self.nplayer-1].directionKey = move
        elif move == pygame.K_RIGHT and self.snakes[0].directionKey != pygame.K_LEFT:
            self.snakes[self.nplayer-1].direction = [self.BLOCK_SIZE, 0]
            self.snakes[self.nplayer-1].directionKey = move
        elif move == pygame.K_UP and self.snakes[self.nplayer-1].directionKey != pygame.K_DOWN:
            self.snakes[self.nplayer-1].direction = [0,-self.BLOCK_SIZE]
            self.snakes[self.nplayer-1].directionKey = move
        elif move == pygame.K_DOWN and self.snakes[0].directionKey != pygame.K_UP:
            self.snakes[self.nplayer-1].direction = [0, self.BLOCK_SIZE]
            self.snakes[self.nplayer-1].directionKey = move

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
            self.play_move(ai_move)
            # self.make_move(self.possible_moves()[random.randrange(0, 3)])

            self.collissionFood()

            for snake in self.snakes:
                snake.move(self.WIDTH, self.HEIGHT, self.BLOCK_SIZE)
                self.collissionSnakes()

            self.drawSnakes()
            self.drawFood()

            pygame.display.update()
            Game.clock.tick(self.snakes[0].speed)
        pygame.quit()
        quit()


def main():
    Game([ Human_Player(), AI_Player(Negamax(7, win_score=100)) ]).gameLoop()


if __name__ == '__main__':
    main()
