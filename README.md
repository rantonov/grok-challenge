# Grok Weather Monitor

This is a simple implementation of a Grok custom monitor.  It reads from a public weather source data about the current
 conditions and sends to Grok the following metric:
 * Temperature in degrees Celsius: ``temp_c``
 * Wind speed in km/h: ``wind_kph``
 * Wind direction: ``wind_degree``
 * Atmospheric pressure in mBar: ``pressure_mb``

## installation
No special installation is necessary.  Make sure to install the required libraries using:
```
pip install -r requirements.txt
```

## Configuration

You need API keys from [Grok](http://grokstream.com/) and [APIXU](https://www.apixu.com/).  
Once you have the keys place them in a file ``config.py`` in the same directory as follows:
```python
GROK_KEY = '<your-grok-key>'
APIXU_KEY = '<your-apixu-key>'
```

## Testing
Run the tests using the following command:
```
python test.py
```

## Running
On a linux box run the script in background using the following command:
```
nohup python mymonitor.py &
```
This will ensure that the script will continue to execute after you log out.