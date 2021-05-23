import configparser

configs = configparser.ConfigParser()
configs.read('infra/configs.ini')


def load_configs():
    configs.read('infra/configs.ini')


def load_configs_for_tests():
    configs.read('../src/infra/configs.ini')


def get_integer(section, option):
    try:
        return configs.getint(section=section, option=option)
    except KeyError:
        raise KeyError(f"Unable to find attribute {option} in the configurations file")


def get_float(section, option):
    try:
        return configs.getfloat(section=section, option=option)
    except KeyError:
        raise KeyError(f"Unable to find attribute {option} in the configurations file")


def get_boolean(section, option):
    try:
        return configs.getboolean(section=section, option=option)
    except KeyError:
        raise KeyError(f"Unable to find attribute {option} in the configurations file")


def set_value(section, option, value):
    try:
        return configs.set(section=section, option=option, value=value)
    except KeyError:
        raise KeyError(f"Unable to find attribute {option} in the configurations file")
