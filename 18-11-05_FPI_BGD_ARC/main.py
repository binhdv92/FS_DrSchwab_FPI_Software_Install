#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import datetime
import keyboard
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import my_util as util

queues_online = []
queues_offline = []


# ## Loading fpi_sources for the watch dog

# In[2]:


#fpi_sources = util.load_json_config(r'sources/fpi_sources.json')['values']
#fpi_sources

fpi_sources = util.load_dat_config('sources/fpi_sources.dat')
fpi_sources


# In[3]:


dummy_fpi_sources = util.load_dat_config('sources/fpi_sources_dummy.dat')
dummy_fpi_sources


# In[4]:

util.makedirs_folders(util.flat_dict_dest_bad_image_folders())

# In[]:
util.makedirs_folders(dummy_fpi_sources)


# ## Parameters of the watch dog

# In[5]:


patterns= ['*.fpi','*.fpih']
ignore_patterns = None
ignore_directories = False
case_sensitive = False
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


# In[6]:


def on_created(event):
    print(f'on created:\t {os.path.normpath(event.src_path)}')
    queues_online.append(os.path.normpath(event.src_path))
    
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


# ## Example for finding fpi_dest_path
fpi_src_abspath = r'__dummy__/DMT1\DMT1_DrSchwab\ARC_U2_Bad_Results/FS_210730671082_BGD_ARC_A_0_2021-07-30-09-55-06.FPI'
#fpi_string = r'//FS.LOCAL/FSGlobal/Global/Shared/Manufacturing/PGT2/PGT2_DrSchwab/CdCl_B_Bad_Results/PGT21B_0_210707730231_2021-07-29_22-58-12.FPI'
#fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT2\PGT2_DrSchwab\ARC_U1_Bad_Results\PGT2_ARC_A_0_210725770433_2021-07-29-12-31-50.FPI'
#fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT1\PGT1_DrSchwab\Cover_Glass_Bad_Results\2021\07\29\ID_2021-07-29_20-13-49.FPI'
#fpi_src_abspath = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT1\PGT1_DrSchwab\PGT12_CdCl_Bad_Results\PGT21A_0_P12CV02A20102000004_2020-10-20_09-05-51.FPI'

# ## Remove and makedirs workspace folder

# In[7]:


print('remove: workspace')
try:
   shutil.rmtree('workspace')
   print('remove: workspace sucessful')
except Exception as e:
   print(e)

print('makedirs: workspace')
try:
   os.makedirs(os.path.join(os.getcwd(),'workspace'))
   print('makedirs: workspace sucessful')
except Exception as e:
   print(e)


# In[8]:


screen_keeper_timer_threshold = datetime.timedelta(minutes=1)
my_observer = Observer()
for i, fpi_source in enumerate(fpi_sources):
    print(f'watchdog scheduling for {fpi_source}')
    my_observer.schedule(my_event_handler, fpi_source , recursive=True)
for i, dummy_fpi_source in enumerate(dummy_fpi_sources):
    print(f'watchdog scheduling for {dummy_fpi_source}')
    my_observer.schedule(my_event_handler, dummy_fpi_source , recursive=True)
my_observer.start()

util.Check_PanelInspection()
util.Close_PanelInspection()
if __name__ == "__main__":
    print('\r\n00:00:00')
    
    tic=datetime.datetime.now()
    tic_original = tic
    queues_online=list(dict.fromkeys(queues_online))
    try:
        while True:            
            if(len(queues_online))!=0:
                print('<queues_online>')
                util.Check_PanelInspection()
                util.Close_PanelInspection()
                ### remove and makedirs workspace folder
                print('remove: workspace')
                try:
                    shutil.rmtree('workspace')
                    print('remove: workspace sucessful')
                except Exception as e:
                    print(e)

                print('makedirs: workspace')
                try:
                    os.makedirs(os.path.join(os.getcwd(),'workspace'))
                    print('makedirs: workspace sucessful')
                except Exception as e:
                    print(e)
                ### remove and makedirs workspace folder
                print('00.00.00.01')   
                fpi_src_abspath = queues_online[0]
                print(f'the start of a queue_online: {fpi_src_abspath}')
                print('00.00.00.11')
                metadata = util.fpi_extracting(fpi_src_abspath)
                print(f'metadata: {metadata}')
                
                if(metadata["alarm_id"] !='' and metadata["size_file_MB"]>=5):
                    print('00.00.00.03')
                    metadata = util.copy_backup_file()
                    if(metadata["plant"] !=''):
                        if(metadata["subid"] != ''):
                            print('00.00.00.04')                        
                            util.data_mining_ods()                        
                        if(metadata["flag_copy_fpi"] == True):
                            print('00.00.00.05')
                            util.open_fpi(metadata['fpi_dest_file_abspath'])
                            metadata = util.saveScreenShoot()
                            metadata = util.saveImageToPNG()

                            if(metadata['flag_saveImageToPNG'] ==True and os.path.exists(metadata['png_dest_file_abspath_01_00'])):
                                print('00.00.00.06')
                                ### get_concat_v_blank
                                print(f"{datetime.datetime.now()}: check file exists: {metadata['png_dest_file_abspath_01_00']}")
                                try:
                                    if(metadata["alarm_id"] == 'CdCl'):
                                        util.get_concat_v_blank()
                                    else:
                                        util.get_concat_h_blank()
                                    print('get_concat_v_blank: OK')
                                except Exception as e:
                                    print(e)
                        
                        util.sending_bgd_email()  
                       
                        
                ###
                print(f'the end of a queue_online: {metadata["fpi_src_abspath"]}')
                print('</queues_online>')
                queues_online=list(dict.fromkeys(queues_online))
                queues_online.pop(0)
                tic=datetime.datetime.now()
                tic_original = tic
   
            else: ### the end of queue
                toc = datetime.datetime.now()
                screen_keeper_timer= toc-tic
                if(screen_keeper_timer>screen_keeper_timer_threshold):
                    print('[screen_keeper][Press F15 to keep screen on]')
                    keyboard.press_and_release('F15')
                    tic= datetime.datetime.now() ##reset timer
                    print(f'[screen_keeper] clicked @ {screen_keeper_timer} {toc}, total time screen idled: {toc-tic_original}')
                    
    except Exception as e:
        print(e)
    finally:
        my_observer.stop()
        my_observer.join()

print('the end of code')
# In[ ]:




