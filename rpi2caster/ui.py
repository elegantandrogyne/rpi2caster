# -*- coding: utf-8 -*-
"""User interface for rpi2caster. Text UI is implemented here, additional UIs
can be added later or imported from separate modules"""
import readline
import glob
import string
from collections import OrderedDict
from contextlib import suppress
from functools import partial
import click
from . import datatypes
from .definitions import MenuItem, DEFAULT_ABORT_KEYS
from .misc import MQ
from .parsing import get_key


def option(key=None, value=None, cond=True, lazy='', text='', desc='', seq=50):
    """Menu item factory for UI menus:
        key   : key to press to choose that option (int, str or None),
                    if None, key will be autogenerated,
        value : value to be returned; will be raised if it is an exception
        cond  : condition to check (function or value),
                    an option is available if this evaluates to True,
        lazy  : function or value to be evaluated before each menu display
                    (similar to condition checking);
                    can be included in text or description strings,
        text  : short description of an option,
                    optional (allows "hidden" options too)
        desc  : additional help/description,
        seq   : menu item sequence number for arbitrary sorting.
    """
    return MenuItem(get_key(key), value, cond, lazy, str(text), str(desc), seq)


def assess(condition, force_bool=False):
    """Try to call the condition and evaluate the retval,
    and if it fails, evaluate the conditional itself.

    Allows lazily evaluating functions, useful for dynamic menus.

    force_bool : converts value to boolean using Python rules."""
    try:
        retval = condition()
    except TypeError:
        # check is not callable
        retval = condition
    return bool(retval) if force_bool else retval


def get_sorted_valid_options(options):
    """Iterate over a list of options and return a dictionary of options
    which will be displayed in menu.

    Any option with unmet condition will be omitted.

    Options will be sorted first by option.seq parameter
    (allows arbitrary menu item positioning), then by displayed key,
    and finally, options with unspecified keys will be assigned
    to numbers, then lowercase and uppercase letters.
    """
    def sort_function(opt):
        """Returns a tuple for sorting options"""
        # sort by sequence, then lowercase key name, then text and description
        # missing parameters will be placed at the bottom
        return (opt.seq,
                opt.key.name.lower() if opt.key.name else 'zzz',
                opt.text if opt.text else 'zzz',
                opt.description if opt.description else 'zzz')

    # input data format: (MenuItem1, MenuItem2...)
    # first check if option condition is met
    valid_opts = [option for option in options
                  if assess(option.condition, force_bool=True)]
    # generate the sequence of keys from 1 to 9, lowercase, uppercase
    # reject all keys already assigned to options
    used_keys = [option.key.name for option in valid_opts if option.key.name]
    autokeys = (string.digits[1:] + string.ascii_letters)
    key_generator = (get_key(k) for k in autokeys if k not in used_keys)
    # ...and apply them to options with missing keys
    ret = [option if (option.key.getchar and option.key.name)
           else option._replace(key=next(key_generator))
           for option in sorted(valid_opts, key=sort_function)]
    # finally, sort the options by their keys and return
    sorted_ret = sorted(ret, key=sort_function)
    return sorted_ret


def build_entry(opt, trailing_newline=1):
    """Build a menu entry for an option"""
    # templates for menu entries
    long_entry = '\t{key:<10}:  {text}\n\t\t\t{desc}' + '\n' * trailing_newline
    short_entry = '\t{key:<10}:  {text}' + '\n' * trailing_newline
    # assess a lazy option parameter and insert it in text and dest
    # if {} are provided in string
    key_name = opt.key.name
    lazy_value = assess(opt.lazy)
    text = opt.text.format(lazy_value)
    desc = opt.description.format(lazy_value)
    # use a proper template depending on available data
    if opt.description:
        return long_entry.format(key=key_name, text=text, desc=desc)
    elif opt.text:
        return short_entry.format(key=key_name, text=text)


class Abort(Exception):
    """Exception - abort the current action"""
    def __str__(self):
        return ''


class Finish(Exception):
    """Exception - finish the current exit to menu etc."""
    def __str__(self):
        return ''


class ClickUI(object):
    """Click-based text user interface"""
    __name__ = 'Text UI based on Click'
    verbosity = 0

    def dynamic_menu(self, options,
                     header='', footer='',
                     default_key=None,
                     allow_abort=True,
                     abort_suffix='Press [{keys}] to exit.\n',
                     func_args=None, func_kwargs=None,
                     catch_exceptions=(Abort, click.Abort,
                                       KeyboardInterrupt, EOFError)):
        """dynamic_menu(options=[MenuItem1, MenuItem2...],
                        header='', footer='',
                        default_key=None, allow_abort=True,
                        abort_suffix='Press [{keys}] to exit.\n',
                        catch_exceptions=[exceptions]):

        Builds menu dynamically and executes the callback with no arguments
        or raises an exception each time.
        After callback is executed, builds menu again and displays
        refreshed options.
        Raising an exception here allows to return from menu.

        options : option definitions iterable: (MenuItem1, MenuItem2...),

                  each MenuItem has following attributes/fields:

                  key (int or str) : key to press to choose that option,

                  value : function or exception to be called or raised;
                          function will be called with
                          *func_args and **func_kwargs

                  cond : condition to check (function or value),
                         an option is available if this evaluates to True,

                  lazy : function or value to be evaluated before
                         each menu display (similar to condition checking)
                         can be included in text or description strings,

                  text : short description of an option,
                         optional (allows "hidden" options too),

                  desc : additional help/description,

                  seq : menu item sequence number for arbitrary sorting.

        header, footer : will be displayed above and below menu options list,

        default_key : if defined and valid, wrong keypress will choose
                      an option defined for this key,

        allow_abort : lets Esc, Ctrl-C and Ctrl-Z keystrokes raise Abort,

        abort_suffix : string to display at the end, informing the user
                       about available abort/exit key combinations
                       (displayed only if allow_abort is True),

        func_args=(), func_kwargs={} : positional and keyword arguments
                                       passed to the function call,

        catch_exceptions : an iterable of exceptions this menu is supposed
                           to catch, rather than bubbling up and crashing
                           the program.
        """
        # no args or kwargs? use empty tuple or dict then
        args = func_args or ()
        kwargs = func_kwargs or {}
        # keep displaying the menu until exception is raised
        while True:
            ret = self.menu(options,
                            header, footer,
                            default_key,
                            allow_abort, abort_suffix)
            # if option value is an expression, it'll bubble up here
            with suppress(catch_exceptions):
                ret(*args, **kwargs)

    def menu(self, options,
             header='', footer='',
             default_key=None,
             allow_abort=True, abort_suffix='Press [{keys}] to abort.\n'):
        """menu(options=[MenuOption1, MenuOption2,...]
                header='', footer='', default_key=None,
                allow_abort=True, abort_suffix='Press [{keys}] to abort.\n'):

        A menu displaying keys, options and descriptions (if provided).

        User is asked to press a key and then the function tries to
        raise an exception (if option.value is Exception subclass)
        or return option.value.

        Additional behavior can be specified with default_key,
        allow_abort and abort_suffix options in the function call.

        options : option definitions iterable: (MenuItem1, MenuItem2...),

                  each MenuItem has following attributes/fields:

                  key (int or str) : key to press to choose that option,

                  value : value to be returned;
                          will be raised if it is an exception

                  cond : condition to check (function or value),
                         an option is available if this evaluates to True,

                  lazy : function or value to be evaluated before
                         each menu display (similar to condition checking)
                         can be included in text or description strings,

                  text : short description of an option,
                         optional (allows "hidden" options too)

                  desc : additional help/description,

                  seq : menu item sequence number for arbitrary sorting.

        header : string to be displayed above option entries,

        footer : string to be displayed below option entries,

        default_key : if unknown key is pressed, option for this key
                      will be selected instead (provided that option
                      is defined, valid and condition is met),

        allow_abort : raise Abort if Esc, Ctrl-C or Ctrl-Z is pressed,
                      otherwise stay in the menu. If any of these keycombos
                      is used as a key for a menu option,
                      it will select that option rather than aborting,

        abort_suffix : string to display at the end, informing the user
                       about available abort/exit key combinations
                       displayed only if allow_abort is True.

        After choice is made, try to raise the corresponding option
        or return it.
        """
        def build_menu():
            """Build a list of options and their descriptions"""
            # header_stirng: displayed above, footer_string: displayed below
            # debug_string: displayed only if verbosity != 0
            header_string = '\n{}\n'.format(header) if header else ''
            footer_string = '\n{}\n'.format(footer) if footer else '\n'
            debug_string = (('\nThe program is now in debugging mode. '
                             'Verbosity: {}\n')
                            .format(self.verbosity)
                            if self.verbosity else '')
            # additional info if abort is allowed
            abort_keys = sorted(key.name
                                for key in DEFAULT_ABORT_KEYS
                                if allow_abort and key.getchar not in rets)
            abort_string = (abort_suffix
                            .format(keys=', '.join(abort_keys))
                            if abort_keys else '')
            # add default key combo if it was specified
            if default_retval == 'etaoin shrdlu cmfwyp':
                prompt = 'Your choice? :\n'
            else:
                prompt = 'Your choice? [{}] :\n'.format(def_key.name)
            # generate menu entries for options
            entries = (build_entry(o) for o in valid_options)
            # return the newly constructed menu list
            return [header_string, debug_string, *entries,
                    footer_string, abort_string, prompt]

        # generate a list of valid options
        valid_options = get_sorted_valid_options(options)
        # dictionary of key: return value pairs
        rets = {option.key.getchar: option.value
                for option in valid_options}
        # get default return value for wrong keypress if we have default_key
        # default to some nonsensical string for wrong dict hits
        # this will make it possible to have None as an option
        # why "etaoin shrdlu cmfwyp"? it's related to typography somehow:
        # https://en.wikipedia.org/wiki/Etaoin_shrdlu
        def_key = get_key(default_key)
        default_retval = rets.get(def_key.getchar, 'etaoin shrdlu cmfwyp')
        # check which keys can be used for aborting the menu
        # pressing one of them would raise Abort, if two conditions are met:
        # aborting is enabled (allow_abort=True) and key is not in options
        abort_getchars = [key.getchar
                          for key in DEFAULT_ABORT_KEYS
                          if allow_abort and key.getchar not in rets]
        # display the menu
        # clear the screen, display the header, options, footer
        click.clear()
        click.echo('\n'.join(build_menu()))
        # wait for user input
        while True:
            getchar = click.getchar()
            if getchar in abort_getchars:
                raise Abort
            retval = rets.get(getchar, default_retval)
            if retval != 'etaoin shrdlu cmfwyp':
                return datatypes.try_raising(retval)

    @staticmethod
    def simple_menu(message, options, default_key=None, allow_abort=True):
        """A simple menu where user is asked what to do.
        Wrong choice points back to the menu if default_option is not defined.

        message : string displayed on screen,

        options : a list of MenuItem namedtuples,

        default_key : default key for wrong hits,

        allow_abort : allow aborting with ctrl-C, ctrl-Z and/or Esc.
        """
        # generate a list of valid options
        valid_options = get_sorted_valid_options(options)
        # dictionary of key: return value pairs
        rets = {option.key.getchar: option.value
                for option in valid_options}
        # get default return value for wrong keypress if we have default_key
        # default to some nonsensical string for wrong dict hits
        # this will make it possible to have None as an option
        # why "etaoin shrdlu cmfwyp"? it's related to typography somehow:
        # https://en.wikipedia.org/wiki/Etaoin_shrdlu
        def_key = get_key(default_key)
        default_retval = rets.get(def_key.getchar, 'etaoin shrdlu cmfwyp')
        # check which keys can be used for aborting the menu
        # pressing one of them would raise Abort, if two conditions are met:
        # aborting is enabled (allow_abort=True) and key is not in options
        abort_keys = [key for key in DEFAULT_ABORT_KEYS
                      if allow_abort and key.getchar not in rets]
        abort_getchars = [key.getchar for key in abort_keys]
        # abort prompt
        abort_s = ('Press [{}] to abort.'
                   .format(', '.join(key.name for key in abort_keys))
                   if abort_keys else '')
        # add default key combo if it was specified
        if default_retval == 'etaoin shrdlu cmfwyp':
            prompt = 'Your choice? :'
        else:
            prompt = 'Your choice? [{}] :'.format(def_key.name)
        # display the menu
        entries = (build_entry(o, trailing_newline=0) for o in valid_options)
        click.echo('\n'.join(['', message, '', *entries, '', abort_s, prompt]))
        # Wait for user input
        while True:
            getchar = click.getchar()
            if getchar in abort_getchars:
                raise Abort
            retval = rets.get(getchar, default_retval)
            if retval != 'etaoin shrdlu cmfwyp':
                return datatypes.try_raising(retval)

    @staticmethod
    def clear():
        """Clears the screen by click.clear() which is OS independent."""
        click.clear()

    @staticmethod
    def paged_display(source, sep='\n'):
        """Display paginated text so that the user can scroll through it;
        works with any iterable"""
        text = sep.join(str(x) for x in source)
        click.echo_via_pager(text)

    def display(self, *args, sep=' ', end='\n', file=None, min_verbosity=0):
        """Displays info for the user:
        args : iterable of arguments to display,
        sep : separation string (default: space),
        end : termination string (default: newline),
        file : redirect output to specified file,
        min_verbosity=0 : display only if this verbosity is met or exceeded
                          (useful for debug-only output)"""
        if self.verbosity >= min_verbosity:
            line = sep.join(str(arg) for arg in args)
            click.echo(message='{}{}'.format(line, end), nl=False, file=file)

    @staticmethod
    def display_header(text, symbol='-', trailing_newline=1):
        """Displays a header banner.

        text : header text,
        symbol : line symbol,
        trailing_newline : a number of \n (newline) characters
                           after the header.
        """
        header = '{line}\n{text}\n{line}' + '\n' * trailing_newline
        click.echo(header.format(text=text, line=symbol * len(text)))

    def display_parameters(self, *data):
        """Takes any number of OrderedDict instances (for keeping the
        item order intact) and iterates over them, displaying parameters.

        data : [OrderedDict('': header, par1: val1, par2: val2)...]

        If key evaluates False, display a header."""

        kv_gen = ((k, v) for par_dict in data for (k, v) in par_dict.items())
        for name, value in kv_gen:
            if name:
                # parameter : value
                entry = '{name} : {value}'.format(name=name, value=value)
                click.echo(entry)
            else:
                # parameter evaluating False: value is a header
                self.display_header('{}'.format(value), trailing_newline=0)

    def pause(self, msg1='', msg2='Press any key to continue...',
              min_verbosity=0, allow_abort=False):
        """Waits until user presses a key"""
        if self.verbosity >= min_verbosity:
            abort_key_names = ', '.join(key.name for key in DEFAULT_ABORT_KEYS)
            abort_key_chars = [key.getchar for key in DEFAULT_ABORT_KEYS]
            suffix = msg2
            if allow_abort:
                suffix = '{}\n[{}: abort]'.format(msg2, abort_key_names)
            click.echo('{}\n{}\n'.format(msg1, suffix))
            char = click.getchar()
            if allow_abort and char in abort_key_chars:
                raise Abort

    @staticmethod
    def edit(text=''):
        """Use click to call a text editor for editing a text"""
        try:
            edited_text = click.edit(text,
                                     editor='nano -t',
                                     require_save=False)
        except click.ClickException:
            edited_text = click.edit(text, require_save=False)
        except click.Abort:
            return text
        return edited_text

    @staticmethod
    def enter(prompt='Enter the value',
              default=None, datatype=None,
              minimum=None, maximum=None,
              condition=lambda x: True,
              allow_abort=True, type_prompt=None):
        """Enter data based on function arguments.

        prompt :    set the custom prompt to show to the user,

        default :   If a default value is given, it will be already filled
                    in the input, and returned if nothing is entered.

                    If this is an exception, empty input will raise it.

                    If None, no empty value is allowed and user will be asked
                    until a proper value is given.

        datatype :  allows to override the default datatype.

                    If it is specified, the function will try to convert
                    the user input string to this datatype, and force
                    re-entering the data if validation fails.

                    Defaults to the type of default_value.
                    If default_value is None or an exception,
                    the function returns a string.

                    If default_value is False and no datatype is specified,
                    the function returns False.

        minimum, maximum : validation limit values;
                           applies to numeric value (float, int),
                           or string/container's length.

        condition: any additional condition check the value needs to
                   pass in validation.

        allow_abort : if ctrl-C or ctrl-Z is pressed, the function will
                      raise Abort to be handled elsewhere.

        type_prompt : info for user about what to enter; if None, use default
        """
        def build_requirements_message():
            """Make a prompt about required datatype and limits."""
            retval_type_handler = datatypes.get_handler(retval_datatype)

            # what type should the input be?
            type_name = retval_type_handler.type_name
            type_str = (type_prompt if type_prompt is not None
                        else 'Type: {}'.format(type_name) if type_name else '')

            # what limits are imposed?
            validated_parameter = retval_type_handler.validated_parameter
            vp_name = datatypes.LIMITED_PARAMETERS.get(validated_parameter)
            min_string = 'min: {}'.format(minimum)
            max_string = 'max: {}'.format(maximum)
            limits_string = [min_string if minimum is not None else '',
                             max_string if maximum is not None else '']
            limits_text = ', '.join(x for x in limits_string if x)
            limits_str = '({} {})'.format(vp_name, limits_text)

            # glue it all together
            return ' '.join([type_str, limits_str if limits_text else ''])

        def get_user_input(question):
            """Enter the value and return it"""
            # get a prefill value from type definition
            # prefill takes a default and if it evaluates to False
            def prefill_callback():
                """A insert_text function wrapper"""
                pf_value = datatypes.get_string(default, default_value_type)
                return readline.insert_text(pf_value)

            # get value from user
            readline.set_startup_hook(prefill_callback)
            value = input(question)
            return value

        # desired type:
        # specified datatype -> type of default value -> string
        default_value_type = datatypes.get_type(default)
        retval_datatype = datatype or default_value_type or str
        # configure the conversion/validation function
        conv_validate = partial(datatypes.convert_and_validate,
                                default=default,
                                datatype=retval_datatype,
                                minimum=minimum, maximum=maximum,
                                condition=condition)

        # display the prompt message once
        click.echo('\n{}\n'.format(prompt))
        # tell the user that they can abort
        click.echo('Press Ctrl-C or Ctrl-Z to abort.' if allow_abort else '')
        # tell user about the constraints
        click.echo(build_requirements_message())

        # loop until the function returns correct value
        while True:
            # get the value from wrapped function
            # raise exceptions (if default value was an exception)
            try:
                value = conv_validate(get_user_input('Enter value : '))
                if value is None:
                    continue
                else:
                    return value

            except (TypeError, ValueError) as error:
                # show the message and loop again
                click.secho('Error: {}'.format(error), fg='red')
            except (KeyboardInterrupt, EOFError, click.Abort):
                if allow_abort:
                    raise Abort

            finally:
                click.echo('\n')
                readline.set_startup_hook()

    @staticmethod
    def open_file(default_filename='',
                  mode='r', message='File name?',
                  allow_abort=True):
        """Allows to enter the input filename and checks if it is readable.
        Repeats until proper filename or nothing is given.
        Returns a file object.
        Raises Abort if filename not specified."""
        def readline_prefill():
            """Pre-fill the input prompt for readline."""
            return readline.insert_text(default_filename)

        # Set readline parameters
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(lambda text, state:
                               (glob.glob(text+'*')+[None])[state])
        prompt = ('{} [Ctrl-C, Ctrl-Z or leave blank to abort] : '
                  if allow_abort else '{} : ').format(message)
        # Check file parameters and catch early permission errors
        checks = {'r': {'readable': True, 'exists': True},
                  'w': {'writable': True, 'exists': True},
                  'w+': {'writable': True, 'exists': False}}
        while True:
            try:
                readline.set_startup_hook(readline_prefill)
                click.echo()
                filename = input(prompt)
                click.echo()
                if not filename and allow_abort:
                    raise Abort
                # okay, got a path, check if file can be accessed
                path = click.Path(resolve_path=True, **checks[mode])(filename)
                return click.File(mode)(path)
            except (click.BadParameter, click.FileError) as exc:
                # permission denied and wrong file exception handler
                click.secho(exc.message, fg='red')
            except (KeyboardInterrupt, EOFError):
                # ctrl-C, ctrl-Z exception handler
                if allow_abort:
                    raise Abort
            finally:
                # readline prefill cleanup
                readline.set_startup_hook()

    def import_file(self, default_filename='', allow_abort=True):
        """Allows user to enter the input filename. Returns a file object.
        Returns default filename or raises Abort if filename not specified."""
        return self.open_file(default_filename,
                              mode='r', message='Enter the input filename',
                              allow_abort=allow_abort)

    def export_file(self, default_filename='', allow_abort=True):
        """Allows user to enter the output filename. Returns a file object.
        Returns default filename or raises Abort if filename not specified."""
        return self.open_file(default_filename,
                              mode='w+', message='Enter the output filename',
                              allow_abort=allow_abort)

    @staticmethod
    def confirm(question='Your choice?', default=True,
                abort_answer=None, force_answer=False):
        """Asks a simple question with yes or no answers.
        Returns True for yes and False for no.

        default : default answer if user presses return,
        abort_answer : if True or False, yes / no answer raises Abort;
                       if None, the outcome is returned for both answers.

        force_answer : disallows aborting by ctrl-C, ctrl-Z or Esc
        """
        # key definitions and their meanings
        keys = OrderedDict()
        keys[get_key('y')] = True
        keys[get_key('enter')] = default
        keys[get_key('n')] = False
        keys[get_key('esc')] = False

        # if "yes" or "no" answer leads to Abort, make its keys point to Abort
        keys.update({key: Abort
                     for key, value in keys.items()
                     if value == abort_answer and abort_answer is not None})

        # add aborting key options if abort is available as a third option
        if not force_answer:
            keys.update({key: Abort for key in DEFAULT_ABORT_KEYS})

        # all keys are defined
        # build answer dict from key getchars
        answers = {key.getchar: answer for key, answer in keys.items()}

        # chunks will form the answer info
        chunks = []
        # get the key names for yes, no, abort
        for ans, ans_name in [(True, 'yes'), (False, 'no'), (Abort, 'abort')]:
            names = [key.name for key, answer in keys.items() if answer == ans]
            if not keys:
                continue
            # add a text for this answer
            chunks.append('{1}: {0}'.format(ans_name, ', '.join(names)))

        # glue the chunks together
        key_info = '[{}]'.format(' || '.join(chunks)) if chunks else ''

        # display user prompts
        click.echo(question)
        click.secho(key_info, fg='cyan')

        while True:
            # get the user input
            click.echo('Your choice?')
            getchar = click.getchar()
            answer = answers.get(getchar)

            # loop further if answer lookup failed
            if answer is None:
                continue

            # return answer, or raise it (if it was Abort)
            return datatypes.try_raising(answer)


class UIFactory(object):
    """UI abstraction layer"""
    impl = ClickUI()
    implementations = {'text_ui': ClickUI,
                       'click': ClickUI}

    def __init__(self):
        MQ.subscribe(self, 'UI')
        self.impl = ClickUI()

    def __getattr__(self, name):
        result = getattr(self.impl, name)
        if result is None:
            raise NameError('{implementation} has no function named {function}'
                            .format(implementation=self.impl.__name__,
                                    function=name))
        else:
            return result

    def update(self, source):
        """Update the UI implementation"""
        name = source.get('impl') or source.get('implementation')
        impl = self.implementations.get(name)
        if impl:
            self.impl = impl()

    def get_name(self):
        """Get the underlying user interface implementation's name."""
        return self.impl.__name__

# instantiate it only once
UI = UIFactory()
