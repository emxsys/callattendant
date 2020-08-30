#!/usr/bin/env python
#
# file: config.py
#
# ==============================================================================
# This file is an elided version of the Flask project's config module:
# https://github.com/pallets/flask/blob/master/src/flask/config.py
# ==============================================================================

import errno
import os
import types

from tempfile import gettempdir
from werkzeug.utils import import_string

# This default configuration (used when when a configuration file is not provided)
# will record messages from blocked (denied) callers, and will simply pass permitted
# and screened callers through to the home phone.
#
default_config = {
    "VERSION": '1.0.0',

    "ENV": 'production',
    "DEBUG": False,
    "TESTING": False,

    "DATABASE": "callattendant.db",
    "SCREENING_MODE": ("whitelist", "blacklist"),

    "BLOCK_ENABLED": True,
    "BLOCK_NAME_PATTERNS": {"V[0-9]{15}": "Telemarketer Caller ID", },
    "BLOCK_NUMBER_PATTERNS": {},

    "BLOCKED_ACTIONS": ("greeting", "record_message" ),
    "BLOCKED_RINGS_BEFORE_ANSWER": 0,
    "BLOCKED_GREETING_FILE": "resources/blocked_greeting.wav",

    "SCREENED_ACTIONS": (),
    "SCREENED_GREETING_FILE": "resources/general_greeting.wav",
    "SCREENED_RINGS_BEFORE_ANSWER": 0,

    "PERMITTED_ACTIONS": (),
    "PERMITTED_GREETING_FILE": "resources/general_greeting.wav",
    "PERMITTED_RINGS_BEFORE_ANSWER": 4,

    "VOICE_MAIL_GREETING_FILE": "resources/general_greeting.wav",
    "VOICE_MAIL_GOODBYE_FILE": "resources/goodbye.wav",
    "VOICE_MAIL_INVALID_RESPONSE_FILE": "resources/invalid_response.wav",
    "VOICE_MAIL_LEAVE_MESSAGE_FILE": "resources/please_leave_message.wav",
    "VOICE_MAIL_MENU_FILE": "resources/voice_mail_menu.wav",
    "VOICE_MAIL_MESSAGE_FOLDER": "messages",

    "GPIO_LED_RING_PIN": 14,
    "GPIO_LED_RING_BRIGHTNESS": 100,
    "GPIO_LED_APPROVED_PIN": 15,
    "GPIO_LED_APPROVED_BRIGHTNESS": 100,
    "GPIO_LED_BLOCKED_PIN":17,
    "GPIO_LED_BLOCKED_BRIGHTNESS":100,
    "GPIO_LED_MESSAGE_PIN": 4,
    "GPIO_LED_MESSAGE_BRIGHTNESS": 100,
    "GPIO_LED_MESSAGE_COUNT_PINS": (11, 8, 25, 5, 18, 9, 7, 27),
    "GPIO_LED_MESSAGE_COUNT_KWARGS": {"active_high": False},
}


class ConfigAttribute:
    """
    Makes an attribute forward to the config
    """

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj.config[self.__name__] = value


class Config(dict):
    """
    Config objects works exactly like a dict but provides ways to fill it
    from files or special dictionaries. You can fill the config from a
    config file, e.g., app.config.from_pyfile('yourconfig.cfg')
    Only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.
    """

    def __init__(self, root_path=None, data_path=None, defaults=default_config):
        """
        Constructor.
            :param root_path:
                Path to the top-level package.
                If None, will use the path to this file, assumed to be in the top package
            :param data_path:
                Path to the data folder.
                The application database and message files are stored here.
                If None, will use the tmp folder - used in unit tests
            :param defaults:
                The default configuration values
        """
        dict.__init__(self, defaults or {})
        if root_path:
            self.root_path = root_path
        else:
            # This file must be in the top-level package
            self.root_path = os.path.dirname(os.path.realpath(__file__))
        if data_path:
            self.data_path = data_path
        else:
            # Use the tmp folder
            self.data_path = gettempdir()
        self["ROOT_PATH"] = self.root_path
        self["DATA_PATH"] = self.data_path

    def normalize_paths(self):
        """
        Normalizes the file based setting will absolute paths built from the
        root_path and data_path values passed in the contstructor.
        """
        rootpath = self.root_path
        datapath = self.data_path
        if not datapath:
            return

        self["DB_FILE"] = os.path.join(datapath, self["DATABASE"])

        self["BLOCKED_GREETING_FILE"] = os.path.join(rootpath, self["BLOCKED_GREETING_FILE"])
        self["SCREENED_GREETING_FILE"] = os.path.join(rootpath, self["SCREENED_GREETING_FILE"])
        self["PERMITTED_GREETING_FILE"] = os.path.join(rootpath, self["PERMITTED_GREETING_FILE"])

        self["VOICE_MAIL_GREETING_FILE"] = os.path.join(rootpath, self["VOICE_MAIL_GREETING_FILE"])
        self["VOICE_MAIL_GOODBYE_FILE"] = os.path.join(rootpath, self["VOICE_MAIL_GOODBYE_FILE"])
        self["VOICE_MAIL_LEAVE_MESSAGE_FILE"] = os.path.join(rootpath, self["VOICE_MAIL_LEAVE_MESSAGE_FILE"])
        self["VOICE_MAIL_INVALID_RESPONSE_FILE"] = os.path.join(rootpath, self["VOICE_MAIL_INVALID_RESPONSE_FILE"])
        self["VOICE_MAIL_MENU_FILE"] = os.path.join(rootpath, self["VOICE_MAIL_MENU_FILE"])

        self["VOICE_MAIL_MESSAGE_FOLDER"] = os.path.join(datapath, self["VOICE_MAIL_MESSAGE_FOLDER"])

    def validate(self):
        """
        Validates the settings.
            :return:
                True if the settings are permissible.
        """
        success = True

        if self["ENV"] not in ("production", "development"):
            print("* ENV is incorrect: {}".format(self["ENV"]))
            success = False

        if not isinstance(self["DEBUG"], bool):
            print("* DEBUG should be a bool: {}".format(type(self["DEBUG"])))
            success = False
        if not isinstance(self["TESTING"], bool):
            print("* TESTING should be bool: {}".format(type(self["TESTING"])))
            success = False
        if not isinstance(self["BLOCK_ENABLED"], bool):
            print("* BLOCK_ENABLED should be a bool: {}".format(type(self["BLOCK_ENABLED"])))
            success = False

        for mode in self["SCREENING_MODE"]:
            if mode not in ("whitelist", "blacklist"):
                print("* SCREENING_MODE option is invalid: {}".format(mode))
                success = False

        for mode in self["BLOCKED_ACTIONS"]:
            if mode not in ("greeting", "record_message", "voice_mail"):
                print("* BLOCKED_ACTIONS option is invalid: {}".format(mode))
                success = False
        for mode in self["SCREENED_ACTIONS"]:
            if mode not in ("greeting", "record_message", "voice_mail"):
                print("* SCREENED_ACTIONS option is invalid: {}".format(mode))
                success = False
        for mode in self["PERMITTED_ACTIONS"]:
            if mode not in ("greeting", "record_message", "voice_mail"):
                print("* PERMITTED_ACTIONS option is invalid: {}".format(mode))
                success = False

        if not isinstance(self["BLOCKED_RINGS_BEFORE_ANSWER"], int):
            print("* BLOCKED_RINGS_BEFORE_ANSWER should be an integer: {}".format(type(self["BLOCKED_RINGS_BEFORE_ANSWER"])))
            success = False
        if not isinstance(self["SCREENED_RINGS_BEFORE_ANSWER"], int):
            print("* SCREENED_RINGS_BEFORE_ANSWER should be an integer: {}".format(type(self["SCREENED_RINGS_BEFORE_ANSWER"])))
            success = False
        if not isinstance(self["PERMITTED_RINGS_BEFORE_ANSWER"], int):
            print("* PERMITTED_RINGS_BEFORE_ANSWER should be an integer: {}".format(type(self["PERMITTED_RINGS_BEFORE_ANSWER"])))
            success = False

        filepath = self["BLOCKED_GREETING_FILE"]
        if not os.path.exists(filepath):
            print("* BLOCKED_GREETING_FILE not found: {}".format(filepath))
            success = False
        filepath = self["SCREENED_GREETING_FILE"]
        if not os.path.exists(filepath):
            print("* SCREENED_GREETING_FILE not found: {}".format(filepath))
            success = False
        filepath = self["PERMITTED_GREETING_FILE"]
        if not os.path.exists(filepath):
            print("* PERMITTED_GREETING_FILE not found: {}".format(filepath))
            success = False

        filepath = self["VOICE_MAIL_GREETING_FILE"]
        if not os.path.exists(filepath):
            print("* VOICE_MAIL_GREETING_FILE not found: {}".format(filepath))
            success = False
        filepath = self["VOICE_MAIL_GOODBYE_FILE"]
        if not os.path.exists(filepath):
            print("* VOICE_MAIL_GOODBYE_FILE not found: {}".format(filepath))
            success = False
        filepath = self["VOICE_MAIL_LEAVE_MESSAGE_FILE"]
        if not os.path.exists(filepath):
            print("* VOICE_MAIL_LEAVE_MESSAGE_FILE not found: {}".format(filepath))
            success = False
        filepath = self["VOICE_MAIL_INVALID_RESPONSE_FILE"]
        if not os.path.exists(filepath):
            print("* VOICE_MAIL_INVALID_RESPONSE_FILE not found: {}".format(filepath))
            success = False
        filepath = self["VOICE_MAIL_MENU_FILE"]
        if not os.path.exists(filepath):
            print("* VOICE_MAIL_MENU_FILE not found: {}".format(filepath))
            success = False
        filepath = self["VOICE_MAIL_MESSAGE_FOLDER"]
        if not os.path.exists(filepath):
            print("* VOICE_MAIL_MESSAGE_FOLDER not found: {}".format(filepath))
            success = False

        return success

    def pretty_print(self):
        """
        Pretty print the given configuration dict object.
        """
        print("[Configuration]")
        keys = sorted(self.keys())
        for key in keys:
            print("  {} = {}".format(key, self[key]))

    def from_pyfile(self, filename, silent=False):
        """Updates the values in the config from a Python file.
            :param filename:
                The filename of the config.  This can either be an
                absolute filename or a filename relative to the data path.
            :param silent:
                set to ``True`` if you want silent failure for missing files.
        """
        filename = os.path.join(self.data_path, filename)
        d = types.ModuleType("config")
        d.__file__ = filename
        try:
            with open(filename, mode="rb") as config_file:
                exec(compile(config_file.read(), filename, "exec"), d.__dict__)
        except OSError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return False
            e.strerror = "Unable to load configuration file ({})".format(e.strerror)
            raise
        self.from_object(d)
        return True

    def from_object(self, obj):
        """
        Updates the values from the given object.  An object can be of one
        of the following two types:
        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly
        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.
        Example of module-based configuration::
            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)
        Nothing is done to the object before loading. If the object is a
        class and has ``@property`` attributes, it needs to be
        instantiated before being passed to this method.
        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.
        See :ref:`config-dev-prod` for an example of class-based configuration
        using :meth:`from_object`.
            :param obj:
                an import name or object
        """
        if isinstance(obj, str):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """
        Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage::
            app.config['IMAGE_STORE_TYPE'] = 'fs'
            app.config['IMAGE_STORE_PATH'] = '/var/app/images'
            app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = app.config.get_namespace('IMAGE_STORE_')
        The resulting dictionary `image_store_config` would look like::
            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }
        This is often useful when configuration options map directly to
        keyword arguments in functions or class constructors.

        :param namespace:
            a configuration namespace
        :param lowercase:
            a flag indicating if the keys of the resulting
            dictionary should be lowercase
        :param trim_namespace:
            a flag indicating if the keys of the resulting
            dictionary should not include the namespace
        """
        rv = {}
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self):
        # return f"<{type(self).__name__} {dict.__repr__(self)}>"
        return '<{} {}>'.format(type(self).__name__, dict.__repr__(self))
