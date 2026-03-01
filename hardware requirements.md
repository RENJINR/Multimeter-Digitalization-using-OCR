# Hardware Requirements

## Essential Components

| Component | Model/Specification | Quantity | Purpose |
|-----------|-------------------|----------|---------|
| **ESP32-CAM** | AI-Thinker ESP32-CAM (with OV2640) | 1 | Captures multimeter display |
| **Arduino Board** | Arduino UNO R3 | 1 | Generates variable voltage |
| **Multimeter** | Digital Multimeter | 1 | Displays voltage to be read |
| **USB Cable** | USB-A to Micro-USB | 1 | For ESP32-CAM |
| **USB Cable** | USB-A to USB-B | 1 | For Arduino UNO |
| **Jumper Wires** | Male-to-Female | 5-10 | Connections |

## Optional Components

| Component | Specification | Purpose |
|-----------|--------------|---------|
| LED | 5mm any color | Flash illumination |
| Resistor | 220Ω | Current limiting for LED |
| Breadboard | 400 points | Prototyping |

## Pin Configuration (from camera_pins.h)

```cpp
// ESP32-CAM AI-Thinker Pin Configuration
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22