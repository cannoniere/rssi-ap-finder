#!/usr/bin/env python5

import os
import sys
import time
import json
import ast
import struct
import tkinter
from tkinter.filedialog import askopenfilenames
import pandas as pd
import psycopg
from dotenv import load_dotenv
import scapy.all as scapy
from datetime import datetime, timezone
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

from db import init_db 

load_dotenv()
from config import settings
from pages import page1, page2, page3

STOP = settings.stop
DATABASE_URL = settings.database_url

# This is awkward, but I'm converting a string to a list of dicts 
RSSI_BINS = [ast.literal_eval(item.strip()) for item in settings.rssi_bins.split(';')]


def get_files(label=''):
    
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilenames(parent=root, title="Select .pcap or .pcapng file"+label)
    return filename

def main():

    try:
        init_db()
    except Exception as e:
        print(f'init_db() failed : {e}')

    input_files = get_files()
    if not input_files:
        print('No input .pcap or .pcapng selected.')

    with psycopg.connect(DATABASE_URL) as conn:
        conn.autocommit = False # this is the default, but making explicit because SQL default is True
        with conn.cursor() as cur:
            
            def get_rssi_bin(rssi):
                if rssi <= RSSI_BINS[0]['max']:
                    return 0
                elif rssi <= RSSI_BINS[1]['max']:
                    return 1
                elif rssi <= RSSI_BINS[2]['max']:
                    return 2
                elif rssi <= RSSI_BINS[3]['max']:
                    return 3
                elif rssi <= RSSI_BINS[4]['max']:
                    return 4
                elif rssi <= RSSI_BINS[5]['max']:
                    return 5
                else:
                    return 6
            
            def is_mgmt_frame(packet):
                return packet[scapy.Dot11].type == 0

            def process_and_insert(packet):
 
                pkt_type = packet[scapy.Dot11].type
                pkt_subtype = packet[scapy.Dot11].subtype
                ra = packet[scapy.Dot11].addr1
                ta = packet[scapy.Dot11].addr2
                try:
                    if packet.haslayer(scapy.PPI_Hdr):
                        payload = packet['PPI'].getlayer('PPI_Hdr')['Raw'].load
                        lat, = struct.unpack('<I',payload[12:16])
                        lon, = struct.unpack('<I',payload[16:20])
                        alt, =struct.unpack('<I',payload[20:24])
                        if lat != 1800000000:
                            lat = (lat - 1800000000)/1e7
                            lon = (lon - 1800000000)/1e7  
                            alt = (alt - 1800000000)/1e4
                        else:
                            # Is it better to record that we saw it without a position or to drop it?
                            # lat = 'NaN'
                            # lon = 'NaN'
                            # alt = 'NaN'
                            return
                        rssi = float(packet.getlayer(scapy.RadioTap).dBm_AntSignal)
                        unix_ts = float(packet.time)
                        ts = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
                    else:
                        print('packet not processed - no PPI_Hdr')
                        return
                except (UnicodeDecodeError, AttributeError) as e:
                    print(f'packet not processed: {e}')
                    return
 
                # Extract SSID from Probe Requests or Beacons
                ssid = 'None'
                if packet.haslayer(scapy.Dot11Elt) and packet[scapy.Dot11Elt].ID == 0:
                    try:
                        ssid = packet[scapy.Dot11Elt].info.decode('utf-8')
                    except Exception as e:
                        print(f'ssid error: {e}')
                        my_list = [f'{b:02x}' for b in packet[scapy.Dot11Elt].info]
                        ssid = '(hex)'+'_'.join(my_list)
                    finally:
                        if ssid == '':
                            ssid = '<hidden>'
                        if '\0' in ssid:
                            my_list = [f'{b:02x}' for b in packet[scapy.Dot11Elt].info]
                            ssid = '(hex)'+'_'.join(my_list)
                            
                try:
                    cur.execute(
                        "INSERT INTO frames (ts, dot11_type, dot11_subtype, ta, ra, ssid, rssi_dbm, rssi_bin, lat, lon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (ts, pkt_type, pkt_subtype, ta, ra, ssid, rssi, get_rssi_bin(rssi), lat, lon)
                    )
                except Exception as e:
                    print(f'DB insertion error - packet skipped')
                return
                                
            for input_file in input_files:
                try:
                    scapy.sniff(
                        offline=input_file, 
                        prn=process_and_insert, 
                        # filter="type mgt", 
                        lfilter=is_mgmt_frame,                    
                        store=False)                
                except Exception as e:
                    print(f'Scapy sniff error: {e}')

            conn.commit()
            conn.autocommit = True

            cur.execute("SELECT count(*) FROM frames;")
            count = cur.fetchone()[0]
            print(f'{count} rows inserted')

            cur.execute("SELECT DISTINCT ta FROM frames;")
            ta_addrs = cur.fetchall()
            cur.execute("SELECT DISTINCT ra FROM frames;")
            ra_addrs = cur.fetchall()
            all_addrs = set(ta_addrs) | set(ra_addrs)
 
            print(f'{len(all_addrs)} unique MACs')

            return

app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = dbc.Container(
    fluid=True,
    className="vh-100",
    children=[
        dbc.Row(
            className="h-100",
            children=[
                # Left navigation column
                dbc.Col(
                    width=2,
                    className="bg-light border-end p-4",
                    children=[
                        dbc.Label("Navigation", className="fw-bold mb-3"),
                        dbc.RadioItems(
                            id="page-selector",
                            options=[
                                {"label": "Page 1", "value": "page-1"},
                                {"label": "Page 2", "value": "page-2"},
                                {"label": "Page 3", "value": "page-3"},
                            ],
                            value="page-1",
                            inline=False,
                        ),
                    ],
                ),

                # Right content column
                dbc.Col(
                    width=10,
                    className="p-4",
                    children=[
                        dbc.Card(
                            dbc.CardBody(id="page-content"),
                            className="h-100",
                        )
                    ],
                ),
            ],
        )
    ],
)


@app.callback(
    Output("page-content", "children"),
    Input("page-selector", "value"),
)
def display_page(selected_page):
    if selected_page == "page-1":
        return page1.layout()

    if selected_page == "page-2":
        return page2.layout()

    if selected_page == "page-3":
        return page3.layout()

    return dbc.Alert("Page not found.", color="danger")


if __name__ == "__main__":

    main()
    app.run(debug=True, use_reloader=False)

            


