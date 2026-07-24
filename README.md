# RTOS_Project

An RTOS-based Smart Climate Controller developed for the Yolo:UNO platform using Python and `asyncio`.

## Features

- Temperature and humidity monitoring (DHT20)
- Air quality monitoring (MQ135)
- Automatic heater control
- Automatic cooler and fan control
- Three-stage humidifier control
- Weather indication using onboard NeoPixel
- LCD1602 environmental display
- OLED controller status display
- RTOS task synchronization using binary semaphores

## Hardware

- Yolo:UNO 
- DHT20
- MQ135
- LCD1602
- OLED I2C Display
- Onboard NeoPixel
- 3 RGB LED Modules
- Cooling Fan

## Software

- Python
- asyncio
- Yolo:UNO Libraries

## Project Structure

```
.
├── main.py
├── README.md
└── assets/
```

## RTOS Tasks

- Sensor Task
- Heater Task
- Cooler Task
- Humidifier Task
- Weather Task
- Air Quality Task
- OLED Task
- Blinky Task

## Running the Project

1. Open the project in the Yolo:UNO IDE.
2. Connect the required hardware (or use the simulator).
3. Upload and run `main.py`.

## Notes

- Sensor data is shared between tasks using global variables.
- Binary semaphores synchronize all consumer tasks after each sensor update.
- The LCD displays environmental information.
- The OLED displays controller status.
- The NeoPixel provides visual weather indications.

## Authors

Real-Time Operating Systems Course Project

Vietnam-German University (VGU)
