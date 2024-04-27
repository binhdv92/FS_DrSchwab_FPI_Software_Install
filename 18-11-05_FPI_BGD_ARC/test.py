# # import cv2
# import numpy as np
# from PIL import Image, ImageGrab

# # 200	80	200 busy
# # 

# class CommentSet():
#     PanelInspection             = [70, 18]
#     PanelInspectionFile         = [17, 47]
#     PanelInspectionPosDropFile  = [200, 200]
#     explorerPos                 = [1753, 12]
#     explorerPosSearch           = [1800, 75]
#     explorerPosPickFile         = [1900, 132]
#     statusWindowBox             = (116,42,212,68)
#     statusWindowBox2            = (130,50,135+100,55+100)
#     statusReady                 = (0,200,0)
#     statusBusy                  = (200,80, 200)
#     statusNone                  = (240, 240, 240)
# commentSet = CommentSet()
# def GetStatus(pix:list):
#     if (pix == [0,200,0]):
#         result = 'ready'
#     elif(pix == [200,80, 200] ):
#         result = 'Busy'
#     elif(pix == [240, 240, 240]):
#         result = 'None'
#     else:
#         result = 'unknown'
#     return result

# previous = ''
# result = ''
# while True:

#     imtemp= ImageGrab.grab(bbox=commentSet.statusWindowBox2)
#     im = np.array(imtemp)
#     pix = im[0][0][:].tolist()
#     result = GetStatus(pix)
    
#     if previous == result:
#         pass
#     else:

#         print(previous, result)
#         previous = result
        
    



# # template = cv2.imread(r'app/media/Busy.png',0)
# # template = cv2.resize(template,(100,100))
# # print(template.shape)
# # w, v = np.linalg.eig(template)
# # # printing eigen values
# # print("Printing the Eigen values of the given square array:\n", w)
# # # printing eigen vectors
# # print("Printing Right eigenvectors of the given square array:\n",v)



# # from PIL import Image, ImageGrab

# # import pytesseract
# '''
# imtemp= ImageGrab.grab(bbox=commentSet.statusWindowBox)
# # imtemp = imtemp.crop((0,0,300,100))
# im1 = np.array(imtemp)
# im1 = cv2.resize(im1,(100,100))
# w, v = np.linalg.eig(im1)
# # printing eigen values
# print("Printing the Eigen values of the given square array:\n", w)
# # printing eigen vectors
# print("Printing Right eigenvectors of the given square array:\n",v)
# '''

# # print(pytesseract.image_to_string(Image.open(r'app/media/Busy.png')))




# # res = cv2.matchTemplate(im1,template,cv2.TM_CCOEFF)
# # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
# # print(res)
# # print(min_val, max_val, min_loc, max_loc)

# # im = Image.open(r'app/media/ReadyFull.PNG')
# # im2 = im.crop(commentSet.statusWindowBox)
# # im2.save(r'app/media/Ready.png')
# # im2.show()

# # im = Image.open(r'app/media/NoneFull.PNG')
# # im2 = im.crop(commentSet.statusWindowBox)
# # im2.save(r'app/media/None.png')
# # im2.show()

# # im = Image.open(r'app/media/BusyFull.PNG')
# # im2 = im.crop(commentSet.statusWindowBox)
# # im2.save(r'app/media/Busy.png')
# # im2.show()

# import multiprocessing
from app.faclib.workers import Workers
from app.configs.configs import Configs

configs = Configs()


# def worker_CopyFpiFile(temp):
#     while True:
#         workerFlagFpiDestPath       = Workers(configs.SqlExtractSelector.FlagFpiDestPath)
#         workerFlagFpiDestPath.CopyBackupFile()
# def worker_FlagTraceabilityPath(temp):
#     while True:
#         workerFlagTraceabilityPath  = Workers(configs.SqlExtractSelector.FlagTraceabilityPath)
#         workerFlagTraceabilityPath.TraceabilitySubIdCorrected()

# def worker_FlagCAPath(temp):
#     while True:
#         workerFlagCAPath            = Workers(configs.SqlExtractSelector.FlagCAPath)
#         workerFlagCAPath.CommonalityAnalysis()

if __name__ == "__main__":
    #while True:
    workers = Workers(configs.SqlExtractSelector.FlagImagePath)
    print(workers.GetPixStatus())
    workers.leftClick(workers.commentSet.positionWindowBox)
    