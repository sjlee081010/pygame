import pygame
import sys
import time
import random

pygame.init()

# 트랙 길이 (픽셀)
TRACK_LENGTH = 1500

# 화면 크기
WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GR - 광클 레이싱 with 아이템")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (255, 0, 0)

FPS = 60
clock = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 30)
BIG_FONT = pygame.font.SysFont(None, 100)

# 트랙 정보
TRACK_COUNT = 4
TRACK_HEIGHT = HEIGHT // TRACK_COUNT

# 차 정보
CAR_HEIGHT = 40
START_X = 50

# 플레이어 키 매핑
player_keys = [pygame.K_q, pygame.K_p, pygame.K_z, pygame.K_m]
CAR_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

# 골 이펙트 변수
FLASH_DURATION = 3
FLASH_INTERVAL = 0.2

# 카메라 변수
camera_x = 0
camera_speed = 0.15  # 부드러운 이동 속도 조절 가능

# 아이템 설정
ITEM_NAMES = ["Bomb", "Booster", "Shell", "Ice"]
ITEM_BOX_SIZE = 30

# 아이템 이미지 불러오기 (파일명 맞게 경로 조정 필요)
item_images = {
    "Bomb": pygame.transform.scale(pygame.image.load("assets/bomb.jpg"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
    "Booster": pygame.transform.scale(pygame.image.load("assets/booster.png"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
    "Shell": pygame.transform.scale(pygame.image.load("assets/shell.png"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
    "Ice": pygame.transform.scale(pygame.image.load("assets/ice.jpg"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
}

# 이미지 로딩 및 크기 조정
background_img = pygame.image.load("./img/background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

car_images = []
car_image_files = ["./img/car_red.png", "./img/car_green.png", "./img/car_blue.png", "./img/car_yellow.png"]

for filename in car_image_files:
    img = pygame.image.load(filename).convert_alpha()
    original_width = img.get_width()
    original_height = img.get_height()
    scale_factor = CAR_HEIGHT / original_height
    new_width = int(original_width * scale_factor)
    new_height = CAR_HEIGHT
    img = pygame.transform.smoothscale(img, (new_width, new_height))
    car_images.append(img)

# Item 클래스 정의
class Item:
    def __init__(self, name):
        self.name = name

    def activate(self, user_idx, players):
        player_count = len(players)

        if self.name == "Bomb":
            target_idx = (user_idx + 1) % player_count
            players[target_idx]["stun"] = FPS * 2  # 2초 기절

        elif self.name == "Booster":
            players[user_idx]["boost"] = FPS * 2  # 2초 부스터

        elif self.name == "Shell":
            leading_idx = max(range(player_count), key=lambda i: players[i]["rect"].x)
            if leading_idx != user_idx:
                players[leading_idx]["stun"] = FPS * 2

        elif self.name == "Ice":
            for i in range(player_count):
                if i != user_idx:
                    players[i]["stun"] = FPS * 1  # 1초 기절

def reset_game():
    global cars, winner, game_over, podium_show_time, flash_start_time, camera_x, players, item_boxes
    cars = []
    players = []
    item_boxes = []

    for i in range(TRACK_COUNT):
        track_y = TRACK_HEIGHT * (i + 1)
        car_y = track_y - CAR_HEIGHT
        img_width = car_images[i].get_width()
        img_height = car_images[i].get_height()
        car = pygame.Rect(START_X, car_y, img_width, img_height)
        cars.append(car)

        # 플레이어 상태 초기화
        players.append({
            "rect": car,
            "stun": 0,
            "boost": 0,
            "color": CAR_COLORS[i]
        })

    winner = None
    game_over = False
    podium_show_time = None
    flash_start_time = None
    camera_x = 0

    # 아이템 박스 생성 (랜덤 위치)
    for i in range(TRACK_COUNT):
        x = random.randint(300, 600)
        y = TRACK_HEIGHT * (i + 1) - ITEM_BOX_SIZE
        item_name = random.choice(ITEM_NAMES)
        box_rect = pygame.Rect(x, y, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        item_boxes.append({
            "rect": box_rect,
            "name": item_name
        })

def start_screen():
    start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 70)
    while True:
        WIN.fill(BLACK)
        title_surf = BIG_FONT.render("GR", True, WHITE)
        WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//3))

        pygame.draw.rect(WIN, GREEN, start_button_rect)
        start_text = FONT.render("START", True, WHITE)
        WIN.blit(start_text, (start_button_rect.centerx - start_text.get_width()//2,
                              start_button_rect.centery - start_text.get_height()//2))

        instruction_texts = ["P1: Q", "P2: P", "P3: Z", "P4: M"]
        spacing = 40
        total_width = sum(FONT.render(text, True, WHITE).get_width() + spacing for text in instruction_texts) - spacing
        start_x = WIDTH // 2 - total_width // 2
        y = start_button_rect.bottom + 40
        for text in instruction_texts:
            surf = FONT.render(text, True, WHITE)
            WIN.blit(surf, (start_x, y))
            start_x += surf.get_width() + spacing

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(30)

def blur_current_screen(scale_factor=0.1):
    screen_copy = WIN.copy()
    small = pygame.transform.smoothscale(screen_copy,
                (int(WIDTH * scale_factor), int(HEIGHT * scale_factor)))
    blurred = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
    return blurred

def countdown():
    finish_line_x = START_X + TRACK_LENGTH
    finish_line = pygame.Rect(finish_line_x, 0, 20, HEIGHT)

    for num in ["3", "2", "1"]:
        start_time = time.time()
        while time.time() - start_time < 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            WIN.blit(background_img, (0, 0))

            for i in range(TRACK_COUNT):
                y = TRACK_HEIGHT * (i + 1)
                pygame.draw.line(WIN, GRAY, (0 - camera_x, y), (TRACK_LENGTH + START_X + 100 - camera_x, y), 4)

            for idx, car in enumerate(cars):
                WIN.blit(car_images[idx], (cars[idx].x - camera_x, cars[idx].y))

            pygame.draw.rect(WIN, WHITE, finish_line.move(-camera_x, 0))

            blurred = blur_current_screen()
            WIN.blit(blurred, (0, 0))

            count_text = BIG_FONT.render(num, True, WHITE)
            WIN.blit(count_text, (
                WIDTH // 2 - count_text.get_width() // 2,
                HEIGHT // 2 - count_text.get_height() // 2)
            )

            pygame.display.update()
            clock.tick(FPS)

def show_podium_screen():
    ranked_cars = sorted(enumerate(cars), key=lambda x: -x[1].x)
    rankings = [index for index, _ in ranked_cars]

    while True:
        WIN.fill(BLACK)
        info_text = FONT.render("Press R to Restart", True, WHITE)
        WIN.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 80))

        podium_width = 120
        podium_heights = {1: 240, 2: 180, 3: 120, 4: 0}
        total_podiums = 4
        total_width = podium_width * total_podiums
        start_x = WIDTH // 2 - total_width // 2
        base_y = HEIGHT * 4 // 5

        draw_order = [3, 1, 2, 4]

        for i, rank in enumerate(draw_order):
            if rank > len(rankings):
                continue

            player_idx = rankings[rank - 1]
            img = car_images[player_idx]
            img_width = img.get_width()
            img_height = img.get_height()
            height = podium_heights[rank]

            x = start_x + i * podium_width
            y = base_y - height

            if height > 0:
                pygame.draw.rect(WIN, GRAY, (x, y, podium_width, height))

            img_x = x + (podium_width // 2) - (img_width // 2)
            img_y = y - img_height
            WIN.blit(img, (img_x, img_y))

            place_text = FONT.render(f"{rank}", True, BLACK)
            WIN.blit(place_text, (x + podium_width // 2 - place_text.get_width() // 2, y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return

        pygame.display.update()
        clock.tick(30)

def game_loop():
    reset_game()
    finish_line_x = START_X + TRACK_LENGTH
    finish_line = pygame.Rect(finish_line_x, 0, 20, HEIGHT)

    global game_over, winner, podium_show_time, flash_start_time, camera_x

    countdown()

    game_started = False
    start_time = time.time()

    while True:
        clock.tick(FPS)
        WIN.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_started:
                if time.time() - start_time > 0.3:
                    game_started = True

            if event.type == pygame.KEYDOWN and game_started and not game_over:
                for idx, key in enumerate(player_keys):
                    p = players[idx]
                    if event.key == key:
                        # 기절 상태면 움직이지 않음
                        if p["stun"] == 0:
                            speed = 10 * (2 if p["boost"] > 0 else 1)
                            cars[idx].x += speed
                            if cars[idx].right >= finish_line_x:
                                winner = idx + 1
                                game_over = True
                                podium_show_time = time.time()
                                flash_start_time = time.time()

        # 상태 업데이트 (기절, 부스터 카운트다운)
        for p in players:
            if p["stun"] > 0:
                p["stun"] -= 1
            if p["boost"] > 0:
                p["boost"] -= 1

        # 아이템 충돌 체크 및 자동 발동
        for idx, p in enumerate(players):
            for box in item_boxes:
                if p["rect"].colliderect(box["rect"]):
                    item = Item(box["name"])
                    print(f"Player {idx+1} item: {box['name']}")
                    item.activate(idx, players)
                    item_boxes.remove(box)
                    break  # 한 프레임에 여러 아이템 획득 방지

        # 카메라 위치 계산
        leading_car_x = max(car.x for car in cars)
        target_camera_x = leading_car_x - WIDTH // 2 + car_images[0].get_width() // 2

        # 카메라 x값 제한
        camera_x = max(0, min(camera_x + (target_camera_x - camera_x) * camera_speed, finish_line_x + 20 - WIDTH))

        # 트랙 그리기
        for i in range(TRACK_COUNT):
            y = TRACK_HEIGHT * (i + 1)
            pygame.draw.line(WIN, GRAY, (0 - camera_x, y), (TRACK_LENGTH + START_X + 100 - camera_x, y), 4)

        # 차량 그리기 및 이펙트
        for idx, car in enumerate(cars):
            WIN.blit(car_images[idx], (car.x - camera_x, car.y))

            if game_over and (idx + 1) == winner:
                if flash_start_time and time.time() - flash_start_time < FLASH_DURATION:
                    if int((time.time() - flash_start_time) / FLASH_INTERVAL) % 2 == 0:
                        car_rect = pygame.Rect(car.x - camera_x, car.y, car.width, car.height)
                        pygame.draw.rect(WIN, WHITE, car_rect, 4)

            # 화면 왼쪽 바깥쪽에 있으면 인디케이터 표시
            if car.x - camera_x + car.width < 0:
                indicator_x = 10
                indicator_y = car.y + car.height // 2
                player_num_surf = SMALL_FONT.render(str(idx + 1), True, WHITE)
                padding = 5
                rect_width = player_num_surf.get_width() + 2 * padding
                rect_height = player_num_surf.get_height() + 2 * padding
                rect = pygame.Rect(indicator_x, indicator_y - rect_height // 2, rect_width, rect_height)
                pygame.draw.rect(WIN, CAR_COLORS[idx], rect, border_radius=5)
                WIN.blit(player_num_surf, (rect.centerx - player_num_surf.get_width() // 2,
                                           rect.centery - player_num_surf.get_height() // 2))

        # 아이템 박스 그리기
        for box in item_boxes:
            img = item_images[box["name"]]
            WIN.blit(img, (box["rect"].x - camera_x, box["rect"].y))

        # 골라인 그리기
        pygame.draw.rect(WIN, WHITE, finish_line.move(-camera_x, 0))

        if game_over:
            if winner is not None:
                winner_color = CAR_COLORS[winner - 1]
                win_text = FONT.render(f"Player {winner} Wins!", True, winner_color)
                WIN.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2))

            if podium_show_time and (time.time() - podium_show_time > 3):
                show_podium_screen()
                return

        pygame.display.update()

def main():
    while True:
        start_screen()
        game_loop()

if __name__ == "__main__":
    main()
