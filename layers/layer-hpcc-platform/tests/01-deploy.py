#!/usr/bin/python3

import amulet
import requests
import unittest


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.d = amulet.Deployment(series='bionic')

        service_name = self.d.charm_name
        print(service_name)

        self.d.add(service_name)
        self.d.expose(service_name)

        self.d.setup(timeout=900)
        self.d.sentry.wait(timeout=900)

        self.unit = self.d.sentry[service_name][0]

    def test_service(self):
        # test we can access over http
        page = requests.get(
            'http://{}:8010'.format(self.unit.info['public-address']))
        self.assertEqual(page.status_code, 200)
        # Now you can use self.d.sentry[SERVICE][UNIT] to address each of the units and perform
        # more in-depth ssteps. Each self.d.sentry[SERVICE][UNIT] has the following methods:
        # - .info - An array of the information of that unit from Juju
        # - .file(PATH) - Get the details of a file on that unit
        # - .file_contents(PATH) - Get plain text output of PATH file from that unit
        # - .directory(PATH) - Get details of directory
        # - .directory_contents(PATH) - List files and folders in PATH on that unit
        # - .relation(relation, service:rel) - Get relation data from return service


if __name__ == '__main__':
    unittest.main()
