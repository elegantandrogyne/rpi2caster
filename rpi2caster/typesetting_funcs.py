# -*- coding: utf-8 -*-
"""
typesetting_funcs:

Contains functions used for calculating line length, justification,
setting wedge positions, breaking the line etc.
"""


def single_justification(wedge_positions=(3, 8),
                         comment='Single justification'):
    """Add 0075 + pos_0075, then 0005 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return pump_start(pos_0075, comment) + pump_stop(pos_0005)


def double_justification(wedge_positions=(3, 8),
                         comment='Double justification'):
    """Add 0075 + pos_0075, then 0005-0075 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return pump_start(pos_0075, comment) + galley_trip(pos_0005)


def galley_trip(pos_0005=8, comment='Line to the galley'):
    """Put the line to the galley"""
    attach = comment and (' // ' + comment) or ''
    return ['NKJS 0075 0005 %s%s' % (pos_0005, attach)]


def pump_start(pos_0075=3, comment='Starting the pump'):
    """Start the pump and set 0075 wedge"""
    attach = comment and (' // ' + comment) or ''
    return ['NKS 0075 %s%s' % (pos_0075, attach)]


def pump_stop(pos_0005=8, comment='Stopping the pump'):
    """Stop the pump"""
    attach = comment and (' // ' + comment) or ''
    return ['NJS 0005 %s%s' % (pos_0005, attach)]


def end_casting():
    """Alias for ending the casting job"""
    return (pump_stop(comment='End casting') +
            galley_trip(comment='Last line out'))


def high_or_low_space():
    """Chooses high or low space"""
    spaces = {True: '_', False: ' '}
    high_or_low = UI.confirm('High space?', default=False)
    return spaces[high_or_low]
