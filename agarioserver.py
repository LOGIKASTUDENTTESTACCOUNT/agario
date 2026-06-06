import time
from socket import *
from threading import Thread
import math

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('localhost', 8080))
sock.listen(5)
sock.setblocking(False)

players = {}
conn_ids = {}
id_counter = 0


def handle_data():
    while True:
        time.sleep(0.01)

        for conn in list(players):
            try:
                data = conn.recv(1024).decode()
                if data:
                    last_msg = data.strip().split('\n')[-1]
                    if ',' in last_msg:
                        parts = last_msg.replace(' ', '').split(',')
                        if len(parts) == 4:
                            pid, x, y, r = map(int, parts)
                            players[conn] = {"id": pid, 'x': x, 'y': y, 'r': r}
            except:
                continue

        conns = list(players.keys())
        for i in range(len(conns)):
            for j in range(i + 1, len(conns)):
                c1, c2 = conns[i], conns[j]
                if c1 not in players or c2 not in players: continue

                p1, p2 = players[c1], players[c2]
                dist = math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])

                if dist < p1['r'] or dist < p2['r']:
                    if p1['r'] >= p2['r'] * 1.1:
                        players[c1]['r'] += int(p2['r'] * 0.5)
                        try:
                            c2.send("LOSE\n".encode())
                        except:
                            pass
                        del players[c2]
                    elif p2['r'] >= p1['r'] * 1.1:
                        players[c2]['r'] += int(p1['r'] * 0.5)
                        try:
                            c1.send("LOSE\n".encode())
                        except:
                            pass
                        del players[c1]

        if players:
            state_strs = [f"{p['id']},{p['x']},{p['y']},{p['r']}" for p in players.values()]
            state_msg = "|".join(state_strs) + "\n"
            for conn in list(players):
                try:
                    conn.send(state_msg.encode())
                except:
                    del players[conn]


Thread(target=handle_data, daemon=True).start()
print("Server running...")

while True:
    try:
        conn, addr = sock.accept()
        conn.setblocking(False)
        id_counter += 1
        players[conn] = {"id": id_counter, 'x': 0, 'y': 0, 'r': 20}
        conn_ids[conn] = id_counter

        start_msg = f"{id_counter},0,0,20\n"
        conn.send(start_msg.encode())
    except:
        pass