# udi-broadlink-poly

This Poly provides an interface between Broadlink and Polyglot v2 server. This a Fork from https://github.com/ch491/udi-broadlink-poly
This nodeserver is not intented has his it would need to be modified to your need.       

Installation
You can install manually :

1. cd ~/.polyglot/nodeservers
2. git clone https://github.com/therealmysteryman/udi-broadlink-poly.git
3. run ./install.sh to install the required dependency.
4. You would need to modify the connection in MultiPass.py

        host = 192.168.2.15 (DHCP reservation), port 80
        mac = 78:0f:77:63:5a:25 Convert to bytes = b'x\x0fwcZ%'
        """
        d = broadlink.gendevice(0x27a9,('172.16.50.28', 80), b'x\x0fwc]\x85', name='Apt', cloud=False)
        
5. Modify the RFCodes.py to include your Binary code to be send by Broadlink


