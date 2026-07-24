from yolo_uno import *
from dht20 import *
from lcd1602 import *
from oled_i2c import *
from pins import *
import asyncio


# Devices
lcd = LCD1602()
oled = OledI2C()

dht = DHT20()


# LEDs
led13 = Pins(D13_PIN)


# Fan
fan = Pins(D9_PIN)


# Analog Sensor
air_sensor = Pins(A0_PIN)      


# RGB Modules
heater = RGBLed(D3_PIN, 4)
cooler = RGBLed(D5_PIN, 4)
humidifier = RGBLed(D7_PIN, 4)


# Shared Variables
temperature = 0
humidity = 0

weather = "GOOD"

air_raw = 0
air_percent = 0

air_status = ""
air_advice = ""

heater_status = "SAFE"
cooler_status = "OFF"
humidifier_status = "OFF"
fan_status = "OFF"


# Binary Semaphores
heater_sem = asyncio.Semaphore(0)
cooler_sem = asyncio.Semaphore(0)
humidifier_sem = asyncio.Semaphore(0)

weather_sem = asyncio.Semaphore(0)
air_sem = asyncio.Semaphore(0)
oled_sem = asyncio.Semaphore(0)


# Heater Functions
def heater_off():
    for i in range(4):
        heater.off(i)


def heater_green():
    for i in range(4):
        heater.show(i, hex_to_rgb("#00FF00"))


def heater_orange():
    for i in range(4):
        heater.show(i, hex_to_rgb("#FFA500"))


def heater_red():
    for i in range(4):
        heater.show(i, hex_to_rgb("#FF0000"))


# Cooler Functions
def cooler_off():
    for i in range(4):
        cooler.off(i)


def cooler_on():
    for i in range(4):
        cooler.show(i, hex_to_rgb("#00FFFF"))


# Humidifier Functions
def humidifier_off():
    for i in range(4):
        humidifier.off(i)


def humidifier_green():
    for i in range(4):
        humidifier.show(i, hex_to_rgb("#00FF00"))


def humidifier_yellow():
    for i in range(4):
        humidifier.show(i, hex_to_rgb("#FFFF00"))


def humidifier_red():
    for i in range(4):
        humidifier.show(i, hex_to_rgb("#FF0000"))
        
        
# Task 1 : Sensor Task
async def task_sensor():
    global temperature
    global humidity
    global weather

    global air_raw
    global air_percent

    while True:
        # Read DHT20
        temperature = await dht.atemperature()
        humidity = await dht.ahumidity()

        # Read MQ135
        air_raw = air_sensor.read_analog()
        air_percent = air_sensor.read_analog_percent()

        print("--------------------------------")
        print("Temperature :", temperature)
        print("Humidity    :", humidity)
        print("Air Quality :", air_percent, "%")

        # LCD
        lcd.clear()

        # Row 1
        lcd.show(str(round(temperature,1)),0,0)
        lcd.show(chr(0),0,4)
        lcd.show("C",0,5)

        lcd.show(str(round(humidity,1)),0,10)
        lcd.show("%",0,14)

        # Row 2
        if temperature >= 35:
            weather = "HOT"
            
        elif temperature >= 35 and humidity <= 40:
           weather = "HOT&DRY"
           
        elif temperature <= 15:
            weather = "COLD"
            
        elif temperature <= 15 and humidity <= 40:
            weather = "COLD&DRY"

        elif humidity >= 85 and temperature <= 27:
            weather = "RAIN"

        elif humidity < 40:
            weather = "DRY"

        else:
            weather = "GOOD"

        lcd.show("STATUS:"+weather,1,0)

        # Wake Tasks
        heater_sem.release()
        cooler_sem.release()
        humidifier_sem.release()

        weather_sem.release()
        air_sem.release()
        oled_sem.release()

        await asleep_ms(5000)



# Task 2 : Heater
async def task_heater():
    global temperature
    global heater_status

    while True:
        await heater_sem.acquire()

        if temperature < 20:
            heater_red()
            heater_status = "HEATING"

        elif temperature < 28:
            heater_green()
            heater_status = "SAFE"

        elif temperature < 32:
            heater_orange()
            heater_status = "WARM"

        else:
            heater_red()
            heater_status = "HOT"

        print("Heater :", heater_status)



# Task 3 : Cooler
async def task_cooler():
    global temperature
    global cooler_status
    global fan_status

    while True:
        await cooler_sem.acquire()

        if temperature > 30:
            cooler_on()

            fan.write_digital(1)

            cooler_status = "ON"
            fan_status = "ON"

            print("Cooler ON")

        else:
            cooler_off()

            fan.write_digital(0)

            cooler_status = "OFF"
            fan_status = "OFF"

            print("Cooler OFF")
            
            
# Task 4 : Humidifier
async def task_humidifier():
    global humidity
    global humidifier_status

    while True:
        await humidifier_sem.acquire()

        if humidity < 40:
            humidifier_green()
            humidifier_status = "LOW"

            await asleep_ms(5000)

            if humidity < 40:
                humidifier_yellow()
                humidifier_status = "MED"

                await asleep_ms(3000)

            if humidity < 40:
                humidifier_red()
                humidifier_status = "HIGH"

                await asleep_ms(2000)

        else:
            humidifier_off()
            humidifier_status = "OFF"

        print("Humidifier :", humidifier_status)



# Task 5 : Weather Prediction
async def task_weather():
    global temperature
    global humidity
    global weather

    while True:
        await weather_sem.acquire()

        # Too Hot (Blink Red)
        if temperature >= 40:
            weather = "TOO HOT"
            print("WARNING : TOO HOT")

            for i in range(10):
                neopix.show(0, hex_to_rgb("#FF0000"))
                await asleep_ms(250)
                neopix.off(0)
                await asleep_ms(250)

        # Hot (Solid Red)
        elif temperature >= 35:
            weather = "HOT"
            print("WARNING : HOT")

            neopix.show(0, hex_to_rgb("#FF0000"))

        # Cold (Blink Blue)
        elif temperature <= 15:
            weather = "COLD"
            print("WARNING : COLD")

            for i in range(10):
                neopix.show(0, hex_to_rgb("#0000FF"))
                await asleep_ms(250)
                neopix.off(0)
                await asleep_ms(250)

        # Rain (Blink Cyan)
        elif humidity >= 85 and temperature <= 27:
            weather = "RAIN"
            print("WEATHER : RAIN")

            for i in range(10):
                neopix.show(0, hex_to_rgb("#00FFFF"))
                await asleep_ms(250)
                neopix.off(0)
                await asleep_ms(250)

        # Dry (Blink Yellow)
        elif humidity < 40:
            weather = "DRY"
            print("WARNING : DRY")

            for i in range(10):
                neopix.show(0, hex_to_rgb("#FFFF00"))
                await asleep_ms(250)
                neopix.off(0)
                await asleep_ms(250)

        # Good (Solid Green)
        else:
            weather = "GOOD"
            print("WEATHER : GOOD")

            neopix.show(0, hex_to_rgb("#00FF00"))



# Task 6 : Air Quality
async def task_air():
    global air_percent
    global air_status
    global air_advice

    while True:
        await air_sem.acquire()

        if air_percent < 30:
            air_status = "GOOD"
            air_advice = "FRESH AIR"

        elif air_percent < 60:
            air_status = "NORMAL"
            air_advice = "VENTILATE"

        elif air_percent < 80:
            air_status = "POOR"
            air_advice = "OPEN WINDOW"

        else:
            air_status = "DANGER"
            air_advice = "LEAVE AREA"

        print("Air :", air_status)
        print("Advice :", air_advice)



# Task 7 : OLED Display
async def task_oled():
    while True:
        await oled_sem.acquire()

        oled.fill(0)

        oled.text("Device Status",0,0)

        oled.text("Heat :"+heater_status,0,16)
        oled.text("Cool :"+cooler_status,0,28)
        oled.text("Humi :"+humidifier_status,0,40)
        oled.text("Air  :"+air_status,0,52)

        oled.show()
        
        
# Task 8 : Heartbeat LED
async def task_blinky():
    while True:
        led13.write_digital(1)
        await asleep_ms(1000)

        led13.write_digital(0)
        await asleep_ms(1000)



# Setup
async def setup():

    print("====================================")
    print(" Smart Climate Controller (RTOS)")
    print("====================================")

    # Turn OFF all devices
    heater_off()
    cooler_off()
    humidifier_off()

    fan.write_digital(0)

    neopix.off(0)

    oled.fill(0)
    oled.text("Smart Climate",0,0)
    oled.text("Controller",0,16)
    oled.text("RTOS Starting",0,32)
    oled.show()

    await asleep_ms(2000)

    # Create Tasks
    create_task(task_sensor())
    create_task(task_blinky())
    create_task(task_heater())
    create_task(task_cooler())
    create_task(task_humidifier())
    create_task(task_weather())
    create_task(task_air())
    create_task(task_oled())



# Main
async def main():
    await setup()

    while True:
        await asleep_ms(100)



# Run Scheduler
run_loop(main())