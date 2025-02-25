import socket

# Configuración del cliente
def cliente():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect(("localhost", 12345))  # Conectar al servidor

    # Recibir mensaje de bienvenida del servidor
    bienvenida = cliente_socket.recv(1024).decode()
    print(bienvenida)

    # Enviar mensajes al servidor
    while True:
        mensaje = input("Escribe un mensaje (o 'salir' para terminar): ")
        cliente_socket.send(mensaje.encode())
        if mensaje.lower() == "salir":
            break
        respuesta = cliente_socket.recv(1024).decode()
        print(f"Respuesta del servidor: {respuesta}")

    cliente_socket.close()

if __name__ == "__main__":
    cliente()