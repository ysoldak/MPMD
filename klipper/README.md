# Running Monoprice Mini Delta with [Ramps 1.4](https://reprap.org/wiki/RAMPS_1.4) and klipper.

Setup I have:
- AtMega2560
- RAMPS 1.4
- [DRV8825](https://www.pololu.com/product/2133) stepper drivers

### Setting up drivers
#### Adjusting Current
Amperage on drivers MUST be adjusted, stock 3A is too high for MPMD motors that can consume 0.5A max.  
Formula from documentation: `Current Limit = VREF × 2`

- Turn ON the board
- Measure V between GND pin on the driver and potentiometer (the thing you can adjust with a screwdriver) on the driver
- Adjust potentiometer until voltage is approx. 0.250V, this gives current limit of 0.5A

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
Formula to calculate **step_distance** for klipper config and MPMD:  
`step_distance: 1/((200*M)/T/2)`, here M is microsteps (8, 16 or 32) and T is number of teeth on motor pulley, stock is 14, I use 16T.

Stock pulley + 1/16 microsteps gives us: `step_distance: 0.00875`
