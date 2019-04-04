# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_hue`
================================================================================

CircuitPython helper library for the Philips Hue

* Author(s): Brent Rubell

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit ESP32SPI or ESP_ATcontrol library:
    https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI
    https://github.com/adafruit/Adafruit_CircuitPython_ESP_ATcontrol
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Hue.git"

class Bridge:
    """
    HTTP Interface for interacting with a Philips Hue Bridge.
    """
    def __init__(self, bridge_ip, username, wifi_manager):
        """
        Creates an instance of the Hue Interface.
        :param str bridge_ip: Static IP Address of the Hue Bridge.
        :param str username: Optional unique username
        :param wifi_manager wifi_manager: WiFiManager from ESPSPI_WiFiManager/ESPAT_WiFiManager
        """
        wifi_type = str(type(wifi_manager))
        if ('ESPSPI_WiFiManager' in wifi_type or 'ESPAT_WiFiManager' in wifi_type):
            self._wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self._ip = bridge_ip
        self._user = philips_username
        # set up hue web address path
        self._web_address = bridge_ip+'/api'
        # set up hue username address path
        self._username = self._web_address+self._username

    def create_username(self, app_name, app_id):
        """Creates and returns an unique, randomly-generated Hue username.
        :param str app_name: Application Name.
        :param str app_id: Application Identifier.
        """
        data = {"devicetype":"{0}#{1}".format(app_name, app_id)}
        resp = self._post(self._web_address, data)
        # if it retunrs a 101 http response code...
        if resp.status_code = 101:
            raise ValueError('Press the link button and run this method again..')
        for res in resp.json()['success']:
            return res['username']

    # HTTP Requests
    def _post(self, path, data):
        """POST data
        :param str path: Formatted LIFX API URL
        :param json data: JSON data to POST to the LIFX API.
        """
        response = self._wifi.post(
            path,
            json=data,
            headers=self._auth_header
        )
        response = self._parse_resp(response)
        return response

    def _put(self, path, data):
        """PUT data
        :param str path: Formatted LIFX API URL
        :param json data: JSON data to PUT to the LIFX API.
        """
        response = self._wifi.put(
            path,
            json=data,
            headers=self._auth_header
        )
        response = self._parse_resp(response)
        return response

    def _get(self, path, data):
        """GET data
        :param str path: Formatted LIFX API URL
        :param json data: JSON data to GET from the LIFX API.
        """
        response = self._wifi.get(
            path,
            json=data,
            headers=self._auth_header
        )
        return response.json()