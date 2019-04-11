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
import time
from random import randint

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Hue.git"

class Bridge:
    """
    HTTP Interface for interacting with a Philips Hue Bridge.
    """
    def __init__(self, wifi_manager, bridge_ip=None):
        """
        Creates an instance of the Hue Interface.
        :param str bridge_ip: Optional Static IP Address of the Hue Bridge.
        :param wifi_manager wifi_manager: WiFiManager from ESPSPI_WiFiManager/ESPAT_WiFiManager
        """
        wifi_type = str(type(wifi_manager))
        if ('ESPSPI_WiFiManager' in wifi_type or 'ESPAT_WiFiManager' in wifi_type):
            self._wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        if bridge_ip is None:
            # discover the bridge_ip if not provided
            try:
                response = self._wifi.get('https://discovery.meethue.com')
                json_data = response.json()
                bridge_ip = json_data[0]['internalipaddress']
            except:
                raise TypeError('Ensure the Philips Bridge and CircuitPython device are both on the same WiFi network.')
        self._ip = bridge_ip
        # set up hue web address path
        self.bridge_url = 'http://{}/api'.format(self._ip)

    def register_username(self, username=None):
        """Attempts to register Hue application username for use with your bridge.
        Provides a 30 second delay to press the link button on the bridge.
        Returns username or None.
        :param str username: Unique application username, leave kwarg as None to generate.
        """
        if username is not None:
            self._username_url = self.bridge_url+'/'+ username
        data = {"devicetype":"CircuitPython#pyportal{0}".format(randint(0,100))}
        resp = self._wifi.post(self.bridge_url,json=data)
        connection_attempts = 30
        while username == None and connection_attempts > 0:
            resp = self._wifi.post(self.bridge_url, json=data)
            json = resp.json()[0]
            if json.get('success'):
                username = str(json['success']['username'])
                self._username_url = self.bridge_url+'/'+ username
            connection_attempts-=1
            time.sleep(1)
        return username

    # Lights API
    def show_light_info(self, light_number):
        """Gets the attributes and state of a given light.
        :param int light_number: Light identifier.
        """
        resp = self._get('{0}/lights/{1}'.format(self._username_url, light_number))
        resp_json = resp.json()
        resp.close()
        return resp_json

    def set_light(self, light_number, **kwargs):
        """Allows the user to turn the light on and off, modify the hue and effects.
        You can pass the following as kwargs into this method:
        :param 
        """
        resp = self._put('{0}/lights/{1}/state'.format(self._username_url, light_number), kwargs)
        resp_json = resp.json()
        resp.close()
        return resp_json

    def get_light(self, light_id):
        """Gets the attributes and state of a provided light.
        :param int light_id: Light identifier.
        """
        resp = self._get('{0}/lights/{1}'.format(self._username_url, light_id))
        resp_json = resp.json()
        resp.close()
        return resp_json

    def get_lights(self):
        """Returns all the light resources available for a bridge.
        """
        resp = self._get(self._username_url+'/lights')
        resp_json = resp.json()
        resp.close()
        return resp_json

    # Groups API
    def create_group(self, lights, group_name):
        """Creates a new group containing the lights specified and optional name.
        :param list lights: List of light identifiers.
        :param str group_name: Optional group name.
        """
        data = {'lights':lights,
                'name':group_name,
                'type':lightGroup
        }
        resp = self._post(self._username_url+'/groups', data)
        resp_json = resp.json()
        resp.close()
        return resp_json

    def set_group(self, group_id, is_on, bri, hue, sat):
        """Modifies the state of all lights in a group.
        :param int group_id: Group identifier.
        :param bool is_on: On/Off state of the light.
        :param int bri: Brightness (0 to 254).
        :param int hue: Hue (0 to 65535).
        :param int sat: Saturation of the light (0 to 254).
        """
        data = {'on':is_on,
                'hue':hue,
                'sat':sat}
        resp = self._put(self._username_url+'/groups/'+group_id+'/action', data)
        resp_json = resp.json()
        resp.close()
        return resp_json

    def set_scene(self, group_id, scene):
        """Sets a group scene.
        :param str scene: The scene identifier
        """
        data = {'scene':scene}
        resp = self._put(self._username_url+'/groups/'+group_id+'/action', data)
        resp_json = resp.json()
        resp.close()
        return resp_json

    def get_groups(self):
        """Returns all the light groups available for a bridge.
        """
        resp = self._get(self._username_url+'/groups')
        resp_json = resp.json()
        resp.close()
        return resp_json

    def get_scenes(self):
        """Returns all the light scenes available for a bridge.
        """
        resp = self._get(self._username_url+'/groups')
        resp_json = resp.json()
        resp.close()
        return resp_json

    """
    HTTP Request and Response Helpers for the Hue API
    """
    # TODO: Add response parsing (_parse_resp) method....

    def _parase_response(self, response):
        """Parses JSON response from the Hue API
        """
        if response.json() == "success":
            return response
        # TODO: raise an error

    def _post(self, path, data):
        """POST data
        :param str path: Formatted Hue API URL
        :param json data: JSON data to POST to the Hue API.
        """
        response = self._wifi.post(
            path,
            json=data
        )
        return response

    def _put(self, path, data):
        """PUT data
        :param str path: Formatted Hue API URL
        :param json data: JSON data to PUT to the Hue API.
        """
        response = self._wifi.put(
            path,
            json=data
        )
        return response

    def _get(self, path, data=None):
        """GET data
        :param str path: Formatted Hue API URL
        :param json data: JSON data to GET from the Hue API.
        """
        response = self._wifi.get(
            path,
            json=data
        )
        return response

    def _delete(self, path):
        """DELETE data
        :param str path: Formatted Hue API URL
        """
        response = self.wifi.delete(
            path
        )
        return response