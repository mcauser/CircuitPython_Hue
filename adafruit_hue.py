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
from random import randint

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
        self._username = philips_username
        # set up hue web address path
        self._web_addr = bridge_ip+'/api'
        # set up hue username address path
        self._username_addr = self._web_addr+self._username

    def register_application(self, username):
        """Registers Hue application for use with your bridge.
        :param str username: Unique alphanumeric username. Can not contain a space.
        """
        #data = {"devicetype":"{0}#{1}".format(username, client_id)}
        data = {"username":username,
                "devicetype":"CircuitPython Hue Client"
        }
        resp = self._post(self._web_addr, data)
        # if it returns a 101 http response code...
        if resp.status_code == 101:
            raise ValueError('Press the link button on your bridge and run your code again...')
        elif resp.status_code == 7:
            raise ValueError('Username can not contain a space.')
        for res in resp.json()['success']:
            return res['username']

    def deregister_application(self, username):
        """Removes a username form the whitelist of registered applications.
        :param str username: Username to remove.
        """
        resp = self.DELETE(self._username_addr/+self._username)

    def get_lights(self):
        """Returns all the light resources available for a bridge.
        """
        resp = self.get(self._username_addr+'/lights')
        return resp

    def get_groups(self):
        """Returns all the light groups available for a bridge.
        """
        resp = self.get(self._username_addr+'/groups')
        return resp

    def get_scenes(self):
        """Returns all the light scenes available for a bridge.
        """
        resp = self.get(self._username_addr+'/groups')
        return resp

    """
    HTTP Request and Response Helpers
    """
    # TODO: Add response parsing (_parse_resp) method....
    def _post(self, path, data):
        """POST data
        :param str path: Formatted Hue API URL
        :param json data: JSON data to POST to the Hue API.
        """
        response = self._wifi.post(
            path,
            json=data,
            headers=self._auth_header
        )
        return response

    def _put(self, path, data):
        """PUT data
        :param str path: Formatted Hue API URL
        :param json data: JSON data to PUT to the Hue API.
        """
        response = self._wifi.put(
            path,
            json=data,
            headers=self._auth_header
        )
        return response

    def _get(self, path, data):
        """GET data
        :param str path: Formatted Hue API URL
        :param json data: JSON data to GET from the Hue API.
        """
        response = self._wifi.get(
            path,
            json=data,
            headers=self._auth_header
        )
        return response

    def _delete(self, path):
        """DELETE data
        :param str path: Formatted Hue API URL
        """
        response = self.wifi.delete(
            path,
            headers=self._create_headers(self._auth_header))
        return response