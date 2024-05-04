# SocketVNC

SocketVNC is a Simple VNC Client API written in Python using the Socket module. 
It allows you to connect to a VNC Server and interact with it.

# Environment
Test with Python 3.11.3-64bit on Windows 11.
numpy==1.26.1,struct,socket
`VNC Server`: Vmware Workstation 17 Win10 64bit

# Usage
```
from SocketVNC.VNC import VNCClient

# connect to VNC Server
client = VNCClient() #host="127.0.0.1", port=5900 by default
client.connect()
client.set_encodings()

# get screenshot img
client.request_frame_update()
img = client.recv_server_msg()
# saveimg
cv2.imwrite("test.png", img)

# keyboard event
client.key_event(ord("w"), 1)
time.sleep(3)
client.key_event(ord("w"), 0)

# mouse event
client.pointer_event(1,100, 100)
client.pointer_event(0,100, 100)

# close connection
client.close()

```