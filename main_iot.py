import time
import network
import random
from secrets import WIFI_SSID, WIFI_PASS, ID_SCOPE, DEVICE_ID, SAS_KEY

try:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        wlan.disconnect()
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        print("Connecting to Wifi")
        time.sleep(0.5)
    print("Connected to Wifi")
    try:
        import iotc
    except:
        import mip
        mip.install('github:Azure/iot-central-micropython-client/package.json')
        import iotc

    from iotc import IoTCClient, IoTCConnectType
    client = IoTCClient(ID_SCOPE, DEVICE_ID, IoTCConnectType.SYMM_KEY, SAS_KEY)
    client.connect()
    while client.is_connected():
        print('Sending telemetry')
        client.send_telemetry({'temperature': random.randint(100, 300) / 10.0, "humidity": random.randint(100, 1000) / 10.0})
        time.sleep(2)
except Exception as error:
    raise error