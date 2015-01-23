#!/usr/bin/python

"""rpi2caster - control a Monotype composition caster with Raspberry Pi.

Monotype composition caster & keyboard paper tower control program.
The program reads a "ribbon" file, then waits for the user to start
casting or punching the paper tape. In the casting mode, during each
machine cycle, the photocell is lit (high state) or obscured (low).
When high, the program reads a line from ribbon and turns on
the solenoid valves respective to the Monotype control codes.
After the photocell is lit (low state on input), the valves are
turned off and the program moves on to the next line."""

"""Typical libs, used by most routines:"""
import sys
import os
import time
import string

"""Used for serializing lists stored in database, and for communicating
with the web application (in the future):"""
import json

"""These libs are used by file name autocompletion:"""
import readline
import glob

"""Essential for polling the photocell for state change:"""
import select

"""MCP23017 driver & hardware abstraction layer library:"""
try:
  import wiringpi2 as wiringpi
except ImportError:
  print('wiringPi2 not installed! It is OK for testing, \
  but you MUST install it if you want to cast!')
  time.sleep(1)

"""rpi2caster uses sqlite3 database for storing caster, interface,
wedge, diecase & matrix parameters:"""
try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()

"""This determines whether some exceptions will be caught
or thrown to stderr, off by default:"""
global DebugMode
DebugMode = False


class DatabaseBackend(object):
  """DatabaseBackend:

  Read/write data for casters, interfaces, diecases, matrices and wedges
  from/to designated sqlite3 database"""

  def __init__(self, databasePath='database/monotype.db'):
    self.databasePath = databasePath


  def add_caster(self, casterSerial, casterName, casterType,
                 unitAdding, diecaseSystem, interfaceID=0):

    """add_caster(self, casterSerial, casterName, casterType,
                  unitAdding, diecaseSystem, interfaceID=0)

    Register a new caster in the database.

    The function uses a SQL query to create a new entry for a caster
    with parameters passed as arguments.

    Explanation of input parameters:

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.

        Must be integer - default: 0

    If we want to use a single Raspberry Pi with several valvesets
    connected at the same time, we have to configure more interfaces.
    Each interface consists of 32 solenoid valves, two MCP23017 I/O,
    expanders, four ULN2803 drivers, a photocell (with its GPIO pin)
    and an emergency stop button (with its GPIO pin as well).

    Each MCP23017 MUST have its unique I2C address, which is set by
    tying pins A0, A1 and A2 to 3V3 or GND. Typically, you tie all
    pins to GND on the first chip (a.k.a. mcp0), and tie A0 to 3V3,
    A1 and A2 to GND on the second chip (a.k.a. mcp1) for interface id=0.
    The hex addresses of the chips mcp0 and mcp1 will be 0x20 and 0x21
    respectively. See the table below.

    If you configure additional interfaces, it's best to order the
    MCP23017 chips' addresses ascending, i.e.

    interfaceID    mcp0 pin    mcp1 pin    mcp0     mcp1
                   A2,A1,A0    A2,A1,A0    addr     addr

    0              000         001         0x20     0x21
    1              010         011         0x22     0x23
    2              100         101         0x24     0x25
    3              110         111         0x26     0x27

    0 means pin tied to GND and 1 means pin tied to 3V3.

    We can define up to 4 interfaces per Raspberry, because maximum
    of 8 MCP23017 chips can work on a single I2C bus, and there are
    two MCP23017s per interface.
    """

    data = (int(casterSerial), casterName, casterType,
            int(unitAdding), diecaseSystem, int(interfaceID))

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()

        """Make sure that the table exists, if not - create it"""
        cursor.execute(
                      'CREATE TABLE IF NOT EXISTS caster_settings ('
                      'id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                      'caster_serial INTEGER NOT NULL, '
                      'caster_name TEXT UNIQUE NOT NULL, '
                      'caster_type TEXT NOT NULL, '
                      'unit_adding INTEGER NOT NULL, '
                      'diecase_system TEXT NOT NULL, '
                      'interface_id INTEGER NOT NULL)'
                      )

        """Create an entry for the caster in the database"""
        cursor.execute(
                      'INSERT INTO caster_settings '
                      '(caster_serial, caster_name, '
                      'caster_type, unit_adding, '
                      'diecase_system, interface_id) '
                      'VALUES (?, ?, ?, ?, ?, ?)', data
                      )
        db.commit()
      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error:')
        if DebugMode:
          raise
      finally:
        pass

  def list_casters(self):
    """list_casters(self):

    List all casters stored in database, or display a message
    if the table does not exist.

    Explanation of columns:

    ID: unique caster entry's ID

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM caster_settings')
        print('\nID, serial No, name, type, unit adding, diecase system, \
        interface ID\n')
        """loop over rows unless an empty row is found, then stop"""
        while True:
          caster = cursor.fetchall()
          if caster != '':
            for row in caster:
              print row
            return True
          else:
            break
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: caster_settings table does not exist in database '
              '- not configured yet?\n')
        if DebugMode:
          raise
      finally:
        pass

  def caster_by_name(self, casterName):
    """caster_by_name(self, casterName):

    Get caster parameters for a caster with a given name.

    The function returns a list: [ID, casterSerial, casterName,
    casterType, unitAdding, diecaseSystem, interfaceID]
    for the first caster with a specified name.

    Explanation of parameters:

    ID: unique caster entry's ID

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.

    If no caster matches, the function returns False.
    """
    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
        'SELECT * FROM caster_settings WHERE caster_name = %s' % casterName
        )
        caster = cursor.fetchone()

        """Check if the function found anything:"""
        if caster is not None:
          return caster
        else:
          print('No casters found!\n')
          return False
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot retrieve caster settings!\n')
        if DebugMode:
          raise
        return False


  def caster_by_id(self, ID=0):
    """caster_by_id(self, ID=0)

    Caster by ID number:

    Get caster parameters for a caster with a given ID number (unique).

    If the ID number is not supplied, the function assumes 0 -
    which is OK, if we have a single caster without configuration changes.

    We can add more caster entries with add_caster, and get configuration
    for any them by its ID. That is useful in case we have several casters,
    or multiple configurations for a single caster in our database
    (that happens if we frequently turn unit shift or unit adding
    on or off - these attachments change the way caster interprets some
    signals, i.e. 0005 and 0075 are no longer used for justification).

    The function returns a list: [ID, casterSerial, casterName,
    casterType, unitAdding, diecaseSystem, interfaceID]
    for the caster with a specified ID.

    Explanation of parameters:

    ID: unique caster entry's ID

    casterSerial: caster's serial number (on nameplate on paper tower),

    casterName: a string for a caster's name,

    casterType: the type of composition caster:
        comp (composition caster),
        large_comp (large comp. caster, a.k.a. type & rule caster)

    unitAdding: determines if the unit adding attachment is on,
        or turned off / not present; if on - justification mode is changed,
        so 0005 is replaced by NJ, 0075 by NK, double justification is NJK;

        possible options: True (UA on), False (UA off / not present)

    diecaseSystem: what diecases the machine supports, possible options:
        norm15 (15x15),
        norm17 (15x17 NI, NL),
        hmn (16x17 HMN),
        kmn (16x17 KMN),
        shift (16x17 unit-shift - D signal activates unit shift,
               EF is used for accessing column D of a diecase)

    interfaceID: the interface ID, i.e. a set of MCP23017 chips and
        photocell & emergency stop GPIO lines the caster uses.

    If no caster is found, the function returns False.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM caster_settings WHERE id = %i' % ID)
        caster = cursor.fetchone()
        if caster is not None:
          return caster
        else:
          print('No casters found!\n')
          return False
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot retrieve caster settings!\n')
        if DebugMode:
          raise
        return False

  def delete_caster(self, ID):
    """delete_caster(self, ID):

    Deletes a caster with a given ID from database.
    """
    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM caster_settings WHERE id=?',ID)
        db.commit()
        print('Caster id=%i successfully deleted' % ID)
        return True
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot delete caster!\n')
        if DebugMode:
          raise
        return False


  def add_interface(self, interfaceName, emergencyGPIO,
                    photocellGPIO, mcp0Address, mcp1Address, pinBase):
    """add_interface(self, interfaceID, interfaceName, emergencyGPIO,
                     photocellGPIO, mcp0Address, mcp1Address, pinBase):

    Registers a Raspberry Pi to Monotype caster interface.

    Use arguments to register a new interface, i.e. I2C expander params,
    emergency stop GPIO and photocell GPIO. The function uses a SQL query
    to add an entry to the database.

    Arguments:

    interfaceID - integer (0...3), auto-incremented, unique

    interfaceName - string, name for an interface (e.g. "caster1")

    emergencyGPIO - emergency button GPIO (Broadcom number), integer,
        must be unique, can be null

    photocellGPIO - photocell GPIO (Broadcom number), integer, must be
        unique, cannot be null

    mcp0Address - mcp0 (first MCP23017) I2C address, hex number
        (e.g. 0x20), must be unique, cannot be null

    mcp1Address - mcp1 (second MCP23017) I2C address, hex number
        (e.g. 0x21), must be unique, cannot be null

    pinBase - integer, base number for pins supplied by the first
        MCP23017 chip (i.e. mcp0). Must be unique, cannot be null.
        Minimum: 65 (0...64 are used by system, so they are reserved).

        Each interface uses 32 pins.

        If you are using multiple interfaces per Raspberry, you SHOULD
        assign the following pin bases to each interface:

        interfaceID    pinBase

        0              65
        1              97          (pinBase0 + 32)
        2              129         (pinBase1 + 32)
        3              161         (pinBase2 + 32)
    """

    """Data we want to write to the database:"""
    data = (int(interfaceID), interfaceName, emergencyGPIO, photocellGPIO,
        json.dumps(mcp0Address), json.dumps(mcp1Address), pinBase)

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        """Create the table first:"""
        cursor.execute(
                      'CREATE TABLE IF NOT EXISTS interface_settings '
                      '(id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                      'interface_name TEXT UNIQUE, '
                      'emergency_gpio INTEGER UNIQUE, '
                      'photocell_gpio INTEGER UNIQUE NOT NULL, '
                      'mcp0_address TEXT UNIQUE NOT NULL, '
                      'mcp1_address TEXT UNIQUE NOT NULL, '
                      'pin_base INTEGER UNIQUE NOT NULL)'
                       )
        """Then add an entry:"""
        cursor.execute(
                      'INSERT INTO interface_settings (id,'
                      'interface_name,emergency_gpio,photocell_gpio,'
                      'mcp0_address,mcp1_address,pin_base) '
                      'VALUES (?, ?, ?, ?, ?, ?, ?)', data
                       )
        db.commit()
      finally:
        pass


  def get_interface(self, interfaceID=0):
    """
    Get interface:

    Return parameters for an interface with a given ID, most typically 0
    for a Raspberry Pi with a single interface (2xMCP23017 & 4xULN2803).

    If no arguments are supplied, get parameters for interface_id == 0.

    This function returns a list: [interfaceID, interfaceName,
    emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase].

    Interface parameters:

    interfaceID - interface ID (0...3)

    interfaceName - name for an interface (e.g. "caster1")

    emergencyGPIO - emergency button GPIO (Broadcom number)

    photocellGPIO - photocell GPIO (Broadcom number)

    mcp0Address - mcp0 (first MCP23017) I2C address, hex number
        (e.g. 0x20)

    mcp1Address - mcp1 (second MCP23017) I2C address, hex number
        (e.g. 0x21)

    pinBase - integer, base number for pins supplied by the first
        MCP23017 chip (i.e. mcp0).
    """
    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
        'SELECT * FROM interface_settings WHERE id = %i' % interfaceID
        )
        interface = cursor.fetchone()
        if interface is not None:
          interface = list(interface)
          """Correction to return proper hex values for I2C addresses:"""
          interface[4] = hex(json.loads(interface[4]))
          interface[5] = hex(json.loads(interface[5]))
          return interface
        else:
          print('No interface with a given ID found!\n')
          return False
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot retrieve interface settings!\n')
        if DebugMode:
          raise

  def list_interfaces(self):
    """List interfaces:

    List all interfaces stored in database with their parameters.


    Interface parameters:

    ID - interface ID (0...3)

    name - name for an interface (e.g. "caster1")

    emergency GPIO - emergency button GPIO (Broadcom number)

    photocell GPIO - photocell GPIO (Broadcom number)

    mcp0 addr - mcp0 (first MCP23017) I2C address, hex number
        (e.g. 0x20)

    mcp1 addr - mcp1 (second MCP23017) I2C address, hex number
        (e.g. 0x21)

    pin base - integer, base number for pins supplied by the first
        MCP23017 chip (i.e. mcp0).
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM interface_settings')
        print('\nID, name, emergency GPIO, photocell GPIO, MCP0 addr, MCP1 addr, pin base:\n')
        while True:
          interface = cursor.fetchone()
          if interface is not None:
            interface = list(interface)
            """Correction to return proper hex values for I2C addresses:"""
            interface[4] = hex(json.loads(interface[4]))
            interface[5] = hex(json.loads(interface[5]))
            print '   '.join(interface)
          else:
            break
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: interface_settings table not found '
              'in database - not configured yet?\n')
        if DebugMode:
          raise
      finally:
        pass

  def add_wedge(self, wedgeID, setWidth, oldPica, steps):
    """add_wedge(self, wedgeID, setWidth, oldPica, steps):

    Registers a wedge in our database.

    Arguments:

    wedgeID - wedge's number, e.g. S5 or 1160. String, cannot be null.

    setWidth - set width of a wedge, e.g. 9.75. Float, cannot be null.

    oldPica - determines if it's an old pica system (i.e. 1pica = 0.1667")
        If the wedge has "E" at the end of its number (e.g. 5-12E), then
        it's an old-pica wedge.
        1, True, 0, False.

    steps - a list with unit values for each of the wedge's steps.
        Not null.

    An additional column, id, will be created and auto-incremented.
    This will be an unique identifier of a wedge.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        """Create the table first:"""
        cursor.execute(
        'CREATE TABLE IF NOT EXISTS wedges (id primary_key, \
        wedge_id text not_null, set_width real not_null, \
        old_pica integer not_null, steps text not_null)'
        )
        """Then add an entry:"""
        cursor.execute(
        'INSERT INTO wedges (wedge_id,set_width,old_pica,steps) \
        VALUES (%s, %f, %i, %s)'
        % wedgeID, setWidth, int(oldPica), json.dumps(steps)
        )
        db.commit()
      finally:
        pass


  def get_wedge(self, wedgeID, setWidth):
    """get_wedge(self, wedgeID, setWidth):

    Checks if a wedge with given ID and set width is registered in database.

    If so, returns:
    ID - unique, int (e.g. 0),
    wedgeID - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Else, returns False.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM wedges WHERE wedge_id = %s \
                      AND set_width = %f' % wedgeID, setWidth)
        wedge = cursor.fetchone()
        if wedge is None:
          print('No wedge %s - %f found in database!' % wedgeID, setWidth)
          return False
        else:
          print('Wedge found in database - OK')
          """Change return value of oldPica to boolean:"""
          wedge[3] = bool(wedge[3])
          """Change return value of steps to list:"""
          wedge[4] = json.loads(wedge[4])
          return wedge
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot get wedge - not configured yet?\n')
        if DebugMode:
          raise
      finally:
        pass


  def delete_wedge(self, ID):
    """delete_wedge(self, ID):

    Deletes a wedge with given unique ID from the database
    (useful in case we no longer have the wedge).
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
        'DELETE FROM wedges WHERE id = %i' % ID
        )
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot delete wedge - not configured yet?\n')
        if DebugMode:
          raise

  def list_wedges(self):
    """list_wedges(self):

    Lists all wedges stored in database, with their step unit values.

    Prints the following to stdout:

    ID - unique, int (e.g. 0),
    wedgeID - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM wedges')
        print(
        '\nid, wedgeID, set width, old pica, unit values for all steps:\n'
        )
        while True:
          wedge = cursor.fetchone()
          if wedge is not None:
            wedge[3] = bool(wedge[3])
            """Change return value of steps to list:"""
            wedge[4] = json.loads(wedge[4])
            print '   '.join(wedge)
          else:
            break
      except sqlite3.OperationalError:
        """In debug mode we get the exact exception code & stack trace."""
        print('Error: cannot list wedges - not configured yet?\n')
        if DebugMode:
          raise
      finally:
        pass


class Monotype(DatabaseBackend):
  """Monotype class:

  A class which stores all methods related to the interface and
  caster itself."""

  def __init__(self, casterName):
    """Setup routine:

    After the class is instantiated, this method reads caster data
    from database and fetches a list of caster parameters: [serialNumber,
    casterName, casterType, justification, diecaseFormat, interfaceID].
    """
    #self.casterName = casterName
    casterParameters = self.caster_by_name(casterName)

    """Parse the obtained parameters:"""

    [casterID, casterSerial, casterName,
    casterType, unitAdding, diecaseSystem,
    interfaceID] = casterParameters

    """
    self.casterID      = casterParameters[0]
    self.casterSerial  = casterParameters[1]
    self.casterName    = casterParameters[2]
    self.casterType    = casterParameters[3]
    self.unitAdding    = casterParameters[4]
    self.diecaseSystem = casterParameters[5]
    self.interfaceID   = casterParameters[6]
    """

    """
    Then, the interface ID is looked up in the database, and interface
    parameters are known: [interfaceID, interfaceName, emergencyGPIO,
    photocellGPIO, mcp0Address, mcp1Address, pinBase]
    """
    interfaceParameters = self.get_interface(interfaceID)

    [interfaceName, emergencyGPIO, photocellGPIO,
    mcp0Address, mcp1Address, pinBase] = interfaceParameters

    """Parse the obtained parameters:"""
    """
    self.interfaceName = interfaceParameters[1]
    self.emergencyGPIO = interfaceParameters[2]
    self.photocellGPIO = interfaceParameters[3]
    self.mcp0Address = interfaceParameters[4]
    self.mcp1Address = interfaceParameters[5]
    self.pinBase = interfaceParameters[6]
    """


    """On init, do the input configuration:

    We need to set up the sysfs interface before (powerbuttond.py -
    a daemon running on boot with root privileges takes care of it).
    """

    gpioSysfsPath = '/sys/class/gpio/gpio%s/' % photocellGPIO
    self.gpioValueFileName = gpioSysfsPath + 'value'
    self.gpioEdgeFileName = gpioSysfsPath + 'edge'


    """Check if the photocell GPIO has been configured - file can be read:"""
    if not os.access(self.gpioValueFileName, os.R_OK):
      print('%s: file does not exist or cannot be read. '
         'You must export the GPIO no %i as input first!'
              % (self.gpioValueFileName, photocellGPIO))
      exit()


    """Ensure that the interrupts are generated for photocell GPIO
    for both rising and falling edge:"""
    with open(self.gpioEdgeFileName, 'r') as edgeFile:
      if (edgeFile.read()[:4] != 'both'):
        print('%s: file does not exist, cannot be read or the interrupt \
        on GPIO no %i is not set to "both". Check the system config.'
        % (self.gpioEdgeFileName, photocellGPIO))
        exit()


    """Output configuration:

    Setup the wiringPi MCP23017 chips for valve outputs:
    """
    wiringpi.mcp23017Setup(pinBase, mcp0Address)
    wiringpi.mcp23017Setup(pinBase + 16, mcp1Address)
    pins = range(pinBase, pinBase + 32)
    """Set all I/O lines on MCP23017s as outputs - mode = 1"""
    for pin in pins:
      wiringpi.pinMode(pin,1)


    """This list defines the names and order of Monotype control signals
    that will be assigned to 32 MCP23017 outputs and solenoid valves.
    You may want to change it, depending on how you wired the valves
    in hardware (e.g. you can fix interchanged lines by swapping signals).

    Monotype ribbon perforations are arranged as follows:

    NMLKJIHGF S ED  0075    CBA 123456789 10 11 12 13 14  0005
                   (large)                               (large)

    O15 is absent in ribbon, and is only used by the keyboard's paper tower.
    It's recommended to assign it to the first or last output line.

    You'll probably want to assign your outputs in one of these orders:

    a) alphanumerically:

    mcp0 bank A | mcp0 bank B                | mcp1 bank A | mcp1 bank B
    ---------------------------------------------------------------------
    12345678    | 9 10 11 12 13 14 0005 0075 | ABCDEFGH    | IJKLMN S O15
    """
    signalsA = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
             '12', '13', '14', '0005', '0075', 'A', 'B', 'C', 'D', 'E',
             'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'S', 'O15']

    """
    b) according to Monotype codes:

    mcp0 bank A | mcp0 bank B     | mcp1 bank A | mcp1 bank B
    -----------------------------------------------------------------------
    NMLKJIHG    | F S ED 0075 CBA | 12345678    | 9 10 11 12 13 14 0005 O15
    """
    signalsB = ['N', 'M', 'L', 'K', 'J', 'I', 'H', 'G', 'F', 'S', 'E',
             'D', '0075', 'C', 'B', 'A', '1', '2', '3', '4', '5', '6',
             '7', '8', '9', '10', '11', '12', '13', '14', '0005', 'O15']

    """
    c) grouping odd and even Monotype signals in valve units,
    where first MCP controls odd signals (upper/lower paper tower inputs
    if you use V air connection block) and second MCP controls even signals:

    mcp0 bank A   | mcp0 bank B      | mcp1 bank A | mcp1 bank B
    --------------------------------------------------------------------
    NLJHFE 0075 B | 13579 11 13 0005 | MKIGSDCA    | 2468 10 12 14 O15
    """
    signalsC = ['N', 'L', 'J', 'H', 'F', 'E', '0075', 'B', '1', '3', '5',
             '7', '9', '11', '13', '0005', 'M', 'K', 'I', 'G', 'S', 'D',
             'C', 'A', '2', '4', '6', '8', '10', '12', '14', 'O15']

    """
    d) grouping odd and even Monotype signals in valve units,
    where first MCP controls left half of signals - N...A,
    and second MCP controls right half - 1...0005:

    mcp0 bank A   | mcp0 bank B | mcp1 bank A      | mcp1 bank B
    --------------------------------------------------------------------
    NLJGFE 0075 B | MKIHSDCA    | 13579 11 13 0005 | 2468 10 12 14 O15
    """
    signalsD = ['N', 'L', 'J', 'H', 'F', 'E', '0075', 'B', 'M', 'K',
              'I', 'G', 'S', 'D', 'C', 'A','1', '3', '5', '7', '9', '11',
              '13', '0005',  '2', '4', '6', '8', '10', '12', '14', 'O15']


    """mcp0 is the MCP23017 with lower address (e.g. 0x20), mcp1 - the chip
    with higher address (e.g. 0x21). If you're using DIP or SOIC chips,
    I/O bank A uses physical pin numbers 21...18, bank B is 1...8.
    See datasheet for further info."""


    """Choose one of predefined orders or define a brand new one:"""
    signals = signalsA

    """Assign wiringPi pin numbers on MCP23017s to the Monotype
    control signals defined earlier.
    """
    self.wiringPiPinNumber = dict(zip(signals, pins))


  def detect_rotation(self):
    """
    Detect rotation:

    Checks if the machine is running by counting pulses on a photocell
    input. One pass of a while loop is a single cycle. If cycles_max
    value is exceeded in a time <= time_max, the program assumes that
    the caster is rotating and it can start controlling the machine.
    """
    cycles = 0
    cycles_max = 3
    """Let's give it 30 seconds timeout."""
    time_start = time.time()
    time_max = 30

    """
    Check for photocell signals, keep checking until max time is exceeded
    or target number of cycles is reached:
    """
    with open(self.gpioValueFileName, 'r') as gpiostate:
      while time.time() <= time_start + time_max and cycles <= cycles_max:
        photocellSignals = select.epoll()
        photocellSignals.register(gpiostate, select.POLLPRI)
        events = photocellSignals.poll(0.5)
        if events:
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())
          previousState = 0
          if photocellState == 1 and previousState == 0:
            previousState = 1
            cycles += 1
          elif photocellState == 0 and previousState == 1:
            previousState = 0
      else:
        if cycles > cycles_max:
          print('\nOkay, the machine is running...\n')
          return True
        else:
          self.machine_stopped()
          self.detect_rotation()
          return False

  def send_signals_to_caster(self, signals, machineTimeout):
    """
    Send signals to caster:

    When casting, the pace is dictated by the caster and its RPM. Thus,
    we can't arbitrarily set the intervals between valve ON and OFF
    signals. We need to get feedback from the machine, and we can use
    contact switch (unreliable in the long run), magnet & reed switch
    (not precise enough) or a photocell + LED (very precise).
    We can use a paper tower's operating lever for obscuring the sensor
    (like John Cornelisse did), or we can use a partially obscured disc
    attached to the caster's shaft (like Bill Welliver did).
    Both ways are comparable; the former can be integrated with the
    valve block assembly, and the latter allows for very precise tweaking
    of duty cycle (bright/dark area ratio) and phase shift (disc's position
    relative to 0 degrees caster position).
    """
    with open(self.gpioValueFileName, 'r') as gpiostate:
      po = select.epoll()
      po.register(gpiostate, select.POLLPRI)
      previousState = 0

      """
      Detect events on a photocell input, and if a rising or falling edge
      is detected, determine the input's logical state (high or low).
      If high - check if it was previously low to be sure. Then send
      all signals passed as an argument (tuple or list).
      In the next cycle, turn all the valves off and exit the loop.
      Set the previous state each time the valves are turned on or off.
      """
      while True:
        """polling for interrupts"""
        events = po.poll(machineTimeout)
        if events:
          """be sure that the machine is working"""
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())

          if photocellState == 1 and previousState == 0:
            """there's a signal from photocell - let the air in"""
            self.activate_valves(signals)
            previousState = 1

          elif photocellState == 0 and previousState == 1:
            """state changes from 1 to 0 - end of air in phase"""
            self.deactivate_valves()
            previousState = 0
            break

        else:
          """Ask the user what to do if the machine is stopped (no events)."""
          self.machine_stopped()


  def activate_valves(self, signals):
    """Activate valves:

    Activates the solenoid valves connected with interface's outputs,
    as specified in the "signals" argument (tuple or list).
    The input array "signals" can contain
    lowercase (a, b, g, s...) or uppercase (A, B, G, S...) descriptions.
    Do nothing if the function receives an empty sequence, which will
    occur if we cast with the matrix found at position O15.
    """
    if len(signals) != 0:
      for monotypeSignal in signals:
        pin = self.wiringPiPinNumber[monotypeSignal]
        wiringpi.digitalWrite(pin,1)


  def deactivate_valves(self):
    """Deactivate valves:

    Turn all valves off after casting/punching any character.
    Call this function to avoid outputs staying turned on if something
    goes wrong, esp. in case of abnormal program termination."""
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)


  def machine_stopped(self):
    """Machine stopped menu:

    This allows us to choose whether we want to continue, return to menu
    or exit if the machine stops during casting.
    """
    choice = ""
    while choice not in ['c', 'm', 'e']:
      choice = raw_input('Machine not running! Check what\'s going on.'
                   '\n(C)ontinue, return to (M)enu or (E)xit program.')
    else:
      if choice.lower() == 'c':
        return True
      elif choice.lower() == 'm':
        self.menu()
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()



class DryRun(object):
  """Dry Run:

  A class which allows to test rpi2caster without an actual interface
  or caster. Most functionality will be developped without an access
  to the machine.
  """

  def __init__(self):
    """Instantiation:

    A lot simpler than "real" operation; we don't set up the GPIO lines
    nor interrupt polling files We'll use substitute routines that
    emulate caster-related actions.
    """
    print('Testing rpi2caster without an actual caster or interface. \
    Debug mode ON.')
    time.sleep(1)

  def send_signals_to_caster(self, signals, machineTimeout):
    """Just send signals, as we don't have a photocell"""
    raw_input('Sensor ON - press [ENTER]')
    self.activate_valves(signals)
    raw_input('Sensor OFF - press [ENTER]')
    self.deactivate_valves()


  def activate_valves(self, signals):
    """If there are any signals, print them out"""
    if len(signals) != 0:
      print('The valves: ',' '.join(signals),' would be activated now.')

  def deactivate_valves(self):
    """No need to do anything"""
    print('The valves would be deactivated now.')

  def detect_rotation(self):
    """FIXME: implement raw input breaking on timeout"""
    print('Now, the program would check if the machine is rotating.\n')
    startTime = time.time()
    while time.time() < startTime + 5:
      answer = raw_input('Press return (to simulate rotation) '
                         'or wait 5sec (to simulate machine off)\n')
    else:
      if answer is None:
        self.machine_stopped()
        self.detect_rotation()

  def machine_stopped(self):
    """Machine stopped menu - the same as in actual casting.

    This allows us to choose whether we want to continue, return to menu
    or exit if the machine stops during casting. It's just a simulation here."""
    choice = ""
    while choice not in ['c', 'm', 'e']:
      choice = raw_input('Machine not running! Check what\'s going on.'
                   '\n(C)ontinue, return to (M)enu or (E)xit program.')
    else:
      if choice.lower() == 'c':
        return True
      elif choice.lower() == 'm':
        self.menu()
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()



class Parsing(object):
  """This class contains file- and line-parsing methods"""


  def signals_parser(self, originalSignals):
    """Parses an input string, passes only A-N, 1-14, 0005, S, 0075.
    Prints any comments to screen."""

    """We need to work on strings. Convert any lists, integers etc."""
    signals = str(originalSignals)

    """This is a comment parser. It looks for any comment symbols defined
    here - e.g. **, *, ##, #, // etc. - and prints the comment to screen.
    If it's an inline comment (placed after combination), we cast this
    combination. If a line in file contains a comment only, we cast nothing.
    So, we need an empty line if we want to cast O15 (place the comment above)."""
    commentSymbols = ['**', '*', '//', '##', '#']
    comment = ''
    for symbol in commentSymbols:
      symbolPosition = signals.find(symbol)
      if symbolPosition != -1:
        comment = signals[symbolPosition + len(symbol):].strip()
        signals = signals[:symbolPosition].strip()

    """Filter out all non-alphanumeric characters and whitespace"""
    signals = filter(str.isalnum, signals).upper()

    """Codes for columns, rows and special signals will be stored
    separately and sorted on output"""
    columns = []
    rows = []
    special_signals = []

    """First, detect special signals: 0005, 0075, S"""
    for special in ['0005', '0075', 'S']:
      if signals.find(special) != -1:
        special_signals.append(special)
        signals = signals.replace(special, '')

    """Look for any numbers between 14 and 100, strip them"""
    for n in range(100, 14, -1):
      signals = signals.replace(str(n), '')

    """From remaining numbers, determine row numbers"""
    for n in range(15, 0, -1):
      pos = signals.find(str(n))
      if pos > -1:
        rows.append(str(n))
      signals = signals.replace(str(n), '')

    """Treat signals as a list and filter it, dump all letters beyond N
    (S was taken care of earlier). That will be the column signals."""
    columns = filter(lambda s: s in list('ABCDEFGHIJKLMN'), list(signals))

    """Make sure no signal appears more than once, and sort them"""
    columns = sorted(set(columns))

    """Return a list containing the signals, as well as a comment."""
    return [columns + rows + special_signals, comment]


class Actions(Parsing):
  """Actions the user can do in this software"""


  def cast_composition(self, filename):
    """ Composition casting routine. The input file is read backwards -
    last characters are cast first, after setting the justification."""

    """Open a file with signals"""
    with open(filename, 'rb') as ribbon:
      contents = ribbon.readlines()


    """For casting, we need to read the file backwards"""
    contents = reversed(contents)

    """Wait until the operator confirms"""
    print('\nThe combinations of Monotype signals will be displayed '
    'on screen while the machine casts the type.\nTurn on the machine '
    'and the program will start automatically.\n')
    #raw_input('\nInput file found. Press return to start casting.\n')
    self.detect_rotation()
    for line in contents:

      """Parse the row, return a list of signals and a comment.
      Both can have zero or positive length."""
      signals, comment = self.signals_parser(line)

      """Print a comment if there is one (positive length)"""
      if len(comment) > 0:
        print comment

      """Cast an empty line, signals with comment, signals with no comment.
      Don't cast a line with comment alone."""
      if len(comment) == 0 or len(signals) > 0:
        if len(signals) > 0:
          print ' '.join(signals)
        else:
          print('O+15 - no signals')
        self.send_signals_to_caster(signals, 5)

    """After punching is finished, notify the user:"""
    raw_input('\nCasting finished. Press return to go to main menu. ')
    self.menu()


  def punch_composition(self, filename):
    """Punching routine.
    When punching, the input file is read forwards. An additional line
    (O+15) is switched on for operating the paper tower, if less than two
    signals are found in a sequence."""

    """Open a file with signals"""
    with open(filename, 'rb') as ribbon:

      """Wait until the operator confirms"""
      print('\nThe combinations of Monotype signals will be displayed '
                'on screen while the paper tower punches the ribbon.\n')
      raw_input('\nInput file found. Turn on the air, fit the tape '
             'on your paper tower and press return to start punching.\n')
      for line in ribbon:

        """Parse the row, return a list of signals and a comment.
        Both can have zero or positive length."""
        signals, comment = self.signals_parser(line)

        """Print a comment if there is one - positive length"""
        if len(comment) > 0:
          print comment

        """Punch an empty line, signals with comment, signals with no comment.
        Don't punch a line with comment alone (prevents erroneous O+15's)."""
        if len(comment) == 0 or len(signals) > 0:

          """Determine if we need to turn O+15 on"""
          if len(signals) < 2:
            signals += ('O15',)
          print ' '.join(signals)
          self.activate_valves(signals)

          """The pace is arbitrary, let's set it to 200ms/200ms"""
          time.sleep(0.2)
          self.deactivate_valves()
          time.sleep(0.2)

    """After punching is finished, notify the user:"""
    raw_input('\nPunching finished. Press return to go to main menu. ')
    self.menu()


  def line_test(self):
    """Test all valves and composition caster's inputs to check
    if everything works and is properly connected. Signals will be tested
    in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL,
    MNH, MNK (feel free to add other important combinations!)"""
    raw_input('This will check if the valves, pin blocks and 0005, S, '
             '0075 mechanisms are working. Press return to continue... ')
    for combination in [['0005'], ['S'], ['0075'], ['1'], ['2'], ['3'], ['4'],
                ['5'], ['6'], ['7'], ['8'], ['9'], ['10'], ['11'], ['12'],
                ['13'], ['14'], ['A'], ['B'], ['C'], ['D'], ['E'], ['F'],
                ['G'], ['H'], ['I'], ['J'], ['K'], ['L'], ['M'], ['N'], ['O15'],
                ['N', 'I'], ['N', 'L'], ['M', 'N', 'H'], ['M', 'N', 'K']]:
      print ' '.join(combination)
      self.send_signals_to_caster(combination, 60)
    raw_input('\nTesting done. Press return to go to main menu. ')
    self.menu()


  def cast_sorts(self):
    """Sorts casting routine, based on the position in diecase.
    Ask user about the diecase row & column, as well as number of sorts."""
    os.system('clear')
    print('Calibration and Sort Casting:\n\n')
    signals = raw_input('Enter column and row symbols (default: G 5, spacebar if O-15) ')
    print('\n')
    if signals == '':
      signals = 'G5'

    parsedSignals, comment = self.signals_parser(signals)

    """O15 yields no signals, but we may want to cast it - check if we
    entered spacebar"""
    if len(parsedSignals) == 0 and signals != ' ':
      print('\nRe-enter the sequence')
      time.sleep(1)
      self.cast_sorts()
    n = raw_input('\nHow many sorts do you want to cast? (default: 10) ')
    print('\n')

    """Default to 10 if user enters non-positive number or letters"""
    if not n.isdigit() or int(n) < 0:
      n = '10'
    n = int(n)

    """Warn if we want to cast too many sorts from a single matrix"""
    print ('\nWe\'ll cast it %i times.\n' % (n))
    if n > 30:
      print('\nWarning: you want to cast a single character more than '
                    '30 times. This may lead to matrix overheating!\n')

    """Ask user if the entered parameters are correct"""
    choice = ''
    while choice not in ['c', 'r', 'm', 'e']:
      choice = raw_input('(C)ontinue, (R)epeat, go back to (M)enu or (E)xit program? ')
    else:
      if choice.lower() == 'c':
        """Check if the machine is running"""
        print('Start the machine...')
        self.detect_rotation()
        """Cast the sorts: turn on the pump first."""
        print('Starting the pump...')
        self.send_signals_to_caster(['N', 'K', '0075'], 5)
        print('Casting characters...')
        """Cast n combinations of row & column, one by one"""
        for i in range(n):
          if len(parsedSignals) > 0:
            print ' '.join(parsedSignals)
          else:
            print('O+15 - no signals')
          self.send_signals_to_caster(parsedSignals, 5)
        """After casting sorts we need to stop the pump"""
        print('Stopping the pump and putting line to the galley...')
        self.send_signals_to_caster(['0005', '0075'], 5)
      elif choice.lower() == 'r':
        self.cast_sorts()
      elif choice.lower() == 'm':
        self.menu()
      elif choice.lower() == 'e':
        self.deactivate_valves()
        exit()

    """Ask what to do after casting"""
    print('\nFinished!')
    finishedChoice = ''
    while finishedChoice not in ['r', 'm', 'e']:
      finishedChoice = raw_input(
                      '(R)epeat, go back to (M)enu or (E)xit program? ')
      if finishedChoice.lower() == 'r':
        self.cast_sorts()
      elif finishedChoice.lower() == 'm':
        self.menu()
      elif finishedChoice.lower() == 'e':
        self.deactivate_valves()
        exit()
      else:
        print('\nNo such option. Choose again.')
        finishedChoice = ''


  def lock_on_position(self):
    """This function allows us to give the program a specific combination
    of Monotype codes, and will keep the valves on until we press return
    (useful for calibration). It also checks the signals' validity"""

    """Let the user enter a combo:"""
    signals = ''
    while signals == '':
      signals = raw_input('Enter the signals to send to the machine: ')
    combination = self.signals_parser(signals)[0]
    if len(combination) > 0:
      print ' '.join(combination)
    self.activate_valves(combination)

    """Wait until user decides to stop sending those signals to valves:"""
    raw_input('Press return to stop and go back to main menu. ')
    self.deactivate_valves()
    self.menu()


class TextUI(object):
  """This class defines a text user interface, i.e. what you can do
  when operating the program from console."""


  """file name auto-complete"""
  def tab_complete(text, state):
    """This function enables tab key auto-completion when you
    enter the filename. Will definitely come in handy."""
    return (glob.glob(text+'*')+[None])[state]
  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(tab_complete)


  def consoleUI(self):
    """Main loop definition. All exceptions should be caught here.
    Also, ensure cleaning up after exit."""
    try:
      self.menu()
    except (IOError, NameError):
      if DebugMode == True:
        print('Debug mode: see what happened.')
        raise
      else:
        raw_input('\nInput file not chosen or wrong input file name. '
                              'Press return to go to main menu.\n')
        self.menu()
    except KeyboardInterrupt:
      print('\nTerminated by user.')
      exit()
    finally:
      print('Goodbye!')
      self.deactivate_valves()


  """Set up an empty ribbon file name first"""
  inputFileName = ''


  def enter_filename(self):
    """Enter the ribbon filename"""
    self.inputFileName = raw_input('\n Enter the ribbon file name: ')


  def menu(self):
    """Main menu. On entering, clear the screen and turn any valves off."""
    os.system('clear')
    self.deactivate_valves()
    print('rpi2caster - CAT (Computer-Aided Typecasting) for Monotype '
    'Composition or Type and Rule casters.\n\nThis program reads '
    'a ribbon (input file) and casts the type on a Composition Caster, '
    '\nor punches a paper tape with a Monotype keyboard\'s paper tower.\n')
    if DebugMode:
      print('\nThe program is now in debugging mode!\n')
    ans = ''
    while ans == '':
      print ("""
  \t Main menu:

  \t 1. Load a ribbon file

  \t 2. Cast type from ribbon file

  \t 3. Punch a paper tape

  \t 4. Cast sorts

  \t 5. Test the valves and pinblocks

  \t 6. Lock the caster on a specified diecase position



  \t 0. Exit to shell

  """)

      if self.inputFileName != '':
        print('Input file name: %s\n' % os.path.realpath(self.inputFileName))

      ans = raw_input('Choose an option: ')
      if ans=='1':
        self.enter_filename()
        self.menu()
      elif ans=='2':
        self.cast_composition(self.inputFileName)
      elif ans=='3':
        self.punch_composition(self.inputFileName)
      elif ans=='4':
        self.cast_sorts()
      elif ans=='5':
        self.line_test()
      elif ans=='6':
        self.lock_on_position()

      elif ans=='0':
        exit()
      else:
        print('\nNo such option. Choose again.')
        ans = ''


class Console(Monotype, Actions, TextUI):
  """Use this class for instantiating text-based console user interface."""

  def __init__(self, casterName):
    """instantiate config for the caster"""
    casterSetup = DatabaseBackend()


    """get casting interface ID from database;
    we need the last item returned by the function, hence [-1]"""
    interfaceID = config.caster_by_name(casterName)[-1]

    """get interface parameters"""
    interfaceParameters = casterSetup.get_interface(interfaceID)

    """assign results to variables passed further"""
    [interfaceID, interfaceName, emergencyGPIO, photocellGPIO, mcp0Address,
    mcp1Address, pinBase] = (interfaceParameters[i] for i in range(7))

    """display interface name and ID"""
    print('Using interface "%s", ID: %i' % interfaceName, interfaceID)

    """set up hardware with obtained interface parameters"""
    caster = Monotype(casterName)

    self.consoleUI()

class Testing(DryRun, Actions, TextUI):
  """A class for testing the program without an actual caster/interface"""
  def __init__(self):
    global DebugMode
    DebugMode = True
    DryRun.__init__(self)
    self.consoleUI()

class WebInterface(Monotype, Actions):
  """Use this class for instantiating text-based console user interface"""

  def __init__(self, casterName):
    """instantiate config for the caster"""
    webCasterConfig = DatabaseBackend

    """get casting interface ID from database"""
    interfaceID = webCasterConfig.caster_by_name(casterName)[-1]

    """get interface parameters"""
    interfaceParameters = webCasterConfig.get_interface(interfaceID)

    """assign results to variables passed further"""
    [interfaceID, interfaceName, emergencyGPIO, photocellGPIO, mcp0Address,
    mcp1Address, pinBase] = (interfaceParameters[i] for i in range(7))

    """display interface name and ID"""
    print('Using interface "%s", ID: %i' % interfaceName, interfaceID)

    """set up hardware with obtained interface parameters"""
    Monotype.__init__(self, casterName)

    self.webUI()

  def webUI(self):
    """This is a placeholder for web interface method. Nothing yet..."""

if __name__ == __main__:
  casting = Console('mkart-cc')