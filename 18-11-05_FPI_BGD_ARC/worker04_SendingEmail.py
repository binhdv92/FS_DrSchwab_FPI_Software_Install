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
    while True:
        workers = Workers(configs.SqlExtractSelector.getSqlExtractSendingEmail())
        workers.SendingEmail()