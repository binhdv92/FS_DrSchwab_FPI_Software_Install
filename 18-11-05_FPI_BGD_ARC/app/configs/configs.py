from __future__ import annotations
from datetime import datetime
from optparse import Option
from typing import Optional
import re, os
from xmlrpc.client import Boolean
from pydantic import BaseModel, Field
import json

class JsonConfigs():
    data:dict

    def __init__(self, path:str = r'app/defaults/des_bad_image_folders.json'):
        self.path = path
        self.load()

    def load(self):
        with open(self.path, 'r') as fileobj:
            s = fileobj.read()
            self.data = json.loads(s)

    def print(self):
        print(json.dumps(self.data, indent=4, sort_keys=True))


class DatConfigs():
    paths:list
    data:list

    def __init__(self, paths:list = [r'app/sources/fpi_sources.dat']):
        self.paths = paths
        self.load()

    def load(self):
        self.data = []
        for path in self.paths:
            with open(path,'r') as f:
                lines = f.readlines()
                for i,v in enumerate(lines):
                    v=v.strip()
                    temp =re.search('^#',v)
                    if(temp == None and v):
                        self.data.append(v)

    def print(self):
        for i in self.data:
            print(i)

def LoadFile(file_name:str):
    abs_file_name = os.path.abspath(file_name)
    # print(f"load_file('{abs_file_name}')")
    with open(abs_file_name, 'r') as fileobj:
        content_of_config_file = fileobj.read()
    return content_of_config_file

class SqlExtractSelector():
    full = '''
SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
FROM		[FAC].[dbo].[BgdBacklog]
where		id = (
                select      max(id) 
                from        [FAC].[dbo].[BgdBacklog] 
                where       SubIdCorrected is null 
                            and FlagFpiDestPath is null
                            and FlagImagePath is null
                            and FlagCAPath is null
                            and FlagTraceabilityPath is null
            )    
'''
    def __init__(self):
        self.FlagFpiDestPath         = self.getSqlExtract("FlagFpiDestPath")
        self.FlagImagePath           = self.getSqlExtractImage()
        self.FlagCAPath              = self.getSqlExtract("FlagCAPath")
        self.FlagTraceabilityPath    = self.getSqlExtractTraceability()
        self.FlagImagePathForce      = self.getSqlExtractImageForce()

    def getSqlExtract(self,key:str):
        return f'''
SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
FROM		[FAC].[dbo].[BgdBacklog]
where		id = (
            select  max(id) 
                from    [FAC].[dbo].[BgdBacklog] 
                where    {key} is null
            )   
'''
    def getSqlExtractImageForce(self):
        return f'''
SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
FROM		[FAC].[dbo].[BgdBacklog]
where       id = (
		        select Max(id) from [FAC].[dbo].[BgdBacklog] 
		        where FlagImagePath is not null and FlagImagePath not in (1))
'''
    def getSqlExtractImage(self):
        return f'''
SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
FROM		[FAC].[dbo].[BgdBacklog]
where		id = (
            select  max(id) 
                from    [FAC].[dbo].[BgdBacklog] 
                where       FlagImagePath is null
                            and FpiSourcePath is not null
            )   
'''
    def getSqlExtractTraceability(self):
        return '''
SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
FROM		[FAC].[dbo].[BgdBacklog]
where		id = (
            select  max(id) 
                from    [FAC].[dbo].[BgdBacklog] 
                where    ((FlagTraceabilityPath is null) or (SubIdCorrected is null))
            )        
'''
    def SelectByID(self,ID:int):
            return f'''
    SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
    FROM		[FAC].[dbo].[BgdBacklog]
    where		id = ({ID})   
    '''
    def getSqlExtractSendingEmail(self):
        return f'''
SELECT		 
            [ID]
            ,[FpiSourcePath]
            ,[ResultRootPath]
            ,[SubIdCorrected]
            ,[FlagFpiDestPath]
            ,[FlagImagePath]
            ,[FlagCAPath]
            ,[FlagTraceabilityPath]
            ,[ExtractSubId]
            ,[ExtractFpiSize]
            ,[ExtractAlarmName]
            ,[ExtractSitePlant]
            ,[ExtractEquipment]
            ,[ExtractTimeStamp]
            ,[ExtractModifiedTimeUTC]
            ,[ExtractIsDummyMode]
            ,[TimeStamp]
            ,[TimeStampUtc]
            ,[ModifiedTimeStampUtc]
            ,[FlagSendingEmail]
FROM		[FAC].[dbo].[BgdBacklog]
where		id = 
			(select  max(id) 
                from		[FAC].[dbo].[BgdBacklog] 
                where		FlagImagePath is not null 
							and FlagTraceabilityPath is not null 
							-- and FlagCAPath is not null
                            and FlagSendingEmail is null
                            -- AND ExtractSitePlant NOT IN ('PGT1') AND ExtractEquipment NOT IN ('ARC_Bad_Results')
            )		
'''

class Configs():
    
    class watchdog():
        patterns: list =['*.fpi','*.fpih']
        ignorePatterns=None
        ignoreDirectories =False
        caseSensitive = False
    version = "v2.0.0"
    fpiPatterns = ['*.fpi','*.fpih']
    #rootPath=r"C:\\Users\\fs126112\\OneDrive - First Solar\\repo\\azure_devops_firstsolar-meos\\GLOBAL_BGD_BREAKAGE_ALERTS\\18-11-05_FPI_BGD_ARC\\app"
    rootPath = r"C:\\repo\\GLOBAL_BGD_BREAKAGE_ALERTS\\18-11-05_FPI_BGD_ARC\\app"
    databaseODS = 'Driver={SQL Server};Server=var_site_plantMESSQLODS.FS.LOCAL;Database=ODS;Trusted_Connection=yes'
    #database = 'Driver={SQL Server};Server=localhost\sqlexpress;Database=FAC;Trusted_Connection=yes;'
    #database = 'Driver={SQL Server};Server=fs-36001\sqlexpress;Database=FAC;Trusted_Connection=yes;'
    database = 'Driver={ODBC Driver 17 for SQL Server};Server=fs-36001\sqlexpress;Database=FAC;UID=IntRi;PWD=IntRi;'
    #database = 'Driver={SQL Server};Server=fs-36001\sqlexpress;Database=FAC;UID=IntRi;PWD:IntRi;Trusted_Connection=yes;'
    fpiSourcesProdPath = [r'app/sources/fpi_sources.dat']
    fpiSourcesDummyPath = [r'app/sources/fpi_sources_dummy.dat']
    isProdMode=True
    flatDictDestBadImageFolders = list
    flatDictDestBadImageFolders_Dummy = list
    SendingEmailThresholdDelta = 30
    
    def __init__(self):
        self.fpiSources= DatConfigs(self.fpiSourcesProdPath + self.fpiSourcesDummyPath)

        self.destBadImageFolders = self.DestBadImageFolders()
        self.FlatDictDestBadImageFolders()
        self.FlatDictDestBadImageFolders_Dummy()
        self.MakeDirFlatDictDestBadImageFolders_Dummy()
        self.sql_arc_job_subid_corrected        = LoadFile('app/sources/arc_bgd/job_subid_corrected.sql')
        self.sql_arc_job_subid                  = LoadFile('app/sources/arc_bgd/arc_job_subid.sql')
        self.sql_arc_job_ca                     = LoadFile('app/sources/arc_bgd/arc_job_ca.sql') 
        self.sql_arc_job_traceability           = LoadFile('app/sources/arc_bgd/arc_job_subid_var_datetime.sql')

        self.sql_cdcl_job_subid_corrected       = LoadFile('app/sources/cdcl_bgd/job_subid_corrected.sql')
        self.sql_cdcl_job_subid                 = LoadFile('app/sources/cdcl_bgd/cdcl_job_subid.sql')
        self.sql_cdcl_job_ca                    = LoadFile('app/sources/cdcl_bgd/cdcl_job_ca.sql')    
        self.sql_cdcl_job_traceability          = LoadFile('app/sources/cdcl_bgd/cdcl_job_subid_var_datetime.sql')
        self.SqlExtractSelector                 = SqlExtractSelector()
    def fpiSourcesMakeDirs(self):
        print(f'configs.fpiSourcesMakeDirs -> {self.fpiSources.data:}')
        for fpi_source in self.fpiSources.data:
            if(not os.path.isdir(fpi_source)):
                try:
                    os.makedirs(fpi_source)
                except:
                    pass
    
    def DestBadImageFolders(self):
        temp = JsonConfigs(r'app/sources/dest_bad_image_folders.json')
        # print(temp.data)
        for i ,alarm in temp.data.items():
            for ii, plant in alarm.items():
                for iii,typex in plant.items():
                    # if(not os.path.isabs(temp.data[i][ii][iii])):
                    #     # if('dummy' in typex): 
                    #     temp.data[i][ii][iii] = os.path.normpath(os.path.join(os.getcwd(),temp.data[i][ii][iii]))
                    temp.data[i][ii][iii] = os.path.normpath(temp.data[i][ii][iii])
        return temp

    def MakeDirFlatDictDestBadImageFolders_Dummy(self,isPrint=False):
        for i in self.flatDictDestBadImageFolders_Dummy:
            try:
                os.makedirs(i)
                if(isPrint): print(f"makedirs : {i}")
            except Exception as e:
                if(isPrint): print(e)

    def MakeDirFlatDictDestBadImageFolders(self,isPrint=False):
        for i in self.flatDictDestBadImageFolders:
            try:
                os.makedirs(i)
                if(isPrint): print(f"makedirs : {i}")
            except Exception as e:
                if(isPrint): print(e)


    def loadDatConfig(self,fpiSourcesPath):
        # print('<loadDatConfig>')
        print(f'dat_file {fpiSourcesPath}')
        fpi_sources = []
        for fpiSourcePath in fpiSourcesPath:
            with open(fpiSourcePath,'r') as f:
                lines = f.readlines()
                for i,v in enumerate(lines):
                    v=v.strip()
                    temp =re.search('^#',v)
                    if(temp == None and v):
                        fpi_sources.append(v)
        # print('</loadDatConfig>')
        return fpi_sources
    
    def FlatDictDestBadImageFolders_Dummy(self):
       
        temp02 = []
        for _ ,alarm in self.destBadImageFolders.data.items():
            for _, plant in alarm.items():
                temp02.append(plant['dummy_fpi'])
                temp02.append(plant['dummy_image'])
                #temp02.append(plant['fpi'])
                #temp02.append(plant['image'])
        self.flatDictDestBadImageFolders_Dummy = temp02
        #return temp02
    def FlatDictDestBadImageFolders(self):
       
        temp02 = []
        for i ,alarm in self.destBadImageFolders.data.items():
            for ii , plant in alarm.items():
                #temp02.append(plant['dummy_fpi'])
                #temp02.append(plant['dummy_image'])
                temp02.append(plant['fpi'])
                temp02.append(plant['image'])
        self.flatDictDestBadImageFolders = temp02
        #return temp02
        
    def disableProdMode(self):
        print('Disable Production Mode')
        self.fpiSources=DatConfigs(self.fpiSourcesDummyPath)
        self.isProdMode=False

    def enableProdMode(self):
        print('Enabled Production Mode')
        self.fpiSources=DatConfigs(self.fpiSourcesProdPath+self.fpiSourcesDummyPath)
        self.isProdMode=True
    def FpiSourcesListDir(self):
        temp=[]
        for fpiSource in self.fpiSources.data:
            listDirs = os.listdir(fpiSource)
            for listDir in listDirs:
                if(listDir.lower().endswith(('.fpi','.fpih'))):
                    temp.append(os.path.normpath(os.path.join(fpiSource.lower(),listDir.lower())))
        return temp

        # fpiSources = [r'//FS.LOCAL/FSGlobal/Global/Shared/Manufacturing/DMT1/DMT1_DrSchwab/ARC_U1_Bad_Results']
# listDirs = os.listdir(fpiSources[0])
# for listDir in listDirs:
#     print(os.path.normpath(os.path.join(fpiSources[0],listDir)))
            
class BgdImage(BaseModel):
    fpiSourcePath:str
    fpiDestPath:Optional[str]
    imagePath: Optional[str]
    dtsTimeStamp: Optional[datetime]
    dtsEquipment: Optional[str]
    subId:Optional[str]
    subIdCorrected:Optional[str]

class Backlogs(BaseModel):        
    ID:                     Optional[int]
    #Paths
    FpiSourcePath:          Optional[str]
    ResultRootPath:         Optional[str]
    #Extract
    ExtractFpiSize:         Optional[int]
    ExtractAlarmName:       Optional[str]
    ExtractSitePlant:       Optional[str]
    ExtractEquipment:       Optional[str]
    ExtractTimeStamp:       Optional[datetime]
    ExtractModifiedTimeUTC: Optional[datetime]
    ExtractIsDummyMode:     Optional[bool]
    ExtractSubId:           Optional[str]
    #Flags
    SubIdCorrected:         Optional[str]
    FpiDestPath:            Optional[str]
    ImagePath:              Optional[str]
    ImagePath01:            Optional[str]
    ImagePathScreenShoot:   Optional[str]
    TraceabilityPath:       Optional[str]
    CommonalityAnalysisPath:Optional[str]

    FlagFpiDestPath:        Optional[int]
    FlagImagePath:          Optional[int]
    FlagCAPath:             Optional[int]
    FlagTraceabilityPath:   Optional[int]
    #Auto generate
    TimeStamp:              Optional[datetime]
    TimeStampUtc:           Optional[datetime]
    ModifiedTimeStampUtc:   Optional[datetime]

'''
    [ID] [int] NOT NULL,
	[FpiSourcePath] [varchar](Max) NOT NULL,
	[FpiDestPath] [varchar](Max),
	[ImagePath] [varchar](Max),
	[DtsTimeStamp] [datetime],
	[DtsEquipment] [varchar](50),
	[SubId] [varchar](20),
	[SubIdCorrected] [varchar](20)
    '''

