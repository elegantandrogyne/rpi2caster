#!/usr/bin/python
# -*- coding: utf-8 -*-

"""rpi2caster - control a Monotype composition caster with Raspberry Pi.

Monotype composition caster & keyboard paper tower control program.

This program sends signals to the solenoid valves connected to the
composition caster's (or keyboard's) paper tower. When casting,
the program uses methods of the Monotype class and waits for the machine
to send feedback (i.e. an "air bar down" signal), then turns on
a group of valves. On the "air bar up" signal, valves are turned off and
the program reads another code sequence, just like the original paper
tower.

The application consists of several layers:
layer 5 - user interface
layer 4 - casting job layer which implements the logic (Casting class)
layer 3 - signals processing for the caster, or mockup caster for testing
layer 2 - lower-level hardware control routines
          (activate_valves, deactivate_valves and send_signals_to_caster)
layer 1 - dependencies: wiringPi library, sysfs GPIO interface
layer 0 - hardware, kernel and /dev filesystem

In "punching" mode, the program sends code sequences to the paper tower
(controlled by valves as well) in arbitrary time intervals, and there is
no machine feedback.

rpi2caster can also:
-cast a user-specified number of sorts from a matrix with given
coordinates (the "pump on", "pump off" and "line to the galley"
code sequences will be issued automatically),
-test all the valves, pneumatic connections and control mechanisms in a
caster (i.e. pinblocks, 0005/S/0075 mechs, unit-adding & unit-shift valves
and attachments), line by line,
-send a user-defined combination of signals for a time as long as the user
desires - just like piercing holes in a piece of ribbon and clamping the
air bar down,
-help calibrating the space transfer wedge by casting a combination without
and with the S-needle with 0075 wedge at 3 and 0005 wedge at 8 (neutral)
-heat the mould up by casting some em-quads

During casting, the program automatically detects the machine movement,
so no additional actions on user's part are required.

In the future, the program will have an "emergency stop" feature.
When an interrupt on a certain Raspberry Pi's GPIO is detected, the program
stops sending codes to the caster and sends a 0005 combination instead.
The pump is immediately stopped.
"""

# IMPORTS:
# Built-in time library
import time
# Config parser for reading the interface settings
import ConfigParser
# Essential for polling the sensor for state change:
import select
# Signals parsing methods for rpi2caster:
import parsing
# Database module for rpi2caster:
import database
# User interfaces module for rpi2caster:
import userinterfaces
# Custom exceptions
import newexceptions
# MCP23017 driver & hardware abstraction layer library:
try:
    import wiringpi2 as wiringpi
    #import wiringpi
except ImportError:
    print 'Missing dependency: wiringPi2 Python bindings: wiringpi2-python'
    print 'Caster control will not work!'
# Set up a default user interface object:
# Instantiate a default text user interface
UI = userinterfaces.TextUI()


class Monotype(object):
    """Monotype(job, name, confFilePath):

    A class which stores all hardware-layer methods, related to caster control.
    This class requires a caster name, and a database object.
    """

    def __init__(self, name='Monotype', configPath='/etc/rpi2caster.conf'):
        """Creates a caster object for a given caster name
        """
        self.UI = UI
        self.name = name
        self.isPerforator = None
        self.interfaceID = None
        self.unitAdding = None
        self.diecaseSystem = None
        self.emergencyGPIO = None
        self.sensorGPIO = None
        self.mcp0Address = None
        self.mcp1Address = None
        self.pinBase = None
        self.signalsArrangement = None
        self.lock = None
        self.sensorGPIOEdgeFile = None
        self.sensorGPIOValueFile = None
        self.wiringPiPinNumber = None

        # Check if config file is readable first
        try:
            with open(configPath, 'r'):
                self.configPath = configPath
            self.cfg = ConfigParser.SafeConfigParser()
            self.cfg.read(self.configPath)
            self.caster_setup()
        except IOError:
            self.UI.display('Cannot open config file:', configPath)
        # It's not configured yet - we'll do it when needed, and only once:
        self.configured = False

    def __enter__(self):
        """Run the setup when entering the context:
        """
        self.UI.debug_info('Entering caster/interface context...')
        if self.lock:
            self.UI.display('Caster %s is already busy!' % self.name)
        else:
            self.lock = True
            return self

    def caster_setup(self):
        """Setup routine:

        Sets up initial default parameters for caster & interface:
        caster - "Monotype" (if no name is given),
        interface ID 0,
        unit-adding disabled,
        diecase format 15x17.
        """
        # Default caster parameters:
        self.isPerforator = False
        self.interfaceID = 0
        self.unitAdding = False
        self.diecaseSystem = 'norm17'
        # Default interface parameters:
        self.emergencyGPIO = 24
        self.sensorGPIO = 17
        self.mcp0Address = 0x20
        self.mcp1Address = 0x21
        self.pinBase = 65
        self.signalsArrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                                   '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
        # Next, this method reads caster data from database and fetches
        # a list of caster parameters: diecaseFormat, unitAdding, interfaceID.
        # In case there is no data, the function will run on default settings.
        self.get_caster_settings()
        self.get_interface_settings()
        # When debugging, display all caster info:
        output = {'\nCaster parameters:\n' : '',
                  'Using caster name: ' : self.name,
                  'Is a perforator? ' : self.isPerforator,
                  '\nInterface parameters:\n' : '',
                  'Interface ID: ' : self.interfaceID,
                  '1st MCP23017 I2C address: ' : self.mcp0Address,
                  '2nd MCP23017 I2C address: ' : self.mcp1Address,
                  'MCP23017 pin base for GPIO numbering: ' : self.pinBase,
                  'Signals arrangement: ' : self.signalsArrangement,
                  'Emergency button GPIO: ' : self.emergencyGPIO,
                  'Sensor GPIO: ' : self.sensorGPIO}
        for parameter in output:
            self.UI.debug_info(parameter, output[parameter])
        prompt = '[Enter] to continue...'
        self.UI.debug_enter_data(prompt)

        # This is done only for a caster interface:
        if not self.isPerforator:
        # Set up an input for machine cycle sensor:
            gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.sensorGPIO
            self.sensorGPIOValueFile = gpioSysfsPath + 'value'
            self.sensorGPIOEdgeFile = gpioSysfsPath + 'edge'
        # Check if the sensor GPIO has been configured - file is readable:
            try:
                with open(self.sensorGPIOValueFile, 'r'):
                    pass
            except IOError:
                message = ('%s : file does not exist or cannot be read. '
                           'You must export the GPIO no %s as input first!'
                           % (self.sensorGPIOValueFile, self.sensorGPIO))
                self.UI.display(message)
                self.UI.exit_program()
            # Ensure that the interrupts are generated for sensor GPIO
            # for both rising and falling edge:
            with open(self.sensorGPIOEdgeFile, 'r') as edgeFile:
                if 'both' not in edgeFile.read():
                    message = ('%s: file does not exist, cannot be read, '
                               'or the interrupt on GPIO %i is not set '
                               'to "both". Check the system configuration.'
                               % (self.sensorGPIOEdgeFile, self.sensorGPIO))
                    self.UI.display(message)
                    self.UI.exit_program()
        # Setup the wiringPi MCP23017 chips for valve outputs
        wiringpi.mcp23017Setup(self.pinBase, self.mcp0Address)
        wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)
        pins = range(self.pinBase, self.pinBase + 32)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in pins:
            wiringpi.pinMode(pin, 1)
        # Make a nice list out of the signal arrangement string:
        signalsArrangement = self.signalsArrangement.split(',')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype
        # control signals
        self.wiringPiPinNumber = dict(zip(signalsArrangement, pins))
        # Mark the caster as configured
        self.configured = True
        # Wait for user confirmation if in debug mode
        self.UI.debug_enter_data('Caster configured. [Enter] to continue... ')

    def get_caster_settings(self):
        """get_caster_settings():

        Reads the settings for a caster with self.name
        from the config file (where it is represented by a section, whose
        name is the same as the caster's).

        The parameters returned are:
        [diecase_system, unit_adding, interface_id]

        where:
        diecase_system - caster's diecase layout and a method of
        accessing 16th row, if applicable:
             norm15     - old 15x15,
             norm17     - 15x17 NI, NL,
             hmn        - 16x17 HMN (rare),
             kmn        - 16x17 KMN (rare),
             shift      - 16x17 unit-shift (most modern).
        unit_adding [0,1] - whether the machine has a unit-adding attachment,
        interface_id [0,1,2,3] - ID of the interface connected to the caster.
        """
        try:
        # Determine if it's a perforator interface
            self.isPerforator = self.cfg.get(self.name, 'is_perforator')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.isPerforator = False
        # We now know if it's a perforator
        try:
            self.interfaceID = self.cfg.get(self.name, 'interface_id')
            if not self.isPerforator:
            # Get caster parameters from conffile
                self.unitAdding = bool(self.cfg.get(self.name, 'unit_adding'))
                self.diecaseSystem = self.cfg.get(self.name, 'diecase_system')
        # Do nothing if config is wrong:
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.UI.display('Incorrect caster parameters. '
                            'Using hardcoded defaults.')
            self.UI.exception_handler()
            return None

    def get_interface_settings(self):
        """get_interface_settings():

        Reads a configuration file and gets interface parameters.

        If the config file is correct, it returns a list:
        [emergencyGPIO, sensorGPIO, mcp0Address, mcp1Address, pinBase]

        emergencyGPIO   - BCM number for emergency stop button GPIO
        sensorGPIO      - BCM number for sensor GPIO
        mcp0Address     - I2C address for 1st MCP23017
        mcp1Address     - I2C address for 2nd MCP23017
        pinBase         - pin numbering base for GPIO outputs on MCP23017

        Multiple interfaces attached to a single Raspberry Pi:

        It's possible to use up to four interfaces (i.e. 2xMCP23017, 4xULN2803)
        for a single Raspberry. It can be used for operating multiple casters,
        or a caster and a keyboard's paper tower, simultaneously (without
        detaching a valve block from the paper tower and moving it elsewhere).

        These interfaces should be identified by numbers: 0, 1, 2, 3.

        Each of the MCP23017 chips has to have unique I2C addresses. They are
        set by pulling the A0, A1, A2 pins up (to 3.3V) or down (to GND).
        There are 2^3 = 8 possible addresses, and an interface uses two chips,
        so you can use up to four interfaces.

        It's best to order the MCP23017 chips' addresses ascending, i.e.

        interfaceID    mcp0 pin        mcp1 pin        mcp0         mcp1
                       A2,A1,A0        A2,A1,A0        addr         addr
        0              000             001             0x20         0x21
        1              010             011             0x22         0x23
        2              100             101             0x24         0x25
        3              110             111             0x26         0x27

        where 0 means the pin is pulled down, and 1 means pin pulled up.

        As for pinBase parameter, it's the wiringPi's way of identifying GPIOs
        on MCP23017 extenders. WiringPi is an abstraction layer which allows
        you to control (read/write) pins on MCP23017 just like you do it on
        typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
        to registers.
        The initial 64 GPIO numbers are reserved for Broadcom SoC,
        so the lowest pin base you can use is 65.
        Each interface (2xMCP23017) uses 32 pins.

        If you are using multiple interfaces per Raspberry, you SHOULD
        assign the following pin bases to each interface:

        interfaceID        pinBase
        0                  65
        1                  98                  (pinBase0 + 32)
        2                  131                 (pinBase1 + 32)
        3                  164                 (pinBase2 + 32)
        """
        ifName = 'Interface' + str(self.interfaceID)
        try:
        # Check if the interface is active, else do nothing
            trueAliases = ['true', '1', 'on', 'yes']
            if self.cfg.get(ifName, 'active').lower() in trueAliases:
                if not self.isPerforator:
                # Emergency stop and sensor are valid only for casters,
                # perforators do not have them
                    self.emergencyGPIO = int(self.cfg.get(ifName, 'stop_gpio'))
                    self.sensorGPIO = int(self.cfg.get(ifName, 'sensor_gpio'))
                self.mcp0Address = int(self.cfg.get(ifName, 'mcp0_address'))
                self.mcp1Address = int(self.cfg.get(ifName, 'mcp1_address'))
                self.pinBase = int(self.cfg.get(ifName, 'pin_base'))
            # Check which signals arrangement the interface uses...
                signalsArrangement = self.cfg.get(ifName, 'signals_arr')
            # ...and get the signals order for it:
                self.signalsArrangement = self.cfg.get('SignalsArrangements',
                                                  signalsArrangement)
            else:
            # This happens if the interface is inactive in conffile:
                self.UI.display('Interface %i is marked as inactive!'
                                % self.interfaceID)
        # In case of wrong configuration, do nothing
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.UI.display('Incorrect interface parameters. '
                            'Using hardcoded defaults.')
            self.UI.exception_handler()
            return None

    def detect_rotation(self):
        """detect_rotation():

        Checks if the machine is running by counting pulses on a sensor
        input. One pass of a while loop is a single cycle. If cycles_max
        value is exceeded in a time <= time_max, the program assumes that
        the caster is rotating and it can start controlling the machine.
        """
        cycles = 0
        cycles_max = 3
        # Let's give it 30 seconds timeout
        time_start = time.time()
        time_max = 30
        # Subroutine definition

        def continue_after_machine_not_rotating():
            """continue_after_machine_not_rotating

            Allows user to decide what to do if the machine is not rotating.
            Continue, abort or exit program.
            """
            def continue_casting():
            # Helper function - continue casting.
                return True
            def return_to_menu():
                raise newexceptions.ReturnToMenu
            def exit_program():
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()

        # End of subroutine definition
        # Check for sensor signals, keep checking until max time is exceeded
        # or target number of cycles is reached
        with open(self.sensorGPIOValueFile, 'r') as gpiostate:
            while time.time() <= time_start + time_max and cycles <= cycles_max:
                sensorSignals = select.epoll()
                sensorSignals.register(gpiostate, select.POLLPRI)
                events = sensorSignals.poll(0.5)
            # Check if the sensor changes state at all
                if events:
                    gpiostate.seek(0)
                    sensorState = int(gpiostate.read())
                    previousState = 0
                # Increment the number of passed machine cycles
                    if sensorState == 1 and previousState == 0:
                        previousState = 1
                        cycles += 1
                    elif sensorState == 0 and previousState == 1:
                        previousState = 0
            else:
            # Determine if the loop ended due to timeout (machine not running)
            # or exceeded number of cycles (machine running):
                if cycles > cycles_max:
                    self.UI.display('\nOkay, the machine is running...\n')
                    return True
                elif continue_after_machine_not_rotating():
                # Check again recursively:
                    return self.detect_rotation()
                else:
                # This will lead to return to menu
                    return False

    def process_signals(self, signals, machineTimeout=5):
        """process_signals(signals, machineTimeout):

        Checks for the machine's rotation, sends the signals (activates
        solenoid valves) after the caster is in the "air bar down" position.

        If no machine rotation is detected (sensor input doesn't change
        its state) during machineTimeout, calls a function to ask user
        what to do (can be useful for resuming casting after manually
        stopping the machine for a short time - not recommended as the
        mould cools down and type quality can deteriorate).

        If the operator decides to go on with casting, the aborted sequence
        will be re-cast so as to avoid missing characters in the composition.

        Safety measure: this function will call "emergency_cleanup" routine
        whenever the operator decides to go back to menu or exit program
        after the machine stops rotating during casting. This is to ensure
        that the pump will not stay on afterwards, leading to lead squirts
        or any other unwanted effects.

        When casting, the pace is dictated by the caster and its RPM. Thus,
        we can't arbitrarily set the intervals between valve ON and OFF
        signals. We need to get feedback from the machine, and we can use
        contact switch (unreliable in the long run), magnet & reed switch
        (not precise enough) or a photocell sensor + LED (very precise).
        We can use a paper tower's operating lever for obscuring the sensor
        (like John Cornelisse did), or we can use a partially obscured disc
        attached to the caster's shaft (like Bill Welliver did).
        Both ways are comparable; the former can be integrated with the
        valve block assembly, and the latter allows for very precise tweaking
        of duty cycle (bright/dark area ratio) and phase shift (disc's position
        relative to 0 degrees caster position).
        """
        # Subroutine definitions
        def send_signals_to_caster(signals, timeout):
            """send_signals_to_caster:

            Sends a combination of signals passed in function's arguments
            to the caster. This function also checks if the machine cycle
            sensor changes its state, and decides whether it's an "air on"
            phase (turn on the valves) or "air off" phase (turn off the valves,
            end function, return True to signal the success).
            If no signals are detected within a given timeout - returns False
            (to signal the casting failure).
            """
            with open(self.sensorGPIOValueFile, 'r') as gpiostate:
                po = select.epoll()
                po.register(gpiostate, select.POLLPRI)
                previousState = 0
                while True:
                # Polling the interrupt file
                    events = po.poll(timeout)
                    if events:
                    # Normal control flow when the machine is working
                    # (cycle sensor generates events)
                        gpiostate.seek(0)
                        sensorState = int(gpiostate.read())
                        if sensorState == 1 and previousState == 0:
                        # Now, the air bar on paper tower would go down -
                        # we got signal from sensor to let the air in
                            self.activate_valves(signals)
                            previousState = 1
                        elif sensorState == 0 and previousState == 1:
                        # Air bar on paper tower goes back up -
                        # end of "air in" phase, turn off the valves
                            self.deactivate_valves()
                            previousState = 0
                            # Signals sent to the caster - successful ending
                            return True
                    else:
                    # Timeout with no signals - failed ending
                        return False

        def continue_after_machine_stopped():
            """continue_after_machine_stopped:

            This allows us to choose whether we want to continue,
            return to menu or exit if the machine is stopped during casting.
            """
            def continue_casting():
            # Helper function - continue casting.
                return True
            def return_to_menu():
            # Make sure the pump is turned off!
            # Raise an exception to be caught by higher-level functions
            # from the Casting class
                emergency_cleanup()
                raise newexceptions.CastingAborted
            def exit_program():
            # Also make sure the pump is turned off.
                emergency_cleanup()
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine has stopped running! Check what happened.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()

        def emergency_cleanup():
            """emergency_cleanup:

            If the machine is stopped, we need to turn the pump off and then
            turn all the lines off. Otherwise, the machine will keep pumping
            while it shouldnot (e.g. after a splash).

            The program will hold execution until the operator clears
            the situation, it needs turning the machine at least one
            full revolution.

            The program MUST turn the pump off to move on.
            """
            pumpOff = False
            stopSignal = ['N', 'J', '0005']
            self.UI.display('Stopping the pump...')
            while not pumpOff:
            # Try stopping the pump until we succeed!
            # Keep calling process_signals until it returns True
            # (the machine receives and processes the pump stop signal)
                pumpOff = send_signals_to_caster(stopSignal, machineTimeout)
            else:
                self.UI.display('Pump stopped. All valves off...')
                self.deactivate_valves()
                time.sleep(1)
                return True
        # End of subroutine definitions
        while not send_signals_to_caster(signals, 30):
        # Keep trying to cast the combination, or end here
        # (subroutine will throw an exception if operator exits)
            continue_after_machine_stopped()
        else:
        # Successful ending - the combination has been cast
            return True

    def activate_valves(self, signals):
        """activate_valves(signals):

        Activates the solenoid valves connected with interface's outputs,
        as specified in the "signals" parameter (tuple or list).
        The input array "signals" contains strings, either
        lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
        Do nothing if the function receives an empty sequence, which will
        occur if we cast with the matrix found at position O15.
        """
        if signals:
            for monotypeSignal in signals:
                pin = self.wiringPiPinNumber[monotypeSignal]
                wiringpi.digitalWrite(pin, 1)

    def deactivate_valves(self):
        """deactivate_valves():

        Turn all valves off after casting/punching any character.
        Call this function to avoid outputs staying turned on if something
        goes wrong, esp. in case of abnormal program termination.
        """
        for pin in range(self.pinBase, self.pinBase + 32):
            wiringpi.digitalWrite(pin, 0)

    def cleanup(self):
        """cleanup():

        Turn all valves off, then set all lines on MCP23017 as inputs.
        TODO: implement GPIO unsetting after wiringpi2-python gets it done.
        """
        self.UI.debug_info('Cleaning up: turning all pins off...')
        for pin in range(self.pinBase, self.pinBase + 32):
            wiringpi.digitalWrite(pin, 0)
        # Wait for user confirmation in debug mode
        self.UI.debug_enter_data('Press [Enter] to continue... ')

    def __exit__(self, *args):
        """On exit, do the cleanup:
        """
        self.UI.debug_info('Exiting caster/interface context.')
        self.lock = False
        self.cleanup()


class MonotypeSimulation(object):
    """MonotypeSimulation:

    A class which allows to test rpi2caster without an actual interface
    or caster. Most functionality will be developped without an access
    to the machine.
    """

    def __init__(self, name='Monotype Simulator', isPerforator=False):
        self.UI = UI
        self.name = name
        self.isPerforator = isPerforator

    def __enter__(self):
        self.UI.debug_info('Entering caster/keyboard simulation context...')
        # Display some info
        self.UI.display('Using caster name:', self.name)
        self.UI.display('This is not an actual caster or interface. ')
        self.UI.enter_data('Press [ENTER] to continue...')
        # Debugging is ON by default
        self.UI.debugMode = True
        return self

    def process_signals(self, signals, machineTimeout=5):
        """Simulates sending signals to the caster.

        Ask if user wants to simulate the machine stop.
        """
        def send_signals_to_caster(signals, timeout):
            prompt = '[Enter] to cast or [S] to stop? '
            if self.UI.enter_data(prompt) in ['s', 'S']:
                self.UI.display('Simulating machine stop...')
                return False
            self.UI.display('Turning the valves on...')
            self.activate_valves(signals)
            self.UI.display('Turning the valves off...')
            self.deactivate_valves()
            self.UI.display('Sequence cast successfully.')
            return True
        def continue_after_machine_stopped():
            """continue_after_machine_stopped:

            This allows us to choose whether we want to continue,
            return to menu or exit if the machine is stopped during casting.
            """
            def continue_casting():
            # Helper function - continue casting.
                return True
            def return_to_menu():
            # Make sure the pump is turned off!
            # Raise an exception to be caught by higher-level functions
            # from the Casting class
                emergency_cleanup()
                raise newexceptions.CastingAborted
            def exit_program():
            # Also make sure the pump is turned off.
                emergency_cleanup()
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine has stopped running! Check what happened.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()
        def emergency_cleanup():
            """emergency_cleanup():

            If the machine is stopped, we need to turn the pump off and then
            turn all the lines off. Otherwise, the machine will keep pumping
            while it shouldnot (e.g. after a splash).

            The program will hold execution until the operator clears the
            situation, it needs turning the machine at least one full
            revolution.

            The program MUST turn the pump off to go on.
            """
            pumpOff = False
            stopSignal = ['N', 'J', '0005']
            self.UI.display('Stopping the pump...')
            while not pumpOff:
            # Try stopping the pump until we succeed!
            # Keep calling process_signals until it returns True
            # (the machine receives and processes the pump stop signal)
                pumpOff = send_signals_to_caster(stopSignal, machineTimeout)
            else:
                self.UI.display('Pump stopped. All valves off...')
                self.deactivate_valves()
                time.sleep(1)
                return True
        # End of subroutine definitions
        while not send_signals_to_caster(signals, 30):
            # Keep trying to cast the combination, or end here
            # (subroutine will throw an exception if operator exits)
            continue_after_machine_stopped()
        else:
            # Successful ending - the combination has been cast
            return True

    def activate_valves(self, signals):
        """If there are any signals, print them out"""
        if len(signals) != 0:
            message = ('Activating valves: ' + ' '.join(signals))
            self.UI.display(message)

    def deactivate_valves(self):
        """No need to do anything"""
        self.UI.display('Valves deactivated.')

    def detect_rotation(self):
        """Detect rotation:

        Ask if the machine is rotating or not (for testing
        the machine not running scenario).
        """
        # Subroutine definition
        def continue_after_machine_not_rotating():
            """continue_after_machine_not_rotating

            Allows user to decide what to do if the machine is not rotating.
            Continue, abort or exit program.
            """
            def continue_casting():
            # Helper function - continue casting.
                return True
            def return_to_menu():
                raise newexceptions.ReturnToMenu
            def exit_program():
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()
        prompt = 'Is the machine running? [Enter] - yes, [N] - no: '
        if self.UI.enter_data(prompt) not in ['n', 'N']:
        # Machine is running
            return True
        elif continue_after_machine_not_rotating():
        # Check again recursively:
            return self.detect_rotation()
        else:
        # This will lead to return to menu
            return False

    def __exit__(self, *args):
        self.deactivate_valves()
        self.UI.debug_info('Exiting caster/keyboard simulation context.')
        pass


class Casting(object):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured:
    -caster
    -database
    -UI.

    These attributes need to be set up before casting anything.
    Normally, you instantiate the Session class and it takes care of all
    setup work.

    Ribbon filename is also an object's attribute, but it's usually
    set up via user interaction. You can also feed the filename
    to class on init.

    All methods related to operating a composition caster are here:
    -casting composition and sorts,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""

    def __init__(self, ribbonFile=''):
        self.UI = UI
        self.caster = MonotypeSimulation()
        self.ribbonFile = ribbonFile
        self.ribbon = []
        self.lineAborted = None
        self.metadata = {}
        self.diecase = None

    def __enter__(self):
        self.UI.debug_info('Entering casting job context...')
        with self.UI:
            self.main_menu()

    def cast_composition(self):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        # Count all characters and lines in the ribbon
        [linesAll, charsAll] = parsing.count_lines_and_characters(self.ribbon)
        # Characters already cast - start with zero
        currentChar = 0
        charsLeft = charsAll
        # Line currently cast: since the caster casts backwards
        # (from the last to the first line), this will decrease.
        currentLine = linesAll
        # The program counts galley trip sequences and determines line count.
        # The first code to send to machine is galley trip (which also sets the
        # justification wedges and turns the pump on). So, subtract this one
        # to have the correct number of lines.
        linesAll -= 1
        # Show the numbers to the operator
        self.UI.display('Lines found in ribbon: %i' % linesAll)
        self.UI.display('Characters: %i' % charsAll)
        # For casting, we need to read the contents in reversed order
        content = reversed(self.ribbon)
        # Display a little explanation
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the machine casts the type.\n'
                 'Turn on the machine and the program will start.\n')
        self.UI.display(intro)
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Read the reversed file contents, line by line, then parse
        # the lines, display comments & code combinations, and feed the
        # combinations to the caster
        for line in content:
        # Parse the row, return a list of signals and a comment.
        # Both can have zero or positive length.
            [rawSignals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(rawSignals)
            # A string with information for user: signals, comments, etc.
            userInfo = ''
            if parsing.check_newline(signals):
            # Decrease the counter for each started new line
                currentLine -= 1
            # Percent of all lines done:
                linePercentDone = 100 * (linesAll - currentLine) / linesAll
            # Display number of the working line,
            # number of all remaining lines, percent done
                userInfo += ('Starting line: %i of %i, %i%% done...\n'
                             % (currentLine, linesAll, linePercentDone))
            elif parsing.check_character(signals):
            # Increase the current character and decrease characters left,
            # then do some calculations
                currentChar += 1
                charsLeft -= 1
            # % of chars to cast in the line
                charPercentDone = 100 * currentChar / charsAll
            # Display number of chars done,
            # number of all and remaining chars, % done
                userInfo += ('Casting character: %i / %i, '
                             '%i remaining, %i%% done...\n'
                             % (currentChar, charsAll,
                                charsLeft, charPercentDone))
        # Append signals to be cast
            userInfo += ' '.join(signals).ljust(15)
        # Add comment
            userInfo += comment
            # Display the info
            self.UI.display(userInfo)
        # Proceed with casting only if code is explicitly stated
        # (i.e. O15 = cast, empty list = don't cast)
            if signals:
                signals = parsing.strip_O_and_15(signals)
                # Cast the sequence
                try:
                    self.caster.process_signals(signals)
                except newexceptions.CastingAborted:
                # On failure - abort the whole job.
                # Check the aborted line so we can get back to it.
                    self.lineAborted = currentLine
                    self.UI.display('\nCasting aborted on line %i.'
                                    % self.lineAborted)
                    self.UI.hold_on_exit()
                    return False
        # After casting is finished, notify the user
        self.UI.display('\nCasting finished successfully!')
        self.UI.hold_on_exit()
        return True

    def punch_composition(self):
        """punch_composition():

        When punching, the input file is read forwards. An additional line
        (O+15) is switched on for operating the paper tower, if less than
        two signals are found in a sequence.

        We can't use automatic machine cycle detection like we do in
        cast_composition, because keyboard's paper tower doesn't run
        by itself - it must get air into tubes to operate, punches
        the perforations, and doesn't give any feedback.

        For punching, O+15 are needed if <2 lines are active.
        That's because of how the keyboard's paper tower is built -
        it has a balance mechanism that advances paper tape only if two
        signals can outweigh constant air pressure on the other side.
        Basically: less than two signals - no ribbon advance...
        """
        # Count a number of combinations punched in ribbon
        combinationsAll = parsing.count_combinations(self.ribbon)
        self.UI.display('Combinations in ribbon: %i', combinationsAll)
        # Wait until the operator confirms.
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the paper tower punches the ribbon.\n')
        self.UI.display(intro)
        prompt = ('\nInput file found. Turn on the air, fit the tape '
                  'on your paper tower and press return to start punching.')
        self.UI.enter_data(prompt)
        for line in self.ribbon:
        # Parse the row, return a list of signals and a comment.
        # Both can have zero or positive length.
            [rawSignals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(rawSignals)
        # A string with information for user: signals, comments, etc.
            userInfo = ''
        # Add signals to be cast
            if signals:
                userInfo += ' '.join(signals).ljust(20)
        # Add comment
            if comment:
                userInfo += comment
        # Display the info
            self.UI.display(userInfo)
        # Send the signals, adding O+15 whenever needed
            if signals:
            # Convert O or 15 to a combined O+15 signal:"""
                signals = parsing.convert_O15(signals)
                if len(signals) < 2:
                    signals.append('O15')
            # Punch it!"""
                self.caster.activate_valves(signals)
            # The pace is arbitrary, let's set it to 200ms/200ms
                time.sleep(0.2)
                self.caster.deactivate_valves()
                time.sleep(0.2)
        # After punching is finished, notify the user:"""
        self.UI.display('\nPunching finished!')
        self.UI.hold_on_exit()
        return True

    def line_test(self):
        """line_test():

        Tests all valves and composition caster's inputs to check
        if everything works and is properly connected. Signals will be tested
        in order: 0075 - S - 0005, 1 towards 14, A towards N, O+15.
        """
        intro = ('This will check if the valves, pin blocks and 0075, S, '
                 '0005 mechanisms are working. Press return to continue... ')
        self.UI.enter_data(intro)
        combinations = (['0075', 'S', '0005']
                        + [str(n) for n in range(1, 15)]
                        + [s for s in 'ABCDEFGHIJKLMNO'])
        # Send all the combinations to the caster, one by one.
        # Set _machine_stopped timeout at 120s.
        try:
            for code in combinations:
                self.UI.display(code)
                code = parsing.signals_parser(code)
                code = parsing.convert_O15(code)
                self.caster.process_signals(code, 120)
        except newexceptions.CastingAborted:
            return False
        else:
            self.UI.display('\nTesting finished!')
            self.UI.hold_on_exit()
            return True

    def cast_sorts(self):
        """cast_sorts():

        Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        self.UI.clear()
        self.UI.display('Calibration and Sort Casting:\n\n')
        prompt = 'Enter column and row symbols (default: G 5): '
        signals = self.UI.enter_data(prompt)
        if not signals:
            signals = 'G 5'
        # Ask for number of sorts and lines
        prompt = '\nHow many sorts? (default: 10): '
        n = self.UI.enter_data(prompt)
        # Default to 10 if user enters non-positive number or letters
        if not n.isdigit() or int(n) < 0:
            n = 10
        else:
            n = int(n)
        prompt = '\nHow many lines? (default: 1): '
        lines = self.UI.enter_data(prompt)
        # Default to 10 if user enters non-positive number or letters
        if not lines.isdigit() or int(lines) < 0:
            lines = 1
        else:
            lines = int(lines)
        # Warn if we want to cast too many sorts from a single matrix
        warning = ('Warning: you want to cast a single character more than '
                   '10 times. This may lead to matrix overheating!\n')
        if n > 10:
            self.UI.display(warning)
        # Use a simple menu to ask if the entered parameters are correct
        def cast_it():
        # TODO: get rid of the ugly recursive calling!
        # Subroutine to cast chosen signals and/or repeat.
            if not self.cast_from_matrix(signals, n, lines):
            # If casting failed, exit to menu
                return False
            options = {'R' : cast_it,
                       'C' : self.cast_sorts,
                       'M' : self.main_menu,
                       'E' : self.UI.exit_program}
            message = ('\nCasting finished!\n '
                       '[R]epeat sequence, [C]hange code, [M]enu or [E]xit? ')
            choice = self.UI.simple_menu(message, options).upper()
            # Execute choice
            options[choice]()
            # End of casting subroutine.
        # After entering parameters, ask the operator if they're OK
        options = {'O' : cast_it,
                   'C' : self.cast_sorts,
                   'M' : self.main_menu,
                   'E' : self.UI.exit_program}
        message = ('Casting %s, %i lines of %i sorts.\n'
                   '[O]K, [C]hange code/quantity, [M]enu or [E]xit? '
                   % (signals, lines, n))
        choice = self.UI.simple_menu(message, options).upper()
        # Execute choice
        options[choice]()

    def cast_from_matrix(self, signals, n=5, lines=1, pos0075=3, pos0005=8):
        """cast_from_matrix(combination, n, pos0075, pos0005):

        Casts n sorts from combination of signals (list),
        with correction wedges if S needle is in action.

        By default, it sets 0075 wedge to 3 and 0005 wedge to 8 (neutral).
        Determines if single justification (0075 only) or double
        justification (0005 + 0075) is used.

        N, K and J signals are for alternate justification scheme,
        used with unit-adding attachment and turned on/off with a large
        IN/OUT valve at the backside of the caster:
        NJ = 0005
        NK = 0075
        NKJ = 0005 + 0075
        """
        # Reset the aborted line counter
        self.lineAborted = None
        # Convert the positions to strings
        pos0005 = str(pos0005)
        pos0075 = str(pos0075)
        # Signals for setting 0005 and 0075 justification wedges
        set0005 = ['N', 'J', '0005', pos0005]
        set0075 = ['N', 'K', '0075', pos0075]
        # Galley trip signal
        galleyTrip = ['N', 'K', 'J', '0005', '0075']
        # Parse the combination
        combination = parsing.signals_parser(signals)
        combination = parsing.strip_O_and_15(combination)
        # Check if the machine is running first, end here if not
        self.UI.display('Start the machine...')
        self.caster.detect_rotation()
        # We're here because the machine is rotating. Start casting the job...
        for currentLine in range(1, lines + 1):
        # Cast each line and if the CastingAborted exception is caught,
        # remember the last line and stop casting.
            try:
            # Cast the sorts: set wedges, turn pump on, cast, line out
            # Set up the justification, turn the pump on
                self.UI.display('Casting line %i of %i'
                                % (currentLine + 1, lines))
                self.UI.display('0005 wedge at ' + pos0005)
                self.caster.process_signals(set0005)
                self.UI.display('0075 wedge at ' + pos0075)
                self.UI.display('Starting the pump...')
                self.caster.process_signals(set0075)
            # Start casting characters
                self.UI.display('Casting characters...')
            # Cast n combinations of row & column, one by one
                for i in range(1, n+1):
                    info = ('%s - casting character %i of %i, %i%% done.'
                            % (' '.join(combination).ljust(20),
                               i, n, 100 * i / n))
                    self.UI.display(info)
                    parsing.strip_O_and_15(combination)
                    self.caster.process_signals(combination)
            # If everything went normally, put the line out to the galley
                self.UI.display('Putting line to the galley...')
                self.caster.process_signals(galleyTrip)
            # After casting sorts we need to stop the pump
                self.UI.display('Stopping the pump...')
                self.caster.process_signals(set0005)
            except newexceptions.CastingAborted:
                self.lineAborted = currentLine
                self.UI.display('Casting aborted on line %i'
                                % self.lineAborted)
                return False
        # We'll be here if casting ends successfully
        return True

    def send_combination(self):
        """send_combination():

        This function allows us to give the program a specific combination
        of Monotype codes, and will keep the valves on until we press return
        (useful for calibration). It also checks the signals' validity.
        """
        signals = ''
        while not signals:
            prompt = 'Enter the signals to send to the caster: '
            signals = self.UI.enter_data(prompt)
        # Parse the combination, get the signals (first item returned
        # by the parsing function)
            signals = parsing.signals_parser(signals)
        # Add O+15 signal if it was desired
            signals = parsing.convert_O15(signals)
        # Turn the valves on
        self.UI.display(' '.join(signals))
        self.caster.activate_valves(signals)
        # Wait until user decides to stop sending those signals to valves
        self.UI.enter_data('Press [Enter] to stop. ')
        self.caster.deactivate_valves()
        return True

    def align_wedges(self, spaceAt='G5'):
        """align_wedges(spaceAt='G5'):

        Allows to align the justification wedges so that when you're
        casting a 9-unit character with the S-needle at 0075:3 and 0005:8
        (neutral position), the    width is the same.

        It works like this:
        1. 0075 - turn the pump on,
        2. cast 10 spaces from the specified matrix (default: G9),
        3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
        4. cast 10 spaces with the S-needle from the same matrix,
        5. put the line to the galley, then 0005 to turn the pump off.
        """
        intro = ('Transfer wedge calibration:\n\n'
                 'This function will cast 10 spaces, then set the correction '
                 'wedges to 0075:3 and 0005:8, \nand cast 10 spaces with the '
                 'S-needle. You then have to compare the length of these two '
                 'sets. \nIf they are identical, all is OK. '
                 'If not, you have to adjust the 52D space transfer wedge.\n\n'
                 'Turn on the machine...')
        self.UI.display(intro)
        # Cast 10 spaces without correction.
        # End here if casting unsuccessful.
        self.UI.display('Now casting with a normal wedge only.')
        if not self.cast_from_matrix(spaceAt, 10):
            return False
        # Cast 10 spaces with the S-needle.
        # End here if casting unsuccessful.
        self.UI.display('Now casting with justification wedges...')
        if not self.cast_from_matrix(spaceAt + 'S', 10):
            return False
        # Finished. Return to menu.
        options = {'R' : self.align_wedges,
                   'M' : self.main_menu,
                   'E' : self.UI.exit_program}
        message = ('Done. Compare the lengths and adjust if needed.'
                   '\n[R]epeat, [M]enu or [E]xit? ')
        choice = self.UI.simple_menu(message, options).upper()
        # Execute choice
        options[choice]()

    def main_menu(self):
        """main_menu:

        Calls self.UI.menu() with options, a header and a footer.
        Options: {option_name : description}
        Header: string displayed over menu
        Footer: string displayed under menu (all info will be added here).
        """
        # Declare subroutines for menu options
        def choose_ribbon_filename():
            """choose_ribbon_filename

            Asks the user for the ribbon filename.
            Checks if the file is readable, and pre-processes it.
            """
            self.ribbonFile = self.UI.enter_input_filename()
            self.ribbon = parsing.read_file(self.ribbonFile)
            # If file read failed, end here
            if not self.ribbon:
                self.UI.display('Error reading file!')
                time.sleep(1)
                return False
            # Read the metadata at the beginning of the ribbon file
            self.metadata = parsing.get_metadata(self.ribbon)
            try:
                self.diecase = self.metadata['diecase']
            except KeyError:
                pass
            # Reset the "line aborted" on a new casting job
            self.lineAborted = None
            return True

        def debug_notice():
            """debug_notice

            Prints a notice if the program is in debug mode.
            """
            if self.UI.debugMode:
                return '\n\nThe program is now in debugging mode!'
            else:
                return ''

        def additional_info():
            """additional_info:

            Displays additional info as a menu footer.
            Starts with an empty list, and checks whether the casting job
            objects has attributes that are parameters to be displayed.
            """
            info = []
            # Add ribbon filename, if any
            if self.ribbonFile:
                info.append('Input file name: ' + self.ribbonFile)
            # Add a caster name
            info.append('Using caster: ' + self.caster.name)
            # Add metadata for ribbon
            for parameter in self.metadata:
                value = str(self.metadata[parameter])
                info.append(str(parameter).capitalize() + ': ' + value)
            # Display the line last casting was aborted on, if applicable:
            if self.lineAborted:
                info.append('Last casting was aborted on line '
                            + str(self.lineAborted))
            # Convert it all to a multiline string
            return '\n'.join(info)

        def heatup():
            """heatup

            Allows to heat up the mould before casting, in order to
            stabilize the mould temperature (affects the type quality).
            Casts two lines of em-quads, which can be thrown back to the pot.
            """
            self.UI.clear()
            self.cast_from_matrix('O15', n=20, lines=2)

        def cast_or_punch():
            """cast_or_punch:

            Determines if the caster specified for the job is actually
            a perforator - if so, a "punch ribbon" feature will be
            available instead of "cast composition".
            """
            if self.caster.isPerforator:
                return ('Punch composition', self.punch_composition)
            else:
                return ('Cast composition', self.cast_composition)

        def preview_ribbon():
            """preview_ribbon:

            Determines if we have a ribbon file that can be previewed,
            and displays its contents line by line, or displays
            an error message.
            """
            if self.ribbon:
                self.UI.clear()
                self.UI.display('Ribbon preview:\n')
                self.UI.display('\n'.join([line for line in self.ribbon]))
            else:
                self.UI.display('No ribbon to preview!')
            self.UI.enter_data('[Enter] to return to menu...')

        def exit_program():
            raise newexceptions.ExitProgram

        # End of menu subroutines
        # Now construct the menu, starting with available options
        options = {1 : 'Load a ribbon file',
                   2 : 'Preview ribbon',
                   3 : cast_or_punch()[0],
                   4 : 'Cast sorts',
                   5 : 'Test the valves and pinblocks',
                   6 : 'Lock the caster on a specified diecase position',
                   7 : 'Calibrate the 0005 and 0075 wedges',
                   8 : 'Cast two lines of 20 quads to heat up the mould',
                   0 : 'Exit program'}
        # Commands: {option_name : function}
        commands = {1 : choose_ribbon_filename,
                    2 : preview_ribbon,
                    3 : cast_or_punch()[1],
                    4 : self.cast_sorts,
                    5 : self.line_test,
                    6 : self.send_combination,
                    7 : self.align_wedges,
                    8 : heatup,
                    0 : exit_program}
        h = ('rpi2caster - CAT (Computer-Aided Typecasting) '
             'for Monotype Composition or Type and Rule casters.'
             '\n\n'
             'This program reads a ribbon (input file) '
             'and casts the type on a composition caster.'
             + debug_notice() + '\n\nMain Menu:')
        # Keep displaying the menu and go back here after any method ends
        while True:
            choice = self.UI.menu(options, header=h, footer=additional_info())
            # Call the function and return to menu.
            try:
            # Catch "return to menu" and "exit program" exceptions here
                if choice in [0, 1, 2]:
                    commands[choice]()
                else:
                # Use the caster context for everything that needs it.
                # (casting, punching, testing routines)
                    with self.caster:
                        commands[choice]()
            except newexceptions.ReturnToMenu:
            # Will skip to the end of the loop, and start all over
                pass
            except newexceptions.ExitProgram:
            # Will exit program
                self.UI.exit_program()

    def __exit__(self, *args):
        self.UI.debug_info('Exiting casting job context.')
        pass


class Session(object):
    """Session:

    This is a top-level abstraction layer.
    Used for injecting dependencies for objects.
    """
    def __init__(self, job, caster, UI, db):
        # Set dependencies as object attributes.
        # Make sure we've got an UI first.
        try:
            assert (isinstance(UI, userinterfaces.TextUI)
                    or isinstance(UI, userinterfaces.WebInterface))
        except NameError:
            print 'Error: User interface not specified!'
            exit()
        except AssertionError:
            print 'Error: User interface of incorrect type!'
            exit()
        # Make sure database and config are of the correct type
        try:
            assert isinstance(db, database.Database)
        except NameError:
        # Not set up? Move on
            pass
        except AssertionError:
        # We can be sure that UI can handle this now
            UI.display('Invalid database!')
            UI.exit_program()
        # We need a job: casting, setup, typesetting...
        try:
        # Any job needs UI and database
            job.UI = UI
            job.db = db
        # UI needs job context
            UI.job = job
        except NameError:
            UI.display('Job not specified!')
        # Database needs UI to communicate messages to user
        db.UI = UI
        # Assure that we're using a caster or simulator for casting
        try:
            if isinstance(job, Casting):
                assert (isinstance(caster, Monotype)
                or isinstance(caster, MonotypeSimulation))
        # Set up mutual dependencies
                job.caster = caster
                caster.UI = UI
                caster.job = job
        except (AssertionError, NameError, AttributeError):
            UI.display('You cannot do any casting without a proper caster!')
            UI.exit_program()
        # An __enter__ method of UI will call main_menu method in job
        with job:
            pass


# End of class definitions.
# And now, for something completely different...
# Initialize the console interface when running the program directly.
if __name__ == '__main__':
    monotype = Monotype(name='mkart-cc')
    UI = userinterfaces.TextUI()
    db = database.Database()
    job = Casting()
    session = Session(job, monotype, UI, db)
