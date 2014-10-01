#!/usr/bin/python

# Monotype composition caster & keyboard paper tower control program by Christophe Slychan
# The program reads a "ribbon" file, then waits for the user to start casting or punching the paper tape.
# In the casting mode, during each machine cycle, the photocell is obscured (high state) or lit (low state).
# When high, the program reads a line from ribbon and turns on the solenoid valves respective to the Monotype control codes.
# After the photocell is lit, the valves are turned off and the program moves on to the next line.

import sys, os, time, string, csv, readline, glob, select
import wiringpi2 as wiringpi

def input_setup():
  # We need to set up the sysfs interface before (powerbuttond.py - a daemon running on boot with root privileges takes care of it)
  # In the future, we'll add configurable GPIO numbers. Why store the device config in the program source, if we can use a .conf file?
  photocellGPIO = 14
  gpioSysfsPath = '/sys/class/gpio/gpio%s/' % photocellGPIO
  global valueFileName
  valueFileName = gpioSysfsPath + 'value'
  edgeFileName = gpioSysfsPath + 'edge'

  # Check if the photocell GPIO has been configured:
  if not os.access(valueFileName, os.R_OK):
    print('%s: file does not exist or cannot be read. You must export the GPIO no %i as input first!' % (valueFileName, photocellGPIO))
    exit()
  # Check if the interrupts are generated for photocell GPIO rising AND falling edge:
  with open(edgeFileName, 'r') as edgeFile:
    if (edgeFile.read()[:4] != "both"):
      print('%s: file does not exist, cannot be read or the interrupt on GPIO no %i is not set to "both". Check the system config.' % (edgeFileName, photocellGPIO))
      exit()

def output_setup():
  # Setup the wiringPi MCP23017 chips for valve outputs:
  wiringpi.mcp23017Setup(65,0x20)
  wiringpi.mcp23017Setup(81,0x21)
  for pin in range(65,97):
    wiringpi.pinMode(pin,1)
  # Assign wiringPi pin numbers on MCP23017s to the Monotype control codes.
  global wiringPiPinNumber
  wiringPiPinNumber = dict([('1', 65), ('2', 66), ('3', 67), ('4', 68), ('5', 69), ('6', 70), ('7', 71), ('8', 72), ('9', 73), ('10', 74), ('11', 75), ('12', 76), ('13', 77), ('14', 78), ('0005', 79), ('0075', 80), ('A', 81), ('B', 82), ('C', 83), ('D', 84), ('E', 85), ('F', 86), ('G', 87), ('H', 88), ('I', 89), ('J', 90), ('K', 91), ('L', 92), ('M', 93), ('N', 94), ('S', 95), ('O15', 96)])

  # Set up comment symbols for parsing the ribbon files:
commentSymbol = '//'

def complete(text, state):
# This function enables tab key auto-completion when you enter the filename. Will definitely come in handy.
  return (glob.glob(text+'*')+[None])[state]
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)

global inputFileName
inputFileName = ""
def enter_filename():
  global inputFileName
  inputFileName = raw_input('\n Enter the ribbon file name: ')

def menu():
# Main menu. On entering, clear the screen and turn any valves off.
  os.system('clear')
  deactivate_valves()
  print('rpi2caster - Monotype Composition Caster control utility.\n\nThis program reads a ribbon (input file) and casts the type on a Composition Caster, \nor punches a paper tape with a Monotype keyboard\'s paper tower.\n')
  ans = True
  while ans:
    print ("""
		Main menu:

		1. Load a ribbon file

		2. Cast type from ribbon file

		3. Punch a paper tape

		4. Calibrate the caster

		5. Test the valves and pinblocks



		0. Exit to shell

		""")

    if inputFileName != '':
      print('Input file name: %s\n' % os.path.realpath(inputFileName))

    ans = raw_input('Choose an option: ')
    if ans=='1':
      enter_filename()
      menu()
    elif ans=='2':
      cast(inputFileName)
    elif ans=='3':
      punch(inputFileName)
    elif ans=='4':
      print('\n Testing the machine...')
    elif ans=='5':
      raw_input('This will check if the valves, pin blocks and 0005, S, 0075 mechanisms are working. Press return to continue...')
      line_test()

    elif ans=='0':
      print('\nGoodbye! :)\n')
      exit()
    else:
      print('\nNo such option. Choose again.')

def activate_valves(mode, signals):
# Activates the valves corresponding to Monotype signals found in an array fed to the function.
# The input array can contain lowercase (a, b, g, s...) or uppercase (A, B, G, S...) signals.
# In "punch" mode, an additional line (O+15) will be activated.
  for monotypeSignal in signals:
    pin = wiringPiPinNumber[str.upper(monotypeSignal)]
    wiringpi.digitalWrite(pin,1)
    if mode == 'punch':
      wiringpi.digitalWrite(wiringPiPinNumber['O15'],1)

def deactivate_valves():
  for pin in range(65,97):
    wiringpi.digitalWrite(pin,0)


def machine_stopped():
# Allow us to choose whether we want to continue, return to menu or exit if the machine stops during casting.
  choice = raw_input("Machine not running! Check what's going on.'\n(C)ontinue, return to (M)enu or (E)xit program.")
  if choice.lower() == 'c':
    return True
  elif choice.lower() == 'm':
    menu()
  elif choice.lower() == 'e':
    exit()
  else:
    print('\nNo such option. Choose again.')

def cast(filename):
# Casting routine.
  with open(filename, 'rb') as ribbon:
    mode = 'cast'
    fileContents = reversed(list(csv.reader(ribbon, delimiter=';')))
    print('\nThe combinations of Monotype signals will be displayed on screen while the machine casts the type.\n')
    raw_input('\nInput file found. Press return to start casting.\n')
    code_reader(fileContents, mode)

def punch(filename):
# Punching routine.
# When punching, the input file is read in reversed order and an additional line (O15) is switched on for operating the paper tower.
  with open(filename, 'rb') as ribbon:
    mode = 'punch'
    fileContents = csv.reader(ribbon, delimiter=';')
    print('\nThe combinations of Monotype signals will be displayed on screen while the paper tower punches the ribbon.\n')
    raw_input('\nInput file found. Turn on the air, fit the tape on your paper tower and press return to start punching.\n')
    code_reader(fileContents, mode)

def code_reader(fileContents, mode):
# A function that works on ribbon file's contents and casts/punches signals, row by row
  for row in fileContents:
    # check if the row begins with a defined comment symbol - if so, print it but don't turn on the valves
    if ((' '.join(row)).startswith(commentSymbol)):
      print(' '.join(row)[2:])
    else:
      cast_row(row, mode, 5)
# After casting/punching is finished:
  raw_input('\nEnd of ribbon. All done. Press return to go to main menu.')
  main()

def line_test():
# Test all valves and composition caster's inputs to check if everything works and is properly connected
# Signals will be tested in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL, MNH, MNK
  for signal in [['0005'], ['S'], ['0075'], ['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7'],
              ['8'], ['9'], ['10'], ['11'], ['12'], ['13'], ['14'], ['A'], ['B'], ['C'], ['D'],
              ['E'], ['F'], ['G'], ['H'], ['I'], ['J'], ['K'], ['L'], ['M'], ['N'], ['O15'],
              ['N', 'I'], ['N', 'L'], ['M', 'N', 'H'], ['M', 'N', 'K']]:
    cast_row(signal, 'cast', 60)
  raw_input('\nTesting done. Press return to go to main menu.')

def cast_row(signals, mode, machineTimeout):
# Detect events on a photocell input and cast all signals in a row.
# Ask the user what to do if the machine is stopped (no events).
  with open(valueFileName, 'r') as gpiostate:
    po = select.epoll()
    po.register(gpiostate, select.POLLPRI)
    previousState = 0
    while 1:
      events = po.poll(machineTimeout)
      if events:
      # machine is working
        gpiostate.seek(0)
        photocellState = int(gpiostate.read())
        if photocellState == 1:
        # print signals to console, so that we know what we cast or test
          print(str.upper(' '.join(signals)))
          activate_valves(mode, signals)
          previousState = 1
        elif photocellState == 0 and previousState == 1:
          deactivate_valves()
          previousState = 0
          break
      else:
        # if machine isn't working, the photocell status is not changing
        machine_stopped()



def main():
# Main loop definition. All exceptions should be caught here.
  try:
    menu()
  except (IOError, NameError):
    raw_input("\nInput file not chosen or wrong input file name. Press return to go to main menu.\n")
    main()
  except KeyboardInterrupt:
    print("Terminated by user.")
    exit()
  finally:
    deactivate_valves()

# Do the main loop.
input_setup()
output_setup()
main()