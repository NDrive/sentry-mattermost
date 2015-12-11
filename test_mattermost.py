from __future__ import absolute_import
from sentry.testutils import TestCase


class MyExtensionTest(TestCase):
    def test_simple(self):
        assert 1 != 2
