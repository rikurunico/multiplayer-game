import socket
import threading
import time

# Buat socket UDP untuk server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 12345)
server_socket.bind(server_address)

# Menyimpan posisi pemain dan latensi
player_positions = {}
player_latencies = {}


# Fungsi untuk menangani penerimaan data dari klien
def handle_client():
    global player_positions, player_latencies
    while True:
        data, client_address = server_socket.recvfrom(1024)
        if data:
            # Parsing data
            message = data.decode()
            player_id, x, y, request_time = message.split(",")
            x, y = int(x), int(y)

            # Hitung latensi (jika request_time tersedia)
            if request_time.isdigit():
                request_time = float(request_time)
                round_trip_time = (time.time() - request_time) * 1000  # dalam milidetik
                player_latencies[player_id] = round_trip_time

            # Simpan posisi pemain
            player_positions[player_id] = {"x": x, "y": y}

            # Kirim data posisi semua pemain dan latensi ke semua klien
            for player, pos in player_positions.items():
                if player != player_id:  # Kirim data ke semua pemain lain
                    server_socket.sendto(
                        f"{player},{pos['x']},{pos['y']},{player_latencies.get(player, 0):.2f}".encode(),
                        client_address,
                    )


# Jalankan thread untuk menangani klien
threading.Thread(target=handle_client, daemon=True).start()

print("Server berjalan di 127.0.0.1:12345")
try:
    while True:
        pass  # Tunggu hingga server dihentikan secara manual
except KeyboardInterrupt:
    print("\nServer dihentikan.")
    server_socket.close()
