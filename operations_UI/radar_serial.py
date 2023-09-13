import serial
import serial.tools.list_ports
import time
 
# # 获取所有串口设备实例。
# # 如果没找到串口设备，则输出：“无串口设备。”
# # 如果找到串口设备，则依次输出每个设备对应的串口号和描述信息。
# ports_list = list(serial.tools.list_ports.comports())
# if len(ports_list) <= 0:
#     print("无串口设备。")
# else:
#     print("可用的串口设备如下：")
#     for comport in ports_list:
#         print(list(comport)[0], list(comport)[1],"port")



ser = serial.Serial("/dev/ttyAMA2",115200,timeout = 5)  # 开启com3口，波特率115200，超时5
ser.flushInput()  # 清空缓冲区

def main():
    while True:
        count = ser.inWaiting() # 获取串口缓冲区数据

        data = ser.read(ser.in_waiting)
        print(data)
        if data!=0:
        # if count!=0:
            print("have data")
        else:
            print("no data")
            break
        # if count !=0 :
        #     recv = ser.read(ser.in_waiting).encoding('utf-8') # 读出串口数据，数据采用gbk编码
        #     print(time.time()," ---  recv --> ", recv)  # 打印一下子
        time.sleep(0.5)  # 延时0.1秒，免得CPU出问题



if __name__ == '__main__':
    main()
