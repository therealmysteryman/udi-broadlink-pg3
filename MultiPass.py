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
import udi_interface
import broadlink

import sys
import json
# Import the Dictionary that contains all nodes and RFCodes for each. (RFCodes.py)
from RFCodes import RFCodes
#import logging
#import urllib3

"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""
LOGGER = udi_interface.LOGGER
SERVERDATA = json.load(open('server.json'))
VERSION = SERVERDATA['credits'][0]['version']
# IF you want a different log format than the current default
#polyinterface.LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

""" Define My MultiPass! Controller Node Class"""
class Controller(udi_interface.Node):
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
    mybroadlink = None

    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = 'MultiPass Controller'
        
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)

        polyglot.ready()
        polyglot.addNode(self)
    
    def parameterHandler(self, params):
        self.poly.Notices.clear()
        self.discover()
    
    def start(self):
        LOGGER.info('Starting MultiPass NodeServer version {}'.format(VERSION))
        self.setDriver('ST', 1)

    def poll(self, polltype):
        pass
    
    def discover(self, *args, **kwargs):
        self.connectbl()

    def connectbl(self, command=None):
        
        # First Try to Auth and see if connection is already established.
        if self.mybroadlink != None:
            result = self.mybroadlink.auth()
            if result: 
                self.setDriver('GV0', 1)
                LOGGER.info('Previous Connection Authenticated to Broadlink @ 172.16.50.28.')
                return
            else:
                self.setDriver('GV0', 0)
        
        # There will be many objects used in the MultiPass! Node Server this is the first. 
        # Attempt to connect to the known Broadlink RM Pro+
        self.mybroadlink = self.connect_broadlink()

        # Once connected create the nodes defined in RFCodes.py.
        if self.mybroadlink != None: self.populate_broadlink()      

    def connect_broadlink(self):
        """
        Connect to the known Broadlink device and Authenticate.
        device = gendevice(devtype, host, mac, name=name, cloud=cloud)
        devtype = 0x27a9 = (rm, "RM pro+", "Broadlink") <-- from broadlink.__init__.py 
        host = 192.168.2.15 (DHCP reservation), port 80
        mac = 78:0f:77:63:5a:25 Convert to bytes = b'x\x0fwcZ%'
        """
        d = broadlink.gendevice(0x27a9,('172.16.50.28', 80), b'x\x0fwc]\x85', name='Apt')

        try:
            result = d.auth()
            self.setDriver('GV0', 1)
            LOGGER.info('Successful Connection and Authentication to Broadlink @ 172.16.50.28.') 
        except:
            self.setDriver('GV0', 0)
            LOGGER.info('Unable to connect to Broadlink @ 172.16.50.28.') 
        return d if result else None
    
    def populate_broadlink(self):
        """
        Once connected and authenticated to broadlink verify nodes match dictionary.
        """
        for node in RFCodes.keys():
            # Create Mac address from Device Name
            address = node.encode('utf-8').hex()
            if len(address) < 12: 
                address = address.zfill(12) # Pad to 12 Hex Characters
            else:
                address = address[:12] # Trim to 12 Hex Characters
            if not self.poly.getNode(address):
                self.poly.addNode(omniamotor(self.poly, self.address, address, node, self.mybroadlink))        
                self.setDriver('GV1', int(self.getDriver('GV1')) + 1 )

    def stop(self):
        try:
            del self.broadlink
        except:
            pass
        self.setDriver('GV0', 0)
        LOGGER.debug('Broadlink Link stopped. GV0=%s', self.getDriver('GV0'))
        self.setDriver('ST', 0)        
        LOGGER.debug('MultiPass NodeServer stopped. ST=%s', self.getDriver('ST'))

    id = 'controller'

    commands = { 'CONNECTBL': connectbl }

    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 0, 'uom': 56} ] 

class omniamotor(udi_interface.Node):
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
    def __init__(self, controller, primary, address, name, dev):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.

        :param controller: Reference to the Controller class
        :param primary: Controller address
        :param address: This nodes address
        :param name: This nodes name
        :param rfc: The Up / Down / Stop byte codes for RF Packets.
        """
        super(omniamotor, self).__init__(controller, primary, address, name)
        self.ctrl = controller
        self.pri = primary
        self.name = name
        self.dev = dev
        LOGGER.info('OmniaBlind Node Created {}.'.format(self.name))
        
        controller.subscribe(controller.START, self.start, address)

    def shortPoll(self):
        LOGGER.debug('shortPoll')
        """
        if int(self.getDriver('ST')) == 1:
            self.setDriver('ST',0)
        else:
            self.setDriver('ST',1)
        """
        LOGGER.debug('Omnia %s: ST=%s',self.name,self.getDriver('ST'))

    def longPoll(self):
        LOGGER.debug('longPoll')

    def start(self):
        """
        Optional.
        This method is run once the Node is successfully added to the ISY
        and we get a return result from Polyglot. Only happens once.
        """
        '''
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
        '''
        self.setDriver('ST', 1)

    def cmd_up(self,command):
        LOGGER.info('Broadlink RM device {}:{}.'.format("TEST-UP",command))
        #LOGGER.info('RFCode Lookup for {}:{}.'.format(self.name,RFCodes[self.name][1]))
        self.dev.send_data(RFCodes[self.name][0])

    def cmd_down(self,command):
        LOGGER.info('Broadlink RM device {}:{}.'.format("TEST-DOWN",command))
        #LOGGER.info('RFCode Lookup for {}:{}.'.format(self.name,RFCodes[self.name][-1]))
        self.dev.send_data(RFCodes[self.name][1])

    def cmd_stop(self,command):
        LOGGER.info('Broadlink RM device {}:{}.'.format("TEST-STOP", command))
        #LOGGER.info('RFCode Lookup for {}:{}.'.format(self.name,RFCodes[self.name][0]))
        self.dev.send_data(RFCodes[self.name][0])

    '''
    def query(self,command=None):
        """
        Called by ISY to report all drivers for this node. This is done in
        the parent class, so you don't need to override this method unless
        there is a need.
        """
        self.reportDrivers()
    '''

    #Hints See: https://github.com/UniversalDevicesInc/hints
    #hint = [1,2,3,4]
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
                    'BUP': cmd_up,
                    'BDOWN': cmd_down,
                    'BSTOP': cmd_stop
                }
    """
    This is a dictionary of commands. If ISY sends a command to the NodeServer,
    this tells it which method to call. DON calls setOn, etc.
    """


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        polyglot.updateProfile()
        polyglot.setCustomParamsDoc()
        Controller(polyglot, 'controller', 'controller', 'PythonTemplate')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

