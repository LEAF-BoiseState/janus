import sys
import janus


def run_example(f):
    """Sample function to run example.

    :param f:           Full path with file name and extension to a config.yml file

    :return:            Model executes, returns Janus class attributes

    """
    return janus.Janus(config_file=f)


def myscript(config_file, iteration_number):
    xfile_name = "x%d.txt" % iteration_number
    with open(xfile_name, "w") as xf:
        run_example(config_file)


def main(unused_command_line_args):
    for i in range(1000):
        myscript('/Users/kek25/Desktop/Janus_run/profitmax/highswitch/config.yml', i)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
