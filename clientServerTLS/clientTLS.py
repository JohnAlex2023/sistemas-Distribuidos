import socket
import ssl
import rsa
import threading

# Configuración del servidor
SERVER_HOST = "192.168.20.28"
SERVER_PORT = 12345

# Generar claves RSA del cliente
(public_key_cliente, private_key_cliente) = rsa.newkeys(512)

# Crear un contexto SSL/TLS para el cliente
# se deshabilita la verificación del certificado para pruebas.
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Crear un socket TCP y envolverlo con TLS
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tls_sock = context.wrap_socket(sock, server_hostname=SERVER_HOST)
tls_sock.connect((SERVER_HOST, SERVER_PORT))

# Enviar la clave pública del cliente al servidor
tls_sock.send(public_key_cliente.save_pkcs1("PEM"))

# Recibir la clave pública del servidor
public_key_data = tls_sock.recv(1024)
public_key_servidor = rsa.PublicKey.load_pkcs1(public_key_data)

# Pedir el nombre de usuario y enviarlo
nombre = input("Ingresa tu nombre de usuario: ")
tls_sock.send(nombre.encode("utf-8"))

def recibir_mensajes():
    while True:
        try:
            mensaje_cifrado = tls_sock.recv(1024)
            if not mensaje_cifrado:
                break  # El servidor cerró la conexión
            
            # Intentar descifrar el mensaje recibido
            try:
                mensaje = rsa.decrypt(mensaje_cifrado, private_key_cliente).decode("utf-8")
            except rsa.DecryptionError:
                print("\nError: No se pudo descifrar el mensaje. ¿Está cifrado correctamente?")
                continue

            print(f"\n{mensaje}")

        except Exception as e:
            print(f"\nError recibiendo mensaje: {e}")
            break

# Hilo para recibir mensajes
threading.Thread(target=recibir_mensajes, daemon=True).start()

print("\nEscribe /privado usuario mensaje para enviar mensajes privados.")
print("Escribe 'salir' para desconectarte.")

while True:
    mensaje = input("")
    if mensaje.lower() == "salir":
        break
    
    # Cifrar el mensaje con la clave pública del servidor
    mensaje_cifrado = rsa.encrypt(mensaje.encode(), public_key_servidor)
    
    # Enviar el mensaje cifrado a través del canal TLS
    tls_sock.send(mensaje_cifrado)

tls_sock.close()
