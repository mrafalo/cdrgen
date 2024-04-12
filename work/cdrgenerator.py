import datetime
import operator
import random
import json
from work.customers import LocalCustomer, InternationalCustomer
from work.operators import LocalOperator, InternationalOperator
from work.cdr import CallRecord
from random import randrange, randint
import numpy as np
import pandas as pd
import utils
import utils.custom_logger as cl

logger = cl.get_logger()

def get_value_from_distribution(_values, _distribution):
    mu = len(_values) / 2  
    sigma = 1.0 
    while True:
        if _distribution == 'gaussian':
            index = int(round(np.random.normal(mu, sigma)))
        elif _distribution == 't-student':
            index = int(round(np.random.standard_t(mu)))
        else:
              index = int(round(np.random.chisquare(mu)))
      
        if 0 <= index < len(_values):
            return _values[index]
        

def get_weibull_call_count(_avg):
    return int(np.random.weibull(0.74) * _avg)


def get_weibull_duration(_avg):
    return int(np.random.weibull(0.61) * _avg)

def get_random_hour():
    probabilities = [1] * 24  
    for hour in range(5, 23):
        probabilities[hour] = 2  
    for hour in range(8, 20):
        probabilities[hour] = 3  
    for hour in range(10, 18):
        probabilities[hour] = 4     
    for hour in range(12, 15):
        probabilities[hour] = 5  
        
    probabilities = np.array(probabilities) / sum(probabilities)
    random_hour = np.random.choice(np.arange(0, 24), p=probabilities)
    
    return random_hour


def normal(call_number):
    return np.random.normal(15.74, 4.21, call_number)


def read_config():
    with open('config.json') as file:
        params = json.load(file)

    return params


def create_operator(_operator_num):
    operators = []
    last_marketshare = 0

    for i in range(_operator_num):
        if i == 0:
            market_sh = random.randint(0, 70)
            last_marketshare += market_sh
            oper = LocalOperator(f"company_{i + 1}", (market_sh / 100))
            operators.append(oper)
        elif i == _operator_num - 1:
            oper = LocalOperator(f"company_{i + 1}", ((100 - last_marketshare) / 100))
            operators.append(oper)

        else:
            market_sh = random.randint(0, (100 - last_marketshare))
            oper = LocalOperator(f"company_{i + 1}", (market_sh / 100))
            operators.append(oper)
            last_marketshare += market_sh
    return operators


def create_international_operator(_operator_num):
    international_operators = []
    for i in range(_operator_num):
        operator_name = 'intl_company_' + str(i)
        intoper = InternationalOperator(operator_name)
        international_operators.append(intoper)
    return international_operators


def create_local_imeis(_customer_num):
    imeis = []
    for j in range(2*_customer_num):
        imeis.append('imei_' + str(j))
     
    return imeis          
    
def create_local_customers(_customer_num, _imeis):
    customers = []
    for i in range(_customer_num):
        
        imei = _imeis[random.randint(i, i+5)]            
        customer = LocalCustomer(i, imei)
        customers.append(customer)
    return customers


def create_intl_customers(_customer_num, _intl_operators):
    internationals = []
    
    for i in range(_customer_num):
        international_operator = _intl_operators[random.randint(0, len(_intl_operators)-1)]
        intc = InternationalCustomer(i, international_operator)
        internationals.append(intc)
    return internationals


def fill_local_operators(_operators, _customers4op, _customer_num):
    for oper in _operators:
        for _ in range(int(oper.marketshare*_customer_num)):
            customer = _customers4op.pop()
            customer.operator = oper
    
    while len(_customers4op) > 0:
        customer = _customers4op.pop()
        customer.operator = oper
        


def fill_possible_contacts(customers, max_friends, max_acquaintances, internationals):
    for _, customer in enumerate(customers):
        # Append friends
        for _ in range(random.randint(2, max_friends * random.randint(1, 10))):
            if np.random.binomial(1, 0.9):
                possible_contact = random.choice(customers)
                if possible_contact.customerid != customer.customerid:
                    customer.friends.append(possible_contact)
                    possible_contact.friends.append(customer)
            else:
                possible_contact = random.choice(internationals)
                customer.friends.append(possible_contact)

        # Append acquaintances
        for _ in range(random.randint(2, max_acquaintances * random.randint(1, 10))):
            if np.random.binomial(1, 0.9):
                possible_contact = random.choice(customers)
                if possible_contact.customerid != customer.customerid:
                    customer.acquaintances.append(possible_contact)
                    possible_contact.acquaintances.append(customer)
            else:
                possible_contact = random.choice(internationals)
                customer.acquaintances.append(possible_contact)


def fill_calls(_customers, _cfg):
    for customer in _customers:
        call_count = get_weibull_call_count(_cfg['AVG_CALLS_CNT'])
        for _ in range(call_count):
            probability = random.randint(1, 10)
            if probability <= 5:
                possible_contact = random.choice(customer.friends)
                customer.call_contacts.append(possible_contact)
            elif probability <= 8:
                possible_contact = random.choice(customer.acquaintances)
                customer.call_contacts.append(possible_contact)
            else:
                possible_contact = random.choice(_customers)
                if possible_contact.customerid!=customer.customerid:
                    customer.call_contacts.append(possible_contact)


def fill_sms(_customers, _cfg):
    for customer in _customers:
        sms_count = get_weibull_call_count(_cfg['AVG_SMS_CNT'])
        for _ in range(sms_count):
            probability = random.randint(1, 10)
            if probability <= 5:
                possible_contact = random.choice(customer.friends)
                customer.sms_contacts.append(possible_contact)
            elif probability <= 8:
                possible_contact = random.choice(customer.acquaintances)
                customer.sms_contacts.append(possible_contact)
            else:
                possible_contact = random.choice(_customers)
                if possible_contact.customerid!=customer.customerid:
                    customer.sms_contacts.append(possible_contact)
                    
def random_date(start_date_str):
    start_date = start_date_str.split('-')
    start = datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]), 0, 0)
    start += datetime.timedelta(minutes=randrange(60))
    start += datetime.timedelta(hours=int(get_random_hour()))
    start += datetime.timedelta(days=randrange(0, 30))
    return start

def add_cdr(_customer, _contact, _timestamp, _duration, _imei, _contact_type, _bts, _target):
    cdr = CallRecord(
                caller = _customer,
                called = _contact,
                timestamp = _timestamp,
                duration_sec = _duration,
                imei = _imei, 
                contact_type = _contact_type,
                caller_operator = _customer.operator.name,
                called_operator = _contact.operator.name,
                roaming = _contact.intl,
                bts = _bts,
                status = 'OK' if (_duration>0) | (_contact_type=='SMS') else 'FAIL'
                )
    
    cdr_row = {'caller_id': cdr.caller.customerid,
           'frauder': cdr.caller.frauder,   
           'probe': cdr.caller.probe,   
           'called_id': cdr.called.customerid,
           'timestamp': cdr.timestamp,
           'duration_sec': cdr.duration_sec,
           'imei':  cdr.imei,
           'contact_type': cdr.contact_type,
           'caller_operator': cdr.caller_operator,
           'called_operator': cdr.called_operator, 
           'roaming': cdr.roaming,
           'bts': cdr.bts,
           'status': cdr.status,
           'target': _target}
    
    return cdr, cdr_row

def get_duration(_avg_duration):
    call_success = np.random.binomial(1, 0.9)
    duration = get_weibull_duration(_avg_duration) if bool(call_success) else call_success
    
    return duration 

def get_timestamp(_start_date):
    return random_date(_start_date).strftime("%Y-%m-%d %H:%M")

def get_imei(_value):
    return random.choice(_value)

def get_bts(_bts_cnt):
    
    bts_list = []
    for i in range(_bts_cnt):
        bts_list.append('bts_' + str(i))
        
    return get_value_from_distribution(bts_list, 'chi')    

def generate_cdr(_customers, _cfg):

    start_date = _cfg['START_DATE']
    bts_cnt = _cfg['NUMBER_OF_BTS']
    avg_duration = _cfg['AVG_CALL_DURATION']
    
    res = pd.DataFrame(columns=["caller_id", "frauder", "probe", "called_id", 
                                "timestamp", "duration_sec", "caller_imei",
                                "contact_type", "caller_operator_id",
                                "called_operator_id", "roaming", "bts", "status", "target"])
    
    res_filename = 'results/cdr_' + start_date + '.csv'
    res.to_csv(res_filename, mode='w', header=True, index=False, sep=';')           
    
    pos = 0
    for customer in _customers:
        pos = pos + 1
        if pos % 1000 == 0:
            logger.info("cdr generation: " + str(pos) + '/' + str(len(_customers)))
            
        for contact in customer.call_contacts:
            if customer.frauder==1:
                cdr, new_row = add_cdr(customer, 
                       contact, 
                       get_timestamp(start_date), 
                       get_duration(avg_duration*1.8), 
                       customer.imei, 
                       'VOICE', 
                       get_bts(int(0.15*bts_cnt)), 
                       1)
           
            elif customer.probe==1:
                cdr, new_row = add_cdr(customer, 
                       contact, 
                       get_timestamp(start_date), 
                       get_duration(avg_duration*1.7), 
                       customer.imei, 
                       'VOICE', 
                       get_bts(int(0.15*bts_cnt)), 
                       0)
            
            elif customer.probe==2:
                cdr, new_row = add_cdr(customer, 
                             contact, 
                       get_timestamp(start_date), 
                       get_duration(avg_duration*1.9), 
                       customer.imei, 
                       'VOICE', 
                       get_bts(int(0.15*bts_cnt)), 
                       0)
                
            else:
                cdr, new_row = add_cdr(customer, 
                        contact, 
                        get_timestamp(start_date), 
                        get_duration(avg_duration), 
                        customer.imei, 
                        'VOICE', 
                        get_bts(int(0.6*bts_cnt)), 
                        0)
                            
            res = pd.DataFrame(new_row, index=[0])
            res.to_csv(res_filename, mode='a', header=False, index=False, sep=';')
           
        for contact in customer.sms_contacts:
            cdr, new_row = add_cdr(customer, 
                                   contact, 
                                   get_timestamp(start_date), 
                                   0, 
                                   customer.imei, 
                                   'SMS', 
                                   get_bts(bts_cnt), 
                                   0)
            
            res = pd.DataFrame(new_row, index=[0])
            res.to_csv(res_filename, mode='a', header=False, index=False, sep=';')
           

    tmp = pd.read_csv(res_filename, sep=';')
    tmp  = tmp.sort_values(by='timestamp')
    tmp.to_csv(res_filename,  mode='w', header=True, index=False, sep=';')
    

def simbox_scenario_gen_cdr(_frauder_num, _simbox_customers, _cfg):
    
    res = pd.DataFrame(columns=["caller_id", "called_id", 
                            "timestamp", "duration_sec", "caller_imei",
                            "contact_type", "caller_operator_id",
                            "called_operator_id", "roaming", "bts", "status", "target"])
        
    start_date = _cfg['START_DATE']
    avg_duration = _cfg['AVG_CALL_DURATION']
    bts_cnt = _cfg['NUMBER_OF_BTS']
    res_filename = 'results/cdr_simbox_' + start_date + '.csv'
    res.to_csv(res_filename, mode='w', header=True, index=False, sep=';')     
    
    pos = 0
    for customer in _simbox_customers:
        
        pos = pos + 1
        
        if pos % 10 == 0:
            logger.info("cdr simbox generation fraud: " + str(_frauder_num) + ' customer:' + str(pos) + '/' + str(len(_simbox_customers)))
            
        for contact in customer.call_contacts:
            cdr, new_row = add_cdr(customer, 
                                   contact, 
                                   get_timestamp(start_date), 
                                   get_duration(avg_duration*2), 
                                   customer.imei, 
                                   'VOICE', 
                                   get_bts(int(0.05*bts_cnt)), 
                                   1)
                
         
            res = pd.DataFrame(new_row, index=[0])
            res.to_csv(res_filename, mode='a', header=False, index=False, sep=';')
           
    tmp = pd.read_csv(res_filename, sep=';')
    tmp  = tmp.sort_values(by='timestamp')
    tmp.to_csv(res_filename,  mode='w', header=True, index=False, sep=';')
    
def simbox_scenario_prepare(_cfg, _frauder_num, _operators, _customers):

    customer_cnt = random.randint(20, 60)
    customers = []
    imei = 's1_imei_' + str(_frauder_num)
    oper = random.choice(_operators)
    
    for i in range(customer_cnt):
        
        customer = LocalCustomer('s_' + str(i) + '_' + str(_frauder_num), imei)
        customer.operator = oper

        for _ in range(random.randint(20, _cfg['SOCIAL_FAR'] * random.randint(120))):
            possible_contact = random.choice(_customers)
            if (possible_contact.customerid != customer.customerid) & (possible_contact.operator.name == customer.operator.name):
                customer.acquaintances.append(possible_contact)
        
        call_count = get_weibull_call_count(_cfg['AVG_CALLS_CNT'] * random.randint(120))
        for _ in range(call_count):
            if len(customer.acquaintances) > 0:
                possible_contact = random.choice(customer.acquaintances)
                customer.call_contacts.append(possible_contact)

        customers.append(customer)


    return customers

def simbox_scenario(_cfg, _customer_num, _operators, _customers):

    for k in range(_customer_num):
        customer_cnt = random.randint(5, 20)
        imei = 's1_imei_' + str(k)
        oper = random.choice(_operators)
        
        for i in range(customer_cnt):
            frauder = random.choice(_customers)
            frauder.operator = oper
            frauder.imei = imei
            frauder.frauder = 1
        
            for _ in range(random.randint(10, _cfg['SOCIAL_FAR'] * random.randint(3, 20))):
                possible_contact = random.choice(_customers)
                if (possible_contact.customerid != frauder.customerid) & (possible_contact.operator.name == frauder.operator.name):
                    frauder.acquaintances.append(possible_contact)
            
            call_count = get_weibull_call_count(_cfg['AVG_CALLS_CNT'] * random.randint(1, 30))
            for _ in range(call_count):
                if len(frauder.acquaintances) > 0:
                    possible_contact = random.choice(frauder.acquaintances)
                    frauder.call_contacts.append(possible_contact)

def multisim_scenario(_cfg, _multisim_num, _operators, _customers):

    for k in range(_multisim_num):
        customer_cnt = random.randint(5, 20)
        imei = 'm1_imei_' + str(k)
        oper = random.choice(_operators)
        
        for i in range(customer_cnt):
            
            frauder = random.choice(_customers)
            if (frauder.frauder != 1) & (frauder.probe != 1):
                frauder.probe = 2
                frauder.operator = oper
                frauder.imei = imei
                
                for _ in range(random.randint(10, _cfg['SOCIAL_FAR'] * random.randint(3, 20))):
                    possible_contact = random.choice(_customers)
                    if (possible_contact.customerid != frauder.customerid) & (possible_contact.operator.name == frauder.operator.name):
                        frauder.acquaintances.append(possible_contact)
                
                call_count = get_weibull_call_count(_cfg['AVG_CALLS_CNT'] * random.randint(1, 30))
                for _ in range(call_count):
                    if len(frauder.acquaintances) > 0:
                        possible_contact = random.choice(frauder.acquaintances)
                        frauder.call_contacts.append(possible_contact)
                    
def probe_scenario(_cfg, _probe_num, _operators, _customers):

    for k in range(_probe_num):
        customer_cnt = random.randint(5, 20)
        imei = 'p1_imei_' + str(k)
        oper = random.choice(_operators)
        
        for i in range(customer_cnt):
            probe = random.choice(_customers)
            
            if probe.frauder != 1:
                probe.operator = oper
                probe.imei = imei
                probe.probe = 1
            
                for _ in range(random.randint(10, _cfg['SOCIAL_FAR'] * random.randint(3, 20))):
                    possible_contact = random.choice(_customers)
                    if (possible_contact.customerid != probe.customerid) :
                        probe.acquaintances.append(possible_contact)
                
                call_count = get_weibull_call_count(_cfg['AVG_CALLS_CNT'] * random.randint(1, 30))
                for _ in range(call_count):
                    if len(probe.acquaintances) > 0:
                        possible_contact = random.choice(probe.acquaintances)
                        probe.call_contacts.append(possible_contact)
                    
def combine_results(_cfg):
    start_date = _cfg['START_DATE']
    res_filename1 = 'results/cdr_' + start_date + '.csv'
    res_filename2 = 'results/cdr_simbox_' + start_date + '.csv'
    res_filename3 = 'results/cdr_final_' + start_date + '.csv'
    
    df1 = pd.read_csv(res_filename1, sep=';')
    df2 = pd.read_csv(res_filename2, sep=';')
    
    res = pd.concat([df1, df2], ignore_index=True)
    
    res  = res.sort_values(by='timestamp')
    res.to_csv(res_filename3,  mode='w', header=True, index=False, sep=';')
    
def run_generator():
    logger.info("starting...")
    
    cfg = read_config()
    
    #operators
    local_operators_list = create_operator(cfg['NUMBER_OF_LOCAL_OPERATORS'])
    intl_operators_list = create_international_operator(cfg['NUMBER_OF_INTL_OPERATORS'])

    logger.info("oprators created...")
    
    #customers
    imeis = create_local_imeis(cfg['NUMBER_OF_LOCAL_CUSTOMERS'])
    local_customers_list = create_local_customers(cfg['NUMBER_OF_LOCAL_CUSTOMERS'], imeis)
    intl_customes_list = create_intl_customers(cfg['NUMBER_OF_INTL_CUSTOMERS'],intl_operators_list)
    local_customers_list_cp = local_customers_list.copy()
    fill_local_operators(local_operators_list, local_customers_list_cp,cfg['NUMBER_OF_LOCAL_CUSTOMERS'])

    logger.info("customers created...")

    #contacts
    fill_possible_contacts(local_customers_list, cfg['SOCIAL_FAR'], cfg['SOCIAL_NEAR'], intl_customes_list)
    fill_calls(local_customers_list, cfg)
    fill_sms(local_customers_list, cfg)

    #simbox fraud scenario
    simbox_scenario(cfg, 3, local_operators_list, local_customers_list)
    multisim_scenario(cfg, 250, local_operators_list, local_customers_list)
    probe_scenario(cfg, 150, local_operators_list, local_customers_list)

    
    logger.info("customer contacts created...")
    #CDR

    generate_cdr(local_customers_list, cfg)
    
    logger.info("CDR records created...")
    
    #simbox gen fraudalent cdr 
    #simbox_scenario_gen_cdr(1, simbox_customers_list, cfg)
    
    #combine_results(cfg)
    
    logger.info("all OK!...")
    
    
