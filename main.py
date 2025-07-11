import pygame
import sys
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
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
player_keys = [pygame.K_d, pygame.K_k, pygame.K_RIGHT, pygame.K_l]
CAR_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

def reset_game():
    global cars, winner, game_over, podium_show_time
    cars = []
    for i in range(TRACK_COUNT):
        track_y = TRACK_HEIGHT * (i + 1)
        car_y = track_y - CAR_HEIGHT
        car = pygame.Rect(START_X, car_y, CAR_WIDTH, CAR_HEIGHT)
        cars.append(car)
    winner = None
    game_over = False
    podium_show_time = None  # 단상화면 전환 시간 초기화

def start_screen():
    start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 70)
    while True:
        WIN.fill(WHITE)
        title_surf = BIG_FONT.render("GR", True, BLACK)
        WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//3))

        pygame.draw.rect(WIN, GREEN, start_button_rect)
        start_text = FONT.render("START", True, WHITE)
        WIN.blit(start_text, (start_button_rect.centerx - start_text.get_width()//2,
                              start_button_rect.centery - start_text.get_height()//2))

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
    # 순위에 따라 색상 인덱스 정렬 (먼저 도착한 순서대로)
    ranked_cars = sorted(enumerate(cars), key=lambda x: -x[1].x)
    rankings = [index for index, _ in ranked_cars]  # 플레이어 인덱스 순위

    while True:
        WIN.fill(BLACK)

        # 안내 문구
        info_text = FONT.render("Press R to Restart", True, WHITE)
        WIN.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 20))

        # 단상 설정
        podium_width = 100
        podium_heights = {
            1: 200,  # 1등
            2: 150,  # 2등
            3: 100,  # 3등
            4: 0     # 4등 (바닥)
        }

        # 단상 위치: 4개를 나란히 정렬 (간격 없이)
        total_podiums = 4
        total_width = podium_width * total_podiums
        start_x = WIDTH // 2 - total_width // 2
        base_y = HEIGHT * 3 // 4  # 화면 중간과 하단 사이

        # 각 순위 위치 지정 (왼쪽부터: 3등, 1등, 2등, 4등)
        draw_order = [3, 1, 2, 4]  # 표시할 등수 순서

        for i, rank in enumerate(draw_order):
            if rank > len(rankings):
                continue  # 참가자 수보다 많은 경우 무시

            player_idx = rankings[rank - 1]
            color = CAR_COLORS[player_idx]
            height = podium_heights[rank]

            x = start_x + i * podium_width
            y = base_y - height

            # 단상 그리기 (높이 0이면 안 그려짐)
            if height > 0:
                pygame.draw.rect(WIN, GRAY, (x, y, podium_width, height))

            # 색상 박스 (자동차 색)
            pygame.draw.rect(WIN, color, (x + 20, y - 40, 60, 40))

            # 순위 숫자 표시
            place_text = FONT.render(str(rank), True, BLACK)
            WIN.blit(place_text, (x + podium_width // 2 - place_text.get_width() // 2, y + 10))

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return

        pygame.display.update()
        clock.tick(30)


def game_loop():
    reset_game()
    finish_line_x = WIDTH - 100
    finish_line = pygame.Rect(finish_line_x, 0, 20, HEIGHT)

    global game_over, winner, podium_show_time

    while True:
        clock.tick(FPS)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and not game_over:
                for idx, key in enumerate(player_keys):
                    if event.key == key:
                        cars[idx].x += 10
                        if cars[idx].right >= finish_line_x:
                            winner = idx + 1
                            game_over = True
                            podium_show_time = time.time()  # 골인 시간 기록

        # 트랙 그리기
        for i in range(TRACK_COUNT):
            y = TRACK_HEIGHT * (i + 1)
            pygame.draw.line(WIN, GRAY, (0, y), (WIDTH, y), 4)

        # 차량 그리기
        for idx, car in enumerate(cars):
            pygame.draw.rect(WIN, CAR_COLORS[idx], car)

        # 골라인 그리기
        pygame.draw.rect(WIN, WHITE, finish_line)

        if game_over:
            font = pygame.font.SysFont(None, 60)
            text = font.render(f"Player {winner} Wins!", True, RED)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

            # 단상 화면 3초 후 전환
            if podium_show_time and (time.time() - podium_show_time > 3):
                show_podium_screen()
                return  # 단상 화면 종료 후 다시 시작 화면으로 돌아감

        pygame.display.update()

def main():
    while True:
        start_screen()
        game_loop()

if __name__ == "__main__":
    main()
