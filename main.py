#!/usr/bin/env python3

import os
import sys
import time
import json
import ast
import logging
import logging.handlers
import multiprocessing as mp
import tkinter
from tkinter.filedialog import askopenfilenames
import pandas as pd
import psycopg
from dotenv import load_dotenv
import scapy.all as scapy

import log
from db import init_db 

load_dotenv()
from config import settings

STOP = settings.stop
DATABASE_URL = settings.database_url

# This is awkward, but I'm converting a string to a list of dicts 
RSSI_BINS = [ast.literal_eval(item.strip()) for item in settings.rssi_bins.split(';')]

for item in RSSI_BINS:
    print(item)
    
def get_files(label=''):
    
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilenames(parent=root, title="Select .pcap or .pcapng file"+label)
    return filename

def main():

    def exit_main():
        log_queue.put(STOP)
        listener.join()
        sys.exit()

    # All module logger handlers write to log_queue
    log_queue = mp.Queue()

    # listener writes all log entries
    listener = mp.Process(
        target=log.log_listener_process,
        args=(log_queue,),
        name="LogListener",
    )
    listener.start()

    # logger for main
    logger = log.configure_queue_logger(__name__, log_queue)

    try:
        init_db(log_queue)
    except Exception as e:
        logger.critical('init_db() failed')
        logger.critical('%s',e)
        exit_main()
    logger.info("DB initialized")

    input_files = get_files()
    if not input_files:
        logger.critical('Input .pcap or .pcapng not selected.')
        exit_main() 
    logger.info("Input .pcap files")

    # Insert into PostgreSQL
    with psycopg.connect(DATABASE_URL) as conn:
        conn.autocommit = False # this is the default, but making explicit because SQL default is True
        with conn.cursor() as cur:

            def get_rssi_bin(rssi):
                if rssi <= RSSI_BIN[0]['max']:
                    return 0
                elif rssi <= RSSI_BIN[1]['max']:
                    return 1
                elif rssi <= RSSI_BIN[2]['max']:
                    return 2
                elif rssi <= RSSI_BIN[3]['max']:
                    return 3
                elif rssi <= RSSI_BIN[4]['max']:
                    return 4
                elif rssi <= RSSI_BIN[5]['max']:
                    return 5
                else:
                    return 6

            def process_and_insert(packet):
 
                pkt_type = packet[scapy.Dot11].type
                pkt_subtype = packet[scapy.Dot11].subtype
                addr1 = packet[scapy.Dot11].addr1 # Destination
                addr2 = packet[scapy.Dot11].addr2 # Source/Transmitter
                try:
                    if pkt.haslayer(PPI_Hdr):
                        payload = pkt['PPI'].getlayer('PPI_Hdr')['Raw'].load
                        lat, = struct.unpack('<I',payload[12:16])
                        lon, = struct.unpack('<I',payload[16:20])
                        alt, =struct.unpack('<I',payload[20:24])
                        if lat != 1800000000:
                            lat = (lat - 1800000000)/1e7
                            lon = (lon - 1800000000)/1e7  
                            alt = (alt - 1800000000)/1e4
                        rssi = pkt.getlayer(RadioTap).dBm_AntSignal
                        time_stamp = float(pkt.time)
                except UnicodeDecodeError as e:
                    logger.warning(f'packet not processed: {e}')

                # Extract SSID from Probe Requests or Beacons
                ssid = None
                if packet.haslayer(Dot11Elt) and packet[Dot11Elt].ID == 0:
                    try:
                        ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore')
                    except:
                        ssid = "<hidden>"

                                
            for input_file in input_files:
                logger.info(input_file)
                sniff(offline=input_file, prn=process_and_insert, filter="type mgt", store=False)                
                cur.execute(
                    "INSERT INTO frames (src_mac, dst_mac, ssid) VALUES (%s, %s, %s)",
                    (addr2, addr1, ssid)
                )
                conn.commit()

#    workers = [
#        mp.Process(
#            target=worker_process,
#            args=(i, log_queue),
#            name=f"Worker-{i}",
#        )
#        for i in range(1, 4)
#    ]
#
#    for p in workers:
#        p.start()
#
#    for p in workers:
#        p.join()
        
    module.func(log_queue)

    # Tell the listener to stop after all workers are done
    log_queue.put(STOP)
    listener.join()



if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
