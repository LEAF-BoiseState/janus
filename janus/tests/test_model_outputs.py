import unittest
import pkg_resources
import glob

import numpy as np

from janus import Janus


class TestEqualOutputs(unittest.TestCase):
    """Test that the default outputs do not change."""

    DEFAULT_CONFIG_FILE = pkg_resources.resource_filename('janus', 'tests/data/config.yml')
    COMP_OUTPUTS_DIR = pkg_resources.resource_filename('janus', 'tests/data/comp_outputs')
    DEFAULT_OUTPUTS_DIR = pkg_resources.resource_filename('janus', 'tests/data/outputs')

    def setUp(self):
        pass

    def testOutputs(self):
        """Test that Xanthos produces correct outputs for the default configuration."""

        # get comp outputs
        old_files = self.read_outputs(TestEqualOutputs.COMP_OUTPUTS_DIR)

        # Set up and run janus
        Janus(TestEqualOutputs.DEFAULT_CONFIG_FILE)

        # Test that new outputs equal old outputs.
        new_files = self.read_outputs(TestEqualOutputs.DEFAULT_OUTPUTS_DIR)

        for k in new_files.keys():
            np.testing.assert_array_equal(new_files[k], old_files[k])

    @staticmethod
    def read_outputs(directory):
        """Read all .npy files in output directory."""

        out_file_names = glob.glob('{}*.npy'.format(directory))

        out_files = {}
        for f in out_file_names:
            arr = np.read(f)
            out_files[f] = arr

        return out_files


if __name__ == '__main__':
    unittest.main()
