 
import socket
import struct
def socket_connect():
    import socket

    # 创建一个客户端套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接服务器
    server_address = ('192.168.123.218', 5002)
    client_socket.connect(server_address)

    # data = struct.pack(x)
    strs = 'hello world'
    # 向服务器发送数据
    client_socket.sendall(strs.encode())

    # 接收来自服务器的响应
    response = client_socket.recv(1024)
    print(f"Received response from server: {response.decode()}")

    # 关闭客户端套接字
    client_socket.close()
    
socket_connect()