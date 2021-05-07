from pydicom.dataset import Dataset
from pynetdicom.sop_class import VerificationSOPClass, MRImageStorage
from pydicom.uid import JPEG2000Lossless

from pynetdicom import (
    AE, evt,
    StoragePresentationContexts,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)

import os, sys, traceback
import re
import datetime


# Implement a handler evt.EVT_C_STORE
def handle_store(event,storage_dir):
    """Handle a C-STORE request event."""
    try:
        os.makedirs(storage_dir, exist_ok=True)
    except:
    # Unable to create output dir, return failure status
        return 0xC001

    #Decode the C-STORE request's *Data Set* parameter to a pydicom Dataset
    try:
        ds = event.dataset
        ds.file_meta = event.file_meta
        desc = ds.SeriesDescription
        if 't1' in desc.lower() and 'post' in desc.lower():
            series = 't1'
        elif 't1' in desc.lower() and 'pre' in desc.lower():
            series = 't1pre'
        elif 't2' in desc.lower():
            series = 't2'
        elif 'flair' in desc.lower():
            series = 'flair'
        else:
            series = 't1ce'
        # We rely on the Acc# and seriesdescrption from the C-STORE request instead of decoding
        dir_name = os.path.join(storage_dir, ds.AccessionNumber, series)
        os.makedirs(dir_name, exist_ok=True)
        #use SOPInstanceUID as filename
        fname = os.path.join(dir_name, ds.SOPInstanceUID+'.dcm')
        ds.save_as(fname, write_like_original=False)

        log =(f"{datetime.datetime.now():%Y-%m-%d|%H:%M:%S} "
              f"| {ds.AccessionNumber} "
              f"| {ds.SeriesDescription} \n"
        )
        with open('logs/cases.log', 'a') as f:
            f.write(log)
    except Exception as e:
        with open('logs/cases.log', 'a')as f:
            f.write(traceback.format_exc())
    
    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store,['/app/data/incoming'])]

# Initialise the Application Entity
ae = AE(ae_title=b'BRAIN_MRI')

# Add the supported presentation contexts
ae.supported_contexts = StoragePresentationContexts
ae.add_supported_context(VerificationSOPClass)
ae.add_supported_context(MRImageStorage,JPEG2000Lossless)

# Start listening for incoming association requests
ae.start_server(('0.0.0.0', 11112), evt_handlers=handlers)
