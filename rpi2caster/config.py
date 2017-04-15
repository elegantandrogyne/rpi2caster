# -*- coding: utf-8 -*-
"""Global settings for rpi2caster. Acts as a single point of truth (SPOT)
for every application-wide setting."""
import configparser as cp
import json
from click import get_app_dir
from . import datatypes as dt, definitions as d

# Paths: user's local settings and data directory, user's config file...
USER_DATA_DIR = get_app_dir('rpi2caster', force_posix=True, roaming=True)
USER_CFG_PATH = '{}/rpi2caster.conf'.format(USER_DATA_DIR)

# database URL (sqlite, mysql, postgres etc.)
USER_DB_URL = 'sqlite:///{}/rpi2caster.db'.format(USER_DATA_DIR)

# all applicable system-wide config file locations
GLOBAL_CFG_PATHS = ['/etc/rpi2caster/rpi2caster.conf', '/etc/rpi2caster.conf']

# Default values for options
DEFAULTS = dict(default_measure='25cc',
                measurement_unit='cc',
                choose_backend=False,
                database_url=USER_DB_URL,
                sensor='simulation',
                output='simulation',
                emergency_stop_gpio=22,
                sensor_gpio=17,
                bounce_time=25,
                signals_arrangement=d.SIGNALS,
                mcp0=0x20, mcp1=0x21,
                pin_base=65,
                i2c_bus=1)

# Option aliases - alternate names for options in files
ALIASES = {'signals_arrangement': ('signals', 'arrangement'),
           'choose_backend': ('backend_select', 'choose_mode', 'mode_select'),
           'default_measure': ('line_length', 'default_line_length'),
           'measurement_unit': ('typesetting_unit', 'unit', 'pica'),
           'sensor_gpio': ('photocell_gpio', 'light_switch_gpio'),
           'emergency_stop_gpio': ('stop_gpio', 'stop_button_gpio'),
           'database_url': ('db_url', 'database_uri', 'db_uri')}


class Config(cp.ConfigParser):
    """Configuration manager based on ConfigParser"""
    # use custom names for on and off states
    BOOLEAN_STATES = {name: True for name in dt.TRUE_ALIASES}
    BOOLEAN_STATES.update({name: False for name in dt.FALSE_ALIASES})

    def __init__(self, config_path=''):
        super().__init__()
        self.read([*GLOBAL_CFG_PATHS, USER_CFG_PATH, config_path])

    def reset(self):
        """Resets the config to default values"""
        # Populate data with defaults; convert all names to lowercase
        self.read_dict(DEFAULTS, 'defaults')

    def save(self, file=None):
        """Save the configuration to file"""
        if not file:
            return
        self.write(file)

    def get_option(self, option_name='', default=None,
                   minimum=None, maximum=None):
        """Get an option value."""

        # get the first match for this option name or its aliases
        matching_options = matching_options_generator(self, option_name)
        value = next(matching_options)

        # take a default value argument into account, if it was specified
        default_value = default or DEFAULTS.get(option_name)

        # coerce the string into the default value datatype, validate limits
        return dt.convert_and_validate(value, default_value,
                                       minimum=minimum, maximum=maximum)

    def set_option(self, option_name, value, section_name=None):
        """Set an option to a given value"""
        section, option = section_name.lower(), option_name.lower()
        if section:
            self.set(section, option, value)
        else:
            self.set('default', option, value)

    def to_json(self, include_defaults=False):
        """Dump the config to json"""
        dump = {section: {option: value}
                for section, sect_options in self.items()
                for option, value in sect_options.items()}
        if include_defaults:
            dump['default'] = {option: dt.convert(value, str)
                               for option, value in DEFAULTS.items()}
        return json.dumps(dump, indent=4)

    def from_json(self, json_dump):
        """Load the config dump from json"""
        dump = json.loads(json_dump)
        self.read_dict(dump)

    @property
    def interface(self):
        """Return the interface configuration"""
        data = dict(sensor=self.get_option('sensor'),
                    output=self.get_option('output'),
                    choose_backend=self.get_option('choose_backend'),
                    sensor_gpio=self.get_option('sensor_gpio'),
                    emergency_stop_gpio=self.get_option('emergency_stop_gpio'),
                    signals_arrangement=self.get_option('signals_arrangement'),
                    mcp0=self.get_option('mcp0'), mcp1=self.get_option('mcp1'),
                    pin_base=self.get_option('pin_base'),
                    i2c_bus=self.get_option('i2c_bus'),
                    bounce_time=self.get_option('bounce_time'))
        return d.Interface(**data)

    @property
    def preferences(self):
        """Return the typesetting preferences configuration"""
        data = dict(default_measure='25cc',
                    measurement_unit='cc')
        return d.Preferences(**data)


def matching_options_generator(parser, option_name):
    """Look for an option in ConfigParser object, taking aliases into account,
    if the option is not found in any section, get a default value."""
    for section in parser.sections():
        # get all possible names for the desired option
        option_names = [option_name, *ALIASES.get(option_name, ())]
        for name in option_names:
            try:
                candidate = parser[section][name]
                yield candidate
            except (cp.NoSectionError, cp.NoOptionError, KeyError):
                continue
    # option was defined nowhere => use a default one
    # or raise NoOptionError if it fails
    yield DEFAULTS.get(option_name)
    raise GeneratorExit


# make a single instance for importing
CFG = Config()