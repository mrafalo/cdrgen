class LocalCustomer:
    def __init__(self, _customerid, _imei):
        self.customerid = _customerid
        self.operator = ""
        self.friends = []
        self.acquaintances = []
        self.call_contacts = []
        self.sms_contacts = []
        self.imei = _imei
        self.intl = 0
        self.frauder = 0
        self.probe = 0

class InternationalCustomer:
    def __init__(self, internationalid, internationalop):
        self.customerid = internationalid
        self.operator = internationalop
        self.intl = 1
        self.imei = []
