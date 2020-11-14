import sys
import janus


def run_example(f):
    """Sample function to run example.

    :param f:           Full path with file name and extension to a config.yml file

    :return:            Model executes, returns Janus class attributes

    """
    return janus.Janus(config_file=f)


def main(unused_command_line_args):
    for i in range(3):
        run_example('/Users/kek25/Desktop/Janus_run/profitmax/highswitch/config.yml')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
