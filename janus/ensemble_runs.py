import janus


def run_example(f):
    """Sample function to run example.

    :param f:           Full path with file name and extension to a config.yml file

    :return:            Model executes, returns Janus class attributes

    """
    return janus.Janus(config_file=f)


for i in range(1):
    janus_run = run_example('/Users/kendrakaiser/Desktop/Janus_run/erdosrenyi/config.yml')
    print("run", i)
