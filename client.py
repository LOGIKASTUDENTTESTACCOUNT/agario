from socket import *
from pygame import *
from threading import Thread
from random import randint
from math import hypot

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(("localhost", 8080))

initial_data = sock.recv(1024).decode().strip()
parts = initial_data.split(",")
my_id = int(parts[0])
my_player = [int(parts[1]), int(parts[2]), int(parts[3])]  # [X, Y, Радіус]
sock.setblocking(False)

init()
window = display.set_mode((1000, 700))
clock = time.Clock()
all_players = []
running = True


def recieve_data():
    global all_players, running
    buffer = ""
    while running:
        try:
            data = sock.recv(4096).decode()
            if "LOSE" in data:
                print("Тебе з'їли!")
                running = False
                break

            if data:
                buffer += data
                if '\n' in buffer:
                    lines = buffer.split('\n')
                    last_msg = lines[-2]
                    buffer = lines[-1]
                    parts = last_msg.strip("|").split("|")
                    new_players = []
                    for p in parts:
                        if not p: continue
                        p_data = p.replace(' ', '').split(',')
                        if len(p_data) == 4:
                            new_players.append(list(map(int, p_data)))
                    all_players = new_players
        except:
            pass


Thread(target=recieve_data, daemon=True).start()


class Food:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen, color, center, radius):
        draw.circle(screen, color, center, radius)


фф
food = [Food(randint(-2000, 2000), randint(-2000, 2000), 10, (randint(0, 255), randint(0, 255), randint(0, 255))) for _
        in range(300)]

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    window.fill((255, 255, 255))
    scale = max(0.3, min(50 / my_player[2], 1.5))

    keys = key.get_pressed()
    if keys[K_LEFT] or keys[K_a]:
        my_player[0] -= 5
    if keys[K_RIGHT] or keys[K_d]:
        my_player[0] += 5
    if keys[K_UP] or keys[K_w]:
        my_player[1] -= 5
    if keys[K_DOWN] or keys[K_s]:
        my_player[1] += 5

    for fod in food[:]:
        dx = fod.x - my_player[0]
        dy = fod.y - my_player[1]

        if hypot(dx, dy) < my_player[2]:
            my_player[2] += 1
            food.remove(fod)


            new_fod = Food(
                randint(-2000, 2000),
                randint(-2000, 2000),
                10,
                (randint(0, 255), randint(0, 255), randint(0, 255))
            )
            food.append(new_fod)


    for fod in food:
        sx = int((fod.x - my_player[0]) * scale + 500)
        sy = int((fod.y - my_player[1]) * scale + 350)
        fod.draw(window, fod.color, (sx, sy), int(fod.radius * scale))


    for p in all_players:
        if p[0] != my_id:
            sx = int((p[1] - my_player[0]) * scale + 500)
            sy = int((p[2] - my_player[1]) * scale + 350)
            draw.circle(window, (0, 0, 255), (sx, sy), int(p[3] * scale))
        else:
            if p[3] > my_player[2]:
                my_player[2] = p[3]


    draw.circle(window, (255, 0, 0), (500, 350), int(my_player[2] * scale))

    try:
        msg = f"{my_id},{my_player[0]},{my_player[1]},{my_player[2]}\n"
        sock.send(msg.encode())
    except:
        pass

    display.flip()
    clock.tick(60)

quit()



