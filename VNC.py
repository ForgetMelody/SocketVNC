import socket
import struct
import numpy as np


class VNCClient:
    def __init__(self, host="127.0.0.1", port=5900, log=True):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.width = 0
        self.height = 0
        self.img = None
        self.log = log

    # connect to the server and initialize the framebuffer
    def connect(self):
        # Connect to the server
        self.socket.connect((self.host, self.port))
        print("Server protocol version:", self.socket.recv(12))
        # version
        protocol_version = b'RFB 003.008\n'
        self.socket.send(protocol_version)
        response = self.socket.recv(4)
        print("Security type Supported:", response)
        # security type
        self.socket.send(b'\x01')
        response = self.socket.recv(4)
        print("Authentication result:", response)
        # desktop share flag
        self.socket.send(b'\x01')
        (self.width, self.height, self.bits_per_pixel, self.depth, self.big_endian_flag, self.true_color_flag, self.red_max, self.green_max,
         self.blue_max, self.red_shift, self.green_shift, self. blue_shift) = struct.unpack('!HHBB??HHHBBB', self.socket.recv(17))
        self.socket.recv(3)  # Padding
        desktop_name_length = struct.unpack('I', self.socket.recv(4))[0]
        self.desktop_name = self.socket.recv(
            desktop_name_length).decode('utf-8')
        if self.log:
            print("Framebuffer size: (", self.width, ", ", self.height, ")")
            print("Bits per pixel:", self.bits_per_pixel)
            print("Colour depth:", self.depth)
            print("Big endian flag:", self.big_endian_flag)
            print("True color flag:", self.true_color_flag)
            print("Red max:", self.red_max)
            print("Green max:", self.green_max)
            print("Blue max:", self.blue_max)
            print("Red shift:", self.red_shift)
            print("Green shift:", self.green_shift)
            print("Blue shift:", self.blue_shift)
            print("Desktop name:", self.desktop_name)

        # initialize the image
        self.img = np.zeros((self.height, self.width, 4), np.uint8)

    def recvall(self, length):
        data = b''
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return data

    def request_frame_update(self, x=0, y=0, width=None, height=None):
        if width is None:
            width = self.width

        if height is None:
            height = self.height
        msg = struct.pack('!BBHHHH', 3, 0, x, y, width, height)
        self.socket.send(msg)

    def set_encodings(self, encodings: list = [0]):
        encodings_count = len(encodings)
        msg = struct.pack('!BBH', 2, 0, encodings_count)
        for encoding in encodings:
            msg += struct.pack('!I', encoding)
        self.socket.send(msg)

    def pointer_event(self, button_mask, x, y):
        msg = struct.pack('!BBHH', 5, button_mask, x, y)
        self.socket.send(msg)

    def key_event(self, key, pressed):
        msg = struct.pack('!BBBBI', 4, pressed, 66, 2, key)
        self.socket.send(msg)

    # receive the message from the server
    def recv_server_msg(self):
        msg = struct.unpack('!B', self.socket.recv(1))[0]
        # print("Received message type:", msg)
        if msg == 0:  # FramebufferUpdate
            return self.decode_frame()
        else:
            print("Error: Invalid message type")
            return None

    # decode the frame from bytes to numpy array after receiving the message
    def decode_frame(self) -> np.ndarray:
        (padding_, number_of_rectangles) = struct.unpack(
            '!BH', self.socket.recv(3))
        for i in range(number_of_rectangles):
            (x, y, width, height, encoding) = struct.unpack(
                '!HHHHI', self.socket.recv(12))
            if encoding == 0:
                data_length = width * height * 4
                data = self.recvall(data_length)
                self.img[y:y + height, x:x +
                         width] = np.ndarray((height, width, 4), 'B', data)
                self.img[y:y + height, x:x + width, 3] = 255
        return self.img

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    import time
    import cv2
    # 使用示例
    client = VNCClient()
    client.connect()
    client.set_encodings()

    client.request_frame_update()
    img = client.recv_server_msg()
    # saveimg
    cv2.imwrite("test.png", img)

    client.key_event(ord("w"), 1)
    time.sleep(3)
    client.key_event(ord("w"), 0)

    client.pointer_event(1, 100, 100)
    client.pointer_event(0, 100, 100)

    client.close()
