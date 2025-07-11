import pygame
import sys
import random
from item import Item
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("광클 레이싱 with 아이템")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# FPS
FPS = 60
clock = pygame.time.Clock()

# 트랙 설정
TRACK_COUNT = 4
TRACK_HEIGHT = HEIGHT // TRACK_COUNT

# 차량 설정
CAR_WIDTH, CAR_HEIGHT = 60, 40
START_X = 50
FINISH_LINE_X = WIDTH - 100

# 플레이어 설정
player_keys = [pygame.K_d, pygame.K_k, pygame.K_RIGHT, pygame.K_l]
CAR_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

# 아이템 설정
ITEM_NAMES = ["Bomb", "Booster", "Shell", "Ice"]
ITEM_BOX_SIZE = 30

# 아이템 이미지 불러오기
item_images = {
    "Bomb": pygame.transform.scale(pygame.image.load("assets/bomb.jpg"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
    "Booster": pygame.transform.scale(pygame.image.load("assets/booster.png"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
    "Shell": pygame.transform.scale(pygame.image.load("assets/shell.png"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
    "Ice": pygame.transform.scale(pygame.image.load("assets/ice.jpg"), (ITEM_BOX_SIZE, ITEM_BOX_SIZE)),
}

# 게임 초기화 함수
def reset_game():
    global players, winner, game_over, item_boxes
    players = []
    for i in range(TRACK_COUNT):
        y = TRACK_HEIGHT * (i + 1) - CAR_HEIGHT
        car_rect = pygame.Rect(START_X, y, CAR_WIDTH, CAR_HEIGHT)
        players.append({
            "rect": car_rect,
            "color": CAR_COLORS[i],
            "stun": 0,
            "boost": 0
        })
    winner = None
    game_over = False

    # 아이템 박스 생성
    item_boxes = []
    for i in range(TRACK_COUNT):
        x = random.randint(300, 600)
        y = TRACK_HEIGHT * (i + 1) - ITEM_BOX_SIZE
        item_name = random.choice(ITEM_NAMES)
        box_rect = pygame.Rect(x, y, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        item_boxes.append({
            "rect": box_rect,
            "name": item_name
        })

reset_game()

# 골라인
finish_line = pygame.Rect(FINISH_LINE_X, 0, 20, HEIGHT)

# 게임 루프
running = True
while running:
    clock.tick(FPS)
    WIN.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                reset_game()
            elif not game_over:
                for idx, key in enumerate(player_keys):
                    p = players[idx]
                    if event.key == key and p["stun"] == 0:
                        speed = 10 * (2 if p["boost"] > 0 else 1)
                        p["rect"].x += speed
                        if p["rect"].right >= FINISH_LINE_X:
                            winner = idx + 1
                            game_over = True

    # 상태 업데이트
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
                print(f"Player {idx+1} 아이템 획득: {box['name']}")
                item.activate(idx, players)
                item_boxes.remove(box)
                break

    # 트랙 그리기
    for i in range(TRACK_COUNT):
        y = TRACK_HEIGHT * (i + 1)
        pygame.draw.line(WIN, GRAY, (0, y), (WIDTH, y), 4)

    # 차량 그리기
    for p in players:
        pygame.draw.rect(WIN, p["color"], p["rect"])
        if p["stun"] > 0:
            pygame.draw.rect(WIN, RED, p["rect"], 4)  # stun일 때 빨간 테두리

    # 아이템 박스 그리기
    for box in item_boxes:
        img = item_images[box["name"]]
        WIN.blit(img, box["rect"].topleft)

    # 골라인
    pygame.draw.rect(WIN, BLACK, finish_line)

    # 승자 메시지
    if game_over:
        font = pygame.font.SysFont(None, 60)
        text = font.render(f"Player {winner} Wins! Press R to Restart", True, RED)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    pygame.display.update()

pygame.quit()
sys.exit()
