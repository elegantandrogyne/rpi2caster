# -*- coding: utf-8 -*-
"""Style manager"""
from .ui import UIFactory

UI = UIFactory()


class Roman:
    """Roman a.k.a. regular, normal, antiqua letters"""
    name = 'roman'
    alternatives = 'regular, antiqua'
    all_names = '%s (%s)' % (name, alternatives)
    short = 'r'
    codes = ['^rr', '^RR', '^00']


class Italic:
    """Italic letters"""
    name = 'italic'
    alternatives = ''
    all_names = name
    short = 'i'
    codes = ['^ii', '^II', '^01']


class Bold:
    """Bold or semi-bold letters"""
    name = 'bold'
    alternatives = ''
    all_names = name
    short = 'b'
    codes = ['^bb', '^BB', '^03']


class SmallCaps:
    """Small capital letters"""
    name = 'small caps'
    alternatives = ''
    all_names = name
    short = 's'
    codes = ['^sc', '^ss', '^SC', '^SS', '^02']


class Inferior:
    """Lower index a.k.a. subscript"""
    name = 'inferior'
    alternatives = 'lower index, subscript'
    all_names = '%s (%s)' % (name, alternatives)
    short = 'l'
    codes = ['^ll', '^LL', '^05']


class Superior:
    """Upper index a.k.a. superscript"""
    name = 'superior'
    alternatives = 'upper index, superscript'
    all_names = '%s (%s)' % (name, alternatives)
    short = 'u'
    codes = ['^uu', '^UU', '^04']


STYLES = [Roman, Bold, Italic, SmallCaps, Inferior, Superior]


class StylesCollection:
    """Styles collection grouping styles and allowing for edit.
    styles: any iterable containing styles to parse,
            valid options: r, b, i, s, l, u
    """

    def __init__(self, styles='a', default=Roman, multiple=True):
        self.style_list = []
        self.default = default
        self.parse(styles, multiple)

    def __iter__(self):
        return (x for x in self.style_list)

    def __str__(self):
        return self.string

    def __repr__(self):
        return '<styles manager: %s>' % self.string

    def __add__(self, other):
        try:
            return StylesCollection(self.string + other.string)
        except AttributeError:
            return StylesCollection(self.string)

    def __radd__(self, other):
        try:
            return StylesCollection(other.string + self.string)
        except AttributeError:
            return StylesCollection(self.string)

    @property
    def string(self):
        """Return the string of all style short names"""
        return ''.join(style.short for style in self.style_list)

    @property
    def names(self):
        """Get the long names of styles"""
        if self.string == 'rbislu':
            return 'all styles'
        else:
            return ', '.join(style.name for style in self.style_list)

    @property
    def all_names(self):
        """Get all names including alternatives"""
        if self.use_all:
            return 'all styles'
        else:
            return ', '.join(style.all_names for style in self.style_list)

    @property
    def use_all(self):
        """Check if the collection has every style"""
        return len(self.style_list) == 6

    def items(self):
        """Get items - so that the object can be iterated like a dict"""
        return ((style.name, style) for style in self.style_list)

    def choose(self, multiple=True):
        """Choose one or more styles"""
        if multiple:
            header = 'Choose one or more text styles.'
            all_styles = ',\na - all styles.\n'
        else:
            header = 'Choose a style.'
            all_styles = '.\n'
        prompt = ('%s Available options:\n'
                  'r - roman, b - bold, i - italic, s - small caps,\n'
                  'l - lower index (inferior), u - upper index (superior)%s'
                  'Your choice?' % (header, all_styles))
        result = UI.enter(prompt, default=self.string)
        self.parse(result, multiple)

    def parse(self, raw_data, multiple=True):
        """Parse the source (any iterable) for valid styles
        and update the styles set"""
        def s_collection():
            """Parse all styles in a StylesCollection object or an iterable
            of styles"""
            try:
                return [x.short for x in raw_data]
            except (TypeError, AttributeError):
                return []

        def style():
            """A single style is supplied."""
            try:
                return raw_data.short
            except AttributeError:
                return []

        def iterable():
            """A string, dict, list, set, tuple, generator etc. is supplied"""
            try:
                if 'a' in raw_data:
                    return 'rbislu'
                else:
                    return [x for x in 'rbislu' if x in raw_data]
            except TypeError:
                return []

        source = s_collection() or style() or iterable() or self.default.short

        if not multiple:
            # Use the first item only
            source = source[:1]
        # Got the styles string, now make the set
        self.style_list = [s for s in STYLES if s.short in source]
