import socket

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#config server
server_socket.bind(("192.168.201.57",1234))

server_socket.listen(1)#escucha uno a la vez

print("esperando a que se conecten")

#aceptar la conexion entrante
client_socket,client_address = server_socket.accept()
print(f"conexion aceptada en {client_address}")
while True:
    #recibir datos del cliente}
    data = client_socket.recv(1024)
    print(f"cliente: {data.decode()}")

    #envia respuesta a el cliente
    response = input("escribe: ")
    client_socket.send(response.encode())

#cerrar la sesion
client_socket.close()
server_socket.close()