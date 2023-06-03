from R1Control.Common import *
import threading
import socket
import time


class TcpClient(threading.Thread):
    def __init__(self, host, port, max_fruit = 8, recv_interval = 0.1, recv_timeout = 30):
        threading.Thread.__init__(self)

        # 初始化tcp套接字对象
        # 指定使用IPv4地址族
        # 指定使用TCP流式传输协议
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((self.host, self.port))
        
        # 主机IP
        self.host = host

        # 主机端口
        self.port = port

        # 统计当前已摘取数量
        self.current_extracted = 0

        # 最大可摘取果子总数
        self.max_fruit = max_fruit

        # 接收消息间隔时间
        self.recv_interval = recv_interval

        # 接收消息超时时间
        self.recv_timeout = recv_timeout

        # 服务器端信息的拷贝（供外部控制流程使用）
        self.response_copy = invalid_fruit_str

        # 摘取果子动作标志（首次状态都为摘取动作）
        self.action_ready = True


    # 设置当前已摘取果子总数
    def set_current_extracted_count(self):
        self.current_extracted += 1

    # 获取当前已摘取果子总数
    def get_current_extracted_count(self):
        return self.current_extracted


    # 设置最大果子总数
    def set_max_fruit(self, count):
        self.max_fruit = count

    # 获取最大果子总数
    def get_max_fruit(self):
        return self.max_fruit


    # 设置接收间隔时间
    def set_receive_interval(self, interval):
        self.recv_interval = interval

    # 设置接收超时时间
    def set_receive_timeout(self, timeout):
        self.recv_timeout = timeout


    # 重置拷贝数据缓冲区
    def reset_response_copy(self):
        self.response_copy = invalid_fruit_str


    # 好果
    def good_fruit(self):
        if self.response_copy == good_fruit_str:
            return True
        return False
    
    # 坏果
    def bad_fruit(self):
        if self.response_copy == bad_fruit_str:
            return True
        return False
    
    
    # 获取服务器端通知
    def get_server_notification(self):
        if self.good_fruit() == True or self.bad_fruit() == True:
            return True
        return False


    # 获取当前可摘取状态
    def ready_flag(self):
        return self.action_ready
    

    # 关闭tcp流
    def close(self):
        self.client_socket.close()

    # 发送消息到服务器端
    def send_data(self, data):
        self.client_socket.sendall(data.encode())

    # 从服务器端接收消息
    def receive_data(self):
        data = self.client_socket.recv(1024)
        return data.decode()


    def run(self):
        while True:
            # 已摘取完所有果子
            if self.get_current_extracted_count() == self.get_max_fruit():
                break

            # 本地接收的服务器端拷贝消息一旦被重置，那么可以进行下一次摘取动作
            if self.response_copy == invalid_fruit_str:
                self.action_ready = True

            # 满足摘取的条件
            if self.action_ready:

                # 接收服务器端发送的消息
                response = self.receive_data()

                # 接收到好果或坏果的 flag，证明服务器端已完成工作
                if response == good_fruit_str or response == bad_fruit_str:
                    print(f"Server response  ->  Yes: {response}")

                    # 暂停摘取动作
                    self.action_ready = False
                else:
                    print(f"Server response  ->  No: {response}")

                # 拷贝一份服务器端消息供外部控制流程使用
                self.response_copy = response

                # 将拷贝的消息发送到服务器端，证明客户端有响应并且拷贝的数据是否正常
                self.send_data(self.response_copy)

                # 重置接收缓冲区，为下一次接收做准备
                response = invalid_fruit_str
            
            # 接收消息的间隔
            time.sleep(self.recv_interval)

        self.close()
