import threading
import time
import logging
import requests
from config import APIXU_KEY, GROK_KEY

GROK_ENDPOINT = 'https://lyra-cuw3.grokstream.com/_metrics/custom/'
APIXU_ENDPOINT = 'https://api.apixu.com/v1/current.json'


class WeatherMonitor:

    # defaults to be overwritten by params if necessary
    LOCATION_Q = 'Irvine, CA'
    TIME_INTERVAL = 2  # seconds

    # these are the names of the metrics to be uploaded
    metrics = ['temp_c', 'wind_kph', 'wind_degree', 'pressure_mb']

    def __init__(self, location=LOCATION_Q, interval=TIME_INTERVAL):
        self.next_call = time.time()
        self.location = location
        self.interval = interval
        logging.basicConfig(filename='weather_metric.log', format='%(asctime)s %(message)s',
                            level=logging.ERROR)

    def start(self):
        self.post_metric()

    def post_metric(self):
        # get the metrics
        tstamp = time.time()
        try:
            data = self.get_weather()
            # if successful - the dict is not empty
            if len(data):
                # post each of the metrics to Grok and log any errors
                for key, value in data.iteritems():
                    try:
                        self.post_single_metric(key, tstamp, value)
                    except requests.ConnectionError as ex:
                        logging.error('Connectivity issue encountered when posting %s to Grok: %s.' % (key, ex.message))
        except requests.ConnectionError as ex:
            logging.error('Network issue encountered when accessing the weather service: %s.' % ex.message)

        # After all is posted: schedule the next call
        self.next_call = self.next_call + self.interval
        threading.Timer(self.next_call - tstamp, self.post_metric).start()

    def post_single_metric(self, metric_name, timestamp, value):
        payload = {'timestamp': int(timestamp), 'value': value}
        r = requests.post(GROK_ENDPOINT + metric_name, json=payload, auth=(GROK_KEY, ''), verify=False)
        if r.status_code > 299:
            logging.error('Posting %s metric on Grok failed with code %d. Payload = %s.' % (
                metric_name, r.status_code, str(payload)))
        return r.status_code

    def get_weather(self):
        """
        :return: a number of weather related metrics in a dictionary

        """
        params = {'key': APIXU_KEY, 'q': self.location}
        r = requests.get(APIXU_ENDPOINT, params=params)
        if r.status_code > 299:
            logging.error('Weather Service responded with code %d.' % r.status_code)
            return {}
        else:
            return dict((key, r.json()['current'][key]) for key in WeatherMonitor.metrics)


if __name__ == "__main__":
    monitor = WeatherMonitor()
    monitor.start()
