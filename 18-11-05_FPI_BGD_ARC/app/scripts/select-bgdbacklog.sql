/****** Script for SelectTopNRows command from SSMS  ******/
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