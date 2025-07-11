import pygame
import sys

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("광클 레이싱")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# FPS 설정
FPS = 60
clock = pygame.time.Clock()

# 트랙 정보
TRACK_COUNT = 4
TRACK_HEIGHT = HEIGHT // TRACK_COUNT

# 차 정보
CAR_WIDTH, CAR_HEIGHT = 60, 40
START_X = 50

# 플레이어 키 매핑
player_keys = [pygame.K_d, pygame.K_k, pygame.K_RIGHT, pygame.K_l]
CAR_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

# 차량 이미지 로드 (나중에 이미지 경로 추가)
# car_images = [pygame.image.load("car1.png"), pygame.image.load("car2.png"), ...]
# 이미지 크기 조정 예시:
# car_images = [pygame.transform.scale(img, (CAR_WIDTH, CAR_HEIGHT)) for img in car_images]

def reset_game():
    global cars, winner, game_over
    cars = []
    for i in range(TRACK_COUNT):
        # 트랙 바로 위에 플레이어 배치
        track_y = TRACK_HEIGHT * (i + 1)
        car_y = track_y - CAR_HEIGHT  # 차가 트랙 라인 위에 닿도록 배치
        car = pygame.Rect(START_X, car_y, CAR_WIDTH, CAR_HEIGHT)
        cars.append(car)
    winner = None
    game_over = False

reset_game()

# 골라인
FINISH_LINE_X = WIDTH - 100
finish_line = pygame.Rect(FINISH_LINE_X, 0, 20, HEIGHT)

# 메인 루프
running = True
while running:
    clock.tick(FPS)
    WIN.fill(WHITE)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 키 입력 처리 (광클 방식)
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
            else:
                for idx, key in enumerate(player_keys):
                    if event.key == key:
                        cars[idx].x += 10
                        # 승리 판정
                        if cars[idx].right >= FINISH_LINE_X:
                            winner = idx + 1
                            game_over = True

    # 트랙 그리기
    for i in range(TRACK_COUNT):
        y = TRACK_HEIGHT * (i + 1)
        pygame.draw.line(WIN, GRAY, (0, y), (WIDTH, y), 4)

    # 차량 그리기
    for idx, car in enumerate(cars):
        # 나중에 이미지로 대체
        # WIN.blit(car_images[idx], (car.x, car.y))
        pygame.draw.rect(WIN, CAR_COLORS[idx], car)

    # 골라인 그리기
    pygame.draw.rect(WIN, BLACK, finish_line)

    # 승자 표시
    if game_over:
        font = pygame.font.SysFont(None, 60)
        text = font.render(f"Player {winner} Wins! Press R to Restart", True, RED)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    pygame.display.update()

pygame.quit()
sys.exit()
