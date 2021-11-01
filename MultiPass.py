#!/usr/bin/env python3

"""
Import the polyglot interface module.
Also using the broadlink module from: https://github.com/mjg59/python-broadlink
        The MIT License (MIT)
        Copyright (c) 2014 Mike Ryan
        Copyright (c) 2016 Matthew Garrett 
"""
import udi_interface
import broadlink
from switchbot import SwitchBot
import sys
import json
# Import the Dictionary that contains all nodes and RFCodes for each. (RFCodes.py)
from RFCodes import RFCodes

LOGGER = udi_interface.LOGGER
SERVERDATA = json.load(open('server.json'))
VERSION = SERVERDATA['credits'][0]['version']

class Controller(udi_interface.Node):

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
                
        try:
            if 'token' in params:
                self.token = params['token']
            else:
                LOGGER.error('SwitchBot requires \'token\' parameters to be specified in custom configuration.')
                return False
               
            self.discover()
        except Exception as ex:
            LOGGER.error('Error starting MultiPass NodeServer: %s', str(ex))

    def start(self):
        LOGGER.info('Starting MultiPass NodeServer version {}'.format(VERSION))
        self.setDriver('ST', 1)

    def poll(self, polltype):
        pass
    
    def discover(self, *args, **kwargs):
        # broadlink
        self.connectbl()
        # switchbot curtain
        switchbot = SwitchBot(token=self.token)
        sbCurtainId = [ '5F0B798AEF91','5F0B798AEF91','5F0B798AEF91' ]
        
        for node in sbCurtainId :
            if not self.poly.getNode(node):
                self.poly.addNode(sbCurtain(self.poly, self.address, node, node, switchbot.device(id=node)))        

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
 
    def __init__(self, controller, primary, address, name, dev):
    
        super(omniamotor, self).__init__(controller, primary, address, name)
        self.ctrl = controller
        self.pri = primary
        self.name = name
        self.dev = dev
        LOGGER.info('OmniaBlind Node Created {}.'.format(self.name))
        
        controller.subscribe(controller.START, self.start, address)

    def start(self):
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

    #Hints See: https://github.com/UniversalDevicesInc/hints
    #hint = [1,2,3,4]
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
 
    commands = {
                    'BUP': cmd_up,
                    'BDOWN': cmd_down,
                    'BSTOP': cmd_stop
                }

class sbCurtain(udi_interface.Node):
 
    def __init__(self, controller, primary, address, name, dev):
    
        super(sbCurtain, self).__init__(controller, primary, address, name)
        self.dev = dev
        
        controller.subscribe(controller.START, self.start, address)

    def start(self):
        self.setDriver('ST', 1)

    def cmd_open(self,command):
        self.dev.command('open')

    def cmd_close(self,command):
        self.dev.command('close')

        
    #Hints See: https://github.com/UniversalDevicesInc/hints
    #hint = [1,2,3,4]
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
 
    commands = {
                    'BOPEN': cmd_open,
                    'BCLOSE': cmd_close
                }

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

