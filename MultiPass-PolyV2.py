#!/usr/bin/env python3

"""
This is a NodeServer for Polyglot v2 written in Python3
It will contain many different custom objects that will connect random technology.
-----------------------------------------------------------------------------------
Import the polyglot interface module.
Also using the broadlink module from: https://github.com/mjg59/python-broadlink
        The MIT License (MIT)
        Copyright (c) 2014 Mike Ryan
        Copyright (c) 2016 Matthew Garrett 
"""
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import broadlink

import sys
import json
import logging
import urllib3

"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""
LOGGER = polyinterface.LOGGER
# IF you want a different log format than the current default
#polyinterface.LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

"""
Open the server.json file and collect the data within it. 
"""
with open('server.json') as data:
    SERVERDATA = json.load(data)
    data.close()
try:
    VERSION = SERVERDATA['credits'][0]['version']
    LOGGER.info('Broadlink Poly Version {} found.'.format(VERSION))
except (KeyError, ValueError):
    LOGGER.info('Broadlink Poly Version not found in server.json.')
    VERSION = '0.0.0'

"""Define Nodes and RF Codes - Later to be added to the server.json file."""
staticNodes = {
    "Office": [
         b'\xb2\x00\xcc\x01\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x18\x0c\r\x18\x18\x0c\x0c\x18\r\x18\x0c\x18\x18\r\x0c\x18\x0c\x19\x0c\x18\x18\x00\x01+\xa44\r\x18\x0c\x18\x0c\x19\x0c\x18\x0c\x19\x0b\x19\x0c\x18\x18\x0c\x18\r\x0c\x18\r\x18\x18\x0c\x0c\x19\x0c\x18\x18\r\x17\r\x0c\x19\x0c\x18\x0c\x18\x0c\x18\x19\x0c\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x0c\x18\x19\x0c\x0c\x18\x18\r\x0c\x18\r\x17\r\x18\x18\x0c\r\x18\x0c\x18\x0c\x19\x18\x00\x01+\xa44\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\x18\r\x18\x0c\r\x18\x0c\x18\x19\x0c\x0c\x18\x0c\x19\x18\x0c\x18\x0c\r\x18\x0c\x18\r\x18\x0c\x18\x18\x0c\r\x18\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x18\x0c\r\x17\x19\x0c\r\x17\r\x18\r\x17\x18\r\x0c\x18\r\x18\x0c\x18\x18\x00\x02\x13\xa45\x0c\x18\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\r\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\x18\r\x0c\x18\r\x17\x19\x0c\x18\x0c\r\x18\x0c\x18\r\x18\x0c\x18\x18\r\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x18\x0c\r\x18\x18\x0c\r\x17\r\x18\x0c\x18\x18\r\x0c\x19\x0c\x18\x0c\x18\x18\x00\x01+\xa44\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x18\r\x18\x0c\x0c\x19\x0c\x18\x18\x0c\x0c\x18\r\x18\x18\x0c\x19\x0c\x0c\x18\r\x18\x0c\x18\x0c\x19\x18\x0c\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\x19\x0c\x0c\x18\x18\r\x0c\x18\x0c\x18\r\x18\x18\x0c\r\x18\x0c\x18\x0c\x19\x17\x00\x01+\xa45\x0c\x18\x0c\x19\x0c\x18\x0c\x18\r\x17\r\x18\x0c\x19\x18\x0c\x18\x0c\x0c\x19\x0c\x18\x18\r\x0c\x18\x0c\x19\x17\r\x18\x0c\r\x18\x0c\x18\r\x18\x0c\x18\x18\x0c\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x0c\x18\x0c\x18\x19\x0c\x0c\x18\x19\x0c\x0c\x18\r\x18\x0c\x18\x18\r\x0c\x18\x0c\x19\x0b\x19\x18\x00\x05\xdc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', b'\xb2\x01\x84\x03\x18\x0c\x0c\x18\x0c\x18\x19\x0b\x19\x0c\x0c\x18\x0c\x18\r\x17\r\x17\x19\x0c\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x17\r\x18\x0c\x18\x18\x0c\x18\r\x0c\x18\x0c\x18\x18\x0c\x18\x0c\r\x17\r\x17\x19\x0c\x18\x00\x01*\xa44\x0c\x18\r\x17\r\x17\r\x17\r\x18\r\x17\r\x17\x18\x0c\x19\x0c\x0c\x18\r\x18\x17\r\x0c\x18\x0c\x18\x18\x0c\x18\r\x0c\x18\x0c\x18\x0c\x18\x0c\x18\x19\x0b\r\x18\x0c\x18\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x18\x18\x0c\x18\x0c\r\x17\r\x18\x18\x0b\x19\x0c\x0c\x18\x0c\x18\x19\x0b\x19\x00\x02\x08\xa43\r\x17\r\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\x18\x0c\r\x17\r\x18\x18\x0c\x18\x0c\x0c\x18\r\x17\r\x18\x0c\x18\x18\x0c\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\x0c\x18\x18\x0c\x18\r\x0c\x18\x0c\x18\x18\x0c\x19\x0c\x0c\x17\r\x18\x18\x0c\x18\x00\x01+\xa34\r\x17\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x17\x19\x0c\x18\x0c\r\x17\r\x18\x18\x0c\x0c\x18\r\x17\x19\x0b\x19\x0c\x0c\x18\x0c\x18\r\x17\r\x18\x18\x0c\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x17\r\x17\r\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\x18\x0c\x18\x0c\r\x17\r\x17\x19\x0c\x18\x00\x01*\xa44\x0c\x18\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\x18\x0c\x19\x0c\x0c\x18\x0c\x18\x18\r\x0c\x18\x0c\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\x0c\x18\x0c\x18\x18\x0c\r\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\x18\x0c\x18\x0c\r\x17\r\x17\x19\x0c\x18\x0c\x0c\x18\r\x17\x19\x0b\x19\x00\x02\x08\xa44\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\x18\r\x18\x0c\x0c\x18\x0c\x18\x18\x0c\r\x18\x0c\x18\x18\x0c\x18\x0c\r\x17\r\x18\r\x17\r\x17\x18\x0c\r\x17\r\x18\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\x0c\x18\r\x18\x18\x0c\x18\x0c\x0c\x18\r\x17\x18\x0c\x19\x0c\x0c\x18\r\x17\x19\x0b\x19\x00\x01*\xa44\x0c\x18\x0c\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\x18\x0c\r\x17\r\x18\x18\x0c\x18\x0c\r\x17\r\x18\x0c\x18\x0c\x18\x18\x0c\r\x17\r\x17\r\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\r\x17\x18\x0c\x18\r\x0c\x18\x0c\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\x18\x0c\x19\x00\x01*\xa34\r\x17\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x17\x19\x0c\x18\x0c\r\x17\r\x17\x19\x0c\x0c\x18\x0c\x18\x18\r\x17\r\x0c\x18\x0c\x18\x0c\x18\r\x18\x18\x0c\x0c\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\r\x17\r\x17\r\x18\x18\x0c\x18\x0c\r\x17\r\x18\x18\x0c\x18\x0c\x0c\x18\r\x17\x19\x0c\x18\x00\x02\x08\xa44\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x0c\x18\x0c\x18\x19\x0c\x18\x0c\x0c\x18\r\x17\x18\x0c\r\x18\x0c\x18\x18\x0c\x18\x0c\r\x17\r\x18\x0c\x18\r\x17\x18\r\x0c\x18\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x17\r\x18\x18\x0c\x18\x0c\x0c\x18\r\x17\x19\x0c\x18\x0c\x0c\x18\r\x17\x19\x0b\x19\x00\x01*\xa43\r\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x0c\x18\x18\x0c\x19\x0c\x0c\x18\x0c\x18\x18\x0c\r\x17\r\x17\x19\x0c\x18\x0c\r\x17\r\x18\x0c\x18\x0c\x18\x18\x0c\r\x17\r\x18\x0c\x18\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x17\x18\r\x18\x0c\x0c\x18\r\x17\x19\x0c\x18\x0c\x0c\x18\x0c\x18\x18\x0c\x19\x00\x01*\xa44\x0c\x18\x0c\x18\x0c\x18\r\x17\r\x17\r\x18\x0c\x18\x18\x0c\x19\x0b\r\x18\x0c\x18\x18\x0c\r\x17\x0c\x18\x19\x0c\x18\x0c\x0c\x18\r\x18\x0c\x18\x0c\x18\x18\x0c\r\x17\r\x18\x0c\x18\x0c\x18\r\x17\r\x17\r\x17\r\x18\x0c\x18\x18\x0c\x18\r\x0c\x18\x0c\x18\x19\x0b\x19\x0c\x0c\x18\x0c\x18\x18\x0c\x18\x00\x05\xdc\x00\x00\x00\x00',
         b'\xb2\x00\xf6\x01\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x18\x0c\x19\x0c\r\x17\r\x17\x19\x0c\r\x18\x0c\x18\x18\x0c\x18\r\x0c\x18\r\x18\x0c\x18\r\x17\x19\x0c\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\r\x17\r\x18\x0c\x19\x18\x0c\x0c\x18\x18\r\x0c\x18\r\x17\x19\x0c\x18\x0c\x18\r\x18\x0c\r\x18\x0c\x00\x016\xa54\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x18\x0c\x18\r\x0c\x18\x0c\x18\x18\r\x0c\x18\r\x18\x18\x0c\x18\r\x0c\x18\x0c\x18\r\x18\x0c\x18\x18\x0c\r\x18\r\x17\r\x18\x0c\x18\r\x17\r\x18\r\x18\x0c\x18\x18\r\x0c\x18\x18\x0c\r\x18\x0c\x18\x18\x0c\x19\x0c\x18\x0c\x19\x0c\r\x17\r\x00\x016\xa44\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x19\x0c\x18\x0c\r\x18\x0c\x18\x18\x0c\r\x18\x0c\x18\x18\x0c\x19\x0c\r\x17\r\x18\x0c\x18\r\x18\x18\x0c\r\x17\r\x18\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x18\x0c\x0c\x18\x19\x0c\x0c\x18\r\x18\x18\x0c\x19\x0c\x18\x0c\x18\x0c\r\x18\x0c\x00\x016\xa54\x0c\x18\x0c\x19\x0c\x18\r\x17\r\x18\x0c\x18\r\x17\x19\x0c\x18\r\x0c\x18\r\x17\x19\x0c\x0c\x18\x0c\x19\x18\x0c\x19\x0c\x0c\x18\r\x17\r\x18\x0c\x18\x18\r\x0c\x18\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x19\x0c\x18\x18\x0c\r\x18\x18\x0c\r\x18\x0c\x18\x18\x0c\x19\x0c\x18\x0c\x19\x0c\r\x17\r\x00\x016\xa53\r\x18\x0c\x18\x0c\x19\x0c\x18\x0c\x18\r\x18\x0c\x18\x18\r\x18\x0c\r\x18\x0c\x18\x18\x0c\r\x18\x0c\x18\x19\x0b\x19\x0c\r\x17\r\x18\r\x17\r\x17\x19\x0c\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\x19\x0c\x0c\x18\x19\x0c\x0c\x18\x0c\x18\x18\r\x18\x0c\x19\x0c\x18\x0c\r\x18\x0c\x00\x016\xa53\r\x18\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\r\x17\x18\r\x18\x0c\r\x18\r\x17\x19\x0c\x0c\x18\r\x18\x18\x0c\x18\x0c\r\x18\x0c\x18\r\x17\r\x18\x19\x0c\x0c\x18\r\x17\r\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x18\x0c\r\x18\x18\x0c\r\x18\x0c\x18\x18\x0c\x19\x0c\x18\x0c\x19\x0c\r\x17\r\x00\x05\xdc\x00\x00',
         b'\xb2\x00\xa4\x00\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\x0c\x19\x18\x0c\x18\r\x0c\x18\x0c\x18\x19\x0c\x0c\x18\x0c\x18\x19\x0c\x18\x0c\r\x18\x0c\x18\r\x18\x0c\x18\x18\r\x0c\x18\x0c\x18\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\x0c\x19\x18\x0c\x0c\x18\x19\x0c\x0c\x18\x18\x0c\r\x18\x18\x0c\r\x18\x18\x0c\x0c\x19\x18\x00\x01+\xa34\r\x18\x0c\x18\r\x18\x0c\x18\x0c\x18\r\x18\x0c\x18\x18\r\x18\x0c\x0c\x19\x0c\x18\x18\x0c\r\x18\x0c\x18\x18\r\x18\x0c\x0c\x18\r\x18\x0c\x18\r\x18\x18\x0c\r\x17\r\x18\x0c\x19\x0b\x19\x0c\x18\x0c\x18\r\x18\x0c\x18\x18\r\x0c\x18\x18\x0c\r\x18\x18\x0c\r\x17\x18\r\x0c\x19\x17\r\x0c\x18\x18\x00\x05\xdc\x00\x00\x00\x00'
         ]
    }

""" Define My MultiPass! Controller Node Class"""
class Controller(polyinterface.Controller):
    """
    The Controller Class is the primary node from an ISY perspective. It is a Superclass
    of polyinterface.Node so all methods from polyinterface.Node are available to this
    class as well.

    Class Variables:
    self.nodes: Dictionary of nodes. Includes the Controller node. Keys are the node addresses
    self.name: String name of the node
    self.address: String Address of Node, must be less than 14 characters (ISY limitation)
    self.polyConfig: Full JSON config dictionary received from Polyglot for the controller Node
    self.added: Boolean Confirmed added to ISY as primary node
    self.config: Dictionary, this node's Config

    Class Methods (not including the Node methods):
    start(): Once the NodeServer config is received from Polyglot this method is automatically called.
    addNode(polyinterface.Node, update = False): Adds Node to self.nodes and polyglot/ISY. This is called
        for you on the controller itself. Update = True overwrites the existing Node data.
    updateNode(polyinterface.Node): Overwrites the existing node data here and on Polyglot.
    delNode(address): Deletes a Node from the self.nodes/polyglot and ISY. Address is the Node's Address
    longPoll(): Runs every longPoll seconds (set initially in the server.json or default 10 seconds)
    shortPoll(): Runs every shortPoll seconds (set initially in the server.json or default 30 seconds)
    query(): Queries and reports ALL drivers for ALL nodes to the ISY.
    getDriver('ST'): gets the current value from Polyglot for driver 'ST' returns a STRING, cast as needed
    runForever(): Easy way to run forever without maxing your CPU or doing some silly 'time.sleep' nonsense
                  this joins the underlying queue query thread and just waits for it to terminate
                  which never happens.
    """
    
    def __init__(self, polyglot):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.
        """
        super().__init__(polyglot)
        self.name = 'Broadlink RM Controller'
        self.hb = 0
        # This can be used to call your function everytime the config changes
        # But currently it is called many times, so not using.
        # self.poly.onConfig(self.process_config)

    def start(self):
        """
        Optional.
        Polyglot v2 Interface startup done. Here is where you start your integration.
        This will run, once the NodeServer connects to Polyglot and gets it's config.
        In this example I am calling a connect method. While this is optional,
        this is where you should start. No need to Super this method, the parent
        version does nothing.
        """
        LOGGER.info('Starting MultiPass! Polyglot v2 NodeServer version {}'.format(serverdata['version']))
        
        # Show values on startup if desired.
        LOGGER.debug('MultiPass!.ST=%s', self.getDriver('ST'))
        self.setDriver('ST', 1)
        self.heartbeat(0)
        #self.check_params()
        self.set_debug_level(self.getDriver('GV1'))
        #self.poly.add_custom_config_docs("<b>This is some custom config docs data</b>")
        self.connect()
        LOGGER.info('Broadlink Start complete')

    def shortPoll(self):
        """
        Optional.
        This runs every 10 seconds. You would probably update your nodes either here
        or longPoll. No need to Super this method the parent version does nothing.
        The timer can be overriden in the server.json.
        """
        LOGGER.debug('shortPoll')
        for node in self.nodes:
            if node != self.address:
                self.nodes[node].shortPoll()

    def longPoll(self):
        """
        Optional.
        This runs every 30 seconds. You would probably update your nodes either here
        or shortPoll. No need to Super this method the parent version does nothing.
        The timer can be overriden in the server.json.
        """
        LOGGER.debug('longPoll')
        self.heartbeat()

    def query(self, command=None):
        """
        Optional.
        By default a query to the control node reports the FULL driver set for ALL
        nodes back to ISY. If you override this method you will need to Super or
        issue a reportDrivers() to each node manually.
        """
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def heartbeat(self,init=False):
        LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    #def connect(self, *args, **kwargs):
    def connect(self):
        
        # There will be many objects used in the MultiPass! Node Server this is the first. 
        # Attempt to connect to the known Broadlink RM Pro+
        self.broadlink = self.connect_broadlink()

        #self.addNode(TemplateNode(self, self.address, 'templateaddr', 'Template Node Name'))
        ''''
        if self.FirstRun == True:
            self.addNode(Omnia(self, self.address, "No-Address", "Office"))
            self.FirstRun = False
        '''
        # Now to define the Nodes and their unique RF Packet Codes.

    def connect_broadlink():
        """
        Connect to the known Broadlink device and Authenticate.
        device = gendevice(devtype, host, mac, name=name, cloud=cloud)
        devtype = 0x27a9 = (rm, "RM pro+", "Broadlink") <-- from broadlink.__init__.py 
        host = 192.168.2.15 (DHCP reservation), port 80
        mac = 78:0f:77:63:5a:25 Convert to bytes = b'x\x0fwcZ%'
        """
        d = broadlink.gendevice(0x27a9,('192.168.2.16', 80), b'x\x0fwcZ%', name='Apt', cloud=False)

        try:
            result = d.auth()
            LOGGER.info('Successful Connection and Authentication to Broadlink @ 192.168.2.16.') 
        except (KeyError, ValueError):
            LOGGER.info('Unable to connect to Broadlink @ 192.168.2.16.') 
        return d if result else None

    def delete(self):
        """
        Example
        This is sent by Polyglot upon deletion of the NodeServer. If the process is
        co-resident and controlled by Polyglot, it will be terminiated within 5 seconds
        of receiving this message.
        """
        LOGGER.info('Oh God I\'m being deleted. Broadlink-CH.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config))
        LOGGER.info("process_config: Exit")

    def set_module_logs(self, level):
        logging.getLogger('urllib3').setLevel(level)

    def set_debug_level(self,level):
        LOGGER.debug('set_debug_level: {}'.format(level))
        if level is None:
            level = 30
        level = int(level)
        if level == 0:
            level = 30
        LOGGER.info('set_debug_level: Set GV1 to {}'.format(level))
        self.setDriver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        if level <= 10:
            LOGGER.setLevel(logging.DEBUG)
        elif level == 20:
            LOGGER.setLevel(logging.INFO)
        elif level == 30:
            LOGGER.setLevel(logging.WARNING)
        elif level == 40:
            LOGGER.setLevel(logging.ERROR)
        elif level == 50:
            LOGGER.setLevel(logging.CRITICAL)
        else:
            LOGGER.debug("set_debug_level: Unknown level {}".format(level))
        # this is the best way to control logging for modules, so you can
        # still see warnings and errors
        #if level < 10:
        #    self.set_module_logs(logging.DEBUG)
        #else:
        #    # Just warnigns for the modules unless in module debug mode
        #    self.set_module_logs(logging.WARNING)
        # Or you can do this and you will never see mention of module logging
        '''
        if level < 10:
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            # This is the polyinterface default
            LOG_HANDLER.set_basic_config(True,logging.WARNING)
        '''

    def check_params(self):
        return
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        self.removeNoticesAll()
        self.addNotice('Hey there, my IP is {}'.format(self.poly.network_interface['addr']),'hello')
        self.addNotice('Hello Friends! (without key)')
        default_user = "YourUserName"
        default_password = "YourPassword"
        if 'user' in self.polyConfig['customParams']:
            self.user = self.polyConfig['customParams']['user']
        else:
            self.user = default_user
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(self.user))
            st = False

        if 'password' in self.polyConfig['customParams']:
            self.password = self.polyConfig['customParams']['password']
        else:
            self.password = default_password
            LOGGER.error('check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))
            st = False
        # Make sure they are in the params
        self.addCustomParam({'password': self.password, 'user': self.user, 'some_example': '{ "type": "TheType", "host": "host_or_IP", "port": "port_number" }'})

        # Add a notice if they need to change the user/password from the default.
        if self.user == default_user or self.password == default_password:
            # This doesn't pass a key to test the old way.
            self.addNotice('Please set proper user and password in configuration page, and restart this nodeserver')
        # This one passes a key to test the new way.
        self.addNotice('This is a test','test')
    
    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        LOGGER.debug("cmd_set_debug_mode: {}".format(val))
        self.set_debug_level(val)
    
    """
    Optional.
    Since the controller is the parent node in ISY, it will actual show up as a node.
    So it needs to know the drivers and what id it will use. The drivers are
    the defaults in the parent Class, so you don't need them unless you want to add to
    them. The ST and GV1 variables are for reporting status through Polyglot to ISY,
    DO NOT remove them. UOM 2 is boolean.
    The id must match the nodeDef id="controller"
    In the nodedefs.xml
    """
    id = 'controller'

    commands = { 'DISCOVER': connect, 'SET_DM': cmd_set_debug_mode }

    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56},
        {'driver': 'GV1', 'value': 30, 'uom': 25} ] # Debug (Log) Mode, default=30=Warning



class Omnia(polyinterface.Node):
    """
    This is the class that all the Nodes will be represented by. You will add this to
    Polyglot/ISY with the controller.addNode method.

    Class Variables:
    self.primary: String address of the Controller node.
    self.parent: Easy access to the Controller Class from the node itself.
    self.address: String address of this Node 14 character limit. (ISY limitation)
    self.added: Boolean Confirmed added to ISY

    Class Methods:
    start(): This method is called once polyglot confirms the node is added to ISY.
    setDriver('ST', 1, report = True, force = False):
        This sets the driver 'ST' to 1. If report is False we do not report it to
        Polyglot/ISY. If force is True, we send a report even if the value hasn't changed.
    reportDrivers(): Forces a full update of all drivers to Polyglot/ISY.
    query(): Called when ISY sends a query request to Polyglot for this specific node
    """
    def __init__(self, controller, primary, address, name):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.

        :param controller: Reference to the Controller class
        :param primary: Controller address
        :param address: This nodes address
        :param name: This nodes name
        """
        super().__init__(controller, primary, address, name)
        self.ctrl = controller
        self.pri = primary
        self.name = name
        LOGGER.info('Broadlink Node Created {}.'.format(self.name))

    def shortPoll(self):
        LOGGER.debug('shortPoll')
        if int(self.getDriver('ST')) == 1:
            self.setDriver('ST',0)
        else:
            self.setDriver('ST',1)
        LOGGER.debug('%s: get ST=%s',self.lpfx,self.getDriver('ST'))

    def longPoll(self):
        LOGGER.debug('longPoll')

    def start(self):
        """
        Optional.
        This method is run once the Node is successfully added to the ISY
        and we get a return result from Polyglot. Only happens once.
        """
        LOGGER.debug('%s: get ST=%s', self.lpfx, self.getDriver('ST'))
        self.setDriver('ST', 1)
        LOGGER.debug('%s: get ST=%s', self.lpfx, self.getDriver('ST'))
        self.setDriver('ST', 0)
        LOGGER.debug('%s: get ST=%s', self.lpfx, self.getDriver('ST'))
        self.setDriver('ST', 1)
        LOGGER.debug('%s: get ST=%s', self.lpfx, self.getDriver('ST'))
        self.setDriver('ST', 0)
        LOGGER.debug('%s: get ST=%s', self.lpfx, self.getDriver('ST'))
        self.http = urllib3.PoolManager()

    def cmd_up(self,command):
        LOGGER.info('Broadlink RM device {}:{}.'.format("TEST-UP",command))

    def cmd_down(self,command):
        LOGGER.info('Broadlink RM device {}:{}.'.format("TEST-DOWN",command))

    def cmd_stop(self,command):
        LOGGER.info('Broadlink RM device {}:{}.'.format("TEST-STOP", command))

    def query(self,command=None):
        """
        Called by ISY to report all drivers for this node. This is done in
        the parent class, so you don't need to override this method unless
        there is a need.
        """
        self.reportDrivers()

    #Hints See: https://github.com/UniversalDevicesInc/hints
    hint = [1,2,3,4]
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    """
    Optional.
    This is an array of dictionary items containing the variable names(drivers)
    values and uoms(units of measure) from ISY. This is how ISY knows what kind
    of variable to display. Check the UOM's in the WSDK for a complete list.
    UOM 2 is boolean so the ISY will display 'True/False'
    """
    id = 'omniamotor'
    """
    id of the node from the nodedefs.xml that is in the profile.zip. This tells
    the ISY what fields and commands this node has.
    """
    commands = {
                    'UP': cmd_up,
                    'DOWN': cmd_down,
                    'STOP': cmd_stop
                }
    """
    This is a dictionary of commands. If ISY sends a command to the NodeServer,
    this tells it which method to call. DON calls setOn, etc.
    """


if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('PythonTemplate')
        """
        Instantiates the Interface to Polyglot.
        The name doesn't really matter unless you are starting it from the
        command line then you need a line Template=N
        where N is the slot number.
        """
        polyglot.start()
        """
        Starts MQTT and connects to Polyglot.
        """
        control = Controller(polyglot)
        """
        Creates the Controller Node and passes in the Interface
        """
        control.runForever()
        """
        Sits around and does nothing forever, keeping your program running.
        """
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
    sys.exit(0)
