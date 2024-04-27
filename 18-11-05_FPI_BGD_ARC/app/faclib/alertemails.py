import json

class AlertEmails():
    def __init__(self, path=r'sources/api/AlertRecipients.json'):
        self.path = path
        self.data = self.init()
        self.norm()
        self.save()

    def alertNameShort(alertNameShort):
        alertNameShort = alertNameShort.lower()
        tempdict = {
            'arc':'ARC BGD BREAKAGE ALERTS',
            'cdcl':'CDCL BGD BREAKAGE ALERTS',
            'coverglass':'COVERGLASS BGD BREAKAGE ALERTS',
            'fs200vi':'FS200VI IMAGE ALERTS'
        }
        if(alertNameShort in tempdict):
            output = tempdict[alertNameShort]
        else:
            output = ''
        return output

    def init(self):
        with open(f'{self.path}','r') as f:
            s = f.read()
            alertEmails = json.loads(s)
        return alertEmails
    
    def create(self, alertName, sitePlant,emails):
        try:
            if(alertName in self.data):
                if (sitePlant in self.data[alertName]):
                    temp = self.data[alertName][sitePlant]
                    self.data[alertName][sitePlant]= temp + emails
                    self.norm()
                    self.save()
                    print('create successuful')
                else:
                    print(f'{sitePlant} do not exist')
            else:
                print(f'{alertName} do not exist')
        except Exception as e:
            print(f'error: {e}')

    def read(self):
        return self.data

    def update(self, alertName, sitePlant, oldEmail, newEmail):
        try:
            if(alertName in self.data):
                if (sitePlant in self.data[alertName]):
                    self.delete(alertName, sitePlant, [oldEmail])
                    self.create(alertName, sitePlant,[newEmail])
                    self.norm()
                    self.save()
                else:
                    print(f'{sitePlant} do not exist')
            else:
                print(f'{alertName} do not exist')
        except Exception as e:
            print(f'error: {e}')

    def delete(self, alertName, sitePlant, emails):
        flag = 0
        try:
            if(alertName in self.data):
                if (sitePlant in self.data[alertName]):
                    for i in emails:
                        self.data[alertName][sitePlant].remove(i)
                        print(f'success delete {i}')
                    self.norm()
                    self.save()
                else:
                    print(f'{sitePlant} do not exist')
            else:
                print(f'{alertName} do not exist')
        except Exception as e:
            print(f'error: {e}')

    def save(self):
        json_obj = json.dumps(self.data)
        with open(f'{self.path}','w') as f:
            f.write(json_obj)
   
    def print(self):
        print(self.data)

    def norm(self):
        for i,v in enumerate(self.data):
            for ii, vv in enumerate(self.data[v]):
                self.data[v][vv] = list(set(self.data[v][vv]))

import datetime
from random import random

class Queue():
    def __init__(self):
        self.queueOnline=[]
        self.queueOffline = []
        self.previousID = ''
        self.counter = 0 # maximun = 9999
        self.id=''
    
    def append(self,value):
        # create queueID
        self.createID()

        # record in queueOnline 
        self.queueOnline.append(
            {
                "id":self.id,
                "value":value
            }
        )

        # record in database


    def pop(self):
        # remove at queueOnline
        self.queueOnline.pop(0) 

        # mark "Done" in database


    def get(self):
        return self.queueOnline[0]
    
    
    def createID(self):
        # get datetime
        today = datetime.datetime.today().strftime('%Y-%M-%d_%H:%M:%S.%f')

        # compare datetime with previous value to avoid dupliate
        if(self.queueOnline):
            if(today == self.queueOnline[-1]["id"][0:26] ):
                self.counter += 1
            else:
                self.counter = 0 

        # combine into id       
        self.id = f'{today}_{self.counter.__str__().zfill(4)}'
'''
import AlertRecipients as fac

alertEmailsObj = fac.AlertEmails(r'sources/api/AlertRecipients.json')

data = alertEmailsObj.delete('ARC BGD BREAKAGE ALERTS','DMT2',['binhdv92@gmail.com'])
'''

