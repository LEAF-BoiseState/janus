"""
Install archived supplement.

@author   Chris R. Vernon
@email:   chris.vernon@pnnl.gov

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files

"""

import argparse
import pkg_resources

from distutils.dir_util import copy_tree


class InstallSupplement:
    """Transfer tests data to a directory of the users choosing to execute model.

    :param example_data_directory:              Full path to the directory you wish to install
                                                the example data to.  Must be write-enabled
                                                for the user.

    """

    DATA_DIR = pkg_resources.resource_filename('janus', 'tests/data')

    def __init__(self, example_data_directory):

        # full path to the root directory where the example dir will be stored
        self.example_data_directory = example_data_directory

        copy_tree(InstallSupplement.DATA_DIR, self.example_data_directory)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    help_msg = 'Full path to the directory you wish to install the example data to.'
    parser.add_argument('example_data_directory', type=str, help=help_msg)
    args = parser.parse_args()

    zen = InstallSupplement(args.example_data_directory)
    del zen
