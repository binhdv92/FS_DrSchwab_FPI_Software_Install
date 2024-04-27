#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os, pyodbc
import pandas as pd
# import re
# import datetime
# import keyboard
# import time
# import shutil
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import my_util as util
from app.faclib.queues import Queues
from app.faclib.screenkeeper import ScreenKeeper
from app.configs.configs import Configs

##################################
# class
##################################
SqlExtract = f'''
SELECT		 [ID]
			,[FpiSourcePath]
			,[FpiDestPath]
			,[ImagePath]
			,[ExtractSubId]
			,[ExtractFpiSize]
			,[ExtractAlarmName]
			,[ExtractSitePlant]
			,[ExtractEquipment]
			,[ExtractTimeStamp]
			,[ExtractIsDummyMode]
			,[SubIdCorrected]
			,[TimeStamp]
			,[TimeStampUtc]
			,[ModifiedTimeStampUtc]
  FROM		[FAC].[dbo].[BgdBacklog]
  where		id = (select max(id) from [FAC].[dbo].[BgdBacklog])
			and (FpiDestPath is null or ImagePath is null or SubIdCorrected is null)
'''

class Workers():
    def __init__(self):
        self.backlogs = self.load()

    def load(self):
        with pyodbc.connect(configs.database, autocommit=True) as conn:
            df01 = pd.read_sql_query(SqlExtract,conn)
        return df01
  
##################################
# end class
##################################  
# In[]
configs = Configs()
queues = Queues()
#screenKeeper = ScreenKeeper('sk1',60)
#screenKeeper.pause()

# In[6]:
my_event_handler = PatternMatchingEventHandler(
    configs.watchdog.patterns, 
    configs.watchdog.ignorePatterns,
    configs.watchdog.ignoreDirectories, 
    configs.watchdog.caseSensitive)

def on_created(event):
    print(f'on created:\t {os.path.normpath(event.src_path)}')
    # add to Queues and database
    queues.insert_or_update(os.path.normpath(event.src_path))
def on_deleted(event):
    print(f'on deleted:\t {os.path.normpath(event.src_path)}')
def on_modified(event):
    print(f'on modified:\t {os.path.normpath(event.src_path)}')
def on_moved(event):
    print(f'on moved:\t {os.path.normpath(event.src_path)}')
    
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

my_observer = Observer()
#configs.disableProdMode()
configs.fpiSourcesMakeDirs()
print(f'watchdog scheduling')
for fpi_source in configs.fpiSources.data:
    my_observer.schedule(my_event_handler, fpi_source , recursive=True)
my_observer.start()

# In[7]

#util.Check_PanelInspection()
 
if __name__ == "__main__":
    print(os.getcwd())
    try:
        while True:    
            pass
        ## workflow
        # query backlog
        #workers = Workers()
        # workers.load()
        # workers.Copy()
        # workers.Validate()

        #         
            #if(queues.queueOnline):
                #screenKeeper.pause()
                #print('<queues_online>')
                # util.Check_PanelInspection()
                # ### remove and makedirs workspace folder
                # print('remove: workspace')
                # try:
                #     shutil.rmtree('workspace')
                #     print('remove: workspace sucessful')
                # except Exception as e:
                #     print(e)

                # print('makedirs: workspace')
                # try:
                #     os.makedirs(os.path.join(os.getcwd(),'workspace'))
                #     print('makedirs: workspace sucessful')
                # except Exception as e:
                #     print(e)
                # ### remove and makedirs workspace folder
                # print('00.00.00.01')   
                # fpi_src_abspath = queues.get()
                # print(f'the start of a queue_online: {fpi_src_abspath}')
                # print('00.00.00.11')
                # metadata = util.fpi_extracting(fpi_src_abspath)
                # print(f'metadata: {metadata}')
                
                # if(metadata["alarm_id"] !='' and metadata["size_file_MB"]>=5):
                #     print('00.00.00.03')
                #     metadata = util.copy_backup_file()
                #     if(metadata["plant"] !=''):
                #         if(metadata["subid"] != ''):
                #             print('00.00.00.04')                        
                #             util.data_mining_ods()                        
                #         if(metadata["flag_copy_fpi"] == True):
                #             print('00.00.00.05')
                #             util.open_fpi(metadata['fpi_dest_file_abspath'])
                #             metadata = util.saveScreenShoot()
                #             metadata = util.saveImageToPNG()

                #             if(metadata['flag_saveImageToPNG'] ==True and os.path.exists(metadata['png_dest_file_abspath_01_00'])):
                #                 print('00.00.00.06')
                #                 ### get_concat_v_blank
                #                 print(f"{datetime.datetime.now()}: check file exists: {metadata['png_dest_file_abspath_01_00']}")
                #                 try:
                #                     if(metadata["alarm_id"] == 'CdCl'):
                #                         util.get_concat_v_blank()
                #                     else:
                #                         util.get_concat_h_blank()
                #                     print('get_concat_v_blank: OK')
                #                 except Exception as e:
                #                     print(e)
                        
                #         util.sending_bgd_email()  
                       
                        
                # ###
                # print(f'the end of a queue_online: {metadata["fpi_src_abspath"]}')
                #print('</queues_online>')
                #queues_online=list(dict.fromkeys(queues_online))
                #queues_online.pop(0)
                #queues.pop()
                #tic=datetime.datetime.now()
                #screenKeeper.resume()
                #pass
            #else: ### the end of queue
               # pass
                    
    except Exception as e:
        print(e)

    finally:
        my_observer.stop()
        my_observer.join()

print('the end of code')
# In[ ]:




