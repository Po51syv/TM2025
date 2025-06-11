import network
import socket
from machine import Pin, PWM
import time


led = Pin('LED', Pin.OUT)

SSID = 'Bonne nuit'
PASSWORD = 'lol23456'

# PC server IP and port
PC_IP = '192.168.12.139'  # Change to your PC's IP
PC_PORT = 12345

# Setup motors (pins according to your wiring)
motor1_a = PWM(Pin(26))
motor1_b = PWM(Pin(27))
motor2_a = PWM(Pin(17))
motor2_b = PWM(Pin(18))

for m in [motor1_a, motor1_b, motor2_a, motor2_b]:
    m.freq(1000)

def stop():
    for m in [motor1_a, motor1_b, motor2_a, motor2_b]:
        m.duty_u16(0)

def forward(speed=40000):
    motor1_a.duty_u16(speed)
    motor1_b.duty_u16(0)
    motor2_a.duty_u16(speed)
    motor2_b.duty_u16(0)

def backward(speed=40000):
    motor1_a.duty_u16(0)
    motor1_b.duty_u16(speed)
    motor2_a.duty_u16(0)
    motor2_b.duty_u16(speed)

def turn_left(speed=40000):
    motor1_a.duty_u16(0)
    motor1_b.duty_u16(speed)
    motor2_a.duty_u16(speed)
    motor2_b.duty_u16(0)

def turn_right(speed=40000):
    motor1_a.duty_u16(speed)
    motor1_b.duty_u16(0)
    motor2_a.duty_u16(0)
    motor2_b.duty_u16(speed)

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to Wi-Fi...")
start = time.time()
while not wlan.isconnected() and time.time() - start < 15:
    time.sleep(1)

if wlan.isconnected():
    print("Connected. IP:", wlan.ifconfig()[0])
    led.on()
else:
    print("Failed to connect.")
    led.off()
    raise SystemExit

# Connect to PC server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((PC_IP, PC_PORT))
    print("Connected to PC server")
except Exception as e:
    print("Connection error:", e)
    led.off()
    raise SystemExit

while True:
    try:
        data = sock.recv(64)
        if not data:
            print("Disconnected from server")
            break
        cmd = data.decode().strip()
        print("Received command:", cmd)
        if cmd == 'f':
            forward()
        elif cmd == 'b':
            backward()
        elif cmd == 'l':
            turn_left()
        elif cmd == 'r':
            turn_right()
        elif cmd == 's':
            stop()
    except Exception as e:
        print("Error:", e)
        stop()
        break

sock.close()