"""Test that all scenarios render successfully."""

import unittest

import ddt
import lxml.html
from django.core.urlresolvers import reverse
from django.test.client import Client
from xblock.test.tools import assert_equals

from workbench import scenarios
from workbench.runtime_util import reset_global_state


@ddt.ddt
class ScenarioTest(unittest.TestCase):
    """Test the scenario support."""
    def setUp(self):
        super(ScenarioTest, self).setUp()
        reset_global_state()

    def test_all_scenarios(self):
        """Load the home page, examine the scenarios displayed."""
        client = Client()
        response = client.get("/")
        assert response.status_code == 200
        html = lxml.html.fromstring(response.content)
        a_tags = list(html.xpath('//a'))

        # Load the loaded_scenarios from the classes.
        loaded_scenarios = scenarios.get_scenarios().values()

        # We should have an <a> tag for each scenario.
        assert_equals(len(a_tags), len(loaded_scenarios))

        # We should have at least one scenario with a vertical tag, since we use
        # empty verticals as our canary in the coal mine that something has gone
        # horribly wrong with loading the loaded_scenarios.
        assert any("<vertical_demo>" in scen.xml for scen in loaded_scenarios)

        # Since we are claiming in try_scenario that no vertical is empty, let's
        # eliminate the possibility that a scenario has an actual empty vertical.
        assert all("<vertical_demo></vertical_demo>" not in scen.xml for scen in loaded_scenarios)
        assert all("<vertical_demo/>" not in scen.xml for scen in loaded_scenarios)

    @ddt.data(*scenarios.get_scenarios().keys())
    def test_scenario(self, scenario_id):
        """A very shallow test, just to see if the scenario loads all its blocks.

        We don't know enough about each scenario to know what each should do.
        So we load the scenario to see that the workbench could successfully
        serve it.

        """
        url = reverse('workbench_show_scenario', kwargs={'scenario_id': scenario_id})
        client = Client()
        response = client.get(url, follow=True)
        assert response.status_code == 200, scenario_id

        # Be sure we got the whole scenario.  Again, we can't know what to expect
        # here, but at the very least, if there are verticals, they should not be
        # empty.  That would be a sign that some data wasn't loaded properly while
        # rendering the scenario.
        html = lxml.html.fromstring(response.content)
        for vertical_tag in html.xpath('//div[@class="vertical"]'):
            # No vertical tag should be empty.
            assert list(vertical_tag), "Empty <vertical> shouldn't happen!"
