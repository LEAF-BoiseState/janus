import janus


def run_example(f):
    """Sample function to run example.

    :param f:           Full path with file name and extension to a config.yml file

    :return:            Model executes, returns Janus class attributes

    """
    return janus.Janus(config_file=f)


if __name__ == '__main__':

    config_file = "<full path with file name and extension to your config.yml file>"

    janus_run = run_example(config_file)
