import socket
import threading
import tkinter as tk
import time

# Meminta user untuk memasukkan ID pemain
player_id = input("Masukkan ID Pemain (contoh: player1): ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 12345)

# Posisi awal pemain
position = {"x": 0, "y": 0}
other_players = {}
latency = 0  # Variabel latensi


# Fungsi untuk mengirim posisi ke server
def send_position():
    global client_socket, server_address, position, player_id, latency
    while True:
        try:
            # Mengirim data posisi dengan cap waktu
            request_time = time.time()
            client_socket.sendto(
                f"{player_id},{position['x']},{position['y']},{request_time}".encode(),
                server_address,
            )
            time.sleep(0.1)  # Kirim setiap 100ms
        except Exception as e:
            print(f"Error saat mengirim data: {e}")
            break


# Fungsi untuk menerima pembaruan dari server
def receive_updates(canvas, player_shape):
    global client_socket, other_players, latency
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            player_data = data.decode().split(",")
            other_player_id, x, y, player_latency = (
                player_data[0],
                int(player_data[1]),
                int(player_data[2]),
                float(player_data[3]),
            )

            # Update latensi
            if other_player_id != player_id:
                latency = player_latency

            # Update posisi pemain lain
            if other_player_id != player_id:
                other_players[other_player_id] = {"x": x, "y": y}
                update_canvas(canvas, other_players)
        except Exception as e:
            print(f"Error saat menerima data: {e}")
            break


# Fungsi untuk memperbarui canvas dengan posisi pemain lain
def update_canvas(canvas, players):
    canvas.delete("other")
    for player_id, pos in players.items():
        canvas.create_oval(
            pos["x"], pos["y"], pos["x"] + 20, pos["y"] + 20, fill="blue", tags="other"
        )


# Fungsi untuk menangani pergerakan
def move(event, canvas, player_shape):
    global position
    step = 5
    if event.keysym == "Up":
        position["y"] -= step
    elif event.keysym == "Down":
        position["y"] += step
    elif event.keysym == "Left":
        position["x"] -= step
    elif event.keysym == "Right":
        position["x"] += step

    # Update posisi di canvas
    canvas.coords(
        player_shape,
        position["x"],
        position["y"],
        position["x"] + 20,
        position["y"] + 20,
    )


# GUI menggunakan Tkinter
root = tk.Tk()
root.title(f"Simple Game Client - {player_id}")
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()

# Buat lingkaran pemain
player_shape = canvas.create_oval(
    position["x"], position["y"], position["x"] + 20, position["y"] + 20, fill="red"
)

# Label untuk menampilkan latensi
latency_label = tk.Label(root, text=f"Latensi: {latency:.2f} ms", font=("Arial", 12))
latency_label.pack()

# Bind event keyboard
root.bind("<Up>", lambda event: move(event, canvas, player_shape))
root.bind("<Down>", lambda event: move(event, canvas, player_shape))
root.bind("<Left>", lambda event: move(event, canvas, player_shape))
root.bind("<Right>", lambda event: move(event, canvas, player_shape))

# Jalankan thread untuk pengiriman dan penerimaan data
threading.Thread(target=send_position, daemon=True).start()
threading.Thread(
    target=receive_updates, args=(canvas, player_shape), daemon=True
).start()


# Update label latensi secara periodik
def update_latency_label():
    latency_label.config(text=f"Latensi: {latency:.2f} ms")
    root.after(1000, update_latency_label)


update_latency_label()

root.mainloop()
