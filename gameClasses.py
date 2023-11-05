import random
from gameExceptions import *

class Dot:

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'Point({self.x}, {self.y})'


class Ship:

    def __init__(self, length, first_dot, vector):
        self.length = length
        self.first_dot = first_dot
        self.direction = vector

    def dots(self):
        ship_dots = []
        ship_dots.append(self.first_dot)
        if self.direction.upper() == 'V':
            ship_dots.extend(Dot(self.first_dot.x + i, self.first_dot.y) for i in range(1, self.length))
        elif self.direction.upper() == 'H':
            ship_dots.extend(Dot(self.first_dot.x, self.first_dot.y + i) for i in range(1, self.length))
        else:
            raise WrongDirection('Неверное значение направления корабля')
        return ship_dots


class Board:

    _var = {
        'cell': '\u25A1',
        'ship': '\u25A0',
        'miss': 't',
        'bingo': '\u2715'
    }

    def __init__(self):
        self.board = [[self._var['cell']] * 6 for i in range(6)]
        self.hid = True
        self.forbidden = []

    def add_dot(self, dot):
        self.board[dot.x - 1][dot.y - 1] = self._var['ship']

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.not_valid(dot):
                return False
        for dot in ship.dots():
            self.add_dot(dot)
            self.contour(ship)
        return True

    def contour(self, ship):
        '''контур корабль + область вокруг корабля - клетки куда запрещено ставить другие корабли'''
        for dot in ship.dots():
            for i in range(dot.x - 1, dot.x + 2):
                for j in range(dot.y - 1, dot.y + 2):
                    new_point = Dot(i, j)
                    if not Board.out(new_point) and new_point not in self.forbidden:
                        self.forbidden.append(Dot(i, j))

    def shoot(self, x, y):
        '''выстрел по клетке с координатами x, y'''
        if Board.out(Dot(x, y)):
            raise BoardOutException('Точка вне пределах доски')
            return False
        if self.board[x - 1][y - 1] not in (self._var['cell'], self._var['ship']):
            raise TwiceShooting('В данную точку уже стреляли')
            return False
        if self.board[x - 1][y - 1] == self._var['cell']:
            self.board[x - 1][y - 1] = self._var['miss']
            print('Промах!')
        elif self.board[x - 1][y - 1] == self._var['ship']:
            self.board[x - 1][y - 1] = self._var['bingo']
            print('Попадание!')
            return True

    def show(self, visible=True):
        '''вывод доски на экран'''
        print(' ', *range(1, 7))
        for i in range(6):
            print(i + 1, '', end='')
            if visible:
                print('|'.join(self.board[i]))
            else:
                print('|'.join(self.board[i][j] if self.board[i][j] != self._var['ship'] else self._var['cell'] for j in range(6)))

    def not_valid(self, dot):
        '''проверка можно ли в данную  точку поставить клетку корабля'''
        return Board.out(dot) or \
               self.board[dot.x - 1][dot.y - 1] != self._var['cell'] or \
               dot in self.forbidden

    @staticmethod
    def out(dot):
        return dot.x > 6 or dot.x < 1 or dot.y > 6 or dot.y < 1


class Player:

    def __init__(self, board):
        self.board = board
        self.enemy_board = Board()

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                x, y = self.ask()
                self.enemy_board.shoot(x, y)
            except Exception as e:
                print(repr(e))
            else:
                break


class User(Player):

    def ask(self):
        x, y = map(int, input('Ваш ход. Координаты выстрела: ').split())
        return x, y


class AI(Player):

    def ask(self):
        x, y = random.randint(1, 6), random.randint(1, 6)
        print(f'Ход противника. Противник стреляет в клетку {x},{y}: ', end='')
        return x, y


class Game:

    show_enemy = False # Отображать на доске противника корабли?

    def __init__(self):
        self.user_player = User(self.random_board())
        self.ai_player = AI(self.random_board())
        self.user_player.enemy_board = self.ai_player.board
        self.ai_player.enemy_board = self.user_player.board

    def start(self):
        self.greet()
        self.loop()

    def show_battlefield(self, user_board, ai_board):
        '''отрисовывает поле с учетом параметра show_enemy - показывать ли корабли противника'''
        print('*' * 20 +'\nДоска противника:')
        ai_board.show(visible=self.show_enemy)
        print('-' * 18 + '\nВаша доска:')
        user_board.show()

    def greet(self):
        print('<<< МОРСКОЙ БОЙ >>>')
        self.show_battlefield(self.user_player.board, self.ai_player.board)
        print('Приветствую тебя, пользователь.')
        print('Для выстрела необходимо вводить координаты поля через пробел.')
        print('*' * 40)

    def is_last_move(self, player):
        '''инициирует ход игрока, отрисовывает поле и определяет был ли данный ход победным'''
        player.move()
        self.show_battlefield(self.user_player.board, self.ai_player.board)
        return Game.is_win(self.user_player.board, self.ai_player.board)

    def loop(self):
        '''случайным образом выбирает кто будет ходить первым и запускает основной цикл'''
        order = random.randint(0, 1)
        if order:
            first_player, second_player = self.user_player, self.ai_player
        else:
            first_player, second_player = self.ai_player, self.user_player
        while True:
            if self.is_last_move(first_player): break
            if self.is_last_move(second_player): break

    @staticmethod
    def random_board():
        '''генерирует доску с расставленными на ней случайным образом кораблями'''
        data = [
            [1, 3],
            [2, 2],
            [4, 1]
        ]
        while True:
            new_board = Board()
            try:
                for el in data:
                    for i in range(el[0]):
                        while True:
                            if len(new_board.forbidden) >= 36:
                                raise BadBoardException('Неудачная доска')
                            x = random.randint(1, 6)
                            y = random.randint(1, 6)
                            direction = random.choice(['V', 'H'])
                            new_ship = Ship(el[1], Dot(x, y), direction)
                            if new_board.add_ship(new_ship):
                                break
            except BadBoardException as e:
                pass
            else:
                return new_board

    @staticmethod
    def is_win(board_1, board_2):
        '''Проверяет равно ли количество подстрелянных клеток кораблей
        максимальному количеству клеток кораблей для каждой доски'''
        list_1 = []
        list_2 = []
        for i in board_1.board:
            list_1.extend(i)
        for i in board_2.board:
            list_2.extend(i)
        if list_1.count('\u2715') == 11:
            print('Победил противник.')
            return True
        if list_2.count('\u2715') == 11:
            print('Вы победили.')
            return True
        return False
