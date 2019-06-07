import logging

import gcn
import lxml.etree

import sender
from config import logging_kwargs

logging.basicConfig(**logging_kwargs)

# Function to call every time a GCN is received.
# Run only for notices of type
# LVC_PRELIMINARY, LVC_INITIAL, LVC_UPDATE or LVC_RETRACTION
@gcn.handlers.include_notice_types(
    gcn.notice_types.LVC_PRELIMINARY,
    gcn.notice_types.LVC_UPDATE,
    gcn.notice_types.LVC_RETRACTION
)
def process_gcn(payload, root):

    # if root.attrib['role'] != 'observation':
    #     return

    params = {
        elem.attrib['name']:
        elem.attrib['value']
        for elem in root.iterfind('.//Param')
    }

    message_poster = {
        'Preliminary': sender.post_preliminairy,
        'Update': sender.post_update,
        'Retraction': sender.post_retraction,
    }
    message_poster[params['AlertType']]()

def test_send_preliminairy():
    payload = open('MS181101ab-1-Preliminary.xml', 'rb').read()
    payload = str(payload, 'utf-8')
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

def test_send_initial():
    payload = open('MS181101ab-2-Initial.xml', 'rb').read()
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

def test_send_update():
    payload = open('MS181101ab-3-Update.xml', 'rb').read()
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

def test_send_retraction():
    payload = open('MS181101ab-4-Retraction.xml', 'rb').read()
    root = lxml.etree.fromstring(payload)
    process_gcn(payload, root)

if __name__ == '__main__':
    gcn.listen(handler=process_gcn)