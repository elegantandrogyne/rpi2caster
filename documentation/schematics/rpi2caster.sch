EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:special
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:vreg
LIBS:DS1882
LIBS:maxim
LIBS:rpi2caster-cache
EELAYER 27 0
EELAYER END
$Descr A4 8268 11693 portrait
encoding utf-8
Sheet 1 2
Title ""
Date "9 feb 2015"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L MCP23017 U2
U 1 1 54D77B74
P 3600 2350
F 0 "U2" H 3050 3450 50  0000 C CNN
F 1 "MCP23017" H 4050 1250 50  0000 C CNN
F 2 "MODULE" H 3100 1250 50  0001 C CNN
F 3 "DOCUMENTATION" H 3600 2300 50  0001 C CNN
	1    3600 2350
	1    0    0    -1  
$EndComp
$Comp
L CONN_20X2 P2
U 1 1 54D77BD7
P 1650 3950
F 0 "P2" H 1650 5000 60  0000 C CNN
F 1 "Raspberry Pi B+ GPIO" V 1650 3950 50  0000 C CNN
F 2 "" H 1650 3950 60  0000 C CNN
F 3 "" H 1650 3950 60  0000 C CNN
	1    1650 3950
	1    0    0    -1  
$EndComp
$Comp
L ULN2803 U4
U 1 1 54D77C40
P 6300 1350
F 0 "U4" H 6550 1850 60  0000 C CNN
F 1 "ULN2803" H 6550 850 60  0000 C CNN
F 2 "" H 6300 1350 60  0000 C CNN
F 3 "" H 6300 1350 60  0000 C CNN
	1    6300 1350
	1    0    0    -1  
$EndComp
$Comp
L ULN2803 U5
U 1 1 54D77C60
P 6300 3050
F 0 "U5" H 6550 3550 60  0000 C CNN
F 1 "ULN2803" H 6550 2550 60  0000 C CNN
F 2 "" H 6300 3050 60  0000 C CNN
F 3 "" H 6300 3050 60  0000 C CNN
	1    6300 3050
	1    0    0    -1  
$EndComp
Entry Wire Line
	5400 1100 5500 1200
Entry Wire Line
	5400 1200 5500 1300
Entry Wire Line
	5400 1300 5500 1400
Entry Wire Line
	5400 1400 5500 1500
Entry Wire Line
	5400 1500 5500 1600
Entry Wire Line
	5400 1600 5500 1700
Entry Wire Line
	4550 2300 4650 2200
Entry Wire Line
	4550 2400 4650 2300
Entry Wire Line
	4550 2500 4650 2400
Entry Wire Line
	4550 2600 4650 2500
Entry Wire Line
	4550 2700 4650 2600
Entry Wire Line
	4550 2800 4650 2700
Entry Wire Line
	4550 2900 4650 2800
Entry Wire Line
	4550 3000 4650 2900
Entry Wire Line
	4550 1450 4650 1350
Entry Wire Line
	4550 1550 4650 1450
Entry Wire Line
	4550 1650 4650 1550
Entry Wire Line
	4550 1750 4650 1650
Entry Wire Line
	4550 1850 4650 1750
Entry Wire Line
	4550 1950 4650 1850
Entry Wire Line
	4550 2050 4650 1950
Entry Wire Line
	4550 2150 4650 2050
Entry Wire Line
	5400 1000 5500 1100
Entry Wire Line
	5400 900  5500 1000
Entry Wire Line
	5400 2600 5500 2700
Entry Wire Line
	5400 2700 5500 2800
Entry Wire Line
	5400 2800 5500 2900
Entry Wire Line
	5400 2900 5500 3000
Entry Wire Line
	5400 3000 5500 3100
Entry Wire Line
	5400 3100 5500 3200
Entry Wire Line
	5400 3200 5500 3300
Entry Wire Line
	5400 3300 5500 3400
$Comp
L MCP23017 U3
U 1 1 54D77EC7
P 3600 5750
F 0 "U3" H 3050 6850 50  0000 C CNN
F 1 "MCP23017" H 4050 4650 50  0000 C CNN
F 2 "MODULE" H 3100 4650 50  0001 C CNN
F 3 "DOCUMENTATION" H 3600 5700 50  0001 C CNN
	1    3600 5750
	1    0    0    -1  
$EndComp
$Comp
L ULN2803 U6
U 1 1 54D77ED3
P 6300 4750
F 0 "U6" H 6550 5250 60  0000 C CNN
F 1 "ULN2803" H 6550 4250 60  0000 C CNN
F 2 "" H 6300 4750 60  0000 C CNN
F 3 "" H 6300 4750 60  0000 C CNN
	1    6300 4750
	1    0    0    -1  
$EndComp
$Comp
L ULN2803 U7
U 1 1 54D77ED9
P 6300 6450
F 0 "U7" H 6550 6950 60  0000 C CNN
F 1 "ULN2803" H 6550 5950 60  0000 C CNN
F 2 "" H 6300 6450 60  0000 C CNN
F 3 "" H 6300 6450 60  0000 C CNN
	1    6300 6450
	1    0    0    -1  
$EndComp
Entry Wire Line
	5400 4500 5500 4600
Entry Wire Line
	5400 4600 5500 4700
Entry Wire Line
	5400 4700 5500 4800
Entry Wire Line
	5400 4800 5500 4900
Entry Wire Line
	5400 4900 5500 5000
Entry Wire Line
	5400 5000 5500 5100
Entry Wire Line
	4550 5700 4650 5600
Entry Wire Line
	4550 5800 4650 5700
Entry Wire Line
	4550 5900 4650 5800
Entry Wire Line
	4550 6000 4650 5900
Entry Wire Line
	4550 6100 4650 6000
Entry Wire Line
	4550 6200 4650 6100
Entry Wire Line
	4550 6300 4650 6200
Entry Wire Line
	4550 6400 4650 6300
Entry Wire Line
	4550 4850 4650 4750
Entry Wire Line
	4550 4950 4650 4850
Entry Wire Line
	4550 5050 4650 4950
Entry Wire Line
	4550 5150 4650 5050
Entry Wire Line
	4550 5250 4650 5150
Entry Wire Line
	4550 5350 4650 5250
Entry Wire Line
	4550 5450 4650 5350
Entry Wire Line
	4550 5550 4650 5450
Entry Wire Line
	5400 4400 5500 4500
Entry Wire Line
	5400 4300 5500 4400
Entry Wire Line
	5400 6000 5500 6100
Entry Wire Line
	5400 6100 5500 6200
Entry Wire Line
	5400 6200 5500 6300
Entry Wire Line
	5400 6300 5500 6400
Entry Wire Line
	5400 6400 5500 6500
Entry Wire Line
	5400 6500 5500 6600
Entry Wire Line
	5400 6600 5500 6700
$Comp
L R R3
U 1 1 54D77F3C
P 2350 1550
F 0 "R3" V 2430 1550 40  0000 C CNN
F 1 "3k3" V 2357 1551 40  0000 C CNN
F 2 "~" V 2280 1550 30  0000 C CNN
F 3 "~" H 2350 1550 30  0000 C CNN
	1    2350 1550
	-1   0    0    1   
$EndComp
$Comp
L CONN_20X2 P3
U 1 1 54D78051
P 6550 9200
F 0 "P3" H 6550 10250 60  0000 C CNN
F 1 "4 x Matrix BX758" V 6550 9200 50  0000 C CNN
F 2 "" H 6550 9200 60  0000 C CNN
F 3 "" H 6550 9200 60  0000 C CNN
	1    6550 9200
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR2
U 1 1 54D7812E
P 3600 3750
F 0 "#PWR2" H 3600 3750 30  0001 C CNN
F 1 "GND" H 3600 3680 30  0001 C CNN
F 2 "" H 3600 3750 60  0000 C CNN
F 3 "" H 3600 3750 60  0000 C CNN
	1    3600 3750
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR4
U 1 1 54D7813D
P 6100 2150
F 0 "#PWR4" H 6100 2150 30  0001 C CNN
F 1 "GND" H 6100 2080 30  0001 C CNN
F 2 "" H 6100 2150 60  0000 C CNN
F 3 "" H 6100 2150 60  0000 C CNN
	1    6100 2150
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR5
U 1 1 54D7814C
P 6100 3850
F 0 "#PWR5" H 6100 3850 30  0001 C CNN
F 1 "GND" H 6100 3780 30  0001 C CNN
F 2 "" H 6100 3850 60  0000 C CNN
F 3 "" H 6100 3850 60  0000 C CNN
	1    6100 3850
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR6
U 1 1 54D7815B
P 6100 5550
F 0 "#PWR6" H 6100 5550 30  0001 C CNN
F 1 "GND" H 6100 5480 30  0001 C CNN
F 2 "" H 6100 5550 60  0000 C CNN
F 3 "" H 6100 5550 60  0000 C CNN
	1    6100 5550
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR7
U 1 1 54D7816A
P 6100 7250
F 0 "#PWR7" H 6100 7250 30  0001 C CNN
F 1 "GND" H 6100 7180 30  0001 C CNN
F 2 "" H 6100 7250 60  0000 C CNN
F 3 "" H 6100 7250 60  0000 C CNN
	1    6100 7250
	1    0    0    -1  
$EndComp
Entry Wire Line
	7100 1000 7200 1100
Entry Wire Line
	7100 1100 7200 1200
Entry Wire Line
	7100 1200 7200 1300
Entry Wire Line
	7100 1300 7200 1400
Entry Wire Line
	7100 1400 7200 1500
Entry Wire Line
	7100 1500 7200 1600
Entry Wire Line
	7100 1600 7200 1700
Entry Wire Line
	7100 1700 7200 1800
Entry Wire Line
	7100 2700 7200 2800
Entry Wire Line
	7100 2800 7200 2900
Entry Wire Line
	7100 2900 7200 3000
Entry Wire Line
	7100 3000 7200 3100
Entry Wire Line
	7100 3100 7200 3200
Entry Wire Line
	7100 3200 7200 3300
Entry Wire Line
	7100 3300 7200 3400
Entry Wire Line
	7100 3400 7200 3500
Entry Wire Line
	7100 4400 7200 4500
Entry Wire Line
	7100 4500 7200 4600
Entry Wire Line
	7100 4600 7200 4700
Entry Wire Line
	7100 4700 7200 4800
Entry Wire Line
	7100 4800 7200 4900
Entry Wire Line
	7100 4900 7200 5000
Entry Wire Line
	7100 5000 7200 5100
Entry Wire Line
	7100 5100 7200 5200
Entry Wire Line
	7100 6100 7200 6200
Entry Wire Line
	7100 6200 7200 6300
Entry Wire Line
	7100 6300 7200 6400
Entry Wire Line
	7100 6400 7200 6500
Entry Wire Line
	7100 6500 7200 6600
Entry Wire Line
	7100 6600 7200 6700
Entry Wire Line
	7100 6700 7200 6800
Entry Wire Line
	7100 6800 7200 6900
Entry Wire Line
	6950 8250 7050 8150
Entry Wire Line
	6950 8350 7050 8250
Entry Wire Line
	6950 8450 7050 8350
Entry Wire Line
	6950 8550 7050 8450
Entry Wire Line
	6950 8650 7050 8550
Entry Wire Line
	6950 8750 7050 8650
Entry Wire Line
	6950 8850 7050 8750
Entry Wire Line
	6950 10150 7050 10050
Entry Wire Line
	6950 10050 7050 9950
Entry Wire Line
	6950 9950 7050 9850
Entry Wire Line
	6950 9850 7050 9750
Entry Wire Line
	6950 9750 7050 9650
Entry Wire Line
	6950 9650 7050 9550
Entry Wire Line
	6950 9550 7050 9450
Entry Wire Line
	6950 9450 7050 9350
Entry Wire Line
	6950 8950 7050 8850
Entry Wire Line
	6050 8250 6150 8350
Entry Wire Line
	6050 8150 6150 8250
Entry Wire Line
	6050 8350 6150 8450
Entry Wire Line
	6050 8450 6150 8550
Entry Wire Line
	6050 8550 6150 8650
Entry Wire Line
	6050 8650 6150 8750
Entry Wire Line
	6050 8750 6150 8850
Entry Wire Line
	6050 8850 6150 8950
Entry Wire Line
	6050 10050 6150 10150
Entry Wire Line
	6050 9950 6150 10050
Entry Wire Line
	6050 9850 6150 9950
Entry Wire Line
	6050 9750 6150 9850
Entry Wire Line
	6050 9650 6150 9750
Entry Wire Line
	6050 9550 6150 9650
Entry Wire Line
	6050 9450 6150 9550
Entry Wire Line
	6050 9350 6150 9450
Entry Bus Bus
	7050 8000 7150 7900
Entry Wire Line
	5400 6700 5500 6800
$Comp
L R R11
U 1 1 54D7A019
P 1600 7450
F 0 "R11" V 1680 7450 40  0000 C CNN
F 1 "22k" V 1607 7451 40  0000 C CNN
F 2 "~" V 1530 7450 30  0000 C CNN
F 3 "~" H 1600 7450 30  0000 C CNN
	1    1600 7450
	1    0    0    1   
$EndComp
$Comp
L R R10
U 1 1 54D7A028
P 2100 7200
F 0 "R10" H 2180 7200 40  0000 C CNN
F 1 "3k3" V 2107 7201 40  0000 C CNN
F 2 "~" V 2030 7200 30  0000 C CNN
F 3 "~" H 2100 7200 30  0000 C CNN
	1    2100 7200
	0    -1   1    0   
$EndComp
$Comp
L PNP Q2
U 1 1 54D7A11D
P 3650 7800
F 0 "Q2" H 3650 7650 60  0000 R CNN
F 1 "BC557" H 3650 7950 60  0000 R CNN
F 2 "~" H 3650 7800 60  0000 C CNN
F 3 "~" H 3650 7800 60  0000 C CNN
	1    3650 7800
	0    -1   -1   0   
$EndComp
$Comp
L R R8
U 1 1 54D7A166
P 4150 8050
F 0 "R8" V 4230 8050 40  0000 C CNN
F 1 "10k" V 4157 8051 40  0000 C CNN
F 2 "~" V 4080 8050 30  0000 C CNN
F 3 "~" H 4150 8050 30  0000 C CNN
	1    4150 8050
	1    0    0    1   
$EndComp
$Comp
L R R9
U 1 1 54D7A17D
P 3900 8300
F 0 "R9" V 3980 8300 40  0000 C CNN
F 1 "10k" V 3907 8301 40  0000 C CNN
F 2 "~" V 3830 8300 30  0000 C CNN
F 3 "~" H 3900 8300 30  0000 C CNN
	1    3900 8300
	0    1    -1   0   
$EndComp
$Comp
L R R7
U 1 1 54D7A225
P 4800 8650
F 0 "R7" V 4880 8650 40  0000 C CNN
F 1 "2k2" V 4807 8651 40  0000 C CNN
F 2 "~" V 4730 8650 30  0000 C CNN
F 3 "~" H 4800 8650 30  0000 C CNN
	1    4800 8650
	0    1    -1   0   
$EndComp
$Comp
L GND #PWR3
U 1 1 54D7A5FC
P 3600 7400
F 0 "#PWR3" H 3600 7400 30  0001 C CNN
F 1 "GND" H 3600 7330 30  0001 C CNN
F 2 "" H 3600 7400 60  0000 C CNN
F 3 "" H 3600 7400 60  0000 C CNN
	1    3600 7400
	-1   0    0    -1  
$EndComp
$Comp
L CONN_2 P1
U 1 1 54D7A66B
P 850 10100
F 0 "P1" V 800 10100 40  0000 C CNN
F 1 "24VDC" V 900 10100 40  0000 C CNN
F 2 "" H 850 10100 60  0000 C CNN
F 3 "" H 850 10100 60  0000 C CNN
	1    850  10100
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR1
U 1 1 54D7A67F
P 2250 10800
F 0 "#PWR1" H 2250 10800 30  0001 C CNN
F 1 "GND" H 2250 10730 30  0001 C CNN
F 2 "" H 2250 10800 60  0000 C CNN
F 3 "" H 2250 10800 60  0000 C CNN
	1    2250 10800
	1    0    0    -1  
$EndComp
$Comp
L LM2576 U1
U 1 1 54D7B12C
P 2150 10100
F 0 "U1" H 1800 10350 60  0000 C CNN
F 1 "LM2576" H 2400 10350 60  0000 C CNN
F 2 "" H 2150 10100 60  0000 C CNN
F 3 "" H 2150 10100 60  0000 C CNN
F 4 "Texas Instruments" H 2150 10450 60  0001 C CNN "Manufacturer"
	1    2150 10100
	1    0    0    -1  
$EndComp
$Comp
L INDUCTOR_SMALL L1
U 1 1 54D7B30A
P 3100 10200
F 0 "L1" H 3100 10300 50  0000 C CNN
F 1 "100uH" H 3100 10150 50  0000 C CNN
F 2 "~" H 3100 10200 60  0000 C CNN
F 3 "~" H 3100 10200 60  0000 C CNN
	1    3100 10200
	1    0    0    -1  
$EndComp
$Comp
L CPSMALL C1
U 1 1 54D7B384
P 1450 10450
F 0 "C1" H 1475 10500 30  0000 L CNN
F 1 "100u/40V" H 1475 10375 30  0000 L CNN
F 2 "~" H 1450 10450 60  0000 C CNN
F 3 "~" H 1450 10450 60  0000 C CNN
	1    1450 10450
	1    0    0    -1  
$EndComp
$Comp
L CPSMALL C2
U 1 1 54D7B52F
P 3350 10450
F 0 "C2" H 3375 10500 30  0000 L CNN
F 1 "1000u/10V" H 3375 10375 30  0000 L CNN
F 2 "~" H 3350 10450 60  0000 C CNN
F 3 "~" H 3350 10450 60  0000 C CNN
	1    3350 10450
	1    0    0    -1  
$EndComp
$Sheet
S 8750 500  2050 1100
U 54D7CD0F
F0 "Outboard connections for rpi2caster interface" 50
F1 "rpi2caster-aux.sch" 50
$EndSheet
$Comp
L CONN_7 P5
U 1 1 54D7D94B
P 2700 8550
F 0 "P5" V 2670 8550 60  0000 C CNN
F 1 "CONTROL" V 2770 8550 60  0000 C CNN
F 2 "" H 2700 8550 60  0000 C CNN
F 3 "" H 2700 8550 60  0000 C CNN
	1    2700 8550
	1    0    0    -1  
$EndComp
$Comp
L CONN_4 P7
U 1 1 54D7ECB1
P 4650 8250
F 0 "P7" V 4600 8250 50  0000 C CNN
F 1 "SENSOR" V 4700 8250 50  0000 C CNN
F 2 "" H 4650 8250 60  0000 C CNN
F 3 "" H 4650 8250 60  0000 C CNN
	1    4650 8250
	1    0    0    -1  
$EndComp
$Comp
L R R2
U 1 1 54D80541
P 900 8850
F 0 "R2" V 980 8850 40  0000 C CNN
F 1 "10k" V 907 8851 40  0000 C CNN
F 2 "~" V 830 8850 30  0000 C CNN
F 3 "~" H 900 8850 30  0000 C CNN
	1    900  8850
	0    -1   -1   0   
$EndComp
$Comp
L R R1
U 1 1 54D80558
P 900 8750
F 0 "R1" V 980 8750 40  0000 C CNN
F 1 "10k" V 907 8751 40  0000 C CNN
F 2 "~" V 830 8750 30  0000 C CNN
F 3 "~" H 900 8750 30  0000 C CNN
	1    900  8750
	0    -1   -1   0   
$EndComp
$Comp
L CONN_2 P6
U 1 1 54D807E5
P 2800 4250
F 0 "P6" V 2750 4250 40  0000 C CNN
F 1 "EMERG" V 2850 4250 40  0000 C CNN
F 2 "" H 2800 4250 60  0000 C CNN
F 3 "" H 2800 4250 60  0000 C CNN
	1    2800 4250
	0    1    1    0   
$EndComp
$Comp
L R R13
U 1 1 54D807FC
P 3200 4050
F 0 "R13" V 3280 4050 40  0000 C CNN
F 1 "10k" V 3207 4051 40  0000 C CNN
F 2 "~" V 3130 4050 30  0000 C CNN
F 3 "~" H 3200 4050 30  0000 C CNN
	1    3200 4050
	-1   0    0    1   
$EndComp
$Comp
L CONN_4 P4
U 1 1 54D80D4C
P 1650 1750
F 0 "P4" V 1600 1750 50  0000 C CNN
F 1 "SERIAL" V 1700 1750 50  0000 C CNN
F 2 "" H 1650 1750 60  0000 C CNN
F 3 "" H 1650 1750 60  0000 C CNN
	1    1650 1750
	0    -1   -1   0   
$EndComp
$Comp
L CONN_3 K1
U 1 1 54D811A2
P 2000 5800
F 0 "K1" V 1950 5800 50  0000 C CNN
F 1 "1WIRE" V 2050 5800 40  0000 C CNN
F 2 "" H 2000 5800 60  0000 C CNN
F 3 "" H 2000 5800 60  0000 C CNN
	1    2000 5800
	1    0    0    -1  
$EndComp
Wire Bus Line
	4650 750  4650 2900
Wire Bus Line
	4650 750  5400 750 
Wire Bus Line
	5400 750  5400 3300
Wire Bus Line
	4650 4150 4650 6300
Wire Bus Line
	4650 4150 5400 4150
Wire Bus Line
	5400 4150 5400 6700
Wire Wire Line
	2650 5300 2650 5500
Connection ~ 2650 5400
Wire Wire Line
	2650 1000 2650 1450
Connection ~ 2650 1000
Wire Wire Line
	2650 4400 2650 5100
Wire Wire Line
	2050 2800 2050 3100
Wire Wire Line
	2050 3200 2350 3200
Wire Wire Line
	2650 5500 2350 5500
Connection ~ 2350 3200
Wire Wire Line
	6100 7200 6100 7250
Wire Wire Line
	6100 5550 6100 5500
Wire Wire Line
	3600 3700 3600 3750
Wire Wire Line
	6100 3800 6100 3850
Wire Wire Line
	6100 2100 6100 2150
Connection ~ 2350 5500
Wire Bus Line
	6050 7900 6050 10050
Wire Bus Line
	7200 7900 6050 7900
Wire Bus Line
	7050 8000 7050 10050
Connection ~ 2650 5500
Wire Wire Line
	1200 10000 1450 10000
Wire Wire Line
	2250 10650 2250 10800
Wire Wire Line
	1200 10650 3350 10650
Wire Wire Line
	1200 10200 1200 10650
Connection ~ 2050 10650
Connection ~ 2250 10650
Connection ~ 3350 10000
Connection ~ 3350 10200
Wire Wire Line
	3350 10650 3350 10550
Wire Bus Line
	7200 1100 7200 7900
Wire Wire Line
	6100 600  5200 600 
Wire Wire Line
	5200 2300 6100 2300
Wire Wire Line
	5200 4000 6100 4000
Connection ~ 5200 2300
Wire Wire Line
	5200 5700 6100 5700
Connection ~ 5200 4000
Connection ~ 5200 5700
Wire Wire Line
	2050 3500 2250 3500
Wire Wire Line
	2250 3500 2250 5400
Wire Wire Line
	2050 3700 2150 3700
Wire Wire Line
	2150 3700 2150 5300
Wire Wire Line
	5200 600  5200 10300
Wire Wire Line
	2050 2800 800  2800
Connection ~ 2050 3000
Wire Wire Line
	800  2800 800  7000
Wire Wire Line
	2850 10000 3350 10000
Wire Wire Line
	2350 1300 2350 1000
Connection ~ 2350 1000
Wire Wire Line
	2650 1900 2350 1900
Wire Wire Line
	2350 1800 2350 8250
Wire Wire Line
	6150 9050 6150 9350
Connection ~ 6150 9250
Connection ~ 6150 9150
Connection ~ 6150 9300
Wire Wire Line
	6950 9050 6950 9350
Connection ~ 6950 9250
Connection ~ 6950 9150
Wire Wire Line
	5200 10300 7200 10300
Wire Wire Line
	7200 10300 7200 9300
Wire Wire Line
	7200 9300 6950 9300
Connection ~ 6950 9300
Wire Wire Line
	1250 3100 1150 3100
Wire Wire Line
	1150 3100 1150 2700
Wire Wire Line
	1150 2700 2550 2700
Wire Wire Line
	2550 2700 2550 6250
Wire Wire Line
	2550 6250 2650 6250
Wire Wire Line
	2650 2850 2550 2850
Connection ~ 2550 2850
Wire Wire Line
	1250 3200 1050 3200
Wire Wire Line
	1050 3200 1050 2600
Wire Wire Line
	1050 2600 2450 2600
Wire Wire Line
	2450 2600 2450 6350
Wire Wire Line
	2450 2950 2650 2950
Wire Wire Line
	2450 6350 2650 6350
Connection ~ 2450 2950
Wire Wire Line
	2050 3900 2700 3900
Connection ~ 2350 3900
Connection ~ 2650 4850
Wire Wire Line
	3600 4400 2650 4400
Wire Wire Line
	650  1000 3600 1000
Wire Wire Line
	650  3800 1250 3800
Connection ~ 650  3800
Wire Wire Line
	1250 3000 650  3000
Connection ~ 650  3000
Wire Wire Line
	650  1000 650  8850
Wire Wire Line
	2650 5100 650  5100
Wire Wire Line
	2050 3800 3200 3800
Wire Wire Line
	2900 3800 2900 3900
Connection ~ 2900 3800
Wire Wire Line
	3200 4300 3200 4400
Connection ~ 3200 4400
Wire Wire Line
	1700 2100 1700 2200
Wire Wire Line
	1700 2200 2250 2200
Wire Wire Line
	2250 2200 2250 3400
Wire Wire Line
	2250 3400 2050 3400
Wire Wire Line
	2050 3300 2150 3300
Wire Wire Line
	2150 3300 2150 2300
Wire Wire Line
	2150 2300 1600 2300
Wire Wire Line
	1600 2300 1600 2100
Wire Wire Line
	900  3300 1250 3300
Wire Wire Line
	3600 7100 3600 7400
Connection ~ 3600 7200
Connection ~ 2350 7200
Connection ~ 650  5100
Connection ~ 650  8750
Wire Wire Line
	3350 7000 3350 10350
Wire Wire Line
	1150 8750 2350 8750
Wire Wire Line
	1150 8850 2350 8850
Wire Wire Line
	2350 7200 4300 7200
Wire Wire Line
	1600 7700 3450 7700
Connection ~ 1600 7700
Connection ~ 1600 7200
$Comp
L R R4
U 1 1 54D83384
P 2100 8350
F 0 "R4" V 2180 8350 40  0000 C CNN
F 1 "2k2" V 2107 8351 40  0000 C CNN
F 2 "~" V 2030 8350 30  0000 C CNN
F 3 "~" H 2100 8350 30  0000 C CNN
	1    2100 8350
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1250 3700 1150 3700
Wire Wire Line
	1150 3700 1150 8750
Wire Wire Line
	2150 5300 1300 5300
Wire Wire Line
	1300 5300 1300 8850
Connection ~ 1300 8850
Wire Wire Line
	2250 5400 1400 5400
Wire Wire Line
	1400 5400 1400 8450
Wire Wire Line
	1000 3500 1250 3500
Wire Wire Line
	1000 7200 1850 7200
Wire Wire Line
	1000 3500 1000 7200
Wire Wire Line
	900  3300 900  5800
Wire Wire Line
	900  5800 1650 5800
Wire Wire Line
	1650 5700 650  5700
Connection ~ 650  5700
Wire Wire Line
	1650 5900 1650 6100
Wire Wire Line
	1650 6100 2350 6100
Connection ~ 2350 6100
$Comp
L R R5
U 1 1 54D8448A
P 2100 8450
F 0 "R5" V 2180 8450 40  0000 C CNN
F 1 "330R" V 2107 8451 40  0000 C CNN
F 2 "~" V 2030 8450 30  0000 C CNN
F 3 "~" H 2100 8450 30  0000 C CNN
	1    2100 8450
	0    -1   -1   0   
$EndComp
$Comp
L R R6
U 1 1 54D84584
P 2100 8550
F 0 "R6" V 2180 8550 40  0000 C CNN
F 1 "2k2" V 2107 8551 40  0000 C CNN
F 2 "~" V 2030 8550 30  0000 C CNN
F 3 "~" H 2100 8550 30  0000 C CNN
	1    2100 8550
	0    -1   -1   0   
$EndComp
Wire Wire Line
	800  7000 3350 7000
$Comp
L R R12
U 1 1 54D84AD1
P 2100 8650
F 0 "R12" V 2180 8650 40  0000 C CNN
F 1 "470R" V 2107 8651 40  0000 C CNN
F 2 "~" V 2030 8650 30  0000 C CNN
F 3 "~" H 2100 8650 30  0000 C CNN
	1    2100 8650
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3850 7700 5200 7700
Connection ~ 5200 7700
Wire Wire Line
	4150 8300 4300 8300
Wire Wire Line
	4150 7800 4150 7700
Connection ~ 4150 7700
Wire Wire Line
	3650 8000 3650 8300
Connection ~ 4150 8300
Wire Wire Line
	1850 9100 3350 9100
Connection ~ 3350 9100
Wire Wire Line
	4300 7200 4300 8200
Connection ~ 4300 8100
Connection ~ 5200 9650
Wire Wire Line
	5050 8650 5200 8650
Connection ~ 5200 8650
Wire Wire Line
	4300 8400 4300 8650
Wire Wire Line
	4300 8650 4550 8650
Wire Wire Line
	1600 7700 1600 8350
Wire Wire Line
	1600 8350 1850 8350
Wire Wire Line
	1400 8450 1850 8450
Wire Wire Line
	1850 8550 1750 8550
Wire Wire Line
	1750 8550 1750 9650
Connection ~ 1750 9650
Wire Wire Line
	1850 8650 1850 9100
Connection ~ 1450 10650
Wire Wire Line
	1450 9650 1450 10350
Wire Wire Line
	1450 9650 5200 9650
Connection ~ 1450 10000
Wire Wire Line
	1450 10650 1450 10550
Wire Wire Line
	2650 2100 1800 2100
Wire Wire Line
	2350 2000 2650 2000
Connection ~ 2350 1900
Connection ~ 2350 2100
Connection ~ 2350 2000
Wire Wire Line
	1500 2100 650  2100
Connection ~ 650  2100
$Comp
L CSMALL C3
U 1 1 54D876D6
P 1600 10450
F 0 "C3" H 1625 10500 30  0000 L CNN
F 1 "100n/63V" H 1625 10400 30  0000 L CNN
F 2 "~" H 1600 10450 60  0000 C CNN
F 3 "~" H 1600 10450 60  0000 C CNN
	1    1600 10450
	1    0    0    -1  
$EndComp
$Comp
L CSMALL C4
U 1 1 54D876F3
P 2950 7100
F 0 "C4" H 2975 7150 30  0000 L CNN
F 1 "100n/63V" H 2975 7050 30  0000 L CNN
F 2 "~" H 2950 7100 60  0000 C CNN
F 3 "~" H 2950 7100 60  0000 C CNN
	1    2950 7100
	1    0    0    -1  
$EndComp
Wire Wire Line
	1450 10350 1600 10350
Wire Wire Line
	1600 10550 1600 10650
Connection ~ 1600 10650
Connection ~ 1450 10350
Connection ~ 2950 7200
Connection ~ 2950 7000
$EndSCHEMATC
