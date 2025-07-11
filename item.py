FPS = 60  # 1초 = 60프레임

class Item:
    def __init__(self, name):
        self.name = name

    def activate(self, user_idx, players):
        player_count = len(players)

        if self.name == "Bomb":
            target_idx = (user_idx + 1) % player_count
            players[target_idx]["stun"] = FPS * 2

        elif self.name == "Booster":
            players[user_idx]["boost"] = FPS * 2

        elif self.name == "Shell":
            leading_idx = max(range(player_count), key=lambda i: players[i]["rect"].x)
            if leading_idx != user_idx:
                players[leading_idx]["stun"] = FPS * 2

        elif self.name == "Ice":
            for i in range(player_count):
                if i != user_idx:
                    players[i]["stun"] = FPS * 1
