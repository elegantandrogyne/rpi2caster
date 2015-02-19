#!/usr/bin/python

"""rpi2caster - control a Monotype composition caster with Raspberry Pi.

Monotype composition caster & keyboard paper tower control program.

This program sends signals to the solenoid valves connected to the
composition caster's (or keyboard's) paper tower. When casting,
the program uses methods of the Monotype class and waits for the machine
to send feedback (i.e. an "air bar down" signal), then turns on
a group of valves. On the "air bar up" signal, valves are turned off and
the program reads another code sequence, just like the original paper
tower.

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
air bar down.

During casting, the program automatically detects the machine movement,
so no additional actions on user's part are required.

In the future, the program will have an "emergency stop" feature.
When an interrupt on a certain Raspberry Pi's GPIO is detected, the program
stops sending codes to the caster and sends a 0005 combination instead.
The pump is immediately stopped.
"""


"""Typical libs, used by most routines:"""
import sys
import os
import time
import string

"""Config parser for reading the interface settings"""
import ConfigParser

"""Used for serializing lists stored in database, and for communicating
with the web application (in the future):"""
try:
  import json
except ImportError:
  import simplejson as json

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



class Typesetter(object):
  """Typesetter:

  This class contains all methods related to typesetting, i.e. converting
  an input text to a sequence of Monotype codes to be read by the casting
  interface. This class is to be instantiated, so that all data
  and buffers are contained within an object and isolated from other
  typesetting sessions.
  """

  def __init__(self):
    pass


  def __enter__(self):
    pass


  def calculate_wedges(self, setWidth, units):
    """calculate_wedges(setWidth, units):

    Calculate the 0005 and 0075 wedge positions based on the unit width
    difference (positive or negative) for the given set width.

    Since one step of 0075 wedge is 15 steps of 0005, we'll get a total
    would-be number of 0005 steps, then floor-divide it by 15 to get the
    0075 steps, and modulo-divide by 15 to get 0005 steps.

    If number of 0075 steps or 0005 steps is 0, we'll set 1 instead,
    because the wedge cannot have a "0" position.

    The function returns a list: [pos0075, pos0005].

    Maths involved may be a bit daunting, but it's not rocket science...
    First, we need to derive the width in inches of 1 unit 1 set:

    1p [pica] = 1/6" = 0.1667" (old pica), or alternatively:
    1p = 0.1660" (new pica - closer to the Fournier system).
    1p = 12pp [pica-points]. So, 1pp = 1/12p * 1/6["/p] = 1/72".

    In continental Europe, they used ciceros and Didot points:
    1c = 0.1776"
    1c = 12D - so, 1D = 0.0148"

    A set number of the type is the width of an em (i.e., widest char).
    It can, but doesn't have to, be the same as the type size in pp.
    Set numbers were multiples of 1/4, so we can have 9.75, 10, 11.25 etc.

    For example, 327-12D Times New Roman is 12set (so, it's very close),
    but condensed type will have a lower set number.

    And 1 Monotype fundamental unit is defined as 1/18em. Thus, the width
    of 1 unit 1 set = 1/18 pp; 1 unit multi-set = setWidth/18 pp.

    All things considered, let's convert the unit to inches:

    Old pica:
    W(1u 1set) = 1/18 * 1/72" = 1/1296"

    The width in inches  of a given no of units at a given set size is:
    W = s * u / 1296
    (s - set width, u - no of units)

    Now, we go on to explaining what the S-needle does.
    It's used for modifying (adding/subtracting) the width of a character
    to make it wider or narrower, if it's needed (for example, looser or
    tighter spaces when justifying a line).

    When S is disengaged (e.g. G5), the lower transfer wedge (62D)
    is in action. The justification wedges (10D, 11D) have nothing to do,
    and the character width depends solely on the matrix's row and its
    corresponding unit value.

    Suppose we're using a S5 wedge, and the unit values are as follows:
    row   1 2 3 4 5 6 7 8  9  10 11 12 13 14 15 16
    units 5 6 7 8 9 9 9 10 10 11 12 13 14 15 18 18
    (unless unit-shift is engaged)

    The S5 wedge moves with a matrix case, and for row 1, the characters
    will be 5 units wide. So, the width will be:
    W(5u) = setWidth * 5/1296 = 0.003858" * setWidth.

    Now, we want to cast the character with the S-needle.
    Instead of the lower transfer wedge 62D, the upper transfer wedge 52D
    together with justification wedges 10D & 11D affect the character's
    width. The 10D is a coarse justification wedge and adds/subtracts
    0.0075" per step; the 11D is a fine justification wedge and changes
    width by 0.0005" per step. The wedges can have one of 15 positions.

    Notice that 0.0075 = 15 x 0.0005 (so, 0.0005 at 15 equals 0.0075 at 1).
    Position 0 or >15 is not possible.S

    Also notice that 0.0005" precision would mean a resolution of 2000dpi -
    beat that, Hewlett-Packard! :).

    Now, we can divide the character's width in inches by by 0.0005
    (or multiply by 2000) and we get a number of 0005 wedge steps
    to cast the character with the S needle. It'll probably be more than
    15, so we need to floor-divide the number to get 0075 wedge steps,
    and modulo-divide it to get 0005 steps:

    steps = W * 2000          (round that to integer)
    steps0075 = steps // 15   (floor-divide)
    steps0005 = steps % 15    (modulo-divide)

    The equivalent 0005 and 0075 wedge positions for a 5-unit character
    in the 1st row (if we decide to cast it with the S-needle) will be:

    steps = 5/1296 * 2000 * setWidth

    (so it is proportional to set width).
    For example, consider the 5 unit 12 set type, and we have:

    steps = 5 * 12 * 2000 / 1296 = 92.6
    so, steps = 92
    steps // 15 = 6
    steps % 15 = 2

    So, the 0075 wedge will be at pos. 6 and 0005 will be at 3.

    If any of the wedge step numbers is 0, set 1 instead (a wedge must
    be in position 1...15).
    """

    steps = 2000/1296 * setWidth * units
    steps = int(steps)
    steps0075 = steps // 15
    steps0005 = steps % 15
    if not steps0075:
      steps0075 = 1
    if not steps0005:
      steps0005 = 1
    return [steps0075, steps0005]


  def calculate_line_length(self, lineLength, measurement='oldPica'):
    """calculate_line_length(lineLength, measurement='oldPica'):

    Calculates the line length in Monotype fundamental (1-set) units.
    The "length" parameter is in old-pica (0.1667") by default,
    but this can be changed with the "measurement" parameter.
    """

    """Check if the measurement is one of the following:
    oldPica, newPica, cicero
    If not, throw an error.
    """

    inWidth = {
               'oldPica' : 0.1667,
               'newPica' : 0.1660,
               'cicero'  : 0.1776
              }
    if measurement not in inWidth:
      print('Incorrect unit designation!')
      return False

    """Base em width is a width (in inches) of a single em -
    which, by the Monotype convention, is defined as 18 units 12 set.

    Use old-pica (0.1667") value for European cicero system;
    for pica systems, use their respective values.
    """
    if measurement == 'cicero':
      baseEmWidth = inWidth['oldPica']
    else:
      baseEmWidth = inWidth[measurement]

    """To calculate the inch width of a fundamental unit (1-unit 1-set),
    we need to divide the (old or new) pica length in inches by 12*18 = 216:
    """
    fuWidth = baseEmWidth / 216

    """Convert the line length in picas/ciceros to inches:"""
    inLineLength = lineLength * inWidth[measurement]

    """Now, we need to calculate how many units of a given set
    the row will contain. Round that to an integer and return the result.
    """
    unitCount = round(inLineLength / fuWidth)
    return unitCount


  def __exit__(self, *args):
    pass



class Database(object):
  """Database(databasePath):

  A class containing all methods related to storing, retrieving
  and deleting data from a SQLite3 database used for config.

  We're using database because it's easy to access and modify with
  third-party programs (like sqlite, sqlitebrowser or a Firefox plugin),
  and there will be lots of data to store: diecase (matrix case)
  properties, diecase layouts, wedge unit values, caster and interface
  settings (although we may move them to config files - they're "system"
  settings best left default, instead of "foundry" settings the user has
  to set up before being able to cast, based on their type foundry's
  inventory, which varies from one place to another).

  Methods here are for reading/writing data for diecases, matrices,
  wedges (and casters & interfaces) from/to designated sqlite3 database.

  Default database path is ./database/monotype.db - but you can
  override it by instantiating this class with a different name
  passed as an argument. It is necessary that the user who's running
  this program for setup has write access to the database file;
  read access is enough for normal operation.
  Usually you run setup with sudo.
  """

  def __init__(self, job, databasePath='', confFilePath='/etc/rpi2caster.conf'):
    """Set up the job context:"""
    self.job = job

    """Initialize conffile:"""
    config = ConfigParser.SafeConfigParser()
    config.read(confFilePath)

    """Look database path up in conffile:"""
    try:
      configDatabasePath = config.get('Database', 'path')
    except ConfigParser.NoSectionError:
      configDatabasePath = ''

    if databasePath:
      """Use path from function call, if it's there:"""
      self.databasePath = databasePath

    elif configDatabasePath:
      """Use path stored in conffile:"""
      self.databasePath = configDatabasePath

    else:
      """Revert to hardcoded local default:"""
      self.databasePath = 'database/monotype.db'


  def __enter__(self):
    return self


  def add_wedge(self, wedgeName, setWidth, oldPica, steps):
    """add_wedge(wedgeName, setWidth, oldPica, steps):

    Registers a wedge in our database.
    Returns True if successful, False otherwise.

    Arguments:

    wedgeName - wedge's number, e.g. S5 or 1160. String, cannot be null.

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

    """data - a list with wedge parameters to be written:"""
    data = [wedgeName, setWidth, str(oldPica), json.dumps(steps)]

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        """Create the table first:"""
        cursor.execute(
                      'CREATE TABLE IF NOT EXISTS wedges '
                      '(id INTEGER PRIMARY KEY ASC AUTOINCREMENT, '
                      'wedge_id TEXT NOT NULL, '
                      'set_width REAL NOT NULL, '
                      'old_pica TEXT NOT NULL, '
                      'steps TEXT NOT NULL)'
                      )

        """Then add an entry:"""
        cursor.execute(
                      'INSERT INTO wedges '
                      '(wedge_id,set_width,old_pica,steps) '
                      'VALUES (?, ?, ?, ?)', data
                      )
        db.commit()
        return True

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot add wedge!')
        if self.job.debugMode:
          raise
        return False



  def wedge_by_name_and_width(self, wedgeName, setWidth):
    """wedge_by_name_and_width(wedgeName, setWidth):

    Looks up a wedge with given ID and set width in database.
    Useful when coding a ribbon - wedge is obtained from diecase data.

    If wedge is registered, function returns:
    ID - unique, int (e.g. 0),
    wedgeName - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Else, function returns False.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
                      'SELECT * FROM wedges WHERE wedge_id = ? '
                      'AND set_width = ?', [wedgeName, setWidth]
                      )
        wedge = cursor.fetchone()
        if wedge is None:
          print(
                'No wedge %s - %f found in database!'
                 % (wedgeName, setWidth)
               )
          return False
        else:
          wedge = list(wedge)
          print(
                'Wedge %s - %f found in database - OK'
                 % (wedgeName, setWidth)
               )

          """Change return value of oldPica to boolean:"""
          wedge[3] = bool(wedge[3])

          """Change return value of steps to list:"""
          wedge[4] = json.loads(wedge[4])

          """Return [ID, wedgeName, setWidth, oldPica, steps]:"""
          return wedge

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot get wedge!')
        if self.job.debugMode:
          raise


  def wedge_by_id(self, ID):
    """wedge_by_id(ID):

    Gets parameters for a wedge with given ID.

    If so, returns:
    ID - unique, int (e.g. 0),
    wedgeName - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Else, returns False.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute(
                      'SELECT * FROM wedges WHERE id = ? ', [ID]
                      )
        wedge = cursor.fetchone()
        if wedge is None:
          print('Wedge not found!')
          return False
        else:
          wedge = list(wedge)

          """Change return value of oldPica to boolean:"""
          wedge[3] = bool(wedge[3])

          """Change return value of steps to list:"""
          wedge[4] = json.loads(wedge[4])

          """Return [ID, wedgeName, setWidth, oldPica, steps]:"""
          return wedge

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot get wedge!')
        if self.job.debugMode:
          raise


  def delete_wedge(self, ID):
    """delete_wedge(self, ID):

    Deletes a wedge with given unique ID from the database
    (useful in case we no longer have the wedge).

    Returns True if successful, False otherwise.

    First, the function checks if the wedge is in the database at all.
    """
    if self.wedge_by_id(ID):
      with sqlite3.connect(self.databasePath) as db:
        try:
          cursor = db.cursor()
          cursor.execute(
                         'DELETE FROM wedges WHERE id = ?', [ID]
                        )
          return True
        except:
          """In debug mode we get the exact exception code & stack trace."""
          print('Database error: cannot delete wedge!')
          if self.job.debugMode:
            raise
          return False
    else:
      print('Nothing to delete.')
      return False


  def list_wedges(self):
    """list_wedges(self):

    Lists all wedges stored in database, with their step unit values.

    Prints the following to stdout:

    ID - unique, int (e.g. 0),
    wedgeName - string (e.g. S5) - wedge name
    setWidth - float (e.g. 9.75) - set width,
    oldPica - bool - whether this is an old-pica ("E") wedge or not,
    steps - list of unit values for all wedge's steps.

    Returns True if successful, False otherwise.
    """

    with sqlite3.connect(self.databasePath) as db:
      try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM wedges')
        print(
              '\nid, wedge name, set width, old pica, '
              'unit values for all steps:\n'
             )
        while True:
          wedge = cursor.fetchone()
          if wedge is not None:
            wedge = list(wedge)

            """Change return value of steps to list:"""
            wedge[4] = json.loads(wedge[4])

            """Print all the wedge parameters:"""
            for item in wedge:
              print item, '   ',
            print ''
          else:
            break
        return True

      except:
        """In debug mode we get the exact exception code & stack trace."""
        print('Database error: cannot list wedges!')
        if self.job.debugMode:
          raise
        return False


  def __exit__(self, *args):
    pass


class Inventory(object):
  """A "job" class for configuring the Monotype workshop inventory:

  -wedges
  -diecases
  -diecase layouts.
  """

  def __init__(self):

    self.debugMode = False

  def __enter__(self):
    return self


  def add_wedge(self, wedgeName='', setWidth='', oldPica='', steps=''):
    """add_wedge(wedgeName, setWidth, oldPica, steps)

    Used for adding wedges.

    Can be called with or without arguments.

    wedgeName - string - series name for a wedge (e.g. S5, S111)
    setWidth  - float - set width of a particular wedge (e.g. 9.75)
    oldPica - boolean - True if the wedge is European old pica
              ("E" after set width number), False otherwise
    steps - string with unit values for steps - e.g. '5,6,7,8,9,9,9...,16'

    If called without arguments, the function runs at least twice.
    The first time is for entering data, the second (and further) times
    are for validating and correcting the data entered earlier.
    When all data passes validation ("revalidate" flag remains False),
    user is asked if everything is correct and can commit values
    to the database."""


    """
    Let's define unit values for some known wedges.
    This is a dictionary, so you get values (string)
    by referring via key (string), feel free to add any unit values
    for the wedges not listed.

    This data will be useful when adding a wedge. The setup program
    will look up a wedge by its name, then get unit values.

    The MONOSPACE wedge is a special wedge, where all steps have
    the same unit value of 9. It is used for casting constant-width
    (monospace) type, like the typewriters have. You could even cast
    from regular matrices, provided that you use 0005 and 0075 wedges
    to add so many units that you can cast wide characters
    like "M", "W" etc. without overhang. You'll get lots of spacing
    between narrower characters, because they'll be cast on a body
    wider than necessary.
    """
    wedgeData = { 'S5'   : '5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18',
                  'S96'  : '5,6,7,8,9,9,10,10,11,12,13,14,15,16,18,18',
                  'S111' : '5,6,7,8,8,8,9,9,9,9,10,12,12,13,15,15',
                  'S334' : '5,6,7,8,9,9,10,10,11,11,13,14,15,16,18,18',
                  'S344' : '5,6,7,9,9,9,10,11,11,12,12,13,14,15,16,16',
                  'S377' : '5,6,7,8,8,9,9,10,10,11,12,13,14,15,18,18',
                  'S409' : '5,6,7,8,8,9,9,10,10,11,12,13,14,15,16,16',
                  'S467' : '5,6,7,8,8,9,9,9,10,11,12,13,14,15,18,18',
                  'S486' : '5,7,6,8,9,11,10,10,13,12,14,15,15,18,16,16',
                  'S526' : '5,6,7,8,9,9,10,10,11,12,13,14,15,17,18,18',
                  'S536' : '5,6,7,8,9,9,10,10,11,12,13,14,15,17,18,18',
                  'S562' : '5,6,7,8,9,9,9,10,11,12,13,14,15,17,18,18',
                  'S607' : '5,6,7,8,9,9,9,9,10,11,12,13,14,15,18,18',
                  'S611' : '6,6,7,9,9,10,11,11,12,12,13,14,15,16,18,18',
                  'S674' : '5,6,7,8,8,9,9,9,10,10,11,12,13,14,15,18',
                  'S724' : '5,6,7,8,8,9,9,10,10,11,13,14,15,16,18,18',
                  'S990' : '5,5,6,7,8,9,9,9,9,10,10,11,13,14,18,18',
                  'S1063': '5,6,8,9,9,9,9,10,12,12,13,14,15,15,18,18',
                  'S1329': '4,5,7,8,9,9,9,9,10,10,11,12,12,13,15,15',
                  'S1331': '4,5,7,8,8,9,9,9,9,10,11,12,12,13,15,15',
                  'S1406': '4,5,6,7,8,8,9,9,9,9,10,10,11,12,13,15',
                  'MONOSPACE' : '9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9',
                }

    """In this program, all wedges have the "S" (for stopbar) letter
    at the beginning of their designation. However, the user can enter
    a designation with or without "S", so check if it's there, and
    append if needed (only for numeric designations - not the "monospace"
    or other text values!)

    If no name is given, assume that the user means the S5 wedge, which is
    very common and most casting workshops have a few of them.
    """
    while not wedgeName:
      wedgeName = raw_input(
                            'Enter the wedge name, e.g. S5 '
                            '(very typical, default): '
                           )
      if wedgeName == '':
        wedgeName = 'S5'
      elif wedgeName[0].upper() != 'S' and wedgeName.isdigit():
        wedgeName = 'S' + wedgeName
      wedgeName = wedgeName.upper()

    """
    Enter a set width, float. If the width ends with "E", then
    it's a wedge for European foundries with 1.667" (British) pica.
    E will be stripped, and the program will set the wedge as British
    pica.

    Otherwise, user can choose if it's American (0.166") or British pica.
    """
    while not setWidth:
      setWidth = raw_input(
                          'Enter the wedge set width as decimal, '
                          'e.g. 9.75E: '
                          )

      """Determine if it's a British pica wedge - E is present:"""
      if setWidth[-1].upper() == 'E':
        setWidth = setWidth[:-1]
        britPica = True
      else:
        choice = ''
        options = { 'A' : False, 'B' : True }
        while choice not in options:
          choice = raw_input(
                             '[A]merican (0.1660"), '
                             'or [B]ritish (0.1667") pica? '
                            ).upper()
        britPica = options[choice]
      try:
        setWidth = float(setWidth)
      except ValueError:
        setWidth = ''

    """Enter the wedge unit values for steps 1...15 (and optionally 16):"""
    while not steps:
      """First, check if we've got this wedge in our program:"""
      try:
        rawSteps = wedgeData[wedgeName]
      except (KeyError, ValueError):
        """No wedge - enter data:"""
        rawSteps = raw_input(
                            'Enter the wedge unit values for steps 1...16, '
                            'separated by commas. If empty, entering values '
                            'for wedge S5 (very common): '
                            )
        if not rawSteps:
          rawSteps = wedgeData['S5']
      rawSteps = rawSteps.split(',')
      steps = []
      """
      Now we need to be sure that all whitespace is stripped,
      and the value written to database is a list of integers:
      """
      for step in rawSteps:
        step = int(step.strip())
        steps.append(step)
      """
      Display warning if the number of steps is anything other than
      15 or 16 (15 is most common, 16 was used for HMN and KMN systems):
      """
      if len(steps) < 15:
        print('Warning - the wedge you entered has less than 15 steps! \n'
              'This is almost certainly a mistake.\n'
             )
      elif len(steps) > 16:
        print('Warning - the wedge you entered has more than 16 steps! \n'
              'This is almost certainly a mistake.\n'
             )
      else:
        print 'The wedge has ', len(steps), 'steps. That is OK.'


    """Display a summary:"""
    summary = {
               'Wedge' : wedgeName,
               'Set width' : setWidth,
               'British pica wedge?' : britPica
              }
    for parameter in summary:
      print parameter, ' : ', summary[parameter]

    """Loop over all unit values in wedge's steps and display them:"""
    for i, step in zip(range(len(steps)), steps):
      print('Step %i unit value: %i \n' % (i+1, step))

    def commit_wedge():
      if self.database.add_wedge(wedgeName, setWidth, britPica, steps):
        print('Wedge added successfully.')
      else:
        print('Failed to add wedge!')

    def reenter():
      raw_input('Enter parameters again from scratch... ')
      add_wedge()

    # To be deprecated and replaced with a new small menu:
    message = (
               '\nCommit wedge to database? \n'
               '[Y]es / [N]o (enter values again) / return to [M]enu: '
              )
    options = { 'Y' : commit_wedge, 'N' : reenter, 'M' : self.main_menu }
    ans = self.userInterface.simple_menu(message, options).upper()


  def delete_wedge(self):
    """Used for deleting a wedge from database"""
    ID = raw_input('Enter the wedge ID to delete: ')
    if ID.isdigit():
      ID = int(ID)
      if self.database.delete_wedge(ID):
        print('Wedge deleted successfully.')
    else:
      print('Wedge name must be a number!')


  def list_wedges(self):
    """lists all wedges we have"""
    self.database.list_wedges()


  def main_menu(self):

    options =
    choice = self.userInterface.menu  (
          header = (
                    'Setup utility for rpi2caster CAT. '
                    '\nMain menu:'
                   ),
          footer = '',
          options = [
                     [1, 'List casters', 'self.list_casters()'],
                     [2, 'Add caster', 'self.add_caster()'],
                     [3, 'Delete caster', 'self.delete_caster()'],
                     [4, 'List interfaces', 'self.list_interfaces()'],
                     [5, 'Add interface', 'self.add_interface()'],
                     [6, 'Delete interface', 'self.delete_interface()'],
                     [7, 'List wedges', 'self.list_wedges()'],
                     [8, 'Add wedge', 'self.add_wedge()'],
                     [9, 'Delete wedge', 'self.delete_wedge()'],
                     [0, 'Exit program', 'exit()']
                    ]
                )

  def __exit__(self, *args):
    pass



class Monotype(object):
  """Monotype(job, casterName, confFilePath):

  A class which stores all methods related to the interface and
  caster itself.

  This class MUST be instantiated with a caster name, and a
  database object.

  No static methods or class methods here.
  """

  def __init__(
               self, job, casterName='Monotype',
               confFilePath='/etc/rpi2caster.conf'
               ):
    """
    Creates a caster object for a given caster name.
    Uses a conffile to look the caster up and get its parameters,
    then looks up the interface parameters.

    Reverts to hardcoded defaults if no config matches:
    caster - "Monotype" (if no name is given),
    interface ID 0,
    unit-adding disabled,
    diecase format 15x17.
    """

    """Default caster parameters:"""
    self.casterName = casterName
    self.interfaceID = 0
    self.unitAdding = 0
    self.diecaseSystem = 'norm17'

    """Default interface parameters:"""
    self.emergencyGPIO = 18
    self.photocellGPIO = 24
    self.mcp0Address = 0x20
    self.mcp1Address = 0x21
    self.pinBase = 65

    """Initialize config:"""
    self.config = ConfigParser.SafeConfigParser()
    self.config.read(confFilePath)

    """Set up a job context:"""
    self.job = job

    """Run the setup now:"""
    self.caster_setup()

  def __enter__(self):
    return self


  def caster_setup(self):

    """Setup routine:

    After the class is instantiated, this method reads caster data
    from database and fetches a list of caster parameters:
    [diecaseFormat, unitAdding, interfaceID].

    In case there is no data, the function will run on default settings.
    """
    settings = self.get_caster_settings_from_conffile()
    if settings:
      [self.unitAdding, self.diecaseSystem, self.interfaceID] = settings

    """When debugging, display all caster info:"""
    if self.job.debugMode:
      print 'Using caster: ', self.casterName, '\n'
      print 'Caster parameters:\n'
      print 'Diecase system: ', self.diecaseSystem
      print 'Has unit-adding? : ', self.unitAdding
      print '\nInterface ID: ', self.interfaceID


    """
    Then, the interface ID is looked up in the database, and interface
    parameters are obtained:

    [emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase]

    Try to override defaults with the parameters from conffile.
    The parameters will affect the whole object created with this class.
    """
    interfaceSettings = self.get_interface_settings_from_conffile()
    if interfaceSettings:
      [self.emergencyGPIO, self.photocellGPIO,
      self.mcp0Address, self.mcp1Address,
      self.pinBase] = interfaceSettings

    """Print the parameters for debugging:"""
    if self.job.debugMode:
      print '\nInterface parameters:\n'
      print 'Emergency button GPIO: ', self.emergencyGPIO
      print 'Photocell GPIO: ', self.photocellGPIO
      print '1st MCP23017 I2C address: ', self.mcp0Address
      print '2nd MCP23017 I2C address: ', self.mcp1Address
      print 'MCP23017 pin base for GPIO numbering: ', self.pinBase

    """On init, do the input configuration:

    We need to set up the sysfs interface before (powerbuttond.py -
    a daemon running on boot with root privileges takes care of it).
    """
    gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.photocellGPIO
    self.gpioValueFileName = gpioSysfsPath + 'value'
    self.gpioEdgeFileName  = gpioSysfsPath + 'edge'

    """Check if the photocell GPIO has been configured - file can be read:"""
    if not os.access(self.gpioValueFileName, os.R_OK):
      print(
            '%s: file does not exist or cannot be read. '
            'You must export the GPIO no %i as input first!'
              % (self.gpioValueFileName, self.photocellGPIO)
           )
      exit()


    """Ensure that the interrupts are generated for photocell GPIO
    for both rising and falling edge:"""
    with open(self.gpioEdgeFileName, 'r') as edgeFile:
      if (edgeFile.read()[:4] != 'both'):
        print(
              '%s: file does not exist, cannot be read, '
              'or the interrupt on GPIO no %i is not set to "both". '
              'Check the system config.'
               % (self.gpioEdgeFileName, self.photocellGPIO)
              )
        exit()

    """Output configuration:

    Setup the wiringPi MCP23017 chips for valve outputs:
    """
    wiringpi.mcp23017Setup(self.pinBase,      self.mcp0Address)
    wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)

    pins = range(self.pinBase, self.pinBase + 32)

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
    signalsA = [
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                '11', '12', '13', '14', '0005', '0075', 'A', 'B',
                'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                'M', 'N', 'S', 'O15'
               ]

    """
    b) according to Monotype codes:

    mcp0 bank A | mcp0 bank B     | mcp1 bank A | mcp1 bank B
    -----------------------------------------------------------------------
    NMLKJIHG    | F S ED 0075 CBA | 12345678    | 9 10 11 12 13 14 0005 O15
    """
    signalsB = [
                'N', 'M', 'L', 'K', 'J', 'I', 'H', 'G', 'F', 'S', 'E',
                'D', '0075', 'C', 'B', 'A', '1', '2', '3', '4', '5',
                '6', '7', '8', '9', '10', '11', '12', '13', '14',
                '0005', 'O15'
               ]

    """
    c) grouping odd and even Monotype signals in valve units,
    where first MCP controls odd signals (upper/lower paper tower inputs
    if you use V air connection block) and second MCP controls even signals:

    mcp0 bank A   | mcp0 bank B      | mcp1 bank A | mcp1 bank B
    --------------------------------------------------------------------
    NLJHFE 0075 B | 13579 11 13 0005 | MKIGSDCA    | 2468 10 12 14 O15
    """
    signalsC = [
                'N', 'L', 'J', 'H', 'F', 'E', '0075', 'B', '1', '3',
                '5', '7', '9', '11', '13', '0005', 'M', 'K', 'I', 'G',
                'S', 'D', 'C', 'A', '2', '4', '6', '8', '10', '12',
                '14', 'O15'
               ]

    """
    d) grouping odd and even Monotype signals in valve units,
    where first MCP controls left half of signals - N...A,
    and second MCP controls right half - 1...0005:

    mcp0 bank A   | mcp0 bank B | mcp1 bank A      | mcp1 bank B
    --------------------------------------------------------------------
    NLJGFE 0075 B | MKIHSDCA    | 13579 11 13 0005 | 2468 10 12 14 O15
    """
    signalsD = [
                'N', 'L', 'J', 'H', 'F', 'E', '0075', 'B', 'M', 'K',
                'I', 'G', 'S', 'D', 'C', 'A','1', '3', '5', '7', '9',
                '11', '13', '0005',  '2', '4', '6', '8', '10', '12',
                '14', 'O15'
               ]


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

    """Print signals order for debugging:"""
    if self.job.debugMode:
      print '\nSignals arrangement: ',
      for sig in signals:
        print sig,
      print '\n'
      """The program has displayed caster-related debug info,
      now it is time for the user to read it and press Enter to proceed.

      Normally, user goes directly to the main menu."""
      raw_input('Press Enter to continue... ')


  def get_caster_settings_from_conffile(self):
    """get_caster_settings_from_conffile():

    Reads the settings for a caster with self.casterName
    from the config file (where it is represented by a section, whose
    name is self.casterName).

    The parameters returned are:
    [diecase_system, unit_adding, interface_id]

    where:
    diecase_system - caster's diecase layout and a method of
                     accessing 16th row, if applicable:
                         norm15 - old 15x15,
                         norm17 - 15x17 NI, NL,
                         hmn    - 16x17 HMN (rare),
                         kmn    - 16x17 KMN (rare),
                         shift  - 16x17 unit-shift (most modern).
    unit_adding [0, 1] - whether the machine has a unit-adding attachment,
    interface_id [0, 1, 2, 3] - ID of the interface connected to the caster

    """

    try:
      """Get caster parameters from conffile."""

      unitAdding = self.config.get(self.casterName, 'unit_adding')
      diecaseSystem = self.config.get(self.casterName, 'diecase_system')
      interfaceID = self.config.get(self.casterName, 'interface_id')
      """Time to return the data:"""
      return [bool(unitAdding), diecaseSystem, int(interfaceID)]

    except (ConfigParser.NoSectionError, ValueError, TypeError):
      """
      In case of shit happening, return None and fall back on defaults."""
      print('Incorrect caster parameters. Using hardcoded defaults.')
      if self.job.debugMode:
        raise
      return None


  def get_interface_settings_from_conffile(self):
    """get_interface_settings_from_conffile():

    Reads a configuration file and gets interface parameters.

    If the config file is correct, it returns a list:
    [emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase]

    emergencyGPIO - BCM number for emergency stop button GPIO
    photocellGPIO - BCM number for photocell GPIO
    mcp0Address   - I2C address for 1st MCP23017
    mcp1Address   - I2C address for 2nd MCP23017
    pinBase       - pin numbering base for GPIO outputs on MCP23017

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

    interfaceID    mcp0 pin    mcp1 pin    mcp0     mcp1
                   A2,A1,A0    A2,A1,A0    addr     addr

    0              000         001         0x20     0x21
    1              010         011         0x22     0x23
    2              100         101         0x24     0x25
    3              110         111         0x26     0x27

    where 0 means the pin is pulled down, and 1 means pin pulled up.

    As for pinBase parameter, it's the wiringPi's way of identifying GPIOs
    on MCP23017 extenders. WiringPi is an abstraction layer which allows
    you to control (read/write) pins on MCP23017 just like you do it on
    typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
    to registers.
    The initial 64 GPIO numbers are reserved for Broadcom SoC, so the lowest
    pin base you can use is 65. Each interface (2xMCP23017) uses 32 pins.

    If you are using multiple interfaces per Raspberry, you SHOULD
    assign the following pin bases to each interface:

    interfaceID    pinBase

    0              65
    1              98          (pinBase0 + 32)
    2              131         (pinBase1 + 32)
    3              164         (pinBase2 + 32)


    The interface ID is an attribute of an object.
    """
    interfaceName = 'Interface' + str(self.interfaceID)
    try:
      """Check if the interface is active, else return None"""
      trueAliases = ['true', '1', 'on', 'yes']
      if self.config.get(interfaceName, 'active').lower() in trueAliases:
        emergencyGPIO = self.config.get(interfaceName, 'emergency_gpio')
        photocellGPIO = self.config.get(interfaceName, 'photocell_gpio')
        mcp0Address = self.config.get(interfaceName, 'mcp0_address')
        mcp1Address = self.config.get(interfaceName, 'mcp1_address')
        pinBase = self.config.get(interfaceName, 'pin_base')

        """Return parameters:"""
        return [int(emergencyGPIO), int(photocellGPIO),
                int(mcp0Address, 16), int(mcp1Address, 16),
                int(pinBase)]
      else:
        """This happens if the interface is inactive in conffile:"""
        print(
              'Interface ID=', interfaceID, 'is marked as inactive. '
              'We cannot use it - reverting to defaults'
              )
        return None

    except (ConfigParser.NoSectionError, ValueError, TypeError):
      """
      In case of shit happening, return None and fall back on defaults.
      """
      print('Incorrect interface parameters. Using hardcoded defaults.')
      if self.job.debugMode:
        raise
      return None


  def detect_rotation(self):
    """
    detect_rotation():

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
        """Check if the photocell changes state at all:"""
        if events:
          gpiostate.seek(0)
          photocellState = int(gpiostate.read())
          previousState = 0
          """Cycle between 0 and 1, increment the number
          of passed cycles:
          """
          if photocellState == 1 and previousState == 0:
            previousState = 1
            cycles += 1
          elif photocellState == 0 and previousState == 1:
            previousState = 0
      else:
        """In case of cycles exceeded (machine running),
        or timeout (machine stopped):
        """
        if cycles > cycles_max:
          print('\nOkay, the machine is running...\n')
          return True
        else:
          self.machine_stopped()
          self.detect_rotation()
          return False


  def send_signals_to_caster(self, signals, machineTimeout=5):
    """
    send_signals_to_caster(signals, machineTimeout):

    Checks for the machine's rotation, sends the signals (activates
    solenoid valves) after the caster is in the "air bar down" position.

    If no machine rotation is detected (photocell input doesn't change
    its state) during machineTimeout, calls a function to ask user
    what to do (can be useful for resuming casting after manually
    stopping the machine for a short time - not recommended as the
    mould cools down and type quality can deteriorate).

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
            """Now, the air bar on paper tower would go down -
            we got signal from photocell to let the air in:
            """
            self.activate_valves(signals)
            previousState = 1

          elif photocellState == 0 and previousState == 1:
            """Air bar on paper tower goes back up -
            end of "air in" phase, turn off the valves:
            """
            self.deactivate_valves()
            previousState = 0
            break

        else:
          """Ask the user what to do if the machine is stopped
          (no events from the photocell)."""
          self.machine_stopped()


  def activate_valves(self, signals):
    """activate_valves(signals):

    Activates the solenoid valves connected with interface's outputs,
    as specified in the "signals" argument (tuple or list).
    The input array "signals" contains strings, either
    lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
    Do nothing if the function receives an empty sequence, which will
    occur if we cast with the matrix found at position O15.
    """
    if signals:
      for monotypeSignal in signals:
        pin = self.wiringPiPinNumber[monotypeSignal]
        wiringpi.digitalWrite(pin,1)


  def deactivate_valves(self):
    """deactivate_valves():

    Turn all valves off after casting/punching any character.
    Call this function to avoid outputs staying turned on if something
    goes wrong, esp. in case of abnormal program termination.
    """
    for pin in range(self.pinBase, self.pinBase + 32):
      wiringpi.digitalWrite(pin,0)


  def machine_stopped(self):
    """machine_stopped():

    This allows us to choose whether we want to continue, return to menu
    or exit if the machine is stopped during casting.
    """
    choice = ""
    while choice not in ['c', 'm', 'e']:
      choice = raw_input(
                         "Machine not running! Check what\'s going on."
                         "\n(C)ontinue, return to (M)enu "
                         "or (E)xit program."
                        )
    else:
      if choice.lower() == 'c':
        return True
      elif choice.lower() == 'm':
        self.job.userInterface.main_menu()
      elif choice.lower() == 'e':
        exit()


  def __exit__(self, *args):
    """On exit, turn all the valves off"""
    self.deactivate_valves()



class MonotypeSimulation(object):
  """MonotypeSimulation:

  A class which allows to test rpi2caster without an actual interface
  or caster. Most functionality will be developped without an access
  to the machine.
  """

  def __init__(self, job, casterName='Monotype Simulator', configFileName=''):
    self.job = job
    self.casterName = casterName
    print 'Using hypothetical caster: ', self.casterName
    print('Testing rpi2caster without an actual caster or interface. ')
    raw_input('Press [ENTER] to continue...')
    self.job.debugMode = True

  def __enter__(self):
    return self


  def send_signals_to_caster(self, signals, machineTimeout=5):
    """Just send signals, as we don't have a photocell"""
    raw_input('Press [ENTER] to simulate sensor going ON')
    self.activate_valves(signals)
    raw_input('Press [ENTER] to simulate sensor going OFF')
    self.deactivate_valves()


  def activate_valves(self, signals):
    """If there are any signals, print them out"""
    if len(signals) != 0:
      print 'The valves: ',' '.join(signals),' would be activated now.'


  def deactivate_valves(self):
    """No need to do anything"""
    print('The valves would be deactivated now.')


  def detect_rotation(self):
    """FIXME: implement raw input breaking on timeout"""
    print('Now, the program would check if the machine is rotating.\n')
    startTime = time.time()
    answer = None
    while answer is None and time.time() < (startTime + 5):
      answer = raw_input('Press [ENTER] (to simulate rotation) '
                         'or wait 5sec (to simulate machine off)\n')
    else:
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
        self.job.userInterface.main_menu()
      elif choice.lower() == 'e':
        exit()


  def __exit__(self, *args):
    pass



class Parsing(object):
  """This class contains file- and line-parsing methods.
  It contains static methods to be called by other functions only.
  You cannot instantiate it.
  """


  @staticmethod
  def read_file(filename):
    """Open a file with signals, test if it's readable
    and return its contents:
    """
    try:
      contents = []
      with open(filename, 'r') as inputFile:
        contentsGenerator = inputFile.readlines()
        for line in contentsGenerator:
          contents.append(line)
        return contents
    except IOError:
      raw_input(
                'Error: The file cannot be read! '
                '[ENTER] to go back to menu...'
                )
      return False


  @staticmethod
  def signals_parser(originalSignals):
    """signals_parser(originalSignals):

    Parses an input string, and returns a list with two elements:

    -the Monotype signals found in a line: A-N, 1-14, 0005, S, 0075.
    -any comments delimited by symbols from commentSymbols list.
    """

    """We need to work on strings. Convert any lists, integers etc."""
    signals = str(originalSignals)

    """This is a comment parser. It looks for any comment symbols
    defined here - e.g. **, *, ##, #, // etc. - and saves the comment
    to return it later on.

    If it's an inline comment (placed after Monotype code combination),
    this combination will be returned for casting.

    If a line in file contains a comment only, returns no combination.

    If we want to cast O15, we have to feed an empty line
    (place the comment above).

    Example:

    ********
    O15 //comment         <-- casts from O+15 matrix, displays comment
                          <-- casts from O+15 matrix
    //comment             <-- displays comment
    0005 5 //comment      <-- sets 0005 justification wedge to 5,
                              turns pump off, displays comment
    """
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



class Casting(object):
  """
  Casting:

  A "job" class. Job-wide variables include caster (and its parameters),
  interface (and its parameters), database, config, ribbon filename.

  All methods related to operating a composition caster:
  -casting composition and sorts,
  -testing and calibrating the caster,
  -testing the interface
  """

  def __init__(self):
    self.debugMode = False

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass


  def cast_composition(self):
    """cast_composition()

    Composition casting routine. The input file is read backwards -
    last characters are cast first, after setting the justification.
    """

    """Read the file contents:"""
    contents = Parsing.read_file(self.ribbonFile)

    """If file read failed, end here:"""
    if not contents:
      return False

    """For casting, we need to read the contents in reversed order:"""
    contents = reversed(contents)

    """Display a little explanation:"""
    print(
          '\nThe combinations of Monotype signals will be displayed '
          'on screen while the machine casts the type.\n'
          'Turn on the machine and the program will '
          'start automatically.\n'
          )

    """Check if the machine is running - don't do anything when
    it's not rotating yet!"""
    self.caster.detect_rotation()

    """Read the reversed file contents, line by line, then parse
    the lines, display comments & code combinations, and feed the
    combinations to the caster:
    """
    for line in contents:

      """Parse the row, return a list of signals and a comment.
      Both can have zero or positive length."""
      signals, comment = Parsing.signals_parser(line)

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
        self.caster.send_signals_to_caster(signals)

    """After casting is finished, notify the user:"""
    print('\nCasting finished!')

    """End of function."""


  def line_test(self):
    """line_test():

    Tests all valves and composition caster's inputs to check
    if everything works and is properly connected. Signals will be tested
    in order: 0005 - S - 0075, 1 towards 14, A towards N, O+15, NI, NL,
    EF, NJ, NK, NKJ, MNH, MNK (feel free to add other combinations!)
    """
    raw_input('This will check if the valves, pin blocks and 0005, S, '
             '0075 mechanisms are working. Press return to continue... ')

    combinations = [
                    ['0005'], ['S'], ['0075'], ['1'], ['2'], ['3'],
                    ['4'], ['5'], ['6'], ['7'], ['8'], ['9'], ['10'],
                    ['11'], ['12'], ['13'], ['14'], ['A'], ['B'],
                    ['C'], ['D'], ['E'], ['F'], ['G'], ['H'], ['I'],
                    ['J'], ['K'], ['L'], ['M'], ['N'], ['O15'],
                    ['N', 'I'], ['N', 'L'], ['N', 'J'], ['N', 'K'], ['E', 'F'],
                    ['N', 'K', 'J'], ['M', 'N', 'H'], ['M', 'N', 'K']
                   ]

    """Send all the combinations to the caster, one by one:"""
    for combination in combinations:
      print ' '.join(combination)
      self.caster.send_signals_to_caster(combination, 120)

    print('\nTesting finished!')

    """End of function."""


  def cast_sorts(self):
    """cast_sorts():

    Sorts casting routine, based on the position in diecase.
    Ask user about the diecase row & column, as well as number of sorts.
    """
    os.system('clear')
    print('Calibration and Sort Casting:\n\n')
    signals = raw_input(
                        'Enter column and row symbols '
                        '(default: G 5, spacebar if O-15) '
                       )
    print('\n')
    if signals == '':
      signals = 'G5'

    """
    Parse the signals and return a list containing the parsed
    signals and the comments:
    """
    [parsedSignals, comment] = Parsing.signals_parser(signals)

    """
    O15 yields no signals, but we may want to cast it - check if we
    entered spacebar. If parsing yields no signals (for example,
    user entered a string with row > 16 or column > O), check
    if user entered spacebar. If it's not the case, user has to
    enter the combination again.
    """
    if len(parsedSignals) == 0 and signals != ' ':  # if not parsedSignals ??
      print('\nRe-enter the sequence')
      time.sleep(1)
      cast_sorts()                                  # recurse - test it!!!
    n = raw_input(
                  '\nHow many sorts do you want to cast? (default: 10) '
                 )
    print('\n')

    """Default to 10 if user enters non-positive number or letters"""
    if not n.isdigit() or int(n) < 0:
      n = '10'
    n = int(n)

    """Warn if we want to cast too many sorts from a single matrix"""
    print ("\nWe'll cast it %i times.\n" % n)
    if n > 10:
      print(
            'Warning: you want to cast a single character more than '
            '10 times. This may lead to matrix overheating!\n'
           )

    """Ask user if the entered parameters are correct"""
    choice = ''                                         # use simple menu from UI object
    while choice not in ['c', 'r', 'm', 'e']:
      choice = raw_input(
                         '[C]ontinue, [R]epeat, go back to [M]enu '
                         'or [E]xit program? '
                        )
    else:
      if choice.lower() == 'c':

        # Move it to another function (will be useful for casting spaces!)

        """Check if the machine is running"""
        print('Start the machine...')
        self.caster.detect_rotation()

        """Cast the sorts: turn on the pump first."""
        print('Starting the pump...')
        self.caster.send_signals_to_caster(['0075'])

        """Start casting characters"""
        print('Casting characters...')

        """Cast n combinations of row & column, one by one"""
        for i in range(n):
          if len(parsedSignals) > 0:
            print ' '.join(parsedSignals)
          else:
            print('O+15 - no signals')
          self.caster.send_signals_to_caster(parsedSignals)

        """Put the line to the galley:"""
        print('Putting line to the galley...')
        self.caster.send_signals_to_caster(['0005', '0075'])
        """After casting sorts we need to stop the pump"""
        print('Stopping the pump...')
        self.caster.send_signals_to_caster(['0005'])


      elif choice.lower() == 'r':
        cast_sorts()                         # not sure if it'll work
      elif choice.lower() == 'm':
        pass
      elif choice.lower() == 'e':
        self.caster.deactivate_valves()
        exit()                                   # Better to call UI's method

    """Ask what to do after casting"""
    print('\nFinished!')                         # Deprecate std i/o in functions

# Use simple menu from UI

    finishedChoice = ''
    while finishedChoice.lower() not in ['r', 'm', 'e']:
      finishedChoice = raw_input(
                                 '(R)epeat, go back to (M)enu '
                                 'or (E)xit program? '
                                )
      if finishedChoice.lower() == 'r':
        cast_sorts()                            # not sure if it'll work
      elif finishedChoice.lower() == 'm':
        pass
      elif finishedChoice.lower() == 'e':
        self.caster.deactivate_valves()
        exit()                                  # call UI's exit method

      else:   # deprecated
        print('\nNo such option. Choose again.')
        finishedChoice = ''


  def send_combination(self):
    """send_combination():

    This function allows us to give the program a specific combination
    of Monotype codes, and will keep the valves on until we press return
    (useful for calibration). It also checks the signals' validity.
    """

    """Let the user enter a combo:"""
    signals = ''
    while signals == '':
      signals = raw_input(
                          'Enter the signals to send to the machine: '
                         )

    """Parse the combination, get the signals (first item returned
    by the parsing function):"""
    combination = Parsing.signals_parser(signals)[0]

    """Check if we get any signals at all, if so, turn the valves on:"""
    if combination:
      print ' '.join(combination)
      self.caster.activate_valves(combination)

    """Wait until user decides to stop sending those signals to valves:"""
    raw_input('Press return to stop. ')
    self.caster.deactivate_valves()
    """End of function"""


  def align_wedges(self, space='G5'):
    """align_wedges(space='G5'):

    Allows to align the justification wedges so that when you're
    casting a 9-unit character with the S-needle at 0075:3 and 0005:8
    (neutral position), the  width is the same.

    It works like this:
    1. 0075 - turn the pump on,
    2. cast 10 spaces from the specified matrix (default: G9),
    3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
    4. cast 10 spaces with the S-needle from the same matrix,
    5. put the line to the galley, then 0005 to turn the pump off.
    """

    """Print some info for the user:"""
    print('Transfer wedge calibration:\n\n'
          'This function will cast 10 spaces, then set the correction '
          'wedges to 0075:3 and 0005:8, \nand cast 10 spaces with the '
          'S-needle. You then have to compare the length of these two '
          'sets. \nIf they are identical, all is OK. '
          'If not, you have to adjust the 52D wedge.\n\n'
          'Turn on the machine...')

    """Don't start until the machine is running:"""
    self.caster.detect_rotation()

    combinations = (
                    ['0075'] + [space] * 10 + ['0075 0005 8'] + ['0075 3'] +
                    [space + 'S'] * 10 + ['0075 0005'] + ['0005']
                   )

    for sequence in combinations:
      """Make a list out of the strings:"""
      sequence = Parsing.signals_parser(sequence)[0]

      """Display the sequence on screen:"""
      print(' '.join(sequence))

      """Cast the sequence:"""
      self.caster.send_signals_to_caster(sequence)

    """Finished. Return to menu."""
    print('Procedure finished. Compare the lengths and adjust if needed.')



class RibbonPunching(object):
  """Job class for punching the paper tape (ribbon)."""

  def __init__(self):
    self.debugMode = False

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass


  def punch_composition(self):
    """punch_composition():

    When punching, the input file is read forwards. An additional line
    (O+15) is switched on for operating the paper tower, if less than
    two signals are found in a sequence.
    """

    """Read the file contents:"""
    contents = Parsing.read_file(self.ribbonFile)

    """If file read failed, end here:"""
    if not contents:
      return False

    """Wait until the operator confirms.

    We can't use automatic rotation detection like we do in
    cast_composition, because keyboard's paper tower doesn't run
    by itself - it must get air into tubes to operate, punches
    the perforations, and doesn't give any feedback.
    """
    print('\nThe combinations of Monotype signals will be displayed '
              'on screen while the paper tower punches the ribbon.\n')
    raw_input('\nInput file found. Turn on the air, fit the tape '
           'on your paper tower and press return to start punching.\n')
    for line in contents:

      """
      Parse the row, return a list of signals and a comment.
      Both can have zero or positive length.
      """
      signals, comment = Parsing.signals_parser(line)

      """Print a comment if there is one - positive length"""
      if len(comment) > 0:
        print comment

      """
      Punch an empty line, signals with comment, signals with
      no comment.

      Don't punch a line with nothing but comments
      (prevents erroneous O+15's).
      """
      if len(comment) == 0 or len(signals) > 0:

        """Determine if we need to turn O+15 on"""
        if len(signals) < 2:
          signals += ('O15',)
        print ' '.join(signals)
        self.caster.activate_valves(signals)         # keyboard?

        """The pace is arbitrary, let's set it to 200ms/200ms"""
        time.sleep(0.2)
        self.caster.deactivate_valves()              # keyboard?
        time.sleep(0.2)

    """After punching is finished, notify the user:"""
    print('\nPunching finished!')

    """End of function."""



class TextUserInterface(object):
  """TextUserInterface(job):

  Use this class for creating a text-based console user interface.

  A caster object must be created before instantiating this class.

  Suitable for controlling a caster from the local terminal or via SSH,
  supports UTF-8 too.
  """

  def __init__(self, job):
    """
    On instantiating, we must specify the job.
    Then, we'll be able to reach its other sub-classes.
    """
    self.job = job

    """Set up an empty ribbon file name first"""
    job.ribbonFile = ''

  def __enter__(self):
    return self


  def tab_complete(text, state):
    """tab_complete(text, state):

    This function enables tab key auto-completion when you
    enter the filename.
    """
    return (glob.glob(text+'*')+[None])[state]
  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(tab_complete)


  def consoleUI(self):
    """consoleUI():

    Main loop definition. All exceptions should be caught here.
    Also, ensure cleaning up after exit.
    """
    try:
      self.main_menu()
    except (IOError, NameError):
      raw_input(
                '\nInput file not chosen or wrong input file name. '
                'Press return to go to main menu.\n'
                )
      if self.job.debugMode:
        print('Debug mode: see what happened.')
        raise
      self.main_menu()

    except KeyboardInterrupt:
      print('\nTerminated by user.')
      exit()
    finally:
      print('Goodbye!')
      self.job.caster.deactivate_valves()


  def menu(self, options, **kwargs):
    """menu(
            options={'foo':'bar','baz':'qux'}
            header=foo,
            footer=bar):

    A menu which takes three arguments:
    header - string to be displayed above,
    footer - string to be displayed below.,

    After choice is made, executes the command.
    """

    """Parse the keyword arguments. If argument is unset, assign
    an empty string.
    """
    try:
      header = kwargs['header']
    except KeyError:
      header = ''

    try:
      footer = kwargs['footer']
    except KeyError:
      footer = ''


    """Set up vars for conditional statements,
     and lists for appending new items.

     choices - options to be entered by user,
     commands - commands to be executed after option is chosen,
     pauses - flags indicating whether the program will be paused
              on return to menu (waiting for user to press return):
     """
    yourChoice = ''
    choices = []


    """Clear the screen, display header and add two empty lines:"""
    os.system('clear')
    if header:
      print header
      print('')

    """Display all the options; construct the possible choices list:"""

    for choice in options:
       if choice != 0:
        """Print the option choice and displayed text:
        """
        print '\t', choice, ' : ', options[choice], '\n'
        choices.append(str(choice))

    try:
      """If an option "0." is available, print it as a last one:"""
      optionNumberZero = options[0]
      print '\n'
      print '\t', 0, ' : ', optionNumberZero
      choices.append('0')
    except KeyError:
      pass


    """Print footer, if defined:"""
    if footer:
      print('')
      print footer
    print('\n')

    """Ask for user input:"""
    while yourChoice not in choices:
      yourChoice = raw_input('Your choice: ')
    else:
      """Valid option is chosen, return integer if options were numbers,
      else return string:
      """
      try:
        return int(yourChoice)
      except ValueError:
        return yourChoice


  def enter_filename(self):
    """Enter the ribbon filename; check if the file is readable"""
    fn = raw_input('\n Enter the ribbon file name: ')
    fn = os.path.realpath(fn)
    try:
      with open(fn, 'r'):
        return fn
    except IOError:
      raw_input('Wrong filename or file not readable!')
      return ''


  def main_menu(self):
    """Calls menu() with options, a header and a footer.
    Does not use the recursive feature of menu(), because the
    additional information would not be displayed.
    Instead, recursion is implemented in this function.
    """
    """Options: {option_name : description}"""
    options = {
               1 : 'Load a ribbon file',
               2 : 'Cast composition',
               3 : 'Punch a paper tape',
               4 : 'Cast sorts',
               5 : 'Test the valves and pinblocks',
               6 : 'Lock the caster on a specified diecase position',
               7 : 'Calibrate the 0005 and 0075 wedges',
               0 : 'Exit program'
              }


    """Sometimes we need to display notice on returning to menu:"""
    def hold_on_exit():
      raw_input('Press Enter to return to main menu...')

    """Declare local functions for menu options:"""
    def choose_ribbon_filename():
      self.job.ribbonFile = self.enter_filename()
    def cast_composition():
      self.job.cast_composition()
      hold_on_exit()
    def punch_composition():
      self.job.punch_composition()
      hold_on_exit()
    def cast_sorts():
      self.job.cast_sorts()
    def line_test():
      self.job.line_test()
    def send_combination():
      self.job.send_combination()
      hold_on_exit()
    def align_wedges():
      self.job.align_wedges()
      hold_on_exit()
    def exit_program():
      exit()

    def debug_notice():
      """Prints a notice if the program is in debug mode:"""
      if self.job.debugMode:
        return('\n\nThe program is now in debugging mode!')
      else:
        return ''

    def main_menu_additional_info():
      """Displays additional info as a main menu footer:"""
      if self.job.ribbonFile != '':
        return(
               'Input file name: ' + self.job.ribbonFile
              )


    """Commands: {option_name : function}"""
    commands = {
                1 : choose_ribbon_filename,
                2 : cast_composition,
                3 : punch_composition,
                4 : cast_sorts,
                5 : line_test,
                6 : send_combination,
                7 : align_wedges,
                0 : exit_program
               }

    choice = self.menu(
              options,
              header = (
                        'rpi2caster - CAT (Computer-Aided Typecasting) '
                        'for Monotype Composition or Type and Rule casters.'
                        '\n\n'
                        'This program reads a ribbon (input file) '
                        'and casts the type on a Composition Caster, \n'
                        'or punches a paper tape with a paper tower '
                        'taken off a Monotype keyboard.'
                       ) + debug_notice() + '\n\nMain Menu:',

              footer = main_menu_additional_info()
              )


    """Call the function and returnn to menu:"""
    commands[choice]()
    self.main_menu()


  def simple_menu(self, message, options):
    """A simple menu where user is asked what to do.
    Wrong choice points back to the menu.

    Message: string displayed on screen;
    options: a list or tuple of strings - options.
    """
    ans = ''
    while ans not in options:
      ans = raw_input(message)
    return ans


  def __exit__(self, *args):
    pass



class Testing(object):
  """Testing:

  A class for testing the program without an actual caster/interface.
  Certain functions referring to the caster will be replaced with
  placeholder methods from the MonotypeSimulation class.
  """
  def __init__(self):
    pass

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass


class WebInterface(object):
  """WebInterface:

  Use this class for instantiating text-based console user interface"""

  def __init__(self, job):
    """instantiate config for the caster"""
    self.job = job

  def __enter__(self):
    return self

  def webUI(self):
    """This is a placeholder for web interface method. Nothing yet..."""
    pass

  def __exit__(self, *args):
    pass



"""And now, for something completely different...
Initialize the console interface when running the program directly."""
if __name__ == '__main__':

  job = Casting()
  job.database = Database(job)
  job.caster = Monotype(job, 'mkart-cc')
  job.userInterface = TextUserInterface(job)

  with job, database, caster, userInterface:
    userInterface.consoleUI()