import configparser

configs = configparser.ConfigParser()
configs.read('infra/configs.ini')


def load_configs():
    configs.read('infra/configs.ini')


def get_integer(section, option):
    try:
        return configs.getint(section=section, option=option)
    except KeyError:
        raise KeyError(f"Unable to find attribute {option} in the configurations file")
