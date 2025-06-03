import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

TILE_SIZE = 20

MAZE = [
    [1]*30,
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1,0,1,1,0,1,0,1],
    [1,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
    [1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1]*30
]


GRID_HEIGHT = len(MAZE)
GRID_WIDTH = len(MAZE[0])


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добро пожаловать в Pac-Man!")
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()
        self.start_button = QPushButton("Старт")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_game)
        layout.addStretch()
        layout.addWidget(self.start_button)
        layout.addStretch()
        self.setLayout(layout)

    def start_game(self):
        self.hide()
        self.game = PacManGame()
        self.game.show()


class PacManGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pac-Man с паузой и перезапуском")
        self.setGeometry(100, 100, TILE_SIZE * GRID_WIDTH, TILE_SIZE * GRID_HEIGHT)
        self.init_game()
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(150)

    def init_game(self):
        self.pacman_x = 1
        self.pacman_y = 1
        self.direction = Qt.Key_Right
        self.paused = False
        self.game_over = False

        self.food = {(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if MAZE[y][x] == 0}

        self.ghosts = [
            {'x': 28, 'y': 1, 'dir': Qt.Key_Left},
            {'x': 28, 'y': 13, 'dir': Qt.Key_Up}
        ]

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            self.direction = event.key()
        elif event.key() == Qt.Key_Space:
            self.paused = not self.paused
            self.setWindowTitle("Пауза" if self.paused else "Pac-Man с паузой и перезапуском")
        elif event.key() == Qt.Key_R:
            self.init_game()
            self.timer.start(150)
            self.setWindowTitle("Pac-Man с паузой и перезапуском")

    def can_move(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and MAZE[y][x] == 0

    def move_entity(self, x, y, direction):
        nx, ny = x, y
        if direction == Qt.Key_Up:
            ny -= 1
        elif direction == Qt.Key_Down:
            ny += 1
        elif direction == Qt.Key_Left:
            nx -= 1
        elif direction == Qt.Key_Right:
            nx += 1
        if self.can_move(nx, ny):
            return nx, ny
        return x, y

    def game_loop(self):
        if self.paused or self.game_over:
            return

        self.pacman_x, self.pacman_y = self.move_entity(self.pacman_x, self.pacman_y, self.direction)
        self.food.discard((self.pacman_x, self.pacman_y))

        for ghost in self.ghosts:
            if random.random() < 0.3:
                ghost['dir'] = random.choice([Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right])
            ghost['x'], ghost['y'] = self.move_entity(ghost['x'], ghost['y'], ghost['dir'])

            if ghost['x'] == self.pacman_x and ghost['y'] == self.pacman_y:
                self.timer.stop()
                self.setWindowTitle("Game Over! Нажми R для рестарта")
                self.game_over = True

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor(50, 50, 50))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if MAZE[y][x] == 1:
                    painter.drawRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        painter.setBrush(QColor(255, 0, 0))
        for x, y in self.food:
            painter.drawEllipse(x * TILE_SIZE + TILE_SIZE // 3, y * TILE_SIZE + TILE_SIZE // 3, TILE_SIZE // 4, TILE_SIZE // 4)

        painter.setBrush(QColor(255, 255, 0))
        painter.drawEllipse(self.pacman_x * TILE_SIZE, self.pacman_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        painter.setBrush(QColor(0, 0, 255))
        for ghost in self.ghosts:
            painter.drawRect(ghost['x'] * TILE_SIZE, ghost['y'] * TILE_SIZE, TILE_SIZE, TILE_SIZE)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec_())
