##
# The MIT License (MIT)
#
# Copyright (c) 2018 Stefan Wendler
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
##


import requests as req
import optparse as par
import logging as log

from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
from requests.auth import HTTPDigestAuth



class SmartPlug(object):
    """
    Simple class to access a "EDIMAX Smart Plug Switch SP1101W/SP2101W"
    Original author: Stefan Wendler, 2018
    Modified by Brad Fitzgerald, 2020
    """

    def __init__(self, host, auth):
        """
        Create a new SmartPlug instance identified by the given URL.

        :rtype: object
        :param host: The IP/hostname of the SmartPlug. E.g. '172.16.100.75'
        :param auth: User and password to authenticate with the plug. E.g. ('admin', '1234')
        """
        object.__init__(self)

        self.url = "http://%s:10000/smartplug.cgi" % host
        self.auth = auth
        self.domi = getDOMImplementation()

        # Make a request to detect if Authentication type is Digest
        res = req.head(self.url)
        if res.headers['WWW-Authenticate'][0:6] == 'Digest':
            self.auth = HTTPDigestAuth(auth[0], auth[1])

        self.log = log.getLogger("SmartPlug")

    def _xml_cmd_setget_state(self, cmdId, cmdStr):
        """
        Create XML representation of a state command.

        :type self:     object
        :type cmdId:    str
        :type cmdStr:   str
        :rtype:         str
        :param cmdId:   Use 'get' to request plug state, use 'setup' change plug state.
        :param cmdStr:  Empty string for 'get', 'ON' or 'OFF' for 'setup'
        :return:        XML representation of command
        """

        assert (cmdId == "setup" and cmdStr in ["ON", "OFF"]) or (cmdId == "get" and cmdStr == "")

        doc = self.domi.createDocument(None, "SMARTPLUG", None)
        doc.documentElement.setAttribute("id", "edimax")

        cmd = doc.createElement("CMD")
        cmd.setAttribute("id", cmdId)
        state = doc.createElement("Device.System.Power.State")
        cmd.appendChild(state)
        state.appendChild(doc.createTextNode(cmdStr))

        doc.documentElement.appendChild(cmd)

        xml = doc.toxml()
        self.log.debug("Request: %s" % xml)

        return xml

    def _post_xml(self, xml):
        """
        Post XML command as multipart file to SmartPlug, parse XML response.

        :type self:     object
        :type xml:      str
        :rtype:         str
        :param xml:     XML representation of command (as generated by _xml_cmd)
        :return:        'OK' on success, 'FAILED' otherwise
        """

        files = {'file': xml}

        res = req.post(self.url, auth=self.auth, files=files)

        self.log.debug("Status code: %d" % res.status_code)
        self.log.debug("Response: %s" % res.text)

        if res.status_code == req.codes.ok:
            dom = parseString(res.text)

            try:
                val = dom.getElementsByTagName("CMD")[0].firstChild.nodeValue

                if val is None:
                    val = dom.getElementsByTagName("CMD")[0].getElementsByTagName("Device.System.Power.State")[0].\
                        firstChild.nodeValue

                return val

            except Exception as e:

                print(e.__str__())

        return None

    @property
    def state(self):
        """
        Get the current state of the SmartPlug.

        :type self: object
        :rtype:     str
        :return:    'ON' or 'OFF'
        """

        res = self._post_xml(self._xml_cmd_setget_state("get", ""))

        if res != "ON" and res != "OFF":
            raise Exception("Failed to communicate with SmartPlug")

        return res

    @state.setter
    def state(self, value):
        """
        Set the state of the SmartPlug

        :type self:     object
        :type value:    str
        :param value:   'ON', 'on', 'OFF' or 'off'
        """

        if value == "ON" or value == "on":
            res = self._post_xml(self._xml_cmd_setget_state("setup", "ON"))
        else:
            res = self._post_xml(self._xml_cmd_setget_state("setup", "OFF"))

        if res != "OK":
            raise Exception("Failed to communicate with SmartPlug")
