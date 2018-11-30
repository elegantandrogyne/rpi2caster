# -*- coding: utf-8 -*-
"""Casting utility: cast or punch ribbon, cast material for hand typesetting,
make a diecase proof, quickly compose and cast text.
"""
from functools import wraps

# common definitions
import librpi2caster
# QR code generating backend
try:
    import qrcode
except ImportError:
    qrcode = None

from . import ui
from . import monotype
from .functions import pump_stop, single_justification, double_justification
from .models import Ribbon


def cast_this(ribbon_source):
    """Get the ribbon from decorated routine and cast it"""
    @wraps(ribbon_source)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        ribbon = ribbon_source(self, *args, **kwargs)
        return None if not ribbon else self.machine.cast_or_punch(ribbon)
    return wrapper


class Casting:
    """Casting:

    Methods related to operating the composition caster.
    Requires configured caster.

    All methods related to operating a composition caster are here:
    -casting composition and sorts, punching composition,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""
    machine = monotype.SimulationCaster()
    ribbon = Ribbon()

    def __init__(self):
        try:
            machine = monotype.MonotypeCaster()
            if ui.confirm('Use real machine (N = simulation) ?'):
                self.machine = machine
        except librpi2caster.InterfaceException:
            message = ('The hardware interface is not available. \n'
                       'Using simulation mode instead...')
            ui.pause(message)

    @cast_this
    def cast_material(self):
        """Cast typesetting material: typecases, specified sorts, spaces"""
        def make_queue():
            """generate a sequence of items for casting"""
            def add_new_char():
                """Adds a mat to a queue"""
                mat = ui.choose_mat(wedge, specify_units=True)
                if not mat:
                    return None
                # how many matrices? (mat not specified? then don't ask)
                qty_prompt = 'How many sorts? (0 = cancel, start new)'
                qty = ui.enter(qty_prompt, default=10, minimum=0)
                if qty:
                    queue.append((mat, qty))
                    ui.display('Added {} of {}, {} units wide.'
                               .format(qty, mat.code, mat.units))
                    return (mat, qty)
                return None

            def view_queue():
                """Show all characters in the queue"""
                items = ['{} of {}, {} units wide'
                         .format(qty, mat.code, mat.units)
                         for (mat, qty) in queue]
                ui.display('\n'.join(items))

            def cast():
                """Set a flag to finish specifying characters"""
                nonlocal done
                done = True

            queue = []
            done = False
            # menu for user decision
            options = [ui.option(key='n', value=add_new_char, seq=1,
                                 text='next character'),
                       ui.option(key='Del', value=queue.pop, seq=2,
                                 text='delete last entry'),
                       ui.option(key='v', value=view_queue, seq=3,
                                 text='view queue'),
                       ui.option(key='c', value=cast, text='cast', seq=4)]

            while not done:
                if not add_new_char():
                    ui.simple_menu('Choose what to do:',
                                   options, default_key='n')()

            # make a flat list of mats to cast from
            order = [item for mat, qty in queue for item in [mat] * qty]
            return order

        def make_ribbon(queue):
            """Iterate over the queue in order to transform all the items
            to Monotype codes."""
            def start_line():
                """Start a new line"""
                nonlocal units_left
                units_left = galley_units
                ribbon.append(quad.code)

            def end_line(char_wedges):
                """Fill the line with quads and add a variable space
                in order to get the length equal (for tying the type)."""
                num_quads = int(units_left // quad.units + 1)
                # space width: the remainder from dividing units left by 18
                # (or whatever the quad unit width is), in units
                space_units = units_left % quad.units
                # choose a matrix for the space
                space_position = 'G2' if space_units < 16 else 'O15'
                space = ui.choose_mat(wedge, space_position, space_units,
                                      specify_code=False)
                # use single justification to set the character width
                if char_wedges not in (space.wedges, (3, 8)):
                    ribbon.extend(single_justification(char_wedges))
                # add a space to get the width equal
                ribbon.append(space.code)
                # fill in with quads
                ribbon.extend([quad.code] * num_quads)
                ribbon.extend(double_justification(space.wedges))

            # initialize a ribbon with line out and pump stop
            # no justification here
            ribbon = [*pump_stop(), *double_justification()]
            start_line()
            # a list of (n, n+1) pairs of matrices for next char prediction
            pairs = zip(queue, [*queue[1:], None])
            for curr_mat, next_mat in pairs:
                # add a mat to the sequence and update the units count
                ribbon.append(curr_mat.code)
                units_left -= curr_mat.units
                if not next_mat:
                    # all matrices done; fill the line
                    end_line(curr_mat.wedges)
                    break

                # predict if we can put the next sort into the line;
                # if that's not the case, fill and start a new one
                elif next_mat.units > units_left:
                    end_line(curr_mat.wedges)
                    start_line()

                else:
                    # next character will fit in
                    # check if we need to change the justification wedges
                    if curr_mat.wedges not in (next_mat.wedges, (3, 8)):
                        ribbon.extend(single_justification(curr_mat.wedges))

            return ribbon

        wedge = ui.choose_wedge()
        mat_queue = make_queue()
        # nothing to cast?
        if not mat_queue:
            return []
        galley_inches = ui.choose_type_size('Galley width?', '25P')
        # every line will start and end with a quad - O15;
        # that's why the number of units left for the characters will be lower
        quad = ui.choose_mat(wedge, code='O15', specify_code=False)
        galley_units = wedge.inches_to_units(galley_inches) - 2 * quad.units
        # generate the ribbon
        return make_ribbon(mat_queue)

    @cast_this
    def cast_qr_code(self):
        """Set up and cast a QR code which can be printed and then scanned
        with a mobile device."""
        def make_qr(data):
            """make a QR code matrix from data"""
            # QR rendering parameters
            border = ui.enter('QR code border width (squares)?', default=1,
                              minimum=1, maximum=10)
            ec_option = ui.enter('Error correction: 0 = lowest, 3 = highest?',
                                 default=1, minimum=0, maximum=3)
            # set up a QR code and generate a matrix
            modes = (qrcode.constants.ERROR_CORRECT_L,
                     qrcode.constants.ERROR_CORRECT_M,
                     qrcode.constants.ERROR_CORRECT_H,
                     qrcode.constants.ERROR_CORRECT_Q)
            engine = qrcode.QRCode(error_correction=modes[ec_option],
                                   border=border)
            engine.add_data(data)
            qr_matrix = engine.get_matrix()
            return qr_matrix

        def render(pattern, high_space, low_space):
            """translate a pattern into Monotype control codes,
            applying single justification if space widths differ,
            making spaces square in shape"""
            characters = {False: low_space, True: high_space}
            # pump stop and last line out (this will be cast at the end)
            ribbon = [*pump_stop(), *double_justification()]

            for line in pattern:
                # predict the next character
                pairs = zip(line, [*line[1:], None])
                for curr_item, next_item in pairs:
                    # add all spaces in a row
                    curr_mat = characters.get(curr_item)
                    next_mat = characters.get(next_item, curr_mat)
                    ribbon.append(curr_mat.code)
                    # check wedge positions and predict if we need to set them
                    if curr_mat.wedges not in ((3, 8), next_mat.wedges):
                        # set the wedges only if we need to
                        # use single justification in this case
                        ribbon.extend(single_justification(curr_mat.wedges))
                # finish the line with double justification/galley trip
                # will be cast in reverse (i.e. starting with 0075+0005)
                ribbon.extend(double_justification(curr_mat.wedges))
            return ribbon

        # first choose a normal wedge for unit calculations
        wedge = ui.choose_wedge()

        # set the pixel size; smaler is preferred; the same as mould size
        # all pixels will be square; unit correction is used
        inches = ui.choose_type_size('Type size i.e. mould to use?')
        units = wedge.inches_to_units(inches)
        ui.display('The pixel size is {}" - that is {} units {} set.'
                   .format(inches, units, wedge.set_width))

        # enter text and encode it
        text = ui.enter('Enter data to encode', '')
        qr_matrix = make_qr(text)
        # let the operator know how large the code is
        size = len(qr_matrix)
        prompt = ('The resulting QR code is {0} × {0} squares '
                  'or {1} × {1} inches.')
        ui.display(prompt.format(size, round(size * inches, 1)))
        ui.pause('Set your galley accordingly or abort.', allow_abort=True)
        # what matrix coordinates to use as low/high space?
        ui.display('Now choose the matrices to use for printed '
                   'and for non-printed squares.\n\n'
                   'It is recommended to use a high space at N15 '
                   'and a low space at O15 respectively.\n')

        ui.display('Where is the high quad mat for printed squares?')
        high = ui.choose_mat(wedge, code='N15', units=units)
        ui.display('Where is the low quad mat for whitespace?')
        low = ui.choose_mat(wedge, code='O15', units=units)

        # make a sequence of low and high spaces to cast
        return render(qr_matrix, high, low)

    @cast_this
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            raise ui.Abort
        return self.ribbon.contents

    @cast_this
    def diecase_proof(self):
        """Tests the whole diecase, casting from each matrix.
        Casts spaces between characters to be sure that the resulting
        type will be of equal width."""
        def make_diecase():
            """let the user choose the matrix case format,
            return lists of rows and columns to iterate over"""
            rows_15 = [n+1 for n in range(15)]
            rows_16 = [*rows_15, 16]
            cols_15 = [l for l in 'ABCDEFGHIJKLMNO']
            cols_17 = ['NI', 'NL', *cols_15]
            # ask the user about the diecase format
            options = [ui.option(key='1', value=(rows_15, cols_15),
                                 text='15x15 small'),
                       ui.option(key='2', value=(rows_15, cols_17),
                                 text='15x17 extended'),
                       ui.option(key='3', value=(rows_16, cols_17),
                                 text='16x17 HMN, KMN, unit-shift')]
            prompt = 'Choose the matrix case size:'
            diecase = ui.simple_menu(prompt, options, default_key='2')
            # will return the lists of rows (15 or 16) and columns (15 or 17)
            return diecase

        # early cancel
        ui.display('This will cast a matrix case layout.\n'
                   'You need to place a space at G2 and O15. \n'
                   'It is recommended to use high space mats here, '
                   'as the space may be used for supporting \n'
                   'the overhanging characters, if they are too wide '
                   'for the row they are placed, or a wrong wedge is used.')
        if not ui.confirm('Proceed?', default=True, abort_answer=False):
            return None

        # choose a wedge for casting the diecase proof
        wedge = ui.choose_wedge()
        rows, columns = make_diecase()
        # double pump stop and galley trip
        ribbon = [*pump_stop(), *double_justification()]
        # make a ribbon with all positions
        for row in rows:
            ui.display('Processing row {}'.format(row))
            # use G2 for narrower than 16 units and O15 for wide spaces
            # will be adjusted with variable wedges
            space_units = 23 - wedge[row]
            space_code = 'G2' if space_units < 16 else 'O15'
            space = ui.choose_mat(wedge, code=space_code, units=space_units,
                                  specify_code=False, specify_units=False)
            # line starting quad (in print) - cast last
            ribbon.append('O15')
            for column in columns:
                # add a space that will be cast after the character,
                # left of it (in print) b/c width adjustment
                # takes place on the left side of the character
                ribbon.append(space.code)
                # and then a character
                ribbon.append('{} {}'.format(column, row))
            # line ending quad (in print) - cast first
            ribbon.append('O15')
            # end line (cast first), set the wedges
            ribbon.extend(double_justification(space.wedges))

        return ribbon

    def calibrate_machine(self):
        """Casts the "en dash" characters for calibrating the character X-Y
        relative to type body."""
        def make_ribbon():
            """Gets two mats for a given char and adjusts its parameters"""
            sequence = [*pump_stop()]
            # specify the mats
            ui.display('Where is a quad i.e. 18-unit space?')
            quad = ui.choose_mat(wedge, 'O15')
            ui.display('Where is a half-quad i.e. 9-unit space?')
            space = ui.choose_mat(wedge, 'G5')
            ui.display('Where is a calibration character, n or h?')
            char = ui.choose_mat(wedge, specify_units=True)
            ui.display('Where is a dash or hyphen?')
            dash = ui.choose_mat(wedge, specify_units=True)
            # characters and their unit widths chosen...
            items = [(quad, 'square = em quad'),
                     (space, 'half-square = 1/2em quad'),
                     (char, 'calibration character'),
                     (dash, 'dash / hyphen')]
            record = '{} // {}, width: {:2.4f} inches'
            wedges = (3, 8)
            while items:
                mat, name = items.pop()
                if not mat:
                    # skip the character
                    continue
                # get the inch width of a character
                inches = wedge.set_width / 12 * mat.units / 18 * wedge.pica
                # add the character to the queue
                sequence.extend(2 * [record.format(mat.code, name, inches)])

                # check if we need to set the character width correction
                if wedges in (mat.wedges, (3, 8)):
                    continue
                else:
                    # use single justification
                    sequence.extend(single_justification(wedges))
                    wedges = mat.wedges
            sequence.extend(double_justification(wedges))
            return sequence

        # Character width and position calibration
        ui.display('Mould blade opening width and X-Y character calibration:\n'
                   'Measure the quad / half-quad width and adjust '
                   'the mould blade abutment slide adjusting screw c14C1 \n'
                   '(coarse) and micrometer wedge adjusting screw a20D2 (fine)'
                   ' so that the type is of proper width.\n'
                   '\nThen use the 33A1 / 33A2 micrometer screws on the bridge'
                   'to adjust the X-Y position of the character.\n'
                   'Finally, put two dashes next to each other '
                   '(one of them upside down) and adjust the Y position '
                   'so that they line up.\n')

        if ui.confirm('Calibrate the mould and diecase?'):
            # go on, choose a wedge for calibration, widths depend on it
            wedge = ui.choose_wedge()
            ribbon = make_ribbon()
            self.machine.cast(ribbon)

        if ui.confirm('Calibrate the bridge as well?'):
            self.calibrate_bridge()

    def calibrate_bridge(self):
        """Calibrate the bridge draw rods to eliminate the diecase wobble"""
        ui.display('Adjust the matrix case draw rods '
                   'so that the diecase is not wobbling anymore.\n')
        if ui.confirm('Calibrate G-8?'):
            self.machine.testing_mode = True
            with self.machine:
                self.machine.test_one('G8')
                ui.pause('Sending G8, press any key to stop...')

    def diagnostics(self):
        """Settings and alignment menu for servicing the caster"""
        def test_front_pinblock(*_):
            """Sends signals 1...14, one by one"""
            info = 'Testing the front pinblock - signals 1...14.'
            ui.pause(info, allow_abort=True)
            self.machine.test([str(n) for n in range(1, 15)])

        def test_rear_pinblock(*_):
            """Sends NI, NL, A...N"""
            info = 'This will test the rear pinblock - NI, NL, A...N. '
            ui.pause(info, allow_abort=True)
            self.machine.test(['NI', 'NL', *'ABCDEFGHIJKLMN'])

        def test_all(*_):
            """Tests all valves and composition caster's inputs in original
            Monotype order:
            NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
            """
            info = ('This will test all the air lines in the same order '
                    'as the holes on the paper tower: \n{}\n'
                    'MAKE SURE THE PUMP IS DISENGAGED.')
            signals = [*'ONMLKJIHGFSED', '0075', *'CBA',
                       *(str(x) for x in range(1, 15)), '0005', '15']
            ui.pause(info.format(' '.join(signals)), allow_abort=True)
            self.machine.test(signals)

        def test_justification(*_):
            """Tests the 0075-S-0005"""
            info = 'This will test the justification pinblock: 0075, S, 0005.'
            ui.pause(info, allow_abort=True)
            self.machine.test(['0075', 'S', '0005'])

        def test_any_code(*_):
            """Tests a user-specified combination of signals"""
            self.machine.testing_mode = True
            with self.machine:
                while True:
                    ui.display('Enter the signals to send to the caster, '
                               'or leave empty to return to menu: ')
                    signals = ui.enter('Signals?', default=ui.Abort)
                    # signals after operation/row16 mode correction
                    output = self.machine.test_one(signals).get('signals', [])
                    ui.display('Sending {}'.format(' '.join(output)))

        def blow_all(*_):
            """Blow all signals for a short time; add NI, NL also"""
            info = 'Blowing air through all air pins on both pinblocks...'
            ui.pause(info, allow_abort=True)
            queue = ['NI', 'NL', 'A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7',
                     'H8', 'I9', 'J10', 'K11', 'L12', 'M13', 'N14',
                     '0075 S', '0005 O 15']
            self.machine.test(queue, duration=0.3)

        def calibrate_wedges(*_):
            """Allows to calibrate the justification wedges so that when you're
            casting a 9-unit character with the S-needle at 0075:3 and 0005:8
            (neutral position), the    width is the same.

            It works like this:
            1. 0075 - turn the pump on,
            2. cast 7 spaces from the specified matrix (default: G5),
            3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
            4. cast 7 spaces with the S-needle from the same matrix,
            5. put the line to the galley, then 0005 to turn the pump off.
            """
            ui.display('Transfer wedge calibration:\n\n'
                       'This function will cast two lines of 5 spaces: '
                       'first: G5, second: GS5 with wedges at 3/8. \n'
                       'Adjust the 52D space transfer wedge '
                       'until the lengths are the same.\n')
            ui.confirm('Proceed?', default=True, abort_answer=False)
            # prepare casting sequence
            record, justified_record = 'G7', 'GS7'
            pump_start, pump_stop = 'NKS 0075 3', 'NJS 0005 8'
            line_out = 'NKJS 0005 0075 8'
            # start - 7 x G5 - line out - start - 7 x GS5 - line out - stop
            sequence = [pump_start, *[record] * 7, line_out, pump_start,
                        *[justified_record] * 7, line_out, pump_stop]
            self.machine.simple_cast(sequence)

        def test_row_16(*_):
            """Tests the row 16 addressing attachment (HMN, KMN, unit-shift).
            Casts from all matrices in 16th row.
            """
            ui.display('This will test the 16th row addressing.\n'
                       'If your caster has HMN, KMN or unit-shift attachment, '
                       'turn it on.\n')
            # build casting queue
            pump_start, pump_stop = 'NKS 0075', 'NJS 0005'
            line_out = 'NKJS 0005 0075'
            row = ['{}16'.format(col)
                   for col in ('NI', 'NL', *'ABCDEFGHIJKLMNO')]
            # test with actual casting or not?
            if ui.confirm('Use the pump? Y = cast the row, N = test codes.'):
                sequence = [pump_start, *row, line_out, pump_stop]
                self.machine.simple_cast(sequence)
            else:
                self.machine.choose_row16_mode(row16_needed=True)
                self.machine.test(row)

        def options():
            """Generate the menu options"""
            casting_mode = not self.machine.punch_mode
            ret = [ui.option(key='a', value=test_all, seq=1,
                             text='Test outputs',
                             desc='Test all air outputs N...O15, one by one'),
                   ui.option(key='f', value=test_front_pinblock, seq=2,
                             text='Test the front pin block',
                             desc='Test the pins 1...14'),
                   ui.option(key='r', value=test_rear_pinblock, seq=2,
                             text='Test the rear pin block',
                             desc='Test the pins NI, NL, A...N, one by one'),
                   ui.option(key='b', value=blow_all, seq=2,
                             text='Blow all air pins',
                             desc='Blow air into every pin for a short time'),
                   ui.option(key='j', value=test_justification, seq=2,
                             text='Test the justification block',
                             desc='Test the pins for 0075, S and 0005'),
                   ui.option(key='c', value=test_any_code, seq=1,
                             text='Send specified signal combination',
                             desc='Send the specified signals to the machine'),
                   ui.option(key='w', value=calibrate_wedges, seq=4,
                             cond=casting_mode,
                             text='Calibrate the 52D wedge',
                             desc=('Calibrate the space transfer wedge '
                                   'for correct width')),
                   ui.option(key='l', value=test_row_16, seq=5,
                             cond=casting_mode,
                             text='Test the extended 16x17 diecase system',
                             desc=('Cast type from row 16 '
                                   'with HMN, KMN or unit-shift'))]
            return ret

        header = 'Diagnostics and machine calibration menu:'
        catch_exceptions = (ui.Abort, KeyboardInterrupt, EOFError,
                            librpi2caster.MachineStopped)
        # Keep displaying the menu and go back here after any method ends
        ui.dynamic_menu(options=options, header=header, func_args=(self,),
                        catch_exceptions=catch_exceptions)

    def main_menu(self):
        """Main menu for the type casting utility."""
        def choose_ribbon():
            """Import the ribbon from a file"""
            self.ribbon = ui.choose_ribbon()

        def display_ribbon():
            """Display the ribbon contents"""
            ui.paged_display(self.ribbon.contents, sep='')

        def display_details():
            """Collect ribbon, diecase and wedge data here"""
            data = [self.ribbon.parameters if self.ribbon else {},
                    self.machine.parameters]
            ui.display_parameters(*data)
            ui.pause()

        def options():
            """Generate options based on current state of the program."""
            is_punching = self.machine.punch_mode
            is_casting = not is_punching

            got_ribbon = bool(self.ribbon)

            ret = [ui.option(key='m', value=self.calibrate_machine, seq=5,
                             cond=is_casting,
                             text='Calibrate type',
                             desc='Align the character width, then diecase'),

                   ui.option(key='b', value=self.calibrate_bridge, seq=6,
                             cond=is_casting, text='Calibrate bridge',
                             desc='Align the diecase draw rods'),

                   ui.option(key='c', value=self.cast_composition, seq=10,
                             cond=is_casting and got_ribbon,
                             text='Cast composition',
                             desc='Cast type from a selected ribbon'),

                   ui.option(key='r', value=choose_ribbon, seq=10,
                             text='Select ribbon',
                             desc='Select a ribbon from database or file'),

                   ui.option(key='p', value=self.cast_composition, seq=30,
                             cond=is_punching and got_ribbon,
                             text='Punch ribbon',
                             desc='Punch a paper ribbon for casting'),

                   ui.option(key='v', value=display_ribbon, seq=80,
                             text='View codes', cond=got_ribbon,
                             desc='Display all codes in the selected ribbon'),

                   ui.option(key='h', value=self.cast_material, seq=60,
                             cond=is_casting, text='Cast sorts or spaces',
                             desc='Cast characters from specified mats'),

                   ui.option(key='q', value=self.cast_qr_code, seq=70,
                             cond=qrcode, text='Cast QR codes',
                             desc='Cast QR codes from high and low spaces'),

                   ui.option(key='F5', value=display_details, seq=92,
                             text='Show details...',
                             desc='Display ribbon and interface information'),

                   ui.option(key='F6', value=self.diecase_proof, seq=93,
                             text='Diecase proof',
                             desc='Cast every character from the diecase'),

                   ui.option(key='F8', value=self.diagnostics, seq=95,
                             text='Diagnostics menu...',
                             desc='Interface and machine diagnostics')]
            return ret

        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'This program reads a ribbon (from file or database) '
                  'and casts the type on a composition caster.'
                  '\n\nCasting / Punching Menu:')
        exceptions = (ui.Abort, KeyboardInterrupt, EOFError)
        ui.dynamic_menu(options, header, catch_exceptions=exceptions)
