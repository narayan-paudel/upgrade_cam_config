#!/usr/bin/env python

import argparse
import json
import glob

import re

parser = argparse.ArgumentParser()
parser.add_argument('-config_path', '--path', dest='path',default="/Users/epaudel/research_ua/icecube/pole_calibration/hole-freeze-operations/UpgradeCamera/OperationsConfigs/String87/ExposureTimeScans/Quad6plus", help='path to run config')
parser.add_argument('-quick_stat_path', '--quickpath', dest='quickpath',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/quickStat.log", help='path to quick status log')
parser.add_argument('-string_map', '--stringmap', dest='stringmap',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/string_87_quad14_20.json", help='path to string map')
parser.add_argument('-dry_quads', '--dquads', dest='dry_quads',nargs='+',type=int,default=[14,20], help='list of dry quads')
parser.add_argument('-output_path', '--out', dest='out',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/dry_configs/", help='path to string map')

args = parser.parse_args()

# print(f"reading configs from path {args.path}")

config_lists = glob.glob(args.path+"/*.json")
quick_stat_log = args.quickpath
string_map = args.stringmap


# print(f"config_lists {len(config_lists)} {config_lists}")

dry_quads = args.dry_quads
print(f"dry quads {dry_quads}")

class device():
    # def __init__(self, string, quad, wp, hostname, port, control_port, wp_address):
    def __init__(self,xdom, quad, wp, port, control_port, wp_address):
        # self.string = string
        self.xdom = xdom
        self.quad = quad
        self.wp = wp
        self.port = port
        self.control_port = control_port
        self.wp_address = wp_address
        self.domnet_data_port = self.port - self.wp_address
    def set_hostname(self,hostname):
        self.hostname = hostname

def card_wp_to_quad_wp(cwa):
    wp_address = int(cwa[-1])
    wp = int(cwa[-2])
    card = int(cwa[:-2])
    if wp in [0,1]:
        quad = card * 2 + 1
    elif wp in [2,3]:
        quad = card * 2 + 2
    else:
        print(f"Invalid wp {wp} in cwa {cwa}")
    quad_wp = wp%2
    quad_wp_address = wp_address
    return quad, quad_wp, quad_wp_address


def parse_quick_stat(file_path,hostname):
    device_list = []
    with open(file_path, 'r') as f:
        f.readline()  # skip header line
        data = f.readlines()
        for line in data:
            values = line.split(" ")
            values = [istr.strip() for istr in values if istr!="" and istr!="\n"]
            if len(values) >= 8:
                cwa = values[0]
                quad1, wp, wp_address = card_wp_to_quad_wp(cwa)
                quad = int(re.sub('[a-zA-Z]', '',values[1]))
                if quad1 != quad:
                    print(f"conflicting quad calculations {quad1} and {quad}")               
                # hostname = values[2]
                port = int(values[2])
                control_port = int(values[3])
                xdom = values[5]
                # print(f"quad {quad} wp {wp} wp_address {wp_address} port {port} ctrl_port {control_port}")
                idevice = device(xdom,quad, wp, port, control_port, wp_address)
                idevice.set_hostname(hostname)
                # print(f"Parsed device: {idevice}")
                device_list.append(idevice)
            # print(f"line {values}")
    return device_list

device_list = parse_quick_stat(quick_stat_log,hostname="fieldhub87")


def get_port_host(device_list,quad,wp,wp_address):
    return [(idevice.port, idevice.hostname) for idevice in device_list if idevice.quad==quad and idevice.wp==wp and idevice.wp_address==wp_address][0]



for ifile in config_lists[:]:
    with open(ifile, 'r') as f:
        data = json.load(f)
        # print(data)
        data_dry = []
        for imap in data:
            if imap["Quad"] in dry_quads:
                port,host = get_port_host(device_list,imap["Quad"],imap["Wire Pair"],imap["Address"])
                imap["DOMNet Data Port"] = port - imap["Address"]
                imap['host'] = host
                data_dry.append(imap)
        print(data_dry)
        outfile = args.out + ifile.split("/")[-1].replace(".","_dry.")
        print(f"{ifile.split("/")[-1].replace(".","_dry.")}")
        with open(outfile, 'w') as f:
            json.dump(data_dry, f,indent=4)


def parse_string_map(string_map):
    pass

def get_host_port_from_stringmap_icmid(string_map, icmid):
    with open(string_map, 'r') as f:
        data = json.load(f)
        for imap in data:
            if imap["icm_id"] == icmid:
                host = imap["hostname"]
                port = imap["port"]
                control_port = imap["control_port"]
                wp_address = imap["wp_addr"]
    return host,port,control_port,wp_address

def get_host_port_from_quickstat_icmid(file_path,icmid):
    with open(file_path, 'r') as f:
        f.readline()  # skip header line
        data = f.readlines()
        for line in data:
            values = line.split(" ")
            values = [istr.strip() for istr in values if istr!="" and istr!="\n"]
            if values[4]==icmid:
                cwa = values[0]
                quad1, wp, wp_address = card_wp_to_quad_wp(cwa)
                quad = int(re.sub('[a-zA-Z]', '',values[1]))
                if quad1 != quad:
                    print(f"conflicting quad calculations {quad1} and {quad}")               
                # hostname = values[2]
                port = int(values[2])
                control_port = int(values[3])
    return host,port,control_port,wp_address



def compare_quick_status_string_map(quick_stat_log,string_map):
    icmid_list = []
    with open(string_map, 'r') as f:
        data = json.load(f)
        for imap in data:
            icmid_list.append(imap["icm_id"])
    for icmid in icmid_list:
        print(f"comparing quickstatus and string map {get_host_port_from_quickstat_icmid(quick_stat_log,icmid)} {get_host_port_from_stringmap_icmid(string_map, icmid)}")

compare_quick_status_string_map(quick_stat_log,string_map)