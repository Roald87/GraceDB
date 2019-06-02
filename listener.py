import json
import logging

import gcn
import lxml.etree

import sender
from config import logging_kwargs
from voevent import VOEvent

logging.basicConfig(**logging_kwargs)

# Function to call every time a GCN is received.
# Run only for notices of type
# LVC_PRELIMINARY, LVC_INITIAL, or LVC_UPDATE.
@gcn.handlers.include_notice_types(gcn.notice_types.LVC_PRELIMINARY)
def process_gcn(payload, root):
    voe = VOEvent()
    voe.from_string(payload)

    event_info = dict()
    event_info['p_astro'] = voe.p_astro
    event_info['id'] = voe.id

    sender.post_preliminairy(json.dumps(event_info))
    # # Respond only to 'test' events.
    # # VERY IMPORTANT! Replace with the following code
    # # to respond to only real 'observation' events.
    # # if root.attrib['role'] != 'observation':
    # #    return
    # if root.attrib['role'] != 'test':
    #     return
    #
    # # Read all of the VOEvent parameters from the "What" section.
    # params = {elem.attrib['name']:
    #           elem.attrib['value']
    #           for elem in root.iterfind('.//Param')}
    #
    # # Respond only to 'CBC' events. Change 'CBC' to "Burst'
    # # to respond to only unmodeled burst events.
    # if params['Group'] != 'CBC':
    #     return
    #
    # # Print all parameters.
    # for key, value in params.items():
    #     print(key, '=', value)
    #
    # if 'skymap_fits' in params:
    #     # Read the HEALPix sky map and the FITS header.
    #     skymap, header = hp.read_map(params['skymap_fits'],
    #                                  h=True, verbose=False)
    #     header = dict(header)
    #
    #     # Print some values from the FITS header.
    #     print('Distance =', header['DISTMEAN'], '+/-', header['DISTSTD'])

def send_preliminairy():
    payload = open('MS181101ab-1-Preliminary.xml', 'rb').read()
    payload = str(payload, 'utf-8')
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

def send_initial():
    payload = open('MS181101ab-2-Initial.xml', 'rb').read()
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

def send_update():
    payload = open('MS181101ab-3-Update.xml', 'rb').read()
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

def send_retraction():
    payload = open('MS181101ab-4-Retraction.xml', 'rb').read()
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

if __name__ == '__main__':
    gcn.listen(handler=process_gcn)