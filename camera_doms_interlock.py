#!/usr/bin/env python

import argparse
import json
import glob

import re
import os

parser = argparse.ArgumentParser()
parser.add_argument('-config_path', '--path', dest='path',default="/Users/epaudel/research_ua/icecube/pole_calibration/hole-freeze-operations/UpgradeCamera/OperationsConfigs/String87/ExposureTimeScans/Quad6plus", help='path to run config')
parser.add_argument('-host', '--host', dest='host',default="localhost", help='localhost')
parser.add_argument('-outfilename', '--out', dest='out',default="/Users/epaudel/research_ua/icecube/pole_calibration/upgrade_cam_config/dry_configs/reset_camera.sh", help='path to string map')

args = parser.parse_args()

# print(f"reading configs from path {args.path}")

config_lists = glob.glob(args.path+"/*.json")
hostname = args.host
# string_map = args.stringmap

# os.makedirs(args.out, exist_ok=True)
device_list = []


for ifile in config_lists[:]:
    with open(ifile, 'r') as f:
        data = json.load(f)
        # print(data)
        data_dry = []
        for imap in data:
            address = imap["Address"]
            fh_port = int(imap["DOMNet Data Port"] + 1000)
            print(f"host {hostname} {fh_port} {address}")
            device_list.append((hostname,fh_port,address))
print(f"device list {device_list} {len(device_list)}")
unique_dev_list = list(set(device_list))
print(f"device list {unique_dev_list} {len(unique_dev_list)}")

# print(f"outfile {outfile}")
with open(args.out, 'w') as f:
    f.writelines(f"#!/bin/bash \n\n\n")
    for ielt in unique_dev_list:
        hostname,fh_port,address = ielt
        f.writelines(f"echo Interlock status on host {hostname} port {fh_port} address {address} \n")
        f.writelines(f"interlock_status  --host {hostname} -p {fh_port} -w {address} \n")


