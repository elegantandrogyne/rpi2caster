# -*- coding: utf-8 -*-
"""Typesetter program"""

import io
from collections import deque
from .justification import Box, Glue, Penalty, ObjectList
from . import exceptions as e
from . import typesetting_funcs as tsf
from .measure import Measure
from .typesetting_data import Ribbon
from .matrix_data import Diecase, Matrix, diecase_operations
from .wedge_data import Wedge
from .global_config import UI


class Typesetting(object):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """
    def __init__(self, text_file='', ribbon_file='', diecase_id='',
                 manual_mode=False):

        self.measure = Measure(manual_choice=False)
        self.ribbon = Ribbon(ribbon_file)
        self.diecase = Diecase(diecase_id)
        self.source = text_file and open_file(text_file) or []
        # Use a manual compositor (user decides where to break the line)
        # or automatic compositor (hyphenation and justification is done
        # automatically with the Knuth-Plass algorithm)
        self.compositor = (manual_mode and ManualCompositor(self) or
                           AutoCompositor(self))

    def main_menu(self):
        """Main menu for the typesetting utility."""
        def finish():
            """Stop the loop"""
            nonlocal finished
            finished = True

        def choose_diecase():
            """Chooses a diecase from database"""
            self.diecase = Diecase(manual_choice=True)

        def choose_wedge():
            """Chooses a wedge from registered ones"""
            self.diecase.alt_wedge = Wedge(manual_choice=True)

        def change_measure():
            """Change a line length"""
            UI.display('Set the galley width...')
            self.measure = Measure()

        def menu_options():
            """Build a list of options, adding an option"""
            # Options are described with tuples:
            # (function, description, condition)
            opts = [(finish, 'Exit', 'Exits the program'),
                    (choose_diecase, 'Select diecase',
                     'Select a matrix case from database (current: %s)'
                     % (self.diecase or 'not selected')),
                    (choose_wedge, 'Select wedge',
                     'Enter a wedge designation (current: %s)'
                     % self.diecase.alt_wedge),
                    (change_measure, 'Change measure',
                     'Set new line length (current: %s)' % self.measure),
                    (self.diecase.show_layout, 'Show diecase layout',
                     'View the matrix case layout'),
                    (diecase_operations, 'Matrix manipulation',
                     'Work on matrix cases')]
            # Built a list of menu options conditionally
            return [(function, description, long_description)
                    for (function, description, long_description) in opts]

        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'Composition Menu:')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            # Catch any known exceptions here
            try:
                UI.menu(menu_options(), header=header, footer='')()
            except (e.ReturnToMenu, e.MenuLevelUp, KeyboardInterrupt):
                # Will skip to the end of the loop, and start all over
                pass


class Compositor(object):
    """Composition engine class"""
    def __init__(self, context):
        self.context = context


class ManualCompositor(Compositor):
    """Manual composition - allows more control over typesetting process"""
    def __init__(self, context):
        super().__init__(context)


class AutoCompositor(Compositor):
    """Automatic composition with hyphenation and justification"""
    def __init__(self, context):
        super().__init__(context)


class InputText(object):
    """Gets the input text, parses it, generates a sequence of characters
    or commands"""

    def __init__(self, text, context):
        self.context = context
        self.text = text

    def parse_input(self):
        """Generates a sequence of characters from the input text.
        For each character, this function predicts what two next characters
        and one next character are."""
        diecase = self.context.diecase
        # Cache the character set and spaces instead of generating
        # them ad hoc
        charset = diecase.charset
        spaces = diecase.spaces
        style_commands = {'^00': 'r', '^rr': 'r', '^01': 'i', '^ii': 'i',
                          '^02': 'b', '^bb': 'b', '^03': 's', '^ss': 's',
                          '^04': 'l', '^ll': 'l', '^05': 'u', '^uu': 'u'}
        # This variable will prevent yielding a number of subsequent chars
        # after a ligature or command has been found and yielded.
        skip_steps = 0
        # Default style is roman
        style = 'r'
        # Characters which will be skipped
        ignored = ('\n',)
        # Determine the length of character combinations parsed
        # Min = command length i.e. 3
        # Max = ligature length - dictated by diecase
        max_len = max(3, diecase.ligature_length)
        # What if char in text not present in diecase? Hmmm...
        for index, _ in enumerate(self.text):
            if skip_steps:
                # Skip the characters to be skipped
                skip_steps -= 1
                continue
            for i in range(max_len, 0, -1):
                # Start from longest, end with shortest
                try:
                    char = self.text[index:index+i]
                    skip_steps = i - 1
                    if char in ignored:
                        break
                    elif char in style_commands:
                        style = style_commands.get(char, 'r')
                        break
                    elif char in spaces:
                        yield spaces.get(char)
                        break
                    elif (char, style) in charset:
                        yield charset.get((char, style))
                        break
                except (TypeError, AttributeError, ValueError):
                    pass


class Justify(object):
    """Justification class"""
    def __init__(self, method='both'):
        pass


class Line(deque):
    """A line of type, justified to the left, center,right or both."""
    def __init__(self, length):
        super().__init__()
        self.length = length

    def __add__(self, new):
        if isinstance(new, Matrix):
            self.append(new)
        elif isinstance(new, (int, float)):
            self.length += new
        elif isinstance(new, (tuple, list, iter)):
            self.extend([x for x in new])

    def __radd__(self, new):
        if isinstance(new, Matrix):
            self.appendleft(new)
        elif isinstance(new, (int, float)):
            self.length += new
        elif isinstance(new, (tuple, list, iter)):
            self.extendleft([x for x in new])

    def render(self):
        """Renders a line into a series of Matrix objects with appropriate
        widths, and justified spaces."""
        # TODO
        pass

    def _align_left(self):
        """Aligns the previous chunk to the left."""
        pass

    def _align_right(self):
        """Aligns the previous chunk to the right."""
        pass

    def _align_center(self):
        """Aligns the previous chunk to the center."""
        pass

    def _align_both(self):
        """Aligns the previous chunk to both edges and ends the line."""
        pass


class Paragraph(object):
    """A page is broken into a series of paragraphs."""
    def __init__(self, width, style, indent, justification):
        self.width = width
        self.style = style
        self.indent = indent
        self.justification = justification

    def __iter__(self):
        return (x for x in self.nodes)

    def render(self):
        """Render all lines into combinations of Monotype codes"""
        pass

    @property
    def nodes(self):
        """Nodes are all characters, including ligatures, spaces
        and line-breaks"""
        return (node for line in self.lines for node in line)

    @property
    def lines(self):
        """Paragraph's lines"""
        return (line for line in self.lines)


class Page(object):
    """A page is a collection of paragraphs"""
    def __init__(self, width, height):
        self.width = width
        self.height = height


class GalleyBuilder(object):
    """Builds a galley from input sequence"""
    def __init__(self, source, context):
        self.source = (x for x in source)
        self.points = context.measure.points
        self.diecase = context.diecase
        # Cooldown: whether to separate sorts with spaces
        self.cooldown = False
        # Mould heatup: two lines filled with quads to heat the mould
        self.mould_heatup = True
        # Fill line: will add quads/spaces nutil length is met
        self.fill_line = True
        self.quad_padding = 1

    def preheat_mould(self):
        """Appends two lines of em-quads at the end"""
        chunk = []
        if self.mould_heatup:
            quad = self.diecase.decode_matrix('O15')
            quad_qty = int(self.points // quad.points)
            chunk = ['%s preheat' % quad] * quad_qty
            comment = 'Casting quads for mould heatup'
            chunk.extend(tsf.double_justification(comment=comment))
        return chunk * 2

    def make_ribbon(self):
        """Instantiates a Ribbon() object from whatever we've generated"""
        pass

    def build_galley(self):
        """Builds a line of characters from source"""
        def decode_mat(mat):
            """Gets the mat's parameters and stores them
            to avoid recalculation"""
            parameters = {}
            if mat:
                parameters['wedges'] = mat.wedge_positions()
                parameters['points'] = mat.points
                parameters['code'] = str(mat)
                parameters['lowspace'] = mat.islowspace()
            return parameters

        def start_line():
            """Starts a new line"""
            nonlocal points_left, queue
            points_left = self.points - 2 * self.quad_padding * quad['points']
            quads = [quad['code'] + ' quad padding'] * self.quad_padding
            queue.extend(quads)

        def build_line():
            """Puts the matrix in the queue, changing the justification
            wedges if needed, and adding a space for cooldown, if needed."""
            # Declare variables in non-local scope to preserve them
            # after the function exits
            nonlocal queue, points_left, working_mat, current_wedges
            # Take a mat from stash if there is any
            working_mat = working_mat or decode_mat(next(self.source, None))
            # Try to add another character to the line
            # Empty mat = end of line, start filling
            if points_left > working_mat.get('points', 1000):
                # Store wedge positions
                new_wedges = working_mat.get('wedges', (3, 8))
                # Wedges change? Drop in some single justification
                # (not needed if wedge positions were 3, 8)
                if current_wedges != new_wedges:
                    if current_wedges and current_wedges != (3, 8):
                        queue.extend(tsf.single_justification(current_wedges))
                    current_wedges = new_wedges
                # Add the mat
                queue.append(working_mat['code'])
                points_left -= working_mat['points']
                # We need to know what comes next
                working_mat = decode_mat(next(self.source, None))
                if working_mat:
                    next_points = space['points'] + working_mat['points']
                    space_needed = (points_left > next_points and not
                                    working_mat.get('lowspace', True))
                    if self.cooldown and space_needed:
                        # Add a space for matrix cooldown
                        queue.append(space['code'] + ' for cooldown')
                        points_left -= space['points']
                    # Exit and loop further
                    return
            # Finish the line
            var_sp = self.diecase.decode_matrix('G1')
            wedges = current_wedges
            current_wedges = None
            if self.fill_line:
                while points_left > quad['points']:
                    # Coarse fill with quads
                    queue.append(quad['code'] + ' coarse filling line')
                    points_left -= quad['points']
                while points_left > space['points'] * 2:
                    # Fine fill with fixed spaces
                    queue.append(space['code'] + ' fine filling line')
                    points_left -= space['points']
                if points_left >= var_sp.get_min_points():
                    # Put an adjustable space if possible to keep lines equal
                    if wedges:
                        queue.extend(tsf.single_justification(wedges))
                    var_sp.points = points_left
                    queue.append(str(var_sp))
                    wedges = var_sp.wedge_positions()
            # Always cast as many quads as needed, then put the line out
            queue.extend([quad['code'] + ' quad padding'] * self.quad_padding)
            queue.extend(tsf.double_justification(wedges or (3, 8)))
            points_left = 0

        # Store the code and wedge positions to speed up the process
        space = decode_mat(self.diecase.decode_matrix('G1'))
        quad = decode_mat(self.diecase.decode_matrix('O15'))
        working_mat = None
        current_wedges = None
        queue, points_left = tsf.end_casting(), 0
        # Build the whole galley, line by line
        while working_mat != {}:
            start_line()
            while points_left > 0:
                build_line()
        return queue + self.preheat_mould()


def open_file(filename=''):
    """Opens a text file with text that will be typeset"""
    while True:
        # Choose file
        try:
            filename = filename or UI.enter_input_filename()
        except e.ReturnToMenu:
            return []
        # Open it
        with io.open(filename, 'r') as text_file:
            return text_file.readlines()
