#!/usr/bin/python
from pysphere import VIServer
import argparse
import json
import sys

# required arguments
parser = argparse.ArgumentParser(description='Input arguments')
parser.add_argument('-H', '--host', help='host address', required=True)
parser.add_argument('-u', '--username', help='username', required=True)
parser.add_argument('-p', '--password', help='password', required=True)
parser.add_argument('-c', '--container', help='Example, "Home lab', required=True)
parser.add_argument('-s', '--connectionstring', help='Example, sh user1@', required=True)
parser.add_argument('-f', '--shuttlefile', help='shuttle file', required=True)

# parse arguments
args = parser.parse_args()
host = args.host
username = args.username
password = args.password
container = args.container
connectionstring = args.connectionstring
shuttle_file = args.shuttlefile
shuttle_filename = args.shuttlefile

# create server object
server = VIServer()
# connect to server
server.connect(host, username, password)

# get registered vms
vm_list = server.get_registered_vms()

# list for storing vm dictionaries
vm_obj_list = []

# get attributes for each vm
for vm in vm_list:

    # get our attributes
    vm_attr = server.get_vm_by_path(vm)
    vm_name = vm_attr.get_property('name')
    vm_ipv4 = vm_attr.get_property('ip_address', from_cache=False)

    # create our connection string
    vm_cmd = connectionstring + str(vm_ipv4)

    # save to dict
    vm_obj = { 'cmd': vm_cmd, 'name': vm_name }

    # add to list
    vm_obj_list.append(vm_obj) 

# close connection
server.disconnect()

# if list not empty
if vm_obj_list:

    # open file
    with open(shuttle_file, 'r+') as shuttle_file:

        # load as json data
        json_data = json.load(shuttle_file)

        # iterate through list items in search for our container
        for item in json_data['hosts']:

            # check if our container is in the dict
            if container in item:

                # add our dictionary to it
                item[container] = vm_obj_list

                # rewind file to beginning
                shuttle_file.seek(0)
                # write the new version
                shuttle_file.write(json.dumps(json_data,indent=4,sort_keys=True))
                # truncate file
                shuttle_file.truncate()

                print "Container " + container + " found!" +"File " + shuttle_filename + "  updated!"
                sys.exit(0)

        # container not found, create it
        container_dict = {container: vm_obj_list}
        
        # add to end of the list
        json_data['hosts'].append(container_dict)

        # rewind file to beginning
        shuttle_file.seek(0)
        # write the new version
        shuttle_file.write(json.dumps(json_data,indent=4,sort_keys=True))
        # truncate file
        shuttle_file.truncate()

        print "Container " + container + " not found, created. " + shuttle_filename + " updated!"
else:
    print "No VMS found"
