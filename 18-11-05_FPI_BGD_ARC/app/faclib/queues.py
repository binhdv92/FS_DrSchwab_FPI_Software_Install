import datetime, os, re, pyodbc
from app.configs.configs import Configs, Backlogs

configs = Configs()

def FpiExtracting(FpiSourcePath):
    # print('<fpi_extracting>')
    #fpi_string = r'//FS.LOCAL/FSGlobal/Global/Shared/Manufacturing/PGT2/PGT2_DrSchwab/CdCl_B_Bad_Results/PGT21B_0_210707730231_2021-07-29_22-58-12.FPI'
    #fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT2\PGT2_DrSchwab\ARC_U1_Bad_Results\PGT2_ARC_A_0_210725770433_2021-07-29-12-31-50.FPI'
    #fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT1\PGT1_DrSchwab\Cover_Glass_Bad_Results\2021\07\29\ID_2021-07-29_20-13-49.FPI'
    #fpi_string = r'\\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT1\PGT1_DrSchwab\PGT12_CdCl_Bad_Results\PGT21A_0_P12CV02A20102000004_2020-10-20_09-05-51.FPI'

    fpi_string = os.path.normpath(FpiSourcePath.lower())

    #### find subid
    ExtractSubId=''
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
        ExtractSubId = fpi_string[startid:endid]
        subid_type='virtual_subid'
    elif pattern01 != None:
        startid=pattern01.start()
        endid = startid+12
        ExtractSubId = fpi_string[startid:endid]
        subid_type='valid_subid_c12'
    elif pattern01_02 != None:
        startid=pattern01_02.start()
        endid = startid+11
        ExtractSubId = fpi_string[startid:endid]
        subid_type='valid_subid_c11'


    ##### file Alarm ID
    # 03Feb2023: \\FS.LOCAL\FSGlobal\Global\Shared\Manufacturing\PGT3\PGT3_DrSchwab\CoverGlass_B_Bad_Results\FS_BGD_PGT3_CVR_B_1_2023-02-02-11-42-46.FPIH
    ExtractAlarmName = ''
    if (r'drschwab\cdcl' in fpi_string or r'drschwab\pgt12_cdcl' in fpi_string):
        ExtractAlarmName = 'CdCl'
    elif r'drschwab\arc' in fpi_string:
        ExtractAlarmName = 'ARC'
    elif r'drschwab\cover_glass' in fpi_string:
        ExtractAlarmName = 'CoverGlass'
    elif r'drschwab\coverglass' in fpi_string:
        ExtractAlarmName = 'CoverGlass'


    ##### find plant name
    ExtractSitePlant = ''
    if  (r"dmt1\dmt1_drschwab" in fpi_string.lower()):
        ExtractSitePlant="DMT1"
    elif(r"dmt2\dmt2_drschwab" in fpi_string.lower()):
        ExtractSitePlant="DMT2"
    elif(r"kmt1\kmt1_drschwab" in fpi_string.lower()):
        ExtractSitePlant="KMT1"   
    elif(r"kmt2\kmt2_drschwab" in fpi_string.lower()):
        ExtractSitePlant="KMT2"    
    elif(r"pgt1\pgt1_drschwab" in fpi_string.lower()):
        if(r"pgt1\pgt1_drschwab\pgt12" in fpi_string.lower()):
            ExtractSitePlant="PGT12"  
        else:
            ExtractSitePlant="PGT1"          
    elif(r"pgt2\pgt2_drschwab" in fpi_string.lower()):
        ExtractSitePlant="PGT2" 
    elif(r"pgt3\pgt3_drschwab" in fpi_string.lower()):
        ExtractSitePlant="PGT3"
        
    #### find dummy mode
    ExtractIsDummyMode = False
    if('__dummy__' in fpi_string):
        ExtractIsDummyMode=True
        
    ##### get size
    temp_constant_MB = 1048576
    try:
        size_file = os.path.getsize(fpi_string)
        ExtractFpiSize = round(size_file/temp_constant_MB)
    except Exception as e:
        ExtractFpiSize = None
        print(e)

    ## fpi_dest_abspath
    # fpi_bad_image_folders = load_json_config(r'sources/dest_bad_image_folders.json')
    if(ExtractIsDummyMode==False):
        print(f'ExtractAlarmName = {ExtractAlarmName}')
        print(f'ExtractSitePlant = {ExtractSitePlant}')
        ResultRootPath_prefix=os.path.normpath(configs.destBadImageFolders.data[ExtractAlarmName][ExtractSitePlant]['image'])
         # png_bad_image_folder = os.path.normpath(configs.destBadImageFolders.data[ExtractAlarmName][ExtractSitePlant]['image'])
    else:
        ResultRootPath_prefix=os.path.normpath(configs.destBadImageFolders.data[ExtractAlarmName][ExtractSitePlant]['dummy_fpi'])
         # png_bad_image_folder = os.path.normpath(configs.destBadImageFolders.data[ExtractAlarmName][ExtractSitePlant]['dummy_image'])
    
    fpi_src_path_head,fpi_src_abspath_tail02 = os.path.split(FpiSourcePath)
    fpi_src_abspath_tail = fpi_src_abspath_tail02.lower().replace('.fpi','').replace('.fpih','')
    ResultRootPath          = os.path.join(ResultRootPath_prefix,fpi_src_abspath_tail)
    FpiDestPath             = fpi_src_abspath_tail
    ImagePath               = f'{fpi_src_abspath_tail}.png'
    TraceabilityPath        = f'{fpi_src_abspath_tail}_traceability.html'
    CommonalityAnalysisPath = f'{fpi_src_abspath_tail}_ca.html'
    ImagePathScreenShoot    = f'{fpi_src_abspath_tail}_screenshoot.png'                                   
    ImagePath01             = f'{fpi_src_abspath_tail}_01_00.png'

    ##### datetime
    ExtractTimeStamp = ''
    var_datetime_type = ''
    # 2021-08-02-15-53-13
    pattern_datetime_01    = re.search('[2][0][2][0-9][-][0-1][0-9][-][0-3][0-9][-][0-2][0-9][-][0-5][0-9][-][0-5][0-9]',FpiSourcePath)
    pattern_datetime_02    = re.search('[2][0][2][0-9][-][0-1][0-9][-][0-3][0-9][_][0-2][0-9][-][0-5][0-9][-][0-5][0-9]',FpiSourcePath)
    try:
        ExtractModifiedTimeUTC = datetime.datetime.utcfromtimestamp(os.path.getmtime(FpiSourcePath))
        print(f'ExtractModifiedTimeUTC -> 1')
    except:
        print(f'ExtractModifiedTimeUTC -> 2')
        ExtractModifiedTimeUTC = datetime.datetime(2000,1,1,1,1,1)
    if pattern_datetime_01 != None:
        startid_time      = pattern_datetime_01.start()
        endid_datetime    = startid_time+19
        ExtractTimeStamp      = FpiSourcePath[startid_time:endid_datetime]
        ExtractTimeStamp      = ExtractTimeStamp[0:10]+' '+ExtractTimeStamp[11:13]+':'+ExtractTimeStamp[14:16]+':'+ExtractTimeStamp[17:]
        var_datetime_type = 'type-'
    elif pattern_datetime_02 != None:
        startid_time    = pattern_datetime_02.start()
        endid_datetime    = startid_time+19
        ExtractTimeStamp      = FpiSourcePath[startid_time:endid_datetime]
        ExtractTimeStamp      = ExtractTimeStamp[0:10]+' '+ExtractTimeStamp[11:13]+':'+ExtractTimeStamp[14:16]+':'+ExtractTimeStamp[17:]
        var_datetime_type = 'type_'
    else:
        ExtractTimeStamp = datetime.datetime(2000,1,1,1,1,1)

    ExtractEquipment = os.path.split(os.path.split(os.path.normpath(FpiSourcePath))[0])[1]

    # class metadata():
    #     fpiSourcePath=fpi_src_abspath
    #     extractAlarmName=ExtractAlarmName
    #     extractSitePlant=ExtractSitePlant
    #     extractSubId=ExtractSubId
    #     extractSubidType=subid_type
    #     extractFpiSize=ExtractFpiSize
    #     fpiDestPath=fpi_dest_file_abspath
    #     imagePath = ImagePath
    #     #png_dest_file_abspath_screenshoot=png_dest_file_abspath_screenshoot
    #     #png_dest_file_abspath_01_00=png_dest_file_abspath_01_00
    #     #png_dest_file_abspath_02_00=png_dest_file_abspath_02_00
    #     extractIsDummyMode=ExtractIsDummyMode
    #     extractTimeStamp=ExtractTimeStamp
    #     extractTimeStampType=var_datetime_type
    #     extractEquipment=ExtractEquipment
    backlogs = Backlogs(
        #Paths
        FpiSourcePath               = FpiSourcePath
        ,ResultRootPath             = ResultRootPath
        #Extract        
        ,ExtractSubId               = ExtractSubId
        ,ExtractFpiSize             = ExtractFpiSize
        ,ExtractAlarmName           = ExtractAlarmName
        ,ExtractSitePlant           = ExtractSitePlant
        ,ExtractEquipment           = ExtractEquipment
        ,ExtractTimeStamp           = ExtractTimeStamp
        ,ExtractModifiedTimeUTC     = ExtractModifiedTimeUTC
        ,ExtractIsDummyMode         = ExtractIsDummyMode
        # #Flags      
        # SubIdCorrected              = None
        # ,FpiDestPath                = FpiDestPath
        # ,ImagePath                  = ImagePath
        # ,ImagePath01                = ImagePath01
        # ,ImagePathScreenShoot       = ImagePathScreenShoot
        # ,TraceabilityPath           = TraceabilityPath
        # ,CommonalityAnalysisPath    = CommonalityAnalysisPath  
        # FlagFpiDestPath             = None
        # FlagImagePath               =
        # FlagCAPath                  =
        # FlagTraceabilityPath        =
        # #Auto generate      
        # TimeStamp                   =
        # TimeStampUtc                =
        # ModifiedTimeStampUtc        =
    )
    return backlogs 

class Queues():
    def __init__(self):
        self.queueOnline=[]
        self.queueOffline = []
        self.previousID = ''
        self.counter = 0 # maximun = 9999
        self.id=''
    def insert_or_update_multi(self,fpiSourcesPath):
        for fpiSourcePath in fpiSourcesPath:
            self.insert_or_update(fpiSourcePath)

    def insert_or_update(self,fpiSourcePath:str):
        '''input fpiSourcePath is empty mean update'''
        metadata = FpiExtracting(fpiSourcePath)
        print(f'insert_or_update -> {metadata}')
        if(metadata.ExtractFpiSize >=5 and metadata.ExtractSitePlant !='' and \
            (metadata.ExtractAlarmName.lower()=='coverglass' or (metadata.ExtractAlarmName.lower() in ['arc','cdcl'])  and metadata.ExtractSubId!='')):
            try:
                with pyodbc.connect(configs.database, autocommit=True) as conn:
                    with conn.cursor() as cur:
                        sqlInsert = f'''
                        INSERT INTO FAC.dbo.BgdBacklog 
                            (
                                 [FpiSourcePath]
                                ,[ResultRootPath]
                                --,[FpiDestPath]
                                --,[ImagePath]
                                --,[ImagePath01]
                                --,[ImagePathScreenShoot]
                                --,[TraceabilityPath]        
                                --,[CommonalityAnalysisPath]

                                ,[ExtractSubId]
                                ,[ExtractFpiSize]
                                ,[ExtractAlarmName]
                                ,[ExtractSitePlant]
                                ,[ExtractEquipment]
                                ,[ExtractTimeStamp]
                                ,[ExtractModifiedTimeUTC]
                                ,[ExtractIsDummyMode]
                            )
                        VALUES 
                            (
                                 '{fpiSourcePath}'
                                ,'{metadata.ResultRootPath}'
                                -- ,'{metadata.FpiDestPath}'
                                -- ,'{metadata.ImagePath}'
                                -- ,'{metadata.ImagePath01}' 
                                -- ,'{metadata.ImagePathScreenShoot}'    
                                -- ,'{metadata.TraceabilityPath}'     
                                -- ,'{metadata.CommonalityAnalysisPath}'
         
                                ,'{metadata.ExtractSubId}'
                                ,'{metadata.ExtractFpiSize}'
                                ,'{metadata.ExtractAlarmName}'
                                ,'{metadata.ExtractSitePlant}'
                                ,'{metadata.ExtractEquipment}'
                                ,'{metadata.ExtractTimeStamp.strftime("%Y-%m-%d %H:%M:%S")}'
                                ,'{metadata.ExtractModifiedTimeUTC.strftime("%Y-%m-%d %H:%M:%S")}'
                                ,'{metadata.ExtractIsDummyMode}'
                            )
                        '''
                        cur.execute(sqlInsert)
                    conn.commit()   
                print('inserted')
            except Exception as e:
                print(f'failed to insert because {e}')
                print(f'{configs.database}')
                try:
                    with pyodbc.connect(configs.database, autocommit=True) as conn:
                        with conn.cursor() as cur:
                            sqlUpdate = f'''
                            Update FAC.dbo.BgdBacklog 
                            SET 
                                [ResultRootPath]            =   '{metadata.ResultRootPath}'
                                --,[FpiDestPath]              =   '{metadata.FpiDestPath}'
                                --,[ImagePath]                =   '{metadata.ImagePath}'
                                --,[ImagePath01]              =   '{metadata.ImagePath01}'
                                --,[ImagePathScreenShoot]     =   '{metadata.ImagePathScreenShoot}'
                                --,[TraceabilityPath]         =   '{metadata.TraceabilityPath}'    
                                --,[CommonalityAnalysisPath]  =   '{metadata.CommonalityAnalysisPath}'

                                ,[ExtractSubId]             =   '{metadata.ExtractSubId}'
                                ,[ExtractFpiSize]           =   '{metadata.ExtractFpiSize}'
                                ,[ExtractAlarmName]         =   '{metadata.ExtractAlarmName}'
                                ,[ExtractSitePlant]         =   '{metadata.ExtractSitePlant}'
                                ,[ExtractEquipment]         =   '{metadata.ExtractEquipment}'
                                ,[ExtractTimeStamp]         =   '{metadata.ExtractTimeStamp.strftime("%Y-%m-%d %H:%M:%S")}'
                                ,[ExtractModifiedTimeUTC]   =   '{metadata.ExtractModifiedTimeUTC.strftime("%Y-%m-%d %H:%M:%S")}'
                                ,[ExtractIsDummyMode]       =   '{metadata.ExtractIsDummyMode}'
                            where 
                                [FpiSourcePath]             =   '{fpiSourcePath}'
                            '''
                            cur.execute(sqlUpdate)
                        conn.commit()   
                    print('Queues:insert_or_update:Updated')
                except Exception as e:
                    print(e)
        else:
            print(f'Queues:insert_or_update:fail to insert because it not meet filter rules')
   
    # def append(self,value):
    #     # create queueID
    #     #self.createID()

    #     # record in queueOnline 
    #     # self.queueOnline.append(
    #     #     {
    #     #         "id":self.id,
    #     #         "value":value
    #     #     }
    #     # )

    #     # record in database
    #     bgdImage = BgdImage(fpiSourcePath=value)
    #     self.insertDatabase(bgdImage)

    # def pop(self):
    #     # remove at queueOnline
    #     self.queueOnline.pop(0) 

    #     # mark "Done" in database


    # def get(self):
    #     return self.queueOnline[0]
    
    
    # def createID(self):
    #     # get datetime
    #     today = datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S.%f')

    #     # compare datetime with previous value to avoid dupliate
    #     if(self.queueOnline):
    #         if(today == self.queueOnline[-1]["id"][0:26] ):
    #             self.counter += 1
    #         else:
    #             self.counter = 0 

    #     # combine into id       
    #     self.id = f'{today}_{self.counter.__str__().zfill(4)}'

