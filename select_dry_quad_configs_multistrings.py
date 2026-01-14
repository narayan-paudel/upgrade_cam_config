#!/usr/bin/env python

import argparse
import json
import glob

import re
import os

parser = argparse.ArgumentParser()
parser.add_argument('-config_path', '--path', dest='path',default="/Users/epaudel/research_ua/icecube/pole_calibration/hole-freeze-operations/UpgradeCamera/OperationsConfigs/String87/ExposureTimeScans/Quad6plus", help='path to run config')
parser.add_argument('-quick_stat_path_87', '--quickpath87', dest='quickpath87',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/quickStat.log", help='path to quick status log')
parser.add_argument('-quick_stat_path_88', '--quickpath88', dest='quickpath88',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/quickStat.log", help='path to quick status log')
parser.add_argument('-quick_stat_path_89', '--quickpath89', dest='quickpath89',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/quickStat.log", help='path to quick status log')
# parser.add_argument('-string_map', '--stringmap', dest='stringmap',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/string_87_quad14_20.json", help='path to string map')
# parser.add_argument('-dry_quads', '--dquads', dest='dry_quads',nargs='+',type=int,default=[14,20], help='list of dry quads')
parser.add_argument('-output_path', '--out', dest='out',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/dry_configs/", help='path to string map')

args = parser.parse_args()

# print(f"reading configs from path {args.path}")

config_lists = glob.glob(args.path+"/*.json")
quick_stat_log87 = args.quickpath87
quick_stat_log88 = args.quickpath88
quick_stat_log89 = args.quickpath89
# hostname = args.host
# string_map = args.stringmap

os.makedirs(args.out, exist_ok=True)


# print(f"config_lists {len(config_lists)} {config_lists}")

# dry_quads = args.dry_quads

class device():
    # def __init__(self, string, quad, wp, hostname, port, control_port, wp_address):
    def __init__(self,n_string,xdom, quad, wp, port, control_port, wp_address):
        self.n_string = n_string
        self.xdom = xdom
        self.quad = quad
        self.wp = wp
        self.port = port
        self.control_port = control_port
        self.wp_address = wp_address
        self.domnet_data_port = self.port - self.wp_address
        self.hostname = f"fieldhub{self.n_string}" 

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

def dry_quads_from_quickstats(file_path):
    dry_quads = []
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
                dry_quads.append(quad)
    return dry_quads

dry_quads_87 = list(set(dry_quads_from_quickstats(quick_stat_log87)))
dry_quads_88 = list(set(dry_quads_from_quickstats(quick_stat_log88)))
dry_quads_89 = list(set(dry_quads_from_quickstats(quick_stat_log89)))
dry_quads = dry_quads_87 + dry_quads_88 + dry_quads_89
print(f"dry quads 87 {dry_quads_87}")
print(f"dry quads 88 {dry_quads_88}")
print(f"dry quads 89 {dry_quads_89}")


def parse_quick_stat(file_path,n_string):
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
                idevice = device(n_string,xdom,quad, wp, port, control_port, wp_address)
                # print(f"Parsed device: {idevice}")
                device_list.append(idevice)
            # print(f"line {values}")
    return device_list

device_list_87 = parse_quick_stat(quick_stat_log87,n_string=87)
device_list_88 = parse_quick_stat(quick_stat_log88,n_string=88)
device_list_89 = parse_quick_stat(quick_stat_log89,n_string=89)

# print(f"device lsit {device_list_87} {device_list_88} {device_list_89}")


def get_port_host(device_list,quad,wp,wp_address):
    print(quad,wp,wp_address)
    print([(idevice.port, idevice.hostname) for idevice in device_list if idevice.quad==quad and idevice.wp==wp and idevice.wp_address==wp_address])
    return [(idevice.port, idevice.hostname) for idevice in device_list if idevice.quad==quad and idevice.wp==wp and idevice.wp_address==wp_address][0]


print(f"hi {config_lists}")
for ifile in config_lists[:]:
    print(ifile)
    with open(ifile, 'r') as f:
        data = json.load(f)
        print(data)
        data_dry = []
        for imap in data:
            print(f"imap {imap}")
            if imap["String"]==87:
                if imap["Quad"] in dry_quads_87:
                    port,host = get_port_host(device_list_87,imap["Quad"],imap["Wire Pair"],imap["Address"])
                    imap["DOMNet Data Port"] = port - imap["Address"]
                    imap['host'] = host
                    data_dry.append(imap)
            elif imap["String"] == 88:
                if imap["Quad"] in dry_quads_88:
                    port,host = get_port_host(device_list_88,imap["Quad"],imap["Wire Pair"],imap["Address"])
                    imap["DOMNet Data Port"] = port - imap["Address"]
                    imap['host'] = host
                    data_dry.append(imap)
            elif imap["String"] == 89:
                if imap["Quad"] in dry_quads_89:
                    port,host = get_port_host(device_list_89,imap["Quad"],imap["Wire Pair"],imap["Address"])
                    imap["DOMNet Data Port"] = port - imap["Address"]
                    imap['host'] = host
                    data_dry.append(imap)
            else:
                print(f"unrecognized string encountered {imap['String']}, not in [87,88,89] ")
        # print(data_dry)
        outfile = args.out + ifile.split("/")[-1]
        # outfile = args.out + ifile.split("/")[-1].replace(".","_dry.")
        # print(f"{ifile.split("/")[-1].replace(".","_dry.")}")
        print(f"outfile {outfile}")
        with open(outfile, 'w') as f:
            json.dump(data_dry, f,indent=4)


# def parse_string_map(string_map):
#     pass

# def get_host_port_from_stringmap_icmid(string_map, icmid):
#     with open(string_map, 'r') as f:
#         data = json.load(f)
#         for imap in data:
#             if imap["icm_id"] == icmid:
#                 host = imap["hostname"]
#                 port = imap["port"]
#                 control_port = imap["control_port"]
#                 wp_address = imap["wp_addr"]
#     return host,port,control_port,wp_address

# def get_host_port_from_quickstat_icmid(file_path,icmid):
#     with open(file_path, 'r') as f:
#         f.readline()  # skip header line
#         data = f.readlines()
#         for line in data:
#             values = line.split(" ")
#             values = [istr.strip() for istr in values if istr!="" and istr!="\n"]
#             if values[4]==icmid:
#                 cwa = values[0]
#                 quad1, wp, wp_address = card_wp_to_quad_wp(cwa)
#                 quad = int(re.sub('[a-zA-Z]', '',values[1]))
#                 if quad1 != quad:
#                     print(f"conflicting quad calculations {quad1} and {quad}")               
#                 # hostname = values[2]
#                 port = int(values[2])
#                 control_port = int(values[3])
#     return host,port,control_port,wp_address



# def compare_quick_status_string_map(quick_stat_log,string_map):
#     icmid_list = []
#     with open(string_map, 'r') as f:
#         data = json.load(f)
#         for imap in data:
#             icmid_list.append(imap["icm_id"])
#     for icmid in icmid_list:
#         print(f"comparing quickstatus and string map {get_host_port_from_quickstat_icmid(quick_stat_log,icmid)} {get_host_port_from_stringmap_icmid(string_map, icmid)}")

# # compare_quick_status_string_map(quick_stat_log,string_map)