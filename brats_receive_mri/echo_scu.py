from pynetdicom import AE, debug_logger

debug_logger()

ae = AE()
ae.add_requested_context('1.2.840.10008.1.1')
assoc = ae.associate('localhost', 11113)
if assoc.is_established:
    status = assoc.send_c_echo()
    assoc.release()
