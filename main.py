#Некоторые вещи помогал писать друг из-за занятости в жизни.

from random import choice


import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE,
)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 180, 0)
SCORE_COLOR = (255, 255, 255)

SPEED = 10

KEY_MAP = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}

screen = None


def draw_cell(position, color):
    """Рисует одну клетку поля с рамкой."""
    rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None):
        self.position = START_POSITION
        self.body_color = body_color

    def draw(self):
        """Отрисовка объекта. Реализуется в наследниках."""
        raise NotImplementedError(
            f'Метод draw() не реализован в {type(self).__name__}'
        )


class Apple(GameObject):
    """Яблоко: хранит только свою позицию на поле."""

    def __init__(self, occupied=()):
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied=()):
        """Ставит яблоко на случайную свободную клетку.

        Возвращает False, если свободных клеток не осталось.
        """
        blocked = set(occupied)
        free_cells = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in blocked
        ]
        if not free_cells:
            return False
        self.position = choice(free_cells)
        return True

    def draw(self):
        draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка: сегменты, движение, рост и столкновение с собой."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.reset()

    def update_direction(self):
        """Применяет направление, выбранное игроком."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну клетку, с переходом через край поля."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self):
        """Увеличивает длину на один сегмент."""
        self.length += 1

    def collided_with_self(self):
        """Проверяет, попала ли голова в тело змейки."""
        return self.get_head_position() in self.positions[1:]

    def get_head_position(self):
        """Возвращает координаты головы."""
        return self.positions[0]

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [START_POSITION]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None

    def draw(self):
        for position in self.positions[1:]:
            draw_cell(position, self.body_color)
        draw_cell(self.get_head_position(), SNAKE_HEAD_COLOR)


def handle_keys(snake):
    """Меняет направление. Разворот назад и остановка запрещены."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            raise SystemExit
        if event.type != pygame.KEYDOWN:
            continue
        new_direction = KEY_MAP.get(event.key)
        if new_direction and new_direction != OPPOSITE[snake.direction]:
            snake.next_direction = new_direction


def main():
    """Игровой цикл: ввод, обновление состояния, отрисовка."""
    global screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)

    snake = Snake()
    apple = Apple(snake.positions)
    score = 0

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            score += 1
            if not apple.randomize_position(snake.positions):
                snake.reset()
                apple.randomize_position(snake.positions)
                score = 0
        elif snake.collided_with_self():
            snake.reset()
            apple.randomize_position(snake.positions)
            score = 0

        pygame.display.set_caption(f'Змейка — счёт: {score}')
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        screen.blit(font.render(f'Счёт: {score}', True, SCORE_COLOR), (8, 6))
        pygame.display.update()


if __name__ == '__main__':
    main()
