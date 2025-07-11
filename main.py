import pygame
import sys
import time

pygame.init()

WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GR - 광클 레이싱")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 180, 0)

FPS = 60
clock = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 50)
BIG_FONT = pygame.font.SysFont(None, 100)

# 트랙 정보
TRACK_COUNT = 4
TRACK_HEIGHT = HEIGHT // TRACK_COUNT

# 차 정보
CAR_WIDTH, CAR_HEIGHT = 60, 40
START_X = 50

# 플레이어 키 매핑
player_keys = [pygame.K_q, pygame.K_p, pygame.K_z, pygame.K_m]
CAR_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

# 골 이펙트 관련 변수
FLASH_DURATION = 3  # 초
FLASH_INTERVAL = 0.2  # 깜빡이는 간격

background_img = pygame.image.load("./img/background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

car_images = []
car_image_files = ["./img/car_red.png", "./img/car_green.png", "./img/car_blue.png", "./img/car_yellow.png"]

for filename in car_image_files:
    img = pygame.image.load(filename).convert_alpha()
    
    # 비율 유지하며 CAR_HEIGHT에 맞춤
    original_width = img.get_width()
    original_height = img.get_height()
    scale_factor = CAR_HEIGHT / original_height
    new_width = int(original_width * scale_factor)
    new_height = CAR_HEIGHT
    
    # 크기 조정
    img = pygame.transform.smoothscale(img, (new_width, new_height))
    car_images.append(img)

def reset_game():
    global cars, winner, game_over, podium_show_time
    cars = []
    for i in range(TRACK_COUNT):
        track_y = TRACK_HEIGHT * (i + 1)
        car_y = track_y - CAR_HEIGHT
        # 이미지의 폭을 가져옴
        img_width = car_images[i].get_width()
        img_height = car_images[i].get_height()
        car = pygame.Rect(START_X, car_y, img_width, img_height)
        cars.append(car)
    winner = None
    game_over = False
    podium_show_time = None

def start_screen():
    start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 70)
    while True:
        WIN.fill(BLACK)
        title_surf = BIG_FONT.render("GR", True, WHITE)
        WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//3))

        # START 버튼
        pygame.draw.rect(WIN, GREEN, start_button_rect)
        start_text = FONT.render("START", True, WHITE)
        WIN.blit(start_text, (start_button_rect.centerx - start_text.get_width()//2,
                              start_button_rect.centery - start_text.get_height()//2))

        # 아래에 키 설명 텍스트 가로로 추가
        instruction_texts = [
            "P1: Q",
            "P2: P",
            "P3: Z",
            "P4: M"
        ]
        spacing = 40  # 각 텍스트 사이 간격
        total_width = 0
        text_surfs = []

        for text in instruction_texts:
            surf = FONT.render(text, True, WHITE)
            text_surfs.append(surf)
            total_width += surf.get_width() + spacing

        total_width -= spacing  # 마지막 간격 제거
        start_x = WIDTH // 2 - total_width // 2
        y = start_button_rect.bottom + 40

        for surf in text_surfs:
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

def show_podium_screen():
    # 순위에 따라 색상 인덱스 정렬
    ranked_cars = sorted(enumerate(cars), key=lambda x: -x[1].x)
    rankings = [index for index, _ in ranked_cars]  # 플레이어 인덱스 순위

    while True:
        WIN.fill(BLACK)

        # 안내 문구 - 상단에서 살짝 여백 두고
        info_text = FONT.render("Press R to Restart", True, WHITE)
        WIN.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 80))

        # 단상 크기 키우기
        podium_width = 120
        podium_heights = {
            1: 240,
            2: 180,
            3: 120,
            4: 0
        }

        total_podiums = 4
        total_width = podium_width * total_podiums
        start_x = WIDTH // 2 - total_width // 2
        base_y = HEIGHT * 4 // 5

        draw_order = [3, 1, 2, 4]

        for i, rank in enumerate(draw_order):
            if rank > len(rankings):
                continue

            player_idx = rankings[rank - 1]
            img = car_images[player_idx]  # 자동차 이미지
            img_width = img.get_width()
            img_height = img.get_height()
            height = podium_heights[rank]

            x = start_x + i * podium_width
            y = base_y - height

            # 단상
            if height > 0:
                pygame.draw.rect(WIN, GRAY, (x, y, podium_width, height))

            # 자동차 이미지 (단상 위 중앙에 배치)
            img_x = x + (podium_width // 2) - (img_width // 2)
            img_y = y - img_height
            WIN.blit(img, (img_x, img_y))

            # 순위 숫자
            place_text = FONT.render(f"{rank}", True, BLACK)
            WIN.blit(place_text, (x + podium_width // 2 - place_text.get_width() // 2, y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
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
    finish_line_x = WIDTH - 100
    finish_line = pygame.Rect(finish_line_x, 0, 20, HEIGHT)

    for num in ["3", "2", "1"]:
        start_time = time.time()
        while time.time() - start_time < 1:  # 1초 동안 루프
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # 키나 마우스 이벤트 무시 (이벤트만 처리해서 쌓이지 않도록)

            WIN.blit(background_img, (0, 0))

            for i in range(TRACK_COUNT):
                y = TRACK_HEIGHT * (i + 1)
                pygame.draw.line(WIN, GRAY, (0, y), (WIDTH, y), 4)

            for idx, car in enumerate(cars):
                WIN.blit(car_images[idx], (car.x, car.y))

            pygame.draw.rect(WIN, WHITE, finish_line)

            blurred = blur_current_screen()
            WIN.blit(blurred, (0, 0))

            count_text = BIG_FONT.render(num, True, WHITE)
            WIN.blit(count_text, (
                WIDTH // 2 - count_text.get_width() // 2,
                HEIGHT // 2 - count_text.get_height() // 2)
            )

            pygame.display.update()
            clock.tick(FPS)

def game_loop():
    reset_game()
    finish_line_x = WIDTH - 100
    finish_line = pygame.Rect(finish_line_x, 0, 20, HEIGHT)

    global game_over, winner, podium_show_time

    countdown()

    game_started = False
    flash_start_time = None

    start_time = time.time()

    while True:
        clock.tick(FPS)
        WIN.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 카운트다운 끝나고 0.3초 후에 게임 시작 상태로 변경
            if not game_started:
                if time.time() - start_time > 0.3:
                    game_started = True

            if event.type == pygame.KEYDOWN and game_started and not game_over:
                for idx, key in enumerate(player_keys):
                    if event.key == key:
                        cars[idx].x += 10
                        if cars[idx].right >= finish_line_x:
                            winner = idx + 1
                            game_over = True
                            podium_show_time = time.time()
                            flash_start_time = time.time()

        # 트랙 그리기
        for i in range(TRACK_COUNT):
            y = TRACK_HEIGHT * (i + 1)
            pygame.draw.line(WIN, GRAY, (0, y), (WIDTH, y), 4)

        # 차량 그리기
        for idx, car in enumerate(cars):
            WIN.blit(car_images[idx], (car.x, car.y))

            # 골 이펙트: 골인한 자동차에 흰색 테두리 반짝임
            if game_over and (idx + 1) == winner:
                if flash_start_time and time.time() - flash_start_time < FLASH_DURATION:
                    if int((time.time() - flash_start_time) / FLASH_INTERVAL) % 2 == 0:
                        pygame.draw.rect(WIN, WHITE, car, 4)  # 흰색 테두리

        # 골라인 그리기
        pygame.draw.rect(WIN, WHITE, finish_line)
        car_img_width = car_images[idx].get_width()
        if cars[idx].x + car_img_width >= finish_line_x:
            winner = idx + 1
            game_over = True
            podium_show_time = time.time()

        if game_over:
            if winner is not None:
                winner_color = CAR_COLORS[winner - 1]
                text = FONT.render(f"Player {winner} Wins!", True, winner_color)
                WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

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
