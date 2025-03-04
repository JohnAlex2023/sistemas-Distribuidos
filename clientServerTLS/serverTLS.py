import socket
import threading
import rsa
import ssl

# Generar claves RSA para el servidor (usadas para el cifrado a nivel de aplicación)
(public_key, private_key) = rsa.newkeys(512)

# Configuración del servidor 192.168.20.28
HOST = "192.168.20.28"  
PORT = 12345

clientes = {}         # Diccionario para almacenar clientes {nombre: {'socket': socket, 'public_key': clave}}
salas_privadas = {}   # Diccionario para salas privadas {sala_id: (cliente1, cliente2)}

# Crear un socket TCP básico
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# Crear un contexto SSL para TLS
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

print(f"Servidor activo en {HOST}:{PORT} con TLS")

def manejar_cliente(client_socket, client_address):
    try:
        # Enviar la clave pública del servidor al cliente (cifrado a nivel de aplicación)
        client_socket.send(public_key.save_pkcs1("PEM"))
        # Recibir la clave pública del cliente
        public_key_cliente = rsa.PublicKey.load_pkcs1(client_socket.recv(1024))
        # Recibir el nombre del cliente
        nombre = client_socket.recv(1024).decode("utf-8")
        
        print(f"{nombre} ({client_address}) se ha conectado.")
        clientes[nombre] = {'socket': client_socket, 'public_key': public_key_cliente}
        
        # Notificar a todos los clientes sobre la nueva conexión (enviando mensaje cifrado con la clave pública de cada cliente)
        mensaje_conexion = f"{nombre} se ha conectado."
        for cliente in clientes.values():
            if cliente['socket'] != client_socket:
                cliente['socket'].send(rsa.encrypt(mensaje_conexion.encode(), cliente['public_key']))

        while True:
            mensaje = client_socket.recv(1024)
            if not mensaje:
                break
            
            mensaje_descifrado = rsa.decrypt(mensaje, private_key).decode("utf-8")
            print(f"Mensaje recibido: {mensaje_descifrado}")

            partes = mensaje_descifrado.split(" ", 2)
            comando = partes[0]
                
            if comando == "/privado":  
                # /privado usuario mensaje
                if len(partes) < 3:
                    client_socket.send(rsa.encrypt("Uso: /privado usuario mensaje".encode(), public_key))
                    continue
                
                destinatario, mensaje_privado = partes[1], partes[2]
                if destinatario in clientes:
                    # Crear una sala privada si no existe
                    salas_privadas[(nombre, destinatario)] = (clientes[nombre], clientes[destinatario])
                    
                    # Cifrar mensaje con la clave pública del destinatario
                    mensaje_enviar = f"[Privado] {nombre}: {mensaje_privado}"
                    destinatario_public_key = clientes[destinatario]['public_key']
                    clientes[destinatario]['socket'].send(rsa.encrypt(mensaje_enviar.encode(), destinatario_public_key))
                else:
                    client_socket.send(rsa.encrypt("El usuario no está conectado.".encode(), clientes[nombre]['public_key']))

            else:
                # Mensaje público: reenviar a todos menos al remitente
                for cliente in clientes.values():
                    if cliente['socket'] != client_socket:
                        cliente['socket'].send(rsa.encrypt(f"Mensaje publico: {nombre}: {mensaje_descifrado}".encode(), cliente['public_key']))
    
    except Exception as e:
        print(f"Error con {client_address}: {e}")

    finally:
        print(f"Cliente {client_address} desconectado.")
        client_socket.close()
        if nombre in clientes:
            del clientes[nombre]

while True:
    # Aceptar conexión normal
    client_socket, client_address = server_socket.accept()
    try:
        # Envolver la conexión con TLS
        tls_client_socket = context.wrap_socket(client_socket, server_side=True)
        threading.Thread(target=manejar_cliente, args=(tls_client_socket, client_address)).start()
    except Exception as e:
        print(f"Error al establecer TLS con {client_address}: {e}")
        client_socket.close()
