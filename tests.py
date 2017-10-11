import unittest
import time
import random
from mymonitor import WeatherMonitor, GROK_KEY, GROK_ENDPOINT
import requests

TEST_METRIC = 'test_metric'


class TestWeatherMonitor(unittest.TestCase):
    def setUp(self):
        self.mon = WeatherMonitor()

    def test_external(self):
        data = self.mon.get_weather()
        self.assertGreater(len(data), 0, "Weather service appears to be down or is experiencing connectivity issues.")
        try:
            r = requests.get(GROK_ENDPOINT, auth=(GROK_KEY, ''), verify=False)
            self.assertLess(r.status_code, 300, 'Grok service returns status code %d.' % r.status_code)
        except requests.ConnectionError as ex:
            self.fail('Connectivity issues with Grok service: %s.' % ex.message)

    def test_single_post(self):
        self._delete_test_metric()
        metrics = requests.get(GROK_ENDPOINT, auth=(GROK_KEY, ''), verify=False).json()
        time.sleep(1)
        # test that te metric was deleted
        for metric in metrics:
            self.assertFalse(metric["name"] != TEST_METRIC)

        self.mon.post_single_metric(TEST_METRIC, int(time.time()), random.random())

        # get the custom metrics again after a slight delay
        time.sleep(1)
        metrics = requests.get(GROK_ENDPOINT, auth=(GROK_KEY, ''), verify=False).json()
                                
        # make sure that the metric was created
        found = False
        for metric in metrics:
            if metric['name'] == TEST_METRIC:
                found = True
                break
        self.assertTrue(found, 'Did not find the created test metric after posting.')

    def test_count(self):
        count = 10
        self._delete_test_metric()
        for i in range(count):
            self.mon.post_single_metric(TEST_METRIC, int(time.time()), random.random())
            time.sleep(1)
        metrics = requests.get(GROK_ENDPOINT, auth=(GROK_KEY, ''), verify=False).json()
        for metric in metrics:
            if metric['name'] == TEST_METRIC:
                self.assertEqual(metric['last_rowid'], count,
                                 "Row count mismatch. Expected %d, got %d" % (count, metric['last_rowid']))
                break

    def _delete_test_metric(self):
        try:
            requests.delete(GROK_ENDPOINT + TEST_METRIC, auth=(GROK_KEY, ''), verify=False)
        except Exception:
            pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherMonitor)
    unittest.TextTestRunner(verbosity=2).run(suite)
