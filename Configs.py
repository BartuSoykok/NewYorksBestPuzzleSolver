import os.path

from configparser import ConfigParser

config = ConfigParser()

if os.path.isfile('configs.cfg'):
    config.read('configs.cfg')
else:
    config['DEBUG'] = {'print': '0',
                       'print_word_filter': '0',
                       'log': '1'}

    config['SEARCH'] = {'show_parameters': '1',
                        'show_sites': '0'}

    config['TRY'] = {'try_show_words': '0',
                     'try_show_matrices': '0',
                     'try_show_feasible_matrix': '0',
                     'try_solve_time': '1'}

    config['METHOD'] = {'internet': '1',
                        'hint': '1'}

    config['WORD'] = {'banned_words': []}

    with open('configs.cfg', 'w') as configfile:
        config.write(configfile)


def get_setting(section, key):
    return config[section][key]


def set_setting(section, key, value):
    config[section][key] = value


def write():
    with open('configs.cfg', 'w') as configfile:
        config.write(configfile)
