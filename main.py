import pygame
import sys
import time

pygame.init()

# --- NEW: Define Track Length ---
TRACK_LENGTH = 1500  # You can adjust this value for desired track length

# Calculate WIDTH based on track length for full visibility, or keep it fixed
# If you want the window to dynamically fit the track, uncomment the next line:
# WIDTH, HEIGHT = TRACK_LENGTH + 200, 600 # Add some padding
WIDTH, HEIGHT = 800, 600 # Keeping original width for demonstration; scrolling might be needed for longer tracks

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GR - 광클 레이싱")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0) # For indicator if needed

FPS = 60
clock = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 30) # New font for indicators
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

# 골 이펙트 관련 변수
FLASH_DURATION = 3  # 초
FLASH_INTERVAL = 0.2  # 깜빡이는 간격

# --- Camera/Scrolling variables ---
camera_x = 0
camera_speed = 0.5 # Adjust camera scroll speed

def reset_game():
    global cars, winner, game_over, podium_show_time, flash_start_time, camera_x
    cars = []
    for i in range(TRACK_COUNT):
        track_y = TRACK_HEIGHT * (i + 1)
        car_y = track_y - CAR_HEIGHT
        car = pygame.Rect(START_X, car_y, CAR_WIDTH, CAR_HEIGHT)
        cars.append(car)
    winner = None
    game_over = False
    podium_show_time = None
    flash_start_time = None  # 반짝이기 시간 초기화
    camera_x = 0 # Reset camera position on new game

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
    # Sort cars by their final x-position to determine rank
    ranked_cars = sorted(enumerate(cars), key=lambda x: -x[1].x)
    rankings = [index for index, _ in ranked_cars]

    while True:
        WIN.fill(BLACK)
        info_text = FONT.render("Press R to Restart", True, WHITE)
        WIN.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 20))

        podium_width = 100
        podium_heights = {1: 200, 2: 150, 3: 100, 4: 0} # Heights for 1st, 2nd, 3rd, 4th (4th is ground level)
        total_podiums = TRACK_COUNT
        total_width = podium_width * total_podiums
        start_x = WIDTH // 2 - total_width // 2
        base_y = HEIGHT * 3 // 4

        # Drawing order for podium, 1st in middle, 2nd left, 3rd right
        # Adjust this order if you have more than 4 players, or want a different look
        draw_order = [3, 1, 2, 4] # Assuming 4 players

        for i, rank in enumerate(draw_order):
            if rank > len(rankings): # Handle cases with fewer players than TRACK_COUNT
                continue
            player_idx = rankings[rank - 1] # Get original player index from rank
            color = CAR_COLORS[player_idx]
            height = podium_heights.get(rank, 0) # Get height for rank, default to 0 for ranks > 3
            x = start_x + i * podium_width
            y = base_y - height

            # Draw podium block
            if height > 0:
                pygame.draw.rect(WIN, GRAY, (x, y, podium_width, height))
            
            # Draw car on podium (adjusted position)
            pygame.draw.rect(WIN, color, (x + (podium_width - CAR_WIDTH)//2, y - CAR_HEIGHT, CAR_WIDTH, CAR_HEIGHT))
            
            # Draw rank number
            place_text = FONT.render(str(rank), True, BLACK)
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

def game_loop():
    reset_game()
    # --- MODIFIED: Finish line based on TRACK_LENGTH ---
    finish_line_x = START_X + TRACK_LENGTH
    finish_line = pygame.Rect(finish_line_x, 0, 20, HEIGHT)

    global game_over, winner, podium_show_time, flash_start_time, camera_x

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
                            podium_show_time = time.time()
                            flash_start_time = time.time()

        # --- Camera/Scrolling Logic ---
        # Find the leading car
        leading_car_x = 0
        if cars:
            leading_car_x = max(car.x for car in cars)
        
        # Adjust camera to follow the leading car, but don't scroll past the start or end of the track
        target_camera_x = leading_car_x - WIDTH // 2 + CAR_WIDTH // 2
        
        # Ensure camera doesn't go too far left (past 0)
        camera_x = max(0, camera_x)
        
        # Ensure camera doesn't go too far right (past the end of the track)
        # The maximum scrollable position is when the right edge of the window aligns with the finish line
        # minus the window width, plus some padding (e.g., 100 for the finish line width itself)
        max_camera_x = max(0, finish_line_x + finish_line.width - WIDTH)
        
        # Only update camera_x if game is not over
        if not game_over:
            # Smoothly move camera towards target
            camera_x += (target_camera_x - camera_x) * camera_speed
            camera_x = min(camera_x, max_camera_x) # Clamp camera to max scroll
            
        # Draw elements relative to the camera
        
        # 트랙 그리기
        for i in range(TRACK_COUNT):
            y = TRACK_HEIGHT * (i + 1)
            pygame.draw.line(WIN, GRAY, (0 - camera_x, y), (TRACK_LENGTH + START_X + 100 - camera_x, y), 4) # Extend line draw

        # 차량 그리기
        for idx, car in enumerate(cars):
            # Draw car at its actual position minus camera_x
            current_car_x_on_screen = car.x - camera_x
            pygame.draw.rect(WIN, CAR_COLORS[idx], car.move(-camera_x, 0))

            # 골 이펙트: 골인한 자동차에 흰색 테두리 반짝임
            if game_over and (idx + 1) == winner:
                if flash_start_time and time.time() - flash_start_time < FLASH_DURATION:
                    if int((time.time() - flash_start_time) / FLASH_INTERVAL) % 2 == 0:
                        pygame.draw.rect(WIN, WHITE, car.move(-camera_x, 0), 4)  # 흰색 테두리

            # --- Trailing Player Indicator ---
            # If a car is off-screen to the left, draw an indicator
            if current_car_x_on_screen + CAR_WIDTH < 0: # Car is completely off-screen to the left
                indicator_x = 10 # Position of the indicator on the left edge
                indicator_y = car.y + CAR_HEIGHT // 2 # Center vertically on the car's track
                
                # Draw a simple circle or triangle indicator
                # pygame.draw.circle(WIN, CAR_COLORS[idx], (indicator_x, indicator_y), 15)
                # pygame.draw.polygon(WIN, CAR_COLORS[idx], [(indicator_x, indicator_y - 15), (indicator_x + 20, indicator_y), (indicator_x, indicator_y + 15)])
                
                # Draw player number on the indicator
                player_num_surf = SMALL_FONT.render(str(idx + 1), True, WHITE) # Use white text on color
                
                # Draw a background rectangle for the number for better visibility
                indicator_rect_padding = 5
                indicator_rect_width = player_num_surf.get_width() + 2 * indicator_rect_padding
                indicator_rect_height = player_num_surf.get_height() + 2 * indicator_rect_padding
                indicator_rect = pygame.Rect(indicator_x, indicator_y - indicator_rect_height // 2, indicator_rect_width, indicator_rect_height)
                
                # Draw the background rectangle with the car's color
                pygame.draw.rect(WIN, CAR_COLORS[idx], indicator_rect, border_radius=5)
                
                # Blit the player number text
                WIN.blit(player_num_surf, (indicator_rect.centerx - player_num_surf.get_width() // 2, 
                                           indicator_rect.centery - player_num_surf.get_height() // 2))

        # 골라인 그리기 (relative to camera)
        pygame.draw.rect(WIN, WHITE, finish_line.move(-camera_x, 0))

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