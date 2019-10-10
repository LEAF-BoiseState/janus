import unittest
import pkg_resources

import numpy as np

from janus import Janus


class TestEqualOutputs(unittest.TestCase):
    """Test that the default outputs do not change."""

    DEFAULT_CONFIG_FILE = pkg_resources.resource_filename('janus', 'tests/data/config.yml')
    COMP_OUTPUTS_DIR = pkg_resources.resource_filename('janus', 'tests/data/comp_outputs')
    DEFAULT_OUTPUTS_DIR = pkg_resources.resource_filename('janus', 'tests/data/outputs')

    COMP_OUTPUT_DOMAIN = pkg_resources.resource_filename('janus', 'tests/data/comp_outputs/domain_3000m_20yr.npy')
    COMP_OUTPUT_LANDCOVER = pkg_resources.resource_filename('janus', 'tests/data/comp_outputs/landcover_3000m_20yr.npy')
    COMP_OUTPUT_PROFITS = pkg_resources.resource_filename('janus', 'tests/data/comp_outputs/profits_3000m_20yr.npy')

    def test_outputs(self):
        """Test that Xanthos produces correct outputs for the default configuration."""
        # TODO: verify that this test will pass with current data

        # load comp data
        # comp_domain_arr = np.load(TestEqualOutputs.COMP_OUTPUT_DOMAIN)
        comp_landcover_arr = np.load(TestEqualOutputs.COMP_OUTPUT_LANDCOVER)
        comp_profits_arr = np.load(TestEqualOutputs.COMP_OUTPUT_PROFITS)

        # set up and run janus
        res = Janus(config_file=TestEqualOutputs.DEFAULT_CONFIG_FILE, save_result=False, plot_results=False)

        # test that new outputs equal old outputs
        # np.testing.assert_array_equal(res.agent_domain, comp_domain_arr)
        np.testing.assert_array_equal(res.crop_id_all, comp_landcover_arr)
        np.testing.assert_array_equal(res.profits_actual, comp_profits_arr)


if __name__ == '__main__':
    unittest.main()
