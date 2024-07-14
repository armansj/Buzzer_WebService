import machine
import time
import socket
import network

# Set up PWM on GPIO 15 (GP15) for the buzzer
pwm = machine.PWM(machine.Pin(15))
pwm.freq(1000)  # Set default frequency to 1kHz

# Function to play a tone on the buzzer
def play_tone(frequency, duration):
    pwm.freq(frequency)
    pwm.duty_u16(32768)  # Set duty cycle to 50% (maximum for piezo buzzer)
    time.sleep(duration)
    pwm.duty_u16(0)  # Turn off the PWM signal

# WiFi credentials
ssid = 'Vodafone-820C'
password = 'xc5dadQYrqpo2J2sd2q2'

# Initialize WiFi
wifi_status = network.WLAN(network.STA_IF)
wifi_status.disconnect()
wifi_status.active(True)
wifi_status.connect(ssid, password)

# HTML Page
def WebPage():
    html = """
    <html>
        <head>
            <title>Raspberry Pi Pico Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #1a0dab; }
                button { background-color: #4285f4; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>Raspberry Pi Pico Web Server</h1>
            <p><button onclick="playSound()">Play Sound</button></p>
            <script>
                function playSound() {
                    fetch('/play?frequency=1000&duration=0.5');
                }
            </script>
        </body>
    </html>
    """
    return html

# Check WiFi connection
while not wifi_status.isconnected():
    time.sleep(1)
    print('Connecting to WiFi...')

# If connected
print('WiFi connected successfully')
print(wifi_status.ifconfig())

# Set up the socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

try:
    while True:
        conn, addr = s.accept()
        print('Connection from: %s' % str(addr))
        req = conn.recv(1024)
        req = str(req)
        print('Request: %s' % req)

        # Handle different requests
        if '/play?' in req:
            # Parse the request for frequency and duration
            frequency_start = req.find('frequency=') + len('frequency=')
            frequency_end = req.find('&', frequency_start)
            frequency = int(req[frequency_start:frequency_end])

            duration_start = req.find('duration=') + len('duration=')
            duration_end = req.find(' ', duration_start)
            duration = float(req[duration_start:duration_end])

            # Play the tone on the buzzer
            play_tone(frequency, duration)

            # Send a response
            response = WebPage()
            conn.send('HTTP/1.1 200 OK\r\n')
            conn.send('Content-Type: text/html\r\n')
            conn.send('Connection: close\r\n\r\n')
            conn.sendall(response.encode('utf-8'))
        else:
            # Handle other requests here (if any)
            response = WebPage()
            conn.send('HTTP/1.1 200 OK\r\n')
            conn.send('Content-Type: text/html\r\n')
            conn.send('Connection: close\r\n\r\n')
            conn.sendall(response.encode('utf-8'))

        conn.close()

except Exception as e:
    print('Error:', e)

finally:
    s.close()  # Ensure the socket is closed properly

# Clean up
pwm.deinit()

