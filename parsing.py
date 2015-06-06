# -*- coding: utf-8 -*-
"""Parser methods.

This module contains file- and line-parsing methods."""
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']


def read_file(filename):
    """Tries to read a file.

    Returns its contents (if file is readable), or False otherwise.
    """
# Open a file with signals, test if it's readable and return its contents
    try:
        content = []
        with open(filename, 'r') as input_file:
            content_generator = input_file.readlines()
            for line in content_generator:
            # Strip newline characters from lines
                content.append(line.strip('\n'))
            return content
    except IOError:
        return False


def get_metadata(content):
    """get_metadata:

    Catches the parameters included at the beginning of the ribbon.
    These parameters are used for storing diecase ID, set width, title etc.
    and serve mostly informational purposes, but can also be used for
    controlling some aspects of the program (e.g. displaying characters
    being cast).

    The row is parsed if it starts with a parameter, then the assignment
    operator is used for splitting the string in two (parameter and value),
    and a dictionary with parsed parameters is returned.
    """
    parameters = ['diecase', 'title', 'author', 'unit-shift', 'justification']
    symbols = ['=', ':', ' ']
    result = []
    # Work on an unmodified copy and delete lines from the sequence
    for line in content[:]:
        for parameter in parameters:
            if line.startswith(parameter):
                for symbol in symbols:
                    members = line.split(symbol, 1)
                    try:
                        value = members[1].strip()
                        result.append([parameter, value])
                        break
                    except (IndexError, ValueError):
                        pass
                content.remove(line)
    return dict(result)


def comments_parser(input_data):
    """comments_parser(input_data):

    Parses an input string, and returns a list with two elements:
    -the Monotype signals (unprocessed),
    -any comments delimited by symbols from COMMENT_SYMBOLS list.
    We need to work on strings. Convert any lists, integers etc.

    Looks for any comment symbols defined here - **, *, ##, #, // etc.
    splits the line at it and saves the comment to return it later on.
    If it's an inline comment (placed after Monotype code combination),
    this combination will be returned for casting.

    If a line in file contains a comment only, returns no combination.

    In case of column O and row 15 (no signals fed to machine), we still
    need to have the signals listed explicitly in the input sequence.
    The signals_parser will later remove them and convert to O15.

    Example:
    O15 //comment      <-- casts from O+15 matrix, displays comment
                       <-- nothing to do
    //comment          <-- displays comment, no casting
    0005 5 //comment   <-- sets 0005 justification wedge to 5,
                           turns pump off, displays comment.
    """
    try:
        ' '.join(input_data)
    except TypeError:
        input_data = str(input_data)

    # Assume we don't have a comment...
    raw_signals = input_data
    comment = ''
    # ...then look for comment symbols and parse them:
    for symbol in COMMENT_SYMBOLS:
        if symbol in input_data:
        # Split on the first encountered symbol
            [raw_signals, comment] = input_data.split(symbol, 1)
            break
    # Return a list with unprocessed signals and comment
    return [raw_signals.strip(), comment.strip()]


def count_lines_and_characters(contents):
    """Count newlines and characters+spaces in ribbon file.

    This is usually called when pre-processing the file.
    """
    all_lines = 0
    all_chars = 0
    for line in contents:
    # Strip comments
        signals = comments_parser(line)[0]
    # Parse the signals part of the line
        signals = signals_parser(signals)
        if check_character(signals):
            all_chars += 1
        elif check_newline(signals):
            all_lines += 1
    return [all_lines, all_chars]


def count_combinations(contents):
    """Count all combinations in ribbon file.

    This is usually called when pre-processing the file."""
    all_combinations = 0
    for line in contents:
    # Strip comments
        signals = comments_parser(line)[0]
    # If there are signals, increment the combinations counter
        if signals_parser(signals):
            all_combinations += 1
    # Return the number
    return all_combinations


def signals_parser(raw_signals):
    """signals_parser(raw_signals):

    Parses a string with Monotype signals on input.
    Skips all but the "useful" signals: A...O, 1...15, 0005, S, 0075.
    Outputs a list of signals to be processed by send_signals_to_caster
    in Monotype (or MonotypeSimulation) classes.

    Filter out all non-alphanumeric characters and whitespace.
    Convert to uppercase.
    """
    raw_signals = ''.join([x for x in raw_signals if x.isalnum()]).upper()
    # Build a list of justification signals
    justification = [sig for sig in ['0005', '0075'] if sig in raw_signals]
    # Remove these signals from the input string
    for sig in justification:
    # We operate on a string, so cannot remove the item...
        raw_signals = raw_signals.replace(sig, '')
    # Look for any numbers between 16 and 100, remove them
    for number in range(100, 15, -1):
        raw_signals = raw_signals.replace(str(number), '')
    # From remaining numbers, determine row numbers.
    # The highest number will be removed from the raw_signals to avoid
    # erroneously adding its digits as signals.
    rows = []
    for number in range(15, 0, -1):
        if str(number) in raw_signals:
            raw_signals = raw_signals.replace(str(number), '')
            rows.append(str(number))
    # Columns + S justification signal
    columns = [s for s in 'ABCDEFGHIJKLMNOS' if s in raw_signals]
    # Return a list containing all signals
    return columns + rows + justification


def strip_o_and_15(signals):
    """Strip O and 15 signals from input sequence, we don't cast them"""
    return [s for s in signals if s not in ['O', '15']]


def convert_o15(input_signals):
    """Convert O or 15 to O15.

    Combines O and 15 signals to a single O15 signal that can be fed
    to keyboard control routines when punching the ribbon.

    Does not modify the original argument.
    """
    signals = input_signals
    if 'O' in signals or '15' in signals:
        signals.append('O15')
    # Now remove the individual O and 15 signals and return the result
    return strip_o_and_15(signals)


def check_newline(signals):
    """check_newline(signals):

    Checks if the newline (0005, 0075 or NKJ) is present in combination.
    This is called for each new line when parsing the ribbon file
    during casting.
    """
    return (set(['0005', '0075']).issubset(signals)
            or set(['N', 'K', 'J']).issubset(signals))


def check_character(signals):
    """Check if the combination is a character.

    Not-characters (no type is cast) are:
    0005 (pump off) or NJ (pump off, unit-adding),
    0075 (pump on) or NK (pump on, unit-adding),
    0005 0075 (galley trip) or NKJ (galley trip, unit-adding),
    empty sequence.
    """
    return (signals
            and not '0005' in signals
            and not '0075' in signals
            and not set(['N', 'K']).issubset(signals)
            and not set(['N', 'J']).issubset(signals))
