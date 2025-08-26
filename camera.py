import easyocr 
import cv2 
import serial
import time
from rfid_util import rfid_util
""" 
TODO:修改EPC——>读取TID
 """
readTag = [0xA0, 0x06, 0x01, 0x8B, 0x01, 0x00, 0x01, 0xCC]  # 发送的指令
mid_Res = [0xA0, 0x04, 0x01, 0x85, 0x10, 0xC6]  # 预期的返回结果

# 计算校验和的函数
def calcu_check_sum(command):
    checksum = 0
    for byte in command:
        checksum += byte
    return (~checksum + 1) & 0xFF  # 取反并加 1，然后取低 8 位


# 读取 RFID 数据的函数
def read_RFID_data(serial_port, read_tag):
    # 进行校验和计算，拼好发送指令
    read_tag.append(calcu_check_sum(read_tag))

    # 发送指令
    command_len = len(read_tag)
    bytes_written = serial_port.write(bytearray(read_tag))  # 写入数据到串口
    if bytes_written != command_len:
        print("指令发送失败.")
        serial_port.close()
        return []
    # 读取串口返回的数据
    start_time = time.time()  # 或使用 
    buffer = serial_port.readline() # 一次读取最多1024字节的数据
    # 记录结束时间
    end_time = time.time()  # 或使用 time.time()
# 计算执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time:.6f} 秒")
    if len(buffer) == 0:
        print("数据读取失败.")
        serial_port.close()
        return []

    # 返回读取到的数据
    return list(buffer)  # 返回数据以列表形式表示

# 将字符串转换为十六进制格式
def stringToHex(data):
    return ''.join(format(x, '02X') for x in data)

# 将字符串转换为字节数组并追加到 tag
def stringToHexVector(epc_str, tag):
    for i in range(2, len(epc_str), 2):
        tag.append(int(epc_str[i:i+2], 16))

def writeEPC(serial_port, epc_str):
    while True:
        read = read_RFID_data(serial_port, readTag)  # 根据你项目中的readTag
        epc = bytearray()
        
        if len(read) >= 21:
            epc = read[7:19]  # 读取 EPC 数据
        print("EPC: " + stringToHex(epc))
        mid_tag = bytearray([0xA0, 0x11, 0x01, 0x85, 0x00, 0x0C])
        mid_tag.extend(epc)

        mid_res = read_RFID_data(serial_port, mid_tag)
        print(f"中间步骤完成: {stringToHex(mid_res)}")

        set_tag = [0xA0, 0x16, 0x01, 0x94, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x06, 0xE2, 0x80, 0x69, 0x95, 0x00, 0x00, 0x70, 0x03, 0xA0, 0x42]
        stringToHexVector(epc_str, set_tag)  # 这个会将字符串转换为字节并追加到 set_tag 中

        res = read_RFID_data(serial_port, set_tag)
        if len(res) < 10:
            print("写入失败，重来")
            continue
        print(f"写入完成: {stringToHex(res)}")
        return True

# def readTID():
    


# 主程序部分
def main():
    # # 打开COM3串口
    # ser = serial.Serial('COM3', 115200, timeout=1)
    # # 检查串口是否已打开
    # if ser.is_open:
    #     print("COM3串口已打开")
    ifconnect = rfid_util.connect()

    if ifconnect:
        print("RFID设备连接成功")
    # 加载EasyOCR模型 
    reader = easyocr.Reader(['en'])  # 只支持英文

    # 初始化变量
    last_recognized_text = None  # 上一个识别到的文本
    count = 0  # 连续计数器
    written_epc_list = []  # 记录已写入的 current_text
    written_tid_list = []  # 记录已写入的 current_tid
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧")
            break

        # 使用EasyOCR进行OCR识别 
        result = reader.readtext(frame, detail=0)

        # 提取7位标签的文本
        # recognized_five_digit_numbers = [text for text in result if len(text) == 7]
        

        if result:
            current_text = result[0]  # 取第一个识别结果

            if current_text == last_recognized_text:
                count += 1
            else:
                count = 1  # 重置计数器

            last_recognized_text = current_text  # 更新上一个识别的文本

            # 如果计数达到5且不在写入状态，则调用 writeEPC
            if count == 5:
                if current_text not in written_epc_list:
                    print("Tag：" + current_text)
                    # writeEPC(ser, current_text)  # 调用 writeEPC
                    written_epc_list.append(current_text)  # 将 current_text 添加到列表
                    #之后读取RFID，计数五次之后写入excel
                    current_tid = rfid_util.read_single_tid(timeout=2.0, required_count=5)
                    if current_tid:
                        print("TID：" + current_tid)
                        if current_tid not in written_tid_list:
                            written_tid_list.append(current_tid)
                            # 将 current_text 和 current_tid 写入Excel
                            # TODO:写入Excel
                        else:
                            count = 1
                else:
                    count = 1
                
        # 在图像上显示识别结果
        for text in result:
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Camera Feed', frame)

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 关闭摄像头和串口
    cap.release()
    rfid_util.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
