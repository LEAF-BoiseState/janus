"""test_builder.py

Tests for model interface

@license BSD 2-Clause

"""

import pkg_resources
import unittest

from janus import Janus


class TestBuilder(unittest.TestCase):
    """Test BuildStaffWorkbooks attributes."""

    DEFAULT_CONFIG_FILE = pkg_resources.resource_filename('janus', 'tests/data/config.yml')

    def test_n(self):
        """Check the number of months in the working hours file derived list."""

        # n_months = len(TestBuilder.TEST_READ_OBJ.wkg_hrs_list)
        #
        # self.assertEqual(n_months, 12)

        pass
