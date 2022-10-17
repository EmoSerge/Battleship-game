from random import randint


class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"XY({self.x}, {self.y})"


class OutOfRangeException(Exception):
    def __str__(self):
        return "Координаты вне игрового поля! "


class WrongInputException(Exception):
    def __str__(self):
        return "Координаты введены неверно! "


class ClosedException(Exception):
    def __str__(self):
        return "Данное поле занято! "


class WrongPositionException(Exception):
    pass


class Ship:
    def __init__(self, start, size, orient):
        self.start = start
        self.size = size
        self.orient = orient
        self.point = size

    @property
    def pos(self):
        ship_pos = []
        ship_x = self.start.x
        ship_y = self.start.y
        ship_pos.append(XY(ship_x, ship_y))
        for i in range(self.size - 1):

            if self.orient == 0:
                ship_y += 1

            elif self.orient == 1:
                ship_x += 1

            ship_pos.append(XY(ship_x, ship_y))
        return ship_pos

    def hit(self, aim):
        return aim in self.pos


class Field:
    def __init__(self, size=6, vision=True):
        self.size = size
        self.vision = vision
        self.number_ships = 0
        self.cage = [[" "]*size for i in range(size)]
        self.ships = []
        self.busy_fields = []
        self.move_fields = []

    def __str__(self):
        row = ""
        row += "   | Y0| Y1| Y2| Y3| Y4| Y5|"
        for i, j in enumerate(self.cage):
            row += f"\nX{i} | " + " | ".join(j) + " | "

            if not self.vision:
                row = row.replace("■", " ")
        return row

    def outofrange(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, open=False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for s in ship.pos:
            for dx, dy in near:
                sn = XY(s.x + dx, s.y + dy)
                if (not self.outofrange(sn)) and (sn not in self.busy_fields):
                    self.busy_fields.append(sn)
                    if open:
                        self.cage[sn.x][sn.y] = '◦'

    def add_ship(self, ship):
        for k in ship.pos:
            if self.outofrange(k) or (k in self.busy_fields):
                raise WrongPositionException()

        for k in ship.pos:
            self.cage[k.x][k.y] = "■"
            self.busy_fields.append(k)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, s):
        if self.outofrange(s):
            raise OutOfRangeException()

        if s in self.busy_fields:
            raise ClosedException()

        self.busy_fields.append(s)

        for ship in self.ships:
            if ship.hit(s):
                ship.point -= 1
                self.cage[s.x][s.y] = "X"
                if ship.point == 0:
                    self.number_ships -= 1
                    self.contour(ship, open=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.cage[s.x][s.y] = "◦"
        print("Мимо!")
        return False

    def clear(self):
        self.busy_fields = []

    def rnd_placement(self):
        boats = [3, 2, 2, 1, 1, 1, 1]
        self.number_ships = 0
        while self.number_ships != 7:
            attempts = 0
            for b in boats:
                while True:
                    attempts += 1
                    if attempts > 3000:
                        self.number_ships = 0
                        self.cage = [[" "]*self.size for i in range(self.size)]
                        self.ships = []
                        self.busy_fields = []
                        break
                    ship = Ship(XY(randint(0, 5), randint(0, 5)), b, randint(0, 1))
                    try:
                        self.add_ship(ship)
                        self.number_ships += 1
                        break
                    except WrongPositionException:
                        pass
        self.clear()


class Player:
    def __init__(self, userboard, enemy):
        self.userboard = userboard
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except OutOfRangeException as e:
                print(e)
            except ClosedException as r:
                print(r)


class Enemy(Player):
    def ask(self):
        a = XY(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: XY {a.x} {a.y}")
        return a


class User(Player):
    def ask(self):
        while True:
            hod = input(" Введите координаты вашего хода в форме X Y через пробел: ").split()

            if len(hod) != 2:
                print(" Не верный формат ввода! ")
                continue

            x, y = hod

            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            if not(0 <= x <= 5) or not(0 <= y <= 5):
                print(" Введены координаты вне поля, повторите ввод: ")
                continue

            return XY(x, y)


class Game:
    def __init__(self):
        pl = Field()
        pl.rnd_placement()
        co = Field(vision=False)
        co.rnd_placement()

        self.ai = Enemy(co, pl)
        self.us = User(pl, co)

    def loop(self):
        num = 0
        while True:
            print("-"*30)
            print("Ваша доска:")
            print(g.us.userboard)
            print("-"*30)
            print("Доска компьютера:")
            print(g.us.enemy)
            if num % 2 == 0:
                print("-"*30)
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.userboard.number_ships == 0:
                print("-"*30)
                print("Поздравляю, Вы выиграли!")
                print("-"*30)
                print("Доска компьютера:")
                print(g.us.enemy)
                break

            if self.us.userboard.number_ships == 0:
                print("-"*30)
                print("Компьютер выиграл!")
                print("-"*30)
                print("Ваша доска:")
                print(g.us.userboard)
                break
            num += 1


print("-"*30)
print("       Игра морской бой")
g = Game()
g.loop()
