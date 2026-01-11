#!/usr/bin/env python

import argparse
import json
import glob

import re
import os

import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-config_path', '--path', dest='path',default="/Users/epaudel/research_ua/icecube/pole_calibration/hole-freeze-operations/UpgradeCamera/OperationsConfigs/String87/ExposureTimeScans/Quad6plus", help='path to run config')
parser.add_argument('-script', '--s', dest='script',default="mcu_reset", help='reset selected mcu')

args = parser.parse_args()

# print(f"reading configs from path {args.path}")

config_lists = glob.glob(args.path+"/*.json")
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
            host = imap["host"]
            print(f"host {host} {fh_port} {address}")
            device_list.append((host,fh_port,address))
# print(f"device list {device_list} {len(device_list)}")
unique_dev_list = list(set(device_list))
# print(f"device list {unique_dev_list} {len(unique_dev_list)}")
for idevice in unique_dev_list:
    print(f"{args.script} {idevice[0]} {idevice[1]} {idevice[2]}")
    subprocess.run(f"{args.script} --host {idevice[0]} -p {idevice[1]} -w {idevice[2]}", shell=True)




# # print(f"outfile {outfile}")
# with open(args.out, 'w') as f:
#     f.writelines(f"#!/bin/bash \n\n\n")
#     for ielt in unique_dev_list:
#         hostname,fh_port,address = ielt
#         f.writelines(f"echo host {hostname} port {fh_port} address {address} \n")
#         f.writelines(f"mcu_reset --host {hostname} -p {fh_port} -w {address} \n")


