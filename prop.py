#/usr/bin/python 

import xml.etree.ElementTree as ET 
import os,pdb

# grab the ovf information into xml for parsing 
# the information reference source is on https://github.com/veksh/ovfconf
os.system("vmware-rpctool 'info-get guestinfo.ovfEnv' > ovfxml")

tree=ET.parse('ovfxml')
oe='{http://schemas.dmtf.org/ovf/environment/1}'

# var is defined for ovf propert, this funtion call is to retrive the prop info we configure in ovf
# the way reference source is on http://stackoverflow.com/questions/27761626/how-to-deal-with-key-value-style-tags-in-xml-with-python

def pop(val):
    for child in tree.iter(oe+'Property'):
        if child.attrib[oe+"key"] == val :
            val=child.attrib[oe+'value']
            return val
 
dns=pop('dns')
ip=pop('ip')
netmask=pop('netmask')
gateway=pop('gateway')
hostname=pop('hostname')
print(dns,ip,netmask,gateway)

# perpare the content for network file replacement
interface="""auto lo
iface lo inet loopback

auto ens160
iface ens160 inet static 
address %s
netmask %s
gateway %s
dns-nameserver %s""" %(ip,netmask,gateway,dns)

# create the file upon the content and overwite to existing network configuration 
os.system("touch template")
with open("template","w") as NI:
    NI.write(interface)
NI.close()

os.system("cat template > /etc/network/interfaces")
os.system("rm ./template")
os.system("rm ./ovfxml")

# reset network interface 
os.system("ip address flush ens160")
os.system('systemctl restart networking.service')

# modify vm hostname 
#with open("/etc/hostname") as localname:
#    myname=localname.read()
myname=os.uname()[1]

if hostname==myname:
    print("the name has been modified")
else:
    os.system("echo %s > /etc/hostname" %hostname)
    os.system("hostname %s" %hostname)
    
os.system('python /root/ovfenv/remove.py')
