import socket
import threading

# Función para recibir mensajes del servidor
def recibir_mensajes(cliente_socket):
    while True:
        try:
            mensaje = cliente_socket.recv(1024).decode('utf-8')
            print(mensaje)
        except:
            print("[-] Se ha perdido la conexión con el servidor")
            cliente_socket.close()
            break

# Configuración del cliente
def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverIP = "192.168.201.57"
    serverPort = 1234
    try:
        cliente.connect((serverIP, serverPort))
        print(f"Conexión exitosa con el servidor ({serverIP}).")
    except Exception as e:
        print(f"Error al conectar con el servidor ({serverIP}): {e}")
        exit()  # Salir del programa si no se puede conectar


    # Enviar el nombre o identificador del cliente al servidor
    nombre_cliente = input("Ingresa tu nombre: ")
    cliente.send(nombre_cliente.encode('utf-8'))

    # Iniciar un hilo para recibir mensajes
    hilo = threading.Thread(target=recibir_mensajes, args=(cliente,))
    hilo.start()

    while True:
        mensaje = input()
        cliente.send(mensaje.encode('utf-8'))

if __name__ == "__main__":
    iniciar_cliente()