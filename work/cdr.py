class CallRecord:
    def __init__(self, caller, called, timestamp, duration_sec, imei, contact_type, caller_operator, called_operator, roaming, bts, status):
        self.caller = caller
        self.called = called
        self.timestamp = timestamp
        self.duration_sec = duration_sec 
        self.imei = imei, 
        self.contact_type = contact_type,
        self.caller_operator = caller_operator,
        self.called_operator = called_operator,
        self.roaming = roaming,
        self.bts = bts
        self.status = status