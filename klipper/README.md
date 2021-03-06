# [Monoprice](https://mpminidelta.monoprice.com) [Mini Delta](https://www.mpminidelta.com) with RAMPS 1.4 and klipper.

Hardware
- [Arduino Mega 2560 Rev3](https://store.arduino.cc/usa/arduino-mega-2560-rev3)
- [RAMPS 1.4](https://reprap.org/wiki/RAMPS_1.4)
- [DRV8825](https://www.pololu.com/product/2133) stepper drivers
- Power supply from an old router providing 12V/10A and 160W max
- Stock stepper motors, extruder and frame.

Software
- [OctoPrint](https://octoprint.org) running on Raspberry Pi v3 B+
- [Klipper](https://github.com/KevinOConnor/klipper) host installed on the same RPi
- [Klipper](https://www.patreon.com/koconnor/overview) client/firmware installed on Arduino

Shop
- I have this (EUR30): [Popprint Ramps 1.4 With Mega2560 R3 + LCD 12864 Smart Display Controller Module 5 x Driver DRV8825 Stepper Motor Driver Module](https://www.amazon.de/gp/product/B0749GV6L8/)
- Alternative (EUR35), w/o drivers, but single board: [Popprint MKS Gen V1.4 Controller Board Integrated Ramps 1.4 + Mega 2560 Board](https://www.amazon.de/gp/product/B06Y671CKL/)

### Project
The main driver for this project is to run some other firmware that stock on MPMD printer. The stock firmware is very limited in configuration and buggy. For example, the stock firmware does not allow confguration for individual diagonal rod lengths and tower angles. And this is pretty upsetting since the build can not be 100% flawless and all small deviations do add up to weird moves of the effector, resulting in squares printed are not exactly square and making a nice first layer an unreachable dream.

I've started with a port of [Marlin for MPMD](https://github.com/mcheah/Marlin4MPMD), made by Mickey Rozay. It does work, but based on some old Marlin version, pre 1.1.0 and lacked at the moment some nice features like delta calibration.

Klipper project, on the other hand has nice idea of using general purpose hardware (like RPi) for GCODE parser and planner and having just tiny client on printer controller that calculates nothing, just moves motors as requested from the host.
The problem is Klipper has not port for STM32F0 chip MPMD has on its stock board. In turn it supports Arduino/RAMPS and I was lucky to find RAMPS 1.4 package with Arduino 2560 and drivers for just $30. DRV8825 drivers are capable of 1/32 microstepping, compared with stock 1/8.
All this combined, I've decided to give RAMPS a try first, planning to return to the stock board in the future and make a port of klipper fw to MPMD board. 

Big thanks and kudos go to Mickey Rozay who helps me a whole lot along the way.

### Setting up drivers
#### Adjusting Current
Amperage on drivers MUST be adjusted, stock 3A is too high for MPMD motors that can consume 0.5A max.  
Formula from documentation: `Current Limit = VREF × 2`

- Turn ON the board
- Measure V between GND pin on the driver and trim pot (the thing you can adjust with a screwdriver) on the driver
- Adjust trim until voltage is approx. 0.250V, this gives current limit of 0.5A

Motors MUST NOT be hot, just slightly warm.

#### Configuring microsteps
There are 3 jumpers under each motor driver on RAMPS board, install them according to the table below.
1/8 microstepping is default on MPMD; 1/32 makes motors too weak, in my experience, and 1/16 is a good compromise.
```
jumper   Yes/No  step size
 1     2    3
yes  yes   no    1/8 step
no   no    yes   1/16 step
yes  no    yes   1/32 step
```
Formula to calculate **step_distance** for klipper config:  
`1 / ((steps per mm * microsteps) / pulley tooth number / belt pitch)`  
For MPMD with DRV8825 configured for 1/16 microstepping:  
`step_distance: 0.00875` = `1/((200*16)/14/2)`

### Wiring
TODO
- http://www.instructables.com/id/Wiring-3D-Printer-RAMPS-14/
- https://3dprinting.stackexchange.com/questions/5221/how-do-i-use-mega-pin-number-designations-rather-than-ramps-pin-numbers-in-marli

### Calibration
TODO
#### End stops and tower angles
 - `DELTA_CALIBRATE`
 - *edit printer.cfg*
 - `RESTART`
#### Individual diagonal rod lengths
- Print scaled down to 50mm on Y dimention: https://www.thingiverse.com/thing:1274733
- Put numbers into spread sheet
- Set new **arm_length** for all 3 steppers in *printer.cfg*
- `RESTART`

## Other

- https://github.com/rcarlyle/StepperSim
- https://github.com/manticorp/GCodeArcOptimiser
- [G2&G3 on klipper](https://github.com/cruwaller/klipper/commit/fc3fffda5f108007bd75614e2b34fbeacc1af344)
