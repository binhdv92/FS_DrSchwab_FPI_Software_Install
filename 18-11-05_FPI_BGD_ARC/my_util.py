# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 07:43:06 2021

@author: FS126112
"""

import os
import json
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from shutil import copyfile

from PIL import Image
import win32api
import win32con
import win32gui
import keyboard
import time
import datetime
from datetime import datetime, timedelta
import PIL.ImageGrab as IG
import pyautogui
import pyperclip
import psutil
import pyodbc
import re
import pygetwindow as gw
import pandas as pd
import subprocess
#Sfrom fac import AlertEmails


commandSet = {
    'PanelInspection': [70, 18],
    'PanelInspectionFile': [17, 47],
    'PanelInspectionPosDropFile': [200, 200],

    'explorerPos': [1753, 12],
    'explorerPosSearch': [1800, 75],
    'explorerPosPickFile': [1900, 132]
}


def sending_bgd_email():
    print('<sending_bgd_email>')
    metadata = load_json_config('workspace/metadata.json')
    try:
        with open('workspace/df01.html','r') as f:
            df01_html = f.read()
        print('open: workspace/df01.html')
    except Exception as e:
        df01_html = ''
        print(e)
    
    try:
        with open('workspace/df02.html','r') as f:
            df02_html = f.read()
        print('open: workspace/df02.html')
    except Exception as e:
        df02_html =''
        print(e)
           
    email_config = select_email_config_02(alarm_id= metadata['alarm_id'],plant=metadata['plant'],subid=metadata['subid'],png_dest_file_abspath=metadata['png_dest_file_abspath'],dummy_mode=metadata['dummy_mode'])
    
    SUBJECT = email_config['subject']
    TO = email_config['recipients']
    FROM =  email_config['from_address']
    ##composing email_message {df01_html,df02_html,image_file_name}
    msgRoot = MIMEMultipart('related')
    msgRoot['subject'] = SUBJECT
    msgRoot['To'] = ', '.join(map(str,TO))
    msgRoot['From'] = FROM 
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    #df01_html = df01_html+f"<p>{metadata['png_dest_file_abspath']}</p>"
    html_body = load_file('sources/body_template_bgd.html')
    html_body = html_body.replace('var_subid_table',df01_html).replace('var_ca_table',df02_html)\
        .replace('image1_footer',metadata['png_dest_file_abspath'])\
        .replace('fpi_src_abspath',metadata['fpi_src_abspath']).replace('var_equipment',metadata['var_equipment'])
    msgAlternative.attach(MIMEText(html_body,'html'))
    
    ## save html_body
    with open(r'workspace/body.html','w') as f:
        f.write(html_body)
        print('save workspaces/body.html')
        
    ## embedded Image
    if (os.path.exists(metadata['png_dest_file_abspath'])):
        print('exists png_dest_file_abspath')
        with open(metadata['png_dest_file_abspath'], 'rb') as file:
            email_image1 = MIMEImage(file.read())
        email_image1.add_header('Content-ID', "image1")
        msgRoot.attach(email_image1)
    print(f"[f_send_email_02]-> success embeded image {metadata['png_dest_file_abspath']}: ")

    with open(r'workspace/msgRoot.eml','w') as f:
        f.write(msgRoot.as_string())
        print('save workspace/msgRoot.eml')
    ## sending email {info,message}
    
    try:
        with smtplib.SMTP('fsbridge.fs.local', '25') as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.sendmail(FROM, TO, msgRoot.as_string())                                             
        print('</sending_bgd_email>')
    except Exception as e:
        print(e)
        
def select_email_config(alarm_id,plant):
    print('</select_email_config>')
    if(alarm_id == 'ARC'):
        email_config = load_json_config('sources/arc_bgd/email_config.json')[plant]
    elif(alarm_id == 'CdCl'):
        email_config = load_json_config('sources/cdcl_bgd/email_config.json')[plant]
    elif(alarm_id == 'CoverGlass'):
        email_config = load_json_config("sources/cover_glass_bgd/email_config.json")[plant]
    print('<select_email_config>')
    return email_config

def select_email_config_02(alarm_id='',plant='',subid='',simulation=True,png_dest_file_abspath='',dummy_mode=False):
    print('<select_email_config_02>')
    abs_file_name = os.path.abspath('sources/email_production.json')  
    
    with open(abs_file_name, 'r') as fileobj:
        s = fileobj.read()
        content_of_config_file_temp = json.loads(s)    
  
    ##Prepare recipients
    if(content_of_config_file_temp['production'] == True):
        if(dummy_mode==False):
            if(subid!=''):
                if(os.path.exists(png_dest_file_abspath)): 
                    s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','')
                    if(alarm_id == 'ARC'):
                        email_recipients = load_json_config('sources/arc_bgd/email_recipients.json')[plant]
                    elif(alarm_id == 'CdCl'):
                        email_recipients = load_json_config('sources/cdcl_bgd/email_recipients.json')[plant]
                    elif(alarm_id == 'CoverGlass'):
                        email_recipients = load_json_config("sources/cover_glass_bgd/email_recipients.json")[plant]  
                else:
                    s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[NoImage] ')
                    email_recipients = load_json_config('sources/email_recipients_admin.json')['fail']
            else:
                if(alarm_id == 'CoverGlass'):
                    s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','')
                    email_recipients = load_json_config("sources/cover_glass_bgd/email_recipients.json")[plant] 
                else:
                    s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[NoSubid] ')
                    email_recipients = load_json_config('sources/email_recipients_admin.json')['fail']
        else:
            s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[DummyMode] ')
            email_recipients = load_json_config('sources/email_recipients_admin.json')['dummy_mode']   
    else:
        s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[Simulation] ')
        email_recipients = load_json_config('sources/email_recipients_admin.json')['simulation']
    
    content_of_config_file = json.loads(s)
    email_config = content_of_config_file
    email_config['recipients']=email_recipients
    
    dict_to_json(email_config,r'workspace/email_config.json')
    print('</select_email_config_02>')
    return email_config
    
def load_file(file_name):
    print('<load_file>')
    """With this function we load content of a file"""
    abs_file_name = os.path.abspath(file_name)
    print(f"load_file('{abs_file_name}')")
    with open(abs_file_name, 'r') as fileobj:
        content_of_config_file = fileobj.read()
    print('</load_file>')
    return content_of_config_file

def leftClick(pos):
    print('<leftClick>')
    win32api.SetCursorPos(pos)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, pos[0], pos[1], 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, pos[0], pos[1], 0, 0)
    print('</leftClick>')

def press_and_releaseX(key, x, delay):
    print('<press_and_releaseX>')
    print(key)
    for i in range(x):
        keyboard.press_and_release(key)
        
        time.sleep(delay)
    print('</press_and_releaseX>')
         
def get_concat_v_blank(color=(0, 0, 0)):
    print('<get_concat_v_blank>')
    metadata=load_json_config(r'workspace/metadata.json')
    im1=''
    im2=''
    try:
        im1 = Image.open( metadata['png_dest_file_abspath_01_00'])
        im1=im1.transpose(Image.ROTATE_90)
        print('concat png_dest_file_abspath_01_00')
    except:
        print(f"not exists: {metadata['png_dest_file_abspath_01_00']}")
    try:
        im2 = Image.open( metadata['png_dest_file_abspath_screenshoot'])
        print('concat png_dest_file_abspath_screenshoot')
    except:
        print(f"not exists: {metadata['png_dest_file_abspath_01_00']}")
        
    if((im1!='') & (im2!='')):
        dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
        dst.save(metadata['png_dest_file_abspath'])
    elif((im1!='') & (im2!='')):
        dst=im1
        dst.save(metadata['png_dest_file_abspath'])
    elif((im1=='') & (im2!='')):
        dst=im2
        dst.save(metadata['png_dest_file_abspath'])
    else:
        dst=''
    print('</get_concat_v_blank>')
    
def get_concat_h_blank(color=(0, 0, 0)):
    print('<get_concat_h_blank>')
    metadata=load_json_config(r'workspace/metadata.json')
    im1=''
    im2=''
    try:
        im1 = Image.open( metadata['png_dest_file_abspath_01_00'])
        print('concat png_dest_file_abspath_01_00')
    except:
        print(f"not exists: {metadata['png_dest_file_abspath_01_00']}")
    try:
        im2 = Image.open( metadata['png_dest_file_abspath_screenshoot'])
        print('concat png_dest_file_abspath_screenshoot')
    except:
        print(f"not exists: {metadata['png_dest_file_abspath_01_00']}")
        
    if((im1!='') & (im2!='')):
        dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        dst.save(metadata['png_dest_file_abspath'])
    elif((im1!='') & (im2!='')):
        dst=im1
        dst.save(metadata['png_dest_file_abspath'])
    elif((im1=='') & (im2!='')):
        dst=im2
        dst.save(metadata['png_dest_file_abspath'])
    else:
        dst=''
    print('</get_concat_h_blank>')
    

def get_concat_h_blank_rotate(color=(0, 0, 0)):
    print('<get_concat_h_blank_rotate>')
    metadata=load_json_config(r'workspace/metadata.json')
    im1=''
    im2=''
    try:
        im1 = Image.open( metadata['png_dest_file_abspath_01_00'])
        im1=im1.transpose(Image.ROTATE_90)
        print('concat png_dest_file_abspath_01_00')
    except:
        print(f"not exists: {metadata['png_dest_file_abspath_01_00']}")
    try:
        im2 = Image.open( metadata['png_dest_file_abspath_screenshoot'])
        print('concat png_dest_file_abspath_screenshoot')
    except:
        print(f"not exists: {metadata['png_dest_file_abspath_01_00']}")
        
    if((im1!='') & (im2!='')):
        dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        dst.save(metadata['png_dest_file_abspath'])
    elif((im1!='') & (im2!='')):
        dst=im1
        dst.save(metadata['png_dest_file_abspath'])
    elif((im1=='') & (im2!='')):
        dst=im2
        dst.save(metadata['png_dest_file_abspath'])
    else:
        dst=''
    print('</get_concat_h_blank_rotate>')

def flat_dict_dest_bad_image_folders():
    print('<flat_dict_dest_bad_image_folders>')
    temp = load_json_config(r'sources/dest_bad_image_folders.json')
    temp02 = []
    for _ ,alarm in temp.items():
        for _, plant in alarm.items():
            temp02.append(plant['dummy_fpi'])
            temp02.append(plant['dummy_image'])
            temp02.append(plant['fpi'])
            temp02.append(plant['image'])
    print('</flat_dict_dest_bad_image_folders>')
    return temp02

def makedirs_folders(folder_paths):
    print('<makedirs_folders>')
    for i,folder_path in enumerate(folder_paths):
        try:
            os.makedirs(folder_path)
            print(f"makedirs folder_path: {folder_path}")
        except Exception as e:
            print(e)
    print('</makedirs_folders>')

def saveScreenShoot(waitTimeMiniStep = 0.1,waitTimeEachStep = 1,):
    print('<saveScreenShoot>')
    metadata=load_json_config(r'workspace/metadata.json')
    flag_saveScreenShoot = False
    img = IG.grab()
    try:
        img.save(metadata['png_dest_file_abspath_screenshoot'])
        print(f"[saveScreenShoot][ok][saved {metadata['png_dest_file_abspath_screenshoot']}]")
        flag_saveScreenShoot = True
    except:
        print(f"[saveScreenShoot][ok][fail to save {metadata['png_dest_file_abspath_screenshoot']}]")
    
    time.sleep(waitTimeEachStep)
    
    #update metadata
    metadata['flag_saveScreenShoot']=flag_saveScreenShoot
    dict_to_json(metadata,r'workspace/metadata.json')
    
    print('</saveScreenShoot>')
    return metadata


def setting_app(waitTimeMiniStep = 0.1,waitTimeEachStep = 1):
    print('<setting_app>')
    ### Step01 clear PanelInspection
    print('openFPI step01 clear PanelInspection before loading fpi file')
    leftClick(commandSet['PanelInspection'])
    time.sleep(waitTimeMiniStep)
    press_and_releaseX('Enter', 10, 0.1)
    time.sleep(waitTimeMiniStep)
    time.sleep(waitTimeEachStep)

    # Step01: load fpi file
    print('openFPI step02 load fpi file')
    leftClick(commandSet['PanelInspectionFile'])
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('I')
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('A')
    time.sleep(waitTimeMiniStep)
    
    leftClick(commandSet['PanelInspectionFile'])
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('I')
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('S')
    time.sleep(waitTimeMiniStep)
    
    print('</setting_app>')

def find_windows_exists(name = 'PanelInspection'):
    print('<find_windows_exists>')
    pid=''
    for i in psutil.process_iter():
        if('PanelInspection' in i.name()):
            flag=True
            pid=i.pid
    print(f'pid={pid}')
    print('</find_windows_exists>')
    return pid

def Check_PanelInspection():
    print('<Check_PanelInspection>')
    ## find PanelInspection
    pid = find_windows_exists()
    if pid != '':
        print('PanelInspection is opening')
    else:
        print("PanelInspection is not opening, let's open it")
        time.sleep(1)
        app = subprocess.Popen('PanelInspection.exe')
        print('wait 4 seconds')
        time.sleep(4)
        leftClick(commandSet['PanelInspection'])
        press_and_releaseX('Enter', x=20, delay=0.2)
        
        # setting_app()
        pid = find_windows_exists()
        print(f'pid = {pid}')
    print('</Check_PanelInspection>')
def Close_PanelInspection(waitTimeMiniStep = 0.2):
    print('<Close_PanelInspection>')
    ## find PanelInspection

    leftClick(commandSet['PanelInspection'])
    press_and_releaseX('Enter', x=20, delay=0.2)
    
    keyboard.press_and_release('Alt')
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('f')
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('c')
    time.sleep(waitTimeMiniStep)
    press_and_releaseX('Enter', x=20, delay=0.2)

    print('</Close_PanelInspection>')
 
def saveImageToPNG(waitTimeMiniStep = 0.2,waitTimeEachStep = 1):
    print('<saveImageToPNG>')
    print('[saveImageToPNG]')
    metadata=load_json_config(r'workspace/metadata.json')
    flag_saveImageToPNG = False

    
    # clear PanelInspection
    #leftClick(commandSet['PanelInspection'])
    time.sleep(waitTimeMiniStep)
    press_and_releaseX('ESC', 10, 0.1)

    try:
        #leftClick(commandSet['PanelInspectionFile'])
        keyboard.press_and_release('Alt')
        time.sleep(waitTimeMiniStep)
        keyboard.press_and_release('f')
        time.sleep(waitTimeMiniStep)
        keyboard.press_and_release('S')
        time.sleep(waitTimeMiniStep)
        keyboard.press_and_release('S')
        time.sleep(waitTimeMiniStep)
        #keyboard.press_and_release('S')
        #time.sleep(waitTimeMiniStep)
        keyboard.press_and_release('Enter')
        time.sleep(waitTimeMiniStep)
        time.sleep(1)
    
        print(f"save to PNG: {metadata['png_dest_file_abspath']}")
        keyboard.write(metadata['png_dest_file_abspath'])
        time.sleep(1)
        keyboard.press_and_release('Enter')
        time.sleep(waitTimeMiniStep)
    
        time.sleep(waitTimeEachStep)
        print(f"[saveImageToPNG][OK][save][{metadata['png_dest_file_abspath']}]")
        
        flag_saveImageToPNG = True
    except:
        print(f"[saveImageToPNG][fail][save][{metadata['png_dest_file_abspath']}]")

    # clear PanelInspection
    # leftClick(commandSet['PanelInspection']);time.sleep(sleeptime)
    # press_and_releaseX('ESC',10,0.1);

    time.sleep(waitTimeEachStep)
    
    #update metadata
    metadata['flag_saveImageToPNG']=flag_saveImageToPNG
    dict_to_json(metadata,r'workspace/metadata.json')
    print('</saveImageToPNG>')
    return metadata

def open_fpi(fpi_file_name,waitTimeMiniStep = 0.1,waitTimeEachStep = 1):
    print('<open_fpi>')
    ### Step01 clear PanelInspection
    print('openFPI step01 clear PanelInspection before loading fpi file')
    leftClick(commandSet['PanelInspection'])
    time.sleep(waitTimeMiniStep)
    press_and_releaseX('Enter', 10, 0.1)
    time.sleep(waitTimeMiniStep)
    time.sleep(waitTimeEachStep)

    # Step01: load fpi file
    print('openFPI step02 load fpi file')
    leftClick(commandSet['PanelInspectionFile'])
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('L')
    time.sleep(waitTimeMiniStep)
    time.sleep(1)
    keyboard.write(fpi_file_name)
    time.sleep(1)
    time.sleep(waitTimeMiniStep)
    keyboard.press_and_release('Enter')
    time.sleep(waitTimeMiniStep)
    
    time.sleep(waitTimeEachStep)
    press_and_releaseX('Enter', 10, 0.1)
    
    press_and_releaseX('Enter', 10, 0.1)
    time.sleep(waitTimeMiniStep)
    
    press_and_releaseX('Enter', 10, 0.1)
    time.sleep(waitTimeMiniStep)
    
    press_and_releaseX('Enter', 10, 0.1)
    time.sleep(waitTimeMiniStep)
    
    press_and_releaseX('Enter', 10, 0.1)
    time.sleep(waitTimeMiniStep)
    print('openFPI OK open fpi sucessfull')
    print('</open_fpi>')

def copy_backup_file(max_attempt=30,sleep_time_attempt=2):
    print('<copy_backup_file>')
    metadata=load_json_config(r'workspace/metadata.json')
    print(f"[copy_backup_file][info][copy {metadata['fpi_src_abspath']} to {metadata['fpi_dest_file_abspath']}]")
    flag_copy_current=1
    flag_copy_fpi = False
    while flag_copy_current<=max_attempt:
        try:
            copyfile(metadata['fpi_src_abspath'],metadata['fpi_dest_file_abspath'])
            print(f"[copy_backup_file][ok][attemting {flag_copy_current}, done copying ]")
            flag_copy_current = max_attempt+1
            flag_copy_fpi = True
        except:
            print(f"[copy_backup_file][fail][attemting {flag_copy_current}/{max_attempt}, fail to copying, waiting {sleep_time_attempt}]")
            flag_copy_current = flag_copy_current+1
            time.sleep(sleep_time_attempt)
    
    metadata['flag_copy_fpi']=flag_copy_fpi
    dict_to_json(metadata,r'workspace/metadata.json')
    print('</copy_backup_file>')
    return metadata
    
def load_json_config(file_name):
    '''
    load_json_config(file_name=str)
    '''
    #abs_file_name = os.path.abspath(file_name)
    print('<load_json_config>')
    with open(file_name, 'r') as fileobj:
        s = fileobj.read()
        content_of_config_file = json.loads(s)
        print(f'json {file_name}')
    print('</load_json_config>')
    return content_of_config_file

def dict_to_json(dict, json_file_name):
    print('<dict_to_json>')
    json_obj = json.dumps(dict)
    with open(json_file_name,'w') as f:
        f.write(json_obj)
    print(f'dict_to_json: {json_file_name}')
    print('</dict_to_json>')

def load_dat_config(dat_file = 'sources/fpi_source.dat'):
    print('<load_dat_config>')
    print(f'dat_file {dat_file}')
    with open(dat_file,'r') as f:
        lines = f.readlines()
    fpi_sources = []
    for i,v in enumerate(lines):
        v=v.strip()
        temp =re.search('^#',v)
        if(temp == None and v):
            fpi_sources.append(v)
    print('</load_dat_config>')
    return fpi_sources

def find_datetime(fpi_src_abspath):
    print('<find_datetime>')
    var_datetime = None
    var_datetime_type = None
    # 2021-08-02-15-53-13
    pattern_datetime_01    = re.search('[2][0][2][0-9][-][0-1][0-9][-][0-3][0-9][-][0-2][0-9][-][0-5][0-9][-][0-5][0-9]',fpi_src_abspath)
    pattern_datetime_02    = re.search('[2][0][2][0-9][-][0-1][0-9][-][0-3][0-9][_][0-2][0-9][-][0-5][0-9][-][0-5][0-9]',fpi_src_abspath)
        
    if pattern_datetime_01 != None:
        startid_time      = pattern_datetime_01.start()
        endid_datetime    = startid_time+19
        var_datetime      = fpi_src_abspath[startid_time:endid_datetime]
        var_datetime      = var_datetime[0:10]+' '+var_datetime[11:13]+':'+var_datetime[14:16]+':'+var_datetime[17:]
        var_datetime_type = 'type-'
    elif pattern_datetime_02 != None:
        startid_time    = pattern_datetime_02.start()
        endid_datetime    = startid_time+19
        var_datetime      = fpi_src_abspath[startid_time:endid_datetime]
        var_datetime      = var_datetime[0:10]+' '+var_datetime[11:13]+':'+var_datetime[14:16]+':'+var_datetime[17:]
        var_datetime_type = 'type_'
        var_datetime_type = 'type_'
    print('</find_datetime>')
    return var_datetime,var_datetime_type


def data_mining_ods():
    print('<data_mining_ods>')
    metadata = load_json_config('workspace/metadata.json')
    try:
        if(metadata["alarm_id"] == 'ARC'):
            print('data mining ods: arc')
            data_mining_ods_arc_bgd()
        elif(metadata["alarm_id"] == 'CdCl'):
            print('data mining ods: cdcl')
            data_mining_ods_cdcl_bgd()
        else:
            print('pass data mining ods')
    except Exception as e:
        print(e)    
    print('end of data_mining_ods')
    print('</data_mining_ods>')

def data_mining_ods_arc_bgd():
    print('<data_mining_ods_arc_bgd>')
    metadata = load_json_config('workspace/metadata.json')
    try:
        os.remove('workspace/df01.html')
        print('delete workspace/df01.html')
    except Exception as e:
        print(e)
    try:
        os.remove('workspace/df02.html')
        print('delete workspace/df02.html')
    except Exception as e:
        print(e)
    df01_html='blank'
    df02_html='blank'
    var_ods_connection_origin = load_file(file_name='sources/ods_connection_string.txt')
    
    var_ods_connection = var_ods_connection_origin.replace('var_site_plant',metadata['plant'][0:4])
    with open(f'workspace/ods_connection_string.txt','w') as f:
        f.write(var_ods_connection)
    
    var_sql_extraction_02_origin = load_file(file_name='sources/arc_bgd/arc_job_ca.sql')
    var_sql_extraction_02        = var_sql_extraction_02_origin.replace('var_datetime',metadata['var_datetime'])
    ##print(f'var_sql_extraction_02={var_sql_extraction_02}')
    
    print(f'Connect to ods: {var_ods_connection}')    
    try:
        print('quering data')     
        ###
        print('query subid_table')
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            if(metadata["var_datetime"]==''):
                var_sql_extraction_origin = load_file(file_name='sources/arc_bgd/arc_job_subid.sql')
                var_sql_extraction = var_sql_extraction_origin.replace('var_subids',metadata['subid'])
                print('var_datetime blank')
            else:
                var_sql_extraction_origin = load_file(file_name='sources/arc_bgd/arc_job_subid_var_datetime.sql')
                var_sql_extraction = var_sql_extraction_origin.replace('var_subids',metadata['subid']).replace('var_datetime',metadata['var_datetime'])  
                print(f'var_datetime: not black ={metadata["var_datetime"]}')
            with conn.cursor() as cur:
                try:
                    os.remove('workspace/var_sql_extraction.sql')
                    print('delete workspace/var_sql_extraction.sql')
                except Exception as e:
                    print(e)
                with open('workspace/var_sql_extraction.sql','w') as f:
                    f.write(var_sql_extraction)  
                cur.execute(var_sql_extraction)
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            print('df01_html')
            df01 = pd.read_sql_query('set nocount on; select * from ##final', conn)
            df01_html = df01.transpose().to_html(header=False)
            df01_html = f"<p>subid:{metadata['subid']}</p>"+df01_html
            with open('workspace/df01.html','w') as f:
                f.write(df01_html)
                print('save workspace/df01.html')
        ###
        ###
        print('query commonality table')
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            var_sql_extraction_02_origin = load_file(file_name='sources/arc_bgd/arc_job_ca.sql')
            var_sql_extraction_02 = var_sql_extraction_02_origin.replace('var_datetime',metadata["var_datetime"])
            with conn.cursor() as cur:
                try:
                    os.remove('workspace/var_sql_extraction_02.sql')
                    print('delete workspace/var_sql_extraction_02.sql')
                except Exception as e:
                    print(e)
                with open('workspace/var_sql_extraction_02.sql','w') as f:
                    f.write(var_sql_extraction_02)
                    print('save workspace/var_sql_extraction_02.sql')
                cur.execute(var_sql_extraction_02)
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            print('query edge seal')
            df02_es = pd.read_sql_query('set nocount on; select distinct * from ##es order by location', conn)
            df02_es_html = df02_es.to_html()
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            print('query laminator')
            #conn = pyodbc.connect(var_ods_connection, autocommit=True)
            df02_lam = pd.read_sql_query('set nocount on; select distinct * from ##lam order by location, position', conn)
            df02_lam_html = df02_lam.to_html()
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            print('query bsa')
            #conn = pyodbc.connect(var_ods_connection, autocommit=True)
            df02_bsa = pd.read_sql_query('set nocount on; select distinct * from ##bsa order by location', conn)
            df02_bsa_html = df02_bsa.to_html()
        ###
        df02_html = f"<p>datetime: {metadata['var_datetime']}</p>"+"<p>Edge Seal</p>" + df02_es_html + "<p>Laminator</p>" + df02_lam_html + "<p>BSA</p>" +  df02_bsa_html
        with open('workspace/df02.html','w') as f:
            f.write(df02_html)
            print('save workspace/df02.html')
        print('data_mining_ods_arc_bgd: end')
    except Exception as e:
        print(e)
    finally:
        print('data_mining_ods_arc_bgd: close crsr and conn\r\n')
    print('</data_mining_ods_arc_bgd>')  

def data_mining_ods_cdcl_bgd():  
    print('<data_mining_ods_cdcl_bgd>')  
    metadata = load_json_config('workspace/metadata.json')
    try:
        os.remove('workspace/df01.html')
        print('delete workspace/df01.html')
    except Exception as e:
        print(e)
    try:
        os.remove('workspace/df02.html')
        print('delete workspace/df02.html')
    except Exception as e:
        print(e)    
    df01_html='blank'
    df02_html='blank' 
    var_ods_connection_origin = load_file(file_name='sources/ods_connection_string.txt')
    var_ods_connection = var_ods_connection_origin.replace('var_site_plant',metadata["plant"][0:4])
    with open(f'workspace/ods_connection_string.txt','w') as f:
        f.write(var_ods_connection)    
    print(f'Connect to ods: {var_ods_connection}')    
    try:
        print('quering data')      
        print('query subid_table')    
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            if(metadata["var_datetime"]==''):
                var_sql_extraction_origin = load_file(file_name='sources/cdcl_bgd/cdcl_job_subid.sql')
                var_sql_extraction = var_sql_extraction_origin.replace('var_subids',metadata["subid"])
                print('var_datetime blank')
            else:
                var_sql_extraction_origin = load_file(file_name='sources/cdcl_bgd/cdcl_job_subid_var_datetime.sql')
                var_sql_extraction = var_sql_extraction_origin.replace('var_subids',metadata["subid"])\
                                                            .replace('var_datetime',metadata["var_datetime"])
                print(f'var_datetime: not black ={metadata["var_datetime"]}')
            with conn.cursor() as cur:
                try:
                    os.remove('workspace/var_sql_extraction.sql')
                    print('delete workspace/var_sql_extraction.sql')
                except Exception as e:
                    print(e)
                with open('workspace/var_sql_extraction.sql','w') as f:
                    f.write(var_sql_extraction)
                    print('save workspace/var_sql_extraction.sql')
                cur.execute(var_sql_extraction)
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            print('df01_html')
            df01 = pd.read_sql_query('set nocount on; select * from ##final', conn)
            df01_html = df01.transpose().to_html(header=False)
            df01_html = f"<p>subid:{metadata['subid']}</p>"+df01_html
            with open('workspace/df01.html','w') as f:
                f.write(df01_html)
                print('save workspace/df01.html')
        print('query commonality table')
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            var_sql_extraction_02_origin = load_file(file_name='sources/cdcl_bgd/cdcl_job_ca.sql')
            var_sql_extraction_02 = var_sql_extraction_02_origin.replace('var_datetime',metadata["var_datetime"])
            with conn.cursor() as cur:
                try:
                    os.remove('workspace/var_sql_extraction_02.sql')
                    print('delete workspace/var_sql_extraction_02.sql')
                except Exception as e:
                    print(e)
                with open('workspace/var_sql_extraction_02.sql','w') as f:
                    f.write(var_sql_extraction_02)
                    print('save workspace/var_sql_extraction_02.sql')
                cur.execute(var_sql_extraction_02)
        with pyodbc.connect(var_ods_connection, autocommit=True) as conn:
            print('query VTD_COATER')
            #conn = pyodbc.connect(var_ods_connection, autocommit=True)
            df02_es = pd.read_sql_query('set nocount on; select distinct * from ##VTD_COATER order by location', conn)
            df02_es_html = f"<p>datetime: {metadata['var_datetime']}</p>"+"<p>CA VDT COATER</p>" + df02_es.to_html()
            df02_html =  df02_es_html
            with open('workspace/df02.html','w') as f:
                f.write(df02_html)
                print('save workspace/df02.html')
        print('data_mining_ods_cdcl_bgd: end')
    except Exception as e:
        print(e)
    finally:
        print('data_mining_ods_cdcl_bgd: close crsr and conn\r\n')     
    print('</data_mining_ods_cdcl_bgd>')  

def fpi_extracting(fpi_src_abspath):
    print('<fpi_extracting>')
    #fpi_string = r'//FS.LOCAL/FSGlobal/Global/Shared/Manufacturing/PGT2/PGT2_DrSchwab/CdCl_B_Bad_Results/PGT21B_0_210707730231_2021-07-29_22-58-12.FPI'
    #fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT2\PGT2_DrSchwab\ARC_U1_Bad_Results\PGT2_ARC_A_0_210725770433_2021-07-29-12-31-50.FPI'
    #fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT1\PGT1_DrSchwab\Cover_Glass_Bad_Results\2021\07\29\ID_2021-07-29_20-13-49.FPI'
    #fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT1\PGT1_DrSchwab\PGT12_CdCl_Bad_Results\PGT21A_0_P12CV02A20102000004_2020-10-20_09-05-51.FPI'

    fpi_string = os.path.normpath(fpi_src_abspath.lower())

    #### find subid
    subid=''
    subid_type=''
    ## group 01: c12
    pattern01    = re.search('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',fpi_string)
    ## group 02: c11
    pattern01_02 = re.search("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]",fpi_string)
    ## group 03: virtual subid
    pattern03 = re.search('[a-zA-Z][0-9][0-9][a-zA-Z][a-zA-Z][0-9][0-9]',fpi_string)
    if pattern03 != None:
        startid=pattern03.start()
        endid = startid+19
        subid = fpi_string[startid:endid]
        subid_type='virtual_subid'
    elif pattern01 != None:
        startid=pattern01.start()
        endid = startid+12
        subid = fpi_string[startid:endid]
        subid_type='valid_subid_c12'
    elif pattern01_02 != None:
        startid=pattern01_02.start()
        endid = startid+11
        subid = fpi_string[startid:endid]
        subid_type='valid_subid_c11'


    ##### file Alarm ID
    alarm_id = ''
    if (r'drschwab\cdcl' in fpi_string or r'drschwab\pgt12_cdcl' in fpi_string):
        alarm_id = 'CdCl'
    elif r'drschwab\arc' in fpi_string:
        alarm_id = 'ARC'
    elif r'drschwab\cover_glass' in fpi_string:
        alarm_id = 'CoverGlass'


    ##### find plant name
    plant = ''
    if  (r"dmt1\dmt1_drschwab" in fpi_string.lower()):
        plant="DMT1"
    elif(r"dmt2\dmt2_drschwab" in fpi_string.lower()):
        plant="DMT2"
    elif(r"kmt1\kmt1_drschwab" in fpi_string.lower()):
        plant="KMT1"   
    elif(r"kmt2\kmt2_drschwab" in fpi_string.lower()):
        plant="KMT2"    
    elif(r"pgt1\pgt1_drschwab" in fpi_string.lower()):
        if(r"pgt1\pgt1_drschwab\pgt12" in fpi_string.lower()):
            plant="PGT12"  
        else:
            plant="PGT1"          
    elif(r"pgt2\pgt2_drschwab" in fpi_string.lower()):
        plant="PGT2" 
    
        
    #### find dummy mode
    dummy_mode = False
    if('__dummy__' in fpi_string):
        dummy_mode=True
        
    ##### get size
    temp_constant_MB = 1048576
    try:
        size_file = os.path.getsize(fpi_string)
        size_file_MB = round(size_file/temp_constant_MB)
    except Exception as e:
        size_file_MB=None
        print(e)

    ## fpi_dest_abspath
    fpi_bad_image_folders = load_json_config(r'sources/dest_bad_image_folders.json')
    if(dummy_mode==False):
        fpi_bad_image_folder=os.path.normpath(fpi_bad_image_folders[alarm_id][plant]['fpi'])
        png_bad_image_folder = os.path.normpath(fpi_bad_image_folders[alarm_id][plant]['image'])
    else:
        fpi_bad_image_folder=os.path.normpath(fpi_bad_image_folders[alarm_id][plant]['dummy_fpi'])
        png_bad_image_folder = os.path.normpath(fpi_bad_image_folders[alarm_id][plant]['dummy_image'])
    
        ## mkdir: make sure folder exist
        try:
            os.makedirs(fpi_bad_image_folder)
            print(f"makedirs fpi_bad_image_folder: {fpi_bad_image_folder}")
        except Exception as e:
            print(f"makedirs existed fpi_bad_image_folder: {fpi_bad_image_folder}")
            print(e)

        try:
            os.makedirs(png_bad_image_folder)
            print(f"makedirs png_bad_image_folder: {png_bad_image_folder}")
        except Exception as e:
            print(f"makedirs existed png_bad_image_folder: {png_bad_image_folder}")
            print(e)

    fpi_src_path_head,fpi_src_abspath_tail = os.path.split(fpi_src_abspath)
    fpi_dest_file_abspath = os.path.join(fpi_bad_image_folder,fpi_src_abspath_tail)
    png_dest_file_abspath = os.path.join(png_bad_image_folder,f'{fpi_src_abspath_tail[0:4]}.png')
    png_dest_file_abspath_screenshoot = os.path.join(png_bad_image_folder,f'{fpi_src_abspath_tail[0:4]}_screenshoot.png')                                     
    png_dest_file_abspath_01_00 = os.path.join(png_bad_image_folder,f'{fpi_src_abspath_tail[0:4]}_01_00.png')
    png_dest_file_abspath_02_00 = os.path.join(png_bad_image_folder,f'{fpi_src_abspath_tail[0:4]}_02_00.png')  
    
  
    ##### datetime
    var_datetime = ''
    var_datetime_type = ''
    # 2021-08-02-15-53-13
    pattern_datetime_01    = re.search('[2][0][2][0-9][-][0-1][0-9][-][0-3][0-9][-][0-2][0-9][-][0-5][0-9][-][0-5][0-9]',fpi_src_abspath)
    pattern_datetime_02    = re.search('[2][0][2][0-9][-][0-1][0-9][-][0-3][0-9][_][0-2][0-9][-][0-5][0-9][-][0-5][0-9]',fpi_src_abspath)
        
    if pattern_datetime_01 != None:
        startid_time      = pattern_datetime_01.start()
        endid_datetime    = startid_time+19
        var_datetime      = fpi_src_abspath[startid_time:endid_datetime]
        var_datetime      = var_datetime[0:10]+' '+var_datetime[11:13]+':'+var_datetime[14:16]+':'+var_datetime[17:]
        var_datetime_type = 'type-'
    elif pattern_datetime_02 != None:
        startid_time    = pattern_datetime_02.start()
        endid_datetime    = startid_time+19
        var_datetime      = fpi_src_abspath[startid_time:endid_datetime]
        var_datetime      = var_datetime[0:10]+' '+var_datetime[11:13]+':'+var_datetime[14:16]+':'+var_datetime[17:]
        var_datetime_type = 'type_'

    var_equipment = os.path.split(os.path.split(os.path.normpath(fpi_src_abspath))[0])[1]

    metadata = {
        "fpi_src_abspath":fpi_src_abspath,
        "alarm_id":alarm_id,
        "plant":plant,
        "subid":subid,
        "subid_type":subid_type,
        "size_file_MB":size_file_MB,
        "fpi_dest_file_abspath":fpi_dest_file_abspath,
        "png_dest_file_abspath":png_dest_file_abspath,
        "png_dest_file_abspath_screenshoot":png_dest_file_abspath_screenshoot,
        "png_dest_file_abspath_01_00":png_dest_file_abspath_01_00,
        "png_dest_file_abspath_02_00":png_dest_file_abspath_02_00,
        "dummy_mode":dummy_mode,
        "var_datetime":var_datetime,
        "var_datetime_type":var_datetime_type,
        "var_equipment":var_equipment
    }
    
    metadata_json=json.dumps(metadata)
    with open('workspace/metadata.json','w') as f:
        f.write(metadata_json)
        print('save workspace/metadata.json')
    print('</fpi_extracting>')    
    ## return
    return metadata 

'''
if __name__=="__main__":
    alarm_id='cdcl'
    plant='dmt1'
    subid='210730653904'
    var_datetime='2021-07-30 23:53:02'

    df01_html, df02_html = data_mining_ods(alarm_id,plant,subid,var_datetime)
'''