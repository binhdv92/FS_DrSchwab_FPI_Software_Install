
from multiprocessing.connection import wait
from turtle import back, backward
from app.configs.configs import Configs, Backlogs
from PIL import Image
import pyodbc, time, os, psutil, subprocess, win32api, keyboard, win32con
import pandas as pd
from shutil import copyfile
import datetime
import PIL.ImageGrab as IG
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import smtplib
import json
# from my_util import util

configs = Configs()


class CommentSet():
    PanelInspection             = [70, 18]
    PanelInspectionFile         = [17, 47]
    PanelInspectionPosDropFile  = [200, 200]
    explorerPos                 = [1753, 12]
    explorerPosSearch           = [1800, 75]
    explorerPosPickFile         = [1900, 132]
    positionWindowBox           = [130,60]
    statusWindowBox             = (116,42,212,68)
    statusWindowBox2            = (130,60,135+100,55+100)
    statusReady                 = (0,200,0)
    statusBusy                  = (200,80, 200)
    statusNone                  = (240, 240, 240)


class Workers():
    commentSet = CommentSet()
    backlogs: Backlogs
    subIdCorrected:str

    def __init__(self, SqlExtractSelector:str):
        self.SqlExtractSelector = SqlExtractSelector
        self.load_init()
        
    def load_init(self):
        self.backlogs = self.load()
        print(f'load_init -> {self.backlogs.ID}, {self.backlogs.ExtractSubId}')
        if(self.backlogs.ID !=None):
            self.ExtractTimeStampStr                = self.backlogs.ExtractTimeStamp.strftime("%Y-%m-%d %H:%M:%S")
            self.backlogs.FpiDestPath               = f"{self.backlogs.ResultRootPath}.fpi"
            self.backlogs.ImagePath                 = f"{self.backlogs.ResultRootPath}.png"
            self.backlogs.ImagePath01               = f"{self.backlogs.ImagePath[0:-4]}_01_00.png"
            self.backlogs.ImagePathScreenShoot      = f"{self.backlogs.ImagePath[0:-4]}_screenshoot.png"
            self.backlogs.TraceabilityPath          = f"{self.backlogs.ImagePath[0:-4]}_traceability.html"
            self.backlogs.CommonalityAnalysisPath   = f"{self.backlogs.ImagePath[0:-4]}_ca.html"
            self.databaseODS                        = configs.databaseODS.replace('var_site_plant',self.backlogs.ExtractSitePlant[0:4])
        else:
            time.sleep(1)
            print('load_init -> There is no backlogs remaining')

    def load(self):
        # SqlExtract = configs.SqlExtractLoad(backlogSubid=backlogSubid)
        try:
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                    df01 = pd.read_sql_query(self.SqlExtractSelector,conn)
            if(df01.empty):
                backlogs = Backlogs()
            else:
                backlogs = Backlogs.parse_obj(df01.loc[0])
                #for index, row in df01.iterrows():
        except Exception as e:
            backlogs = Backlogs()
            print(f'load -> {e}')             
        return backlogs

#     def load_backlogSubid(self,backlogID ):
#         SqlExtract = f'''
#   SELECT		 [ID]
# 			,[FpiSourcePath]
# 			,[FpiDestPath]
# 			--,[ImagePath]
# 			,[ExtractSubId]
# 			,[ExtractFpiSize]
# 			,[ExtractSitePlant]
# 			,[ExtractAlarmName]
# 			,[ExtractEquipment]
# 			,[ExtractTimeStamp]
# 			,[ExtractIsDummyMode]
# 			,[SubIdCorrected]
# 			,[TimeStamp]
# 			,[TimeStampUtc]
# 			,[ModifiedTimeStampUtc]
#   FROM		[FAC].[dbo].[BgdBacklog]
#   where		id = (
#                 {backlogID}
#             )
# '''
#         with pyodbc.connect(configs.database, autocommit=True) as conn:
#             df01 = pd.read_sql_query(SqlExtract,conn)
#         # backlogs = Backlogs(ID = df01['ID'],FpiSourcePath = df01['FpiSourcePath'], FpiDestPath = df01['FpiDestPath'],
#         #     ImagePath = df01['ImagePath'], ExtractSubId = df01['ExtractSubId'], ExtractFpiSize = df01['ExtractFpiSize'], ExtractSitePlant=df01['ExtractSitePlant'],
#         #     ExtractAlarmName=df01['ExtractAlarmName'], ExtractEquipment = df01['ExtractEquipment'],
#         #     ExtractTimeStamp = df01['ExtractTimeStamp'], ExtractIsDummyMode=df01['ExtractIsDummyMode'], SubIdCorrected = df01['SubIdCorrected'], TimeStamp = ['TimeStamp'],
#         #     TimeStampUtc = df01['TimeStampUtc'], ModifiedTimeStampUtc=df01['ModifiedTimeStampUtc']  )
#             print(f'loaded backlog ID = {df01.loc[0].ID}')
#         return df01.loc[0]

    def UpdateDatabase(self):
        if(os.path.exists(self.backlogs.FpiDestPath)):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set FlagFpiDestPath = 1
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'success update to database {self.backlogs.FpiDestPath}')
        else:
            print(f'fail to Update to database because no exists {self.backlogs.FpiDestPath}')  
        ##   
        if(os.path.exists(self.backlogs.ImagePath)):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set FlagImagePath = 1
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'success update  to database {self.backlogs.ImagePath}')
        else:
            print(f'fail to Update to database because no exists {self.backlogs.ImagePath}')  
    def UpdateDatabase_FlagFpiDestPath(self,code:int):
        try:
            #if(os.path.exists(self.backlogs.TraceabilityPath)):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set FlagFpiDestPath = {code}
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'UpdateDatabase_FlagFpiDestPath -> success update to database {self.backlogs.FpiDestPath}')
            #else:
                #print(f'UpdateDatabase_FlagFpiDestPath -> fail to Update to database because no exists {self.backlogs.FpiDestPath}')     
        except Exception as e:
            print(f'UpdateDatabase_FlagFpiDestPath -> {e}')  
            
    def CopyBackupFile(self, max_attempt=30, sleep_time_attempt=2):
        print(f'CopyBackupFile from {self.backlogs.FpiSourcePath} --> {self.backlogs.FpiDestPath}')        
        flag_copy_current=1
        flag_copy_fpi = False
        if self.backlogs.ID != None:
            if not os.path.exists(self.backlogs.FpiDestPath):
                if os.path.exists(self.backlogs.FpiSourcePath):
                    while flag_copy_current<=max_attempt:
                        try:
                            copyfile(self.backlogs.FpiSourcePath,self.backlogs.FpiDestPath)
                            print(f"[CopyBackupFile][attemting {flag_copy_current}, done copying ] ")
                            flag_copy_current = max_attempt+1
                            flag_copy_fpi = True  
                            self.backlogs.FlagFpiDestPath = 1    
                            self.UpdateDatabase_FlagFpiDestPath()                  
                        except:
                            print(f"[CopyBackupFile][fail][attemting {flag_copy_current}/{max_attempt}, fail to copying, waiting {sleep_time_attempt}]")
                            flag_copy_current = flag_copy_current+1
                            time.sleep(sleep_time_attempt)
                else:
                    self.backlogs.FlagFpiDestPath = 0
                    print(f'do not existed {self.backlogs.FpiSourcePath}')
                    ## update FpiSourcePath mark as skipping this one
            else:
                print(f'existed {self.backlogs.FpiDestPath}')
                self.backlogs.FlagFpiDestPath = 1
            self.UpdateDatabase_FlagFpiDestPath()
                ## update FlagFpiDestPath
        else:
            print('backlogs is empty')
    
    def UpdateDatabase_ImagePath(self,FlagImagePath:int):   
        with pyodbc.connect(configs.database, autocommit=True) as conn:
            with conn.cursor() as cur:
                SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set FlagImagePath = {FlagImagePath}
where id = {self.backlogs.ID}
'''
                cur.execute(SqlUpdate)
            conn.commit()
        print(f'UpdateDatabase_ImagePath -> success update to database {self.backlogs.FpiDestPath}')
             
      
     
    def UpdateDatabase_CAPath(self):
        try:
            #if(os.path.exists(self.backlogs.CommonalityAnalysisPath)):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set FlagCAPath = {self.backlogs.FlagCAPath}
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'UpdateDatabase_CAPath -> success update to database {self.backlogs.CommonalityAnalysisPath}')
            #else:
            #    print(f'UpdateDatabase_CAPath -> fail to Update to database because no exists {self.backlogs.CommonalityAnalysisPath}')     
        except Exception as e:
            print(f'UpdateDatabase_CAPath -> {e}')    
    def UpdateDatabase_SendingEmail(self,SendingEmailCode):
        try:
            #if(os.path.exists(self.backlogs.CommonalityAnalysisPath)):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set [FlagSendingEmail] = {SendingEmailCode}
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'UpdateDatabase_CAPath -> success update to database {self.backlogs.CommonalityAnalysisPath}')
            #else:
            #    print(f'UpdateDatabase_CAPath -> fail to Update to database because no exists {self.backlogs.CommonalityAnalysisPath}')     
        except Exception as e:
            print(f'UpdateDatabase_CAPath -> {e}')  
    def ExtractImage(self,force = True):
        if(self.backlogs.ID !=None):
            if (force or not os.path.exists(self.backlogs.ImagePath)):
                print(f'ExtractImage -> force = True')
                if(os.path.exists(self.backlogs.FpiSourcePath)):
                    print(f'ExtractImage -> {self.backlogs.FpiSourcePath}')
                    self.Check_PanelInspection()
                    self.Close_PanelInspection()
                    flagOpen = self.open_fpi()
                    if(flagOpen):
                        time.sleep(2)
                        self.saveScreenShoot()
                        time.sleep(1)
                        self.saveImageToPNG()
                        time.sleep(1)
                        self.press_and_releaseX('Enter', 10, 0.1)
                        time.sleep(1)
                        self.press_and_releaseX('Enter', 10, 0.1)
                        time.sleep(1)
                        self.press_and_releaseX('Enter', 10, 0.1)
                        if(os.path.exists(self.backlogs.ImagePath01)):
                            self.ConcatImage()
                            self.UpdateDatabase_ImagePath(1)
                            print('OpenFPI successful')
                        else:
                            self.UpdateDatabase_ImagePath(3)
                            print('OpenFPI Fail')
                    else:
                        self.UpdateDatabase_ImagePath(2)
                        print('OpenFPI fail to open FPI')

                else:
                    print(f'ExtractImage -> do not exists {self.backlogs.FpiSourcePath}')
                    self.UpdateDatabase_ImagePath(2)
            else:
                print(f'ExtractImage -> force = False or  exists image files')
                if(os.path.exists(self.backlogs.ImagePath)):
                    print(f'Exists {self.backlogs.ImagePath}, let UpdateDatabase_ImagePath()')
                    self.UpdateDatabase_ImagePath(1)
        else:
            print(f'ExtractImage -> backlogs.ID = {self.backlogs.ID}')
            '''
            null:not extract
            1: success
            2:self.backlogs.ImagePath exists
            3:self.backlogs.FpiSourcePath do not exist
            
            
            '''

    def open_fpi(self,waitTimeMiniStep = 0.1,waitTimeEachStep = 1):
        flag=False
        if(os.path.exists(self.backlogs.FpiSourcePath)):
            print('<open_fpi>')
            ### Step01 clear PanelInspection
            print('openFPI step01 clear PanelInspection before loading fpi file')
            self.leftClick(self.commentSet.PanelInspection)

            time.sleep(waitTimeMiniStep)
            self.press_and_releaseX('Enter', 10, 0.1)
            time.sleep(waitTimeMiniStep)
            self.press_and_releaseX('ESC', 10, 0.1)
            time.sleep(waitTimeEachStep)

            # Step01: load fpi file
            print('openFPI step02 load fpi file')
            self.leftClick(self.commentSet.PanelInspection)
            self.press_and_releaseX('Enter', x=10, delay=0.1)
            time.sleep(waitTimeMiniStep)
            keyboard.press_and_release('alt')
            time.sleep(waitTimeMiniStep)
            keyboard.press_and_release('f')
            time.sleep(waitTimeMiniStep)
            keyboard.press_and_release('l')
            time.sleep(waitTimeMiniStep)
            time.sleep(2)
            keyboard.write(self.backlogs.FpiSourcePath)
            time.sleep(3)
            time.sleep(waitTimeMiniStep)
            keyboard.press_and_release('Enter')
            time.sleep(waitTimeMiniStep)
            
            time.sleep(waitTimeEachStep)
            self.press_and_releaseX('Enter', 10, 0.1)
            
            self.press_and_releaseX('Enter', 10, 0.1)
            time.sleep(waitTimeMiniStep)
            
            self.press_and_releaseX('Enter', 10, 0.1)
            time.sleep(waitTimeMiniStep)
            
            self.press_and_releaseX('Enter', 10, 0.1)
            time.sleep(waitTimeMiniStep)
            
            self.press_and_releaseX('Enter', 10, 0.1)
            time.sleep(waitTimeMiniStep)

            self.press_and_releaseX('ESC', 10, 0.1)
            time.sleep(waitTimeMiniStep)
            print('openFPI OK open fpi sucessfull')
            print('</open_fpi>')
            flag=True
        else:
            print('openFPI fail to open fpi because no exist file fpi')
            flag=False
        return flag

    def find_windows_exists(self, name = 'PanelInspection'):
        # print('<find_windows_exists>')
        pid=''
        for i in psutil.process_iter():
            if('PanelInspection' in i.name()):
                flag=True
                pid=i.pid
        print(f'pid={pid}')
        #print('</find_windows_exists>')
        return pid

    def Check_PanelInspection(self):
        #print('<Check_PanelInspection>')
        ## find PanelInspection
        pid = self.find_windows_exists()
        if pid != '':
            print('PanelInspection is opening')
        else:
            print("PanelInspection is not opening, let's open it")
            time.sleep(1)
            app = subprocess.Popen('PanelInspection.exe')
            print('wait 4 seconds')
            time.sleep(4)
            self.leftClick(self.commentSet.PanelInspection)
            self.press_and_releaseX('Enter', x=20, delay=0.2)
            
            # setting_app()
            pid = self.find_windows_exists()
            print(f'pid = {pid}')
        print('</Check_PanelInspection>')
    def Exit_PanelInspection(self, delay = 0.2):
        self.leftClick(self.commentSet.PanelInspection)
        self.press_and_releaseX('Enter', x=10, delay=delay)
        pid = self.find_windows_exists()
        if(pid):
            p = psutil.Process(pid)
            p.terminate()
        else:
            print('do not exit pid PanelInspection')

    def Close_PanelInspection(self, repeat = 10, delay = 0.2, waitTimeMiniStep = 0.2):
        # print('<Close_PanelInspection>')
        ## find PanelInspection

        self.leftClick(self.commentSet.PanelInspection)
        self.press_and_releaseX('Enter', x=10, delay=delay)
        
        keyboard.press_and_release('Alt')
        time.sleep(waitTimeMiniStep)
        keyboard.press_and_release('f')
        time.sleep(waitTimeMiniStep)
        keyboard.press_and_release('c')
        time.sleep(waitTimeMiniStep)
        self.press_and_releaseX('Enter', x=repeat, delay=0.2)
        print('</Close_PanelInspection>')

    def saveScreenShoot(self, waitTimeMiniStep = 0.1,waitTimeEachStep = 1):
        flag_saveScreenShoot = False
        img = IG.grab()
        try:
            #img.save(metadata['png_dest_file_abspath_screenshoot'])
            img.save(self.backlogs.ImagePathScreenShoot)
            print(f"[saveScreenShoot][ok][saved {self.backlogs.ImagePathScreenShoot}")
            flag_saveScreenShoot = True
        except:
            print(f"[saveScreenShoot][ok][fail to save {self.backlogs.ImagePathScreenShoot}")
        time.sleep(waitTimeEachStep)
    def ScreenKeeper(self):
        keyboard.press_and_release('f5')
        print(f'ScreenKeeper @ {datetime.datetime.now()}')
    def saveImageToPNG(self, waitTimeMiniStep = 0.2,waitTimeEachStep = 1):
        print('<saveImageToPNG>')
        flag_saveImageToPNG = False

        try:
            self.leftClick(self.commentSet.PanelInspection)
            time.sleep(waitTimeMiniStep)
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
            time.sleep(2)
        
            print(f"save to PNG: {self.backlogs.ImagePath}")
            #keyboard.write(metadata['png_dest_file_abspath'])
            keyboard.write(self.backlogs.ImagePath)
            time.sleep(3)
            keyboard.press_and_release('Enter')
            time.sleep(waitTimeMiniStep)
        
            time.sleep(waitTimeEachStep)
            print(f"[saveImageToPNG][OK][save][{self.backlogs.ImagePath}]")
            
            flag_saveImageToPNG = True
        except:
            print(f"[saveImageToPNG][fail][save][{self.backlogs.ImagePath}]")

        # clear PanelInspection
        # leftClick(commandSet['PanelInspection']);time.sleep(sleeptime)
        # press_and_releaseX('ESC',10,0.1);

        time.sleep(waitTimeEachStep)
    
    def ConcatImage(self):
        print('concat')
        print(self.backlogs.ImagePathScreenShoot)
        print(self.backlogs.ImagePath01)
        if(os.path.exists(self.backlogs.ImagePathScreenShoot) and os.path.exists(self.backlogs.ImagePath01)):
            print('ConcatImage')
            ### get_concat_v_blank
            try:
                if(self.backlogs.ExtractSitePlant == 'CdCl'):
                    #self.get_concat_v_blank() old version 
                    self.get_concat_h_blank()
                else:
                    self.get_concat_h_blank()
                print('get_concat_h_blank: OK')
            except Exception as e:
                print(e)
        else:
            print('ConcatImage fail')
                
    def get_concat_v_blank(self, color=(0, 0, 0)):
        print('<get_concat_v_blank>')
        #metadata=load_json_config(r'workspace/metadata.json')
        im1=''
        im2=''
        try:
            im1 = Image.open( self.backlogs.ImagePath01)
            im1=im1.transpose(Image.ROTATE_90)
            im1_w,im1_h = im1.size
            im1=im1.resize((1920,1080))
            print('concat ImagePath01')
        except:
            print(f"not exists: {self.backlogs.ImagePath01}")
        try:
            im2 = Image.open( self.backlogs.ImagePathScreenShoot)
            print('concat png_dest_file_abspath_screenshoot')
        except:
            print(f"not exists: {self.backlogs.ImagePathScreenShoot}")
            
        if((im1!='') & (im2!='')):
            dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color)
            dst.paste(im1, (0, 0))
            dst.paste(im2, (0, im1.height))
            dst.save(self.backlogs.ImagePath)
        elif((im1!='') & (im2!='')):
            dst=im1
            dst.save(self.backlogs.ImagePath)
        elif((im1=='') & (im2!='')):
            dst=im2
            dst.save(self.backlogs.ImagePath)
        else:
            dst=''
        print('</get_concat_v_blank>')
        
    def get_concat_h_blank(self, color=(0, 0, 0)):
        print('<get_concat_h_blank>')
        #metadata=load_json_config(r'workspace/metadata.json')
        im1=''
        im2=''
        try:
            im1 = Image.open( self.backlogs.ImagePath01)
            im1_w,im1_h = im1.size
            im1=im1.resize((1080,1902))
            print('concat ImagePath01')
        except:
            print(f"not exists: {self.backlogs.ImagePath01}")
        try:
            im2 = Image.open( self.backlogs.ImagePathScreenShoot)
            print('concat ImagePathScreenShoot')
        except:
            print(f"not exists: {self.backlogs.ImagePathScreenShoot}")
            
        if((im1!='') & (im2!='')):
            dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
            dst.paste(im1, (0, 0))
            dst.paste(im2, (im1.width, 0))
            dst.save(self.backlogs.ImagePath)
        elif((im1!='') & (im2!='')):
            dst=im1
            dst.save(self.backlogs.ImagePath)
        elif((im1=='') & (im2!='')):
            dst=im2
            dst.save(self.backlogs.ImagePath)
        else:
            dst=''
        print('</get_concat_h_blank>')
    def leftClick(self, pos):
        ##print('<leftClick>')
        win32api.SetCursorPos(pos)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, pos[0], pos[1], 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, pos[0], pos[1], 0, 0)
        print('</leftClick>')

    def press_and_releaseX(self, key, x, delay):
        #print('<press_and_releaseX>')
        print(key)
        for i in range(x):
            keyboard.press_and_release(key)
            
            time.sleep(delay)
        print('</press_and_releaseX>')

    def SubIdCorrected(self):
        print(f'SubIdCorrectedLoadSql')
        if(self.backlogs.ExtractTimeStamp and self.backlogs.ExtractAlarmName.lower() not in ['arc','cdcl']):
                self.subIdCorrected = 'Fail: not input to corrected'
        else:
            if (self.backlogs.ExtractAlarmName.lower() =='arc'):
                self.job_subid = configs.sql_arc_job_subid_corrected
            elif (self.backlogs.ExtractAlarmName.lower() =='cdcl'):
                self.job_subid = configs.sql_cdcl_job_subid_corrected
            with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                with conn.cursor() as cur:
                    self.job_subid = self.job_subid.replace('var_subids',self.backlogs.ExtractSubId).replace('var_datetime',self.backlogs.ExtractTimeStamp.strftime("%Y-%m-%d %H:%M:%S"))
                    cur.execute(self.job_subid)
            with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                df01 = pd.read_sql_query('set nocount on; select * from ##subid_table', conn)
                # df01_html = df01.transpose().to_html(header=False)
            if(df01.empty):
                self.subIdCorrected = 'Fail: not found in database'
            else:
                self.subIdCorrected = df01.loc[0].Subid
        self.UpdateDatabase_Subid()

    def UpdateDatabase_Subid(self):
        try:
            #if(self.backlogs.SubIdCorrected):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set [SubIdCorrected] = '{self.backlogs.SubIdCorrected}'
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'UpdateDatabase_Subid -> success update to database SubIdCorrected {self.backlogs.SubIdCorrected}')
        # else:
            #     print(f'UpdateDatabase_Subid ->fail to Update to database SubIdCorrected because no exists {self.backlogs.SubIdCorrected}')     
        except Exception as e:
            print(f'UpdateDatabase_Subid -> {e}')

    def UpdateDatabase_FlagTraceabilityPath(self):
        try:
            #if(os.path.exists(self.backlogs.TraceabilityPath)):
            with pyodbc.connect(configs.database, autocommit=True) as conn:
                with conn.cursor() as cur:
                    SqlUpdate = f'''
Update fac.dbo.BgdBacklog
set FlagTraceabilityPath = {self.backlogs.FlagTraceabilityPath}
where id = {self.backlogs.ID}
    '''
                    cur.execute(SqlUpdate)
                conn.commit()
            print(f'UpdateDatabase_FlagTraceabilityPath -> success update to database {self.backlogs.FlagTraceabilityPath}')
            #else:
                #print(f'UpdateDatabase_FlagTraceabilityPath -> fail to Update to database because no exists {self.backlogs.TraceabilityPath}')     
        except Exception as e:
            print(f'UpdateDatabase_FlagTraceabilityPath -> {e}')  

    def TraceabilitySubIdCorrected(self):
        if(self.backlogs.ID !=None):
            # print(f'({self.backlogs}')
            if(self.backlogs.ExtractAlarmName.lower() in ['coverglass']):
                self.backlogs.SubIdCorrected = 'unavilable'
                self.backlogs.FlagTraceabilityPath = 0
            elif(self.backlogs.ExtractAlarmName.lower() in ['arc','cdcl']):
                if(not self.backlogs.ExtractTimeStamp):
                    if (self.backlogs.ExtractAlarmName.lower() =='arc'):
                        self.job_subid = configs.sql_arc_job_subid
                    elif (self.backlogs.ExtractAlarmName.lower() =='cdcl'):
                        self.job_subid = configs.sql_cdcl_job_subid
                else:
                    if (self.backlogs.ExtractAlarmName.lower() =='arc'):
                        self.job_subid = configs.sql_arc_job_subid
                    elif (self.backlogs.ExtractAlarmName.lower() =='cdcl'):
                        self.job_subid = configs.sql_cdcl_job_subid
                ## 
                self.job_subid = self.job_subid.replace('var_subids',self.backlogs.ExtractSubId).replace('var_datetime',self.ExtractTimeStampStr)
                
                # print(self.job_subid)
                with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                    with conn.cursor() as cur:
                        cur.execute(self.job_subid)
                with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                    df01 = pd.read_sql_query('set nocount on; select * from ##final', conn)
                    df01_html = df01.transpose().to_html(header=False)
                
                # save the result to database
                if(df01.empty):
                    self.backlogs.SubIdCorrected = 'unfound'
                    self.backlogs.FlagTraceabilityPath = 0
                else:
                    self.backlogs.SubIdCorrected = df01.loc[0].subid
                    self.backlogs.FlagTraceabilityPath = 1
                with open(self.backlogs.TraceabilityPath,'w') as f:
                    f.write(df01_html)      
            self.UpdateDatabase_Subid()
            self.UpdateDatabase_FlagTraceabilityPath()
            
    def CommonalityAnalysis(self):
        if(self.backlogs.ID !=None):
            if(self.backlogs.ExtractAlarmName.lower() in ['coverglass']):
                self.backlogs.FlagCAPath = 0
            elif(self.backlogs.ExtractAlarmName.lower() in ['arc','cdcl']):
                if(not os.path.exists(self.backlogs.CommonalityAnalysisPath)):
                    print(f'CommonalityAnalysis: backlogs.ID = {self.backlogs.ID}')
                    if(self.backlogs.ExtractTimeStamp):
                        if (self.backlogs.ExtractAlarmName.lower() == 'arc'):
                            print(f'debug:527.a')
                            self.job_ca = configs.sql_arc_job_ca
                            ##
                            if(self.ExtractTimeStampStr == '2000-01-01 01:01:01'):
                                pass
                            else:
                                self.job_ca = self.job_ca.replace('var_datetime',self.ExtractTimeStampStr)
                                with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                                    with conn.cursor() as cur:
                                        cur.execute(self.job_ca)
                                with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                                    print('query edge seal')
                                    df02_es = pd.read_sql_query('set nocount on; select distinct * from ##es order by location', conn)
                                    df02_es_html = df02_es.to_html()
                                    df02_lam = pd.read_sql_query('set nocount on; select distinct * from ##lam order by location, position', conn)
                                    df02_lam_html = df02_lam.to_html()
                                    df02_bsa = pd.read_sql_query('set nocount on; select distinct * from ##bsa order by location', conn)
                                    df02_bsa_html = df02_bsa.to_html()
                                df02_html = f"<p>datetime: {self.backlogs.ExtractTimeStamp}</p>"+"<p>Edge Seal</p>" + df02_es_html + "<p>Laminator</p>" + df02_lam_html + "<p>BSA</p>" +  df02_bsa_html
                        elif (self.backlogs.ExtractAlarmName.lower() == 'cdcl'):
                            print(f'debug:527.b')
                            self.job_ca = configs.sql_cdcl_job_ca
                            self.job_ca = self.job_ca.replace('var_datetime',self.ExtractTimeStampStr)
                            with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                                with conn.cursor() as cur:
                                    cur.execute(self.job_ca)
                            with pyodbc.connect(self.databaseODS, autocommit=True) as conn:
                                df02_es = pd.read_sql_query('set nocount on; select distinct * from ##VTD_COATER order by location', conn)
                                df02_es_html = f"<p>datetime: {self.backlogs.ExtractTimeStamp}</p>"+"<p>CA VDT COATER</p>" + df02_es.to_html()
                            df02_html =  df02_es_html           
                            ###
                        with open(self.backlogs.CommonalityAnalysisPath,'w') as f:
                            f.write(df02_html)
                            print(f'save to {self.backlogs.CommonalityAnalysisPath}')
                        print('data_mining_ods_arc_bgd: end')
                        self.backlogs.FlagCAPath = 1
                    else:
                        self.backlogs.FlagCAPath = 0
                        print(f'CommonalityAnalysis -> failed because ExtractTimeStamp = {self.backlogs.ExtractTimeStamp} and ExtractAlarmName = {self.backlogs.ExtractAlarmName}')
                else:
                    self.backlogs.FlagCAPath = 1
                    print(f'CommonalityAnalysis of backlogs.ID = {self.backlogs.ID} is existed on disk. ')
            else:
                self.backlogs.FlagCAPath = 0
            self.UpdateDatabase_CAPath()
        else:
            print(f'CommonalityAnalysis -> failed because {self.backlogs.ID}')
    def GetStatus(self, pix:list):
        if (pix == [0,200,0]):
            result = 'ready'
        elif(pix == [200,80, 200] ):
            result = 'busy'
        elif(pix == [240, 240, 240]):
            result = 'none'
        else:
            result = 'unknown'
        return result
    def GetPixStatus(self):
        imtemp= IG.grab(bbox=self.commentSet.statusWindowBox2)
        im = np.array(imtemp)
        pix = im[0][0][:].tolist()
        return pix
    def SendingEmail(self):
        threshold = datetime.timedelta(minutes=120)
        if(self.backlogs.ID !=None):
            tic = self.backlogs.ExtractModifiedTimeUTC.to_pydatetime()
            toc = datetime.datetime.utcnow()
            myDeltaTime = toc - tic
            print(f'datetime.datetime.utcnow({toc}) - ExtractModifiedTimeUTC({tic})')
            print('myDeltaTime', myDeltaTime)
            if(myDeltaTime <= threshold):
                print('<sending_bgd_email>')
                try:
                    #with open('workspace/df01.html','r') as f:
                    with open(f'{self.backlogs.ResultRootPath}_traceability.html','r') as f:
                        df01_html = f.read()
                except Exception as e:
                    df01_html = ''
                    print(e)
                
                try:
                    with open(f'{self.backlogs.ResultRootPath}_ca.html','r') as f:
                        df02_html = f.read()
                    print('open: workspace/df02.html')
                except Exception as e:
                    df02_html =''
                    print(e)
                    
                email_config = self.select_email_config_02(alarm_id= self.backlogs.ExtractAlarmName,plant=self.backlogs.ExtractSitePlant\
                    ,subid=self.backlogs.ExtractSubId,png_dest_file_abspath=self.backlogs.ImagePath,dummy_mode=self.backlogs.ExtractIsDummyMode)
                
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
                with open(r'app/sources/body_template_bgd.html','r') as f:
                    html_body = f.read()
                html_body = html_body.replace('var_subid_table',df01_html).replace('var_ca_table',df02_html)\
                    .replace('image1_footer',self.backlogs.ImagePath)\
                    .replace('fpi_src_abspath',self.backlogs.FpiSourcePath).replace('var_equipment',self.backlogs.ExtractEquipment)\
                    .replace('var_backlogs_id',str(self.backlogs.ID))\
                    .replace('__ExtractedSubId__',self.backlogs.ExtractSubId)
                msgAlternative.attach(MIMEText(html_body,'html'))
                
                ## save html_body
                # with open(r'workspace/body.html','w') as f:
                #     f.write(html_body)
                #     print('save workspaces/body.html')
                    
                ## embedded Image
                if (os.path.exists(self.backlogs.ImagePath)):
                    print('exists png_dest_file_abspath')
                    with open(self.backlogs.ImagePath, 'rb') as file:
                        email_image1 = MIMEImage(file.read())
                    email_image1.add_header('Content-ID', "image1")
                    msgRoot.attach(email_image1)
                print(f"[f_send_email_02]-> success embeded image {self.backlogs.ImagePath}: ")

                ## sending email {info,message}
                
                try:
                    with smtplib.SMTP('fsbridge.fs.local', '25') as server:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.sendmail(FROM, TO, msgRoot.as_string())                                             
                    print('</sending_bgd_email>')
                    self.UpdateDatabase_SendingEmail(1)
                except Exception as e:
                    self.UpdateDatabase_SendingEmail(-1)
                    print(e)
            else:
                print('do not send email due to over due:')
                self.UpdateDatabase_SendingEmail(2)
    def select_email_config_02(self, alarm_id='',plant='',subid='',simulation=True,png_dest_file_abspath='',dummy_mode=False):
        alarm_id =alarm_id.upper()
        plant =plant.upper()
        print('<select_email_config_02>')
        abs_file_name = os.path.abspath(r'app/sources/email_production.json')  
        
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
                            email_recipients = self.load_json_config(r'app/sources/arc_bgd/email_recipients.json')[plant]
                        elif(alarm_id == 'CDCL'):
                            email_recipients = self.load_json_config(r'app/sources/cdcl_bgd/email_recipients.json')[plant]
                        elif(alarm_id == 'COVERGLASS'):
                            email_recipients = self.load_json_config(r'app/sources/cover_glass_bgd/email_recipients.json')[plant]  
                    else:
                        s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[NoImage] ')
                        email_recipients = self.load_json_config(r'app/sources/email_recipients_admin.json')['fail']
                else:
                    if(alarm_id == 'COVERGLASS'):
                        s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','')
                        email_recipients = self.load_json_config(r'app/sources/cover_glass_bgd/email_recipients.json')[plant] 
                    else:
                        s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[NoSubid] ')
                        email_recipients = self.load_json_config(r'app/sources/email_recipients_admin.json')['fail']
            else:
                s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[DummyMode] ')
                email_recipients = self.load_json_config(r'app/sources/email_recipients_admin.json')['dummy_mode']   
        else:
            s=s.replace('var_site_plant',plant).replace('var_alarm_id',alarm_id).replace('var_mode_flag','[Simulation] ')
            email_recipients = self.load_json_config(r'app/sources/email_recipients_admin.json')['simulation']
        
        content_of_config_file = json.loads(s)
        email_config = content_of_config_file
        email_config['recipients']=email_recipients
        
        #dict_to_json(email_config,r'workspace/email_config.json')
        print('</select_email_config_02>')
        return email_config

    def load_json_config(self,file_name):
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