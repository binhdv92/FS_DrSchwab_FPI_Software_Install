SET NOCOUNT ON
--declare @subid varchar(20) = '230130601913'
declare @subid varchar(20) = 'var_subids'

IF OBJECT_ID('tempdb..#subid','U') IS NOT NULL BEGIN DROP TABLE  #subid END
select @subid as subid
into #subid

/* -----------------------*/
IF OBJECT_ID('tempdb..#ARC_BGD','U') IS NOT NULL BEGIN DROP TABLE #ARC_BGD END
select 

				MS.Subid
				,SR.Reason AS ScrapReason
				,MS.Operator AS Operator
				,MS.ModuleReturn
				,MS.comment
				,MS.ReadTime
				,GE.name as ARC_BGD_Equipment

INTO			#ARC_BGD
from			ModuleAssembly.History.Scrap_ModuleScrap AS MS
INNER JOIN		ods.mfg.ScrapReason AS SR
				ON MS.ScrapReasonId = SR.ReasonId
INNER JOIN		ods.mfg.GlobalProcess AS GP
				ON MS.ProcessId = GP.ProcessId
INNER JOIN		ods.mfg.GlobalEquipment AS GE
				ON MS.EquipmentId = GE.EquipmentId
INNER JOIN		ods.mfg.ScrapCategory AS SC
				ON MS.ScrapCategoryId = SC.CategoryId
INNER JOIN		ods.mfg.GlobalUnit AS GU
				ON MS.UnitId = GU.UnitId
INNER JOIN		ods.mfg.GlobalPlant AS GPL
				ON GU.PlantId = GPL.PlantId
INNER JOIN		ods.mfg.GlobalSite AS GS
				ON GPL.SiteId = GS.SiteId
WHERE
				ms.SubId = @subid

				-- AND GE.Name LIKE '%-ARC_POST_WASHER_BGD%'
				AND MS.HistoryAction IN ('U', 'I')
				-- AND ods.mfg.fn_Plant() = GPL.DisplayName
				AND ms.ModuleReturn =0

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_ARC_BGD','U') IS NOT NULL BEGIN DROP TABLE  #pp_ARC_BGD END
SELECT TOP 1 
				pp_ARC_BGD.id AS subid
				,pp_ARC_BGD.Location AS Edge_Seal_Location
				,pp_ARC_BGD.TimeStamp AS Edge_Seal_TimeStamp
INTO			#pp_ARC_BGD
FROM			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] AS pp_ARC_BGD 
WHERE			pp_ARC_BGD.ID = @subid
				AND pp_ARC_BGD.[Location] LIKE '%ARC_WASHER'
ORDER BY		pp_ARC_BGD.TimeStamp DESC

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_edge_seal','U') IS NOT NULL BEGIN DROP TABLE  #pp_edge_seal END
SELECT  TOP 1
				pp_edge_seal.id AS subid
				,pp_edge_seal.Location AS Edge_Seal_Location
				,pp_edge_seal.TimeStamp AS Edge_Seal_TimeStamp
INTO			#pp_edge_seal
FROM			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] AS pp_edge_seal 
WHERE			pp_edge_seal.ID = @subid
				AND pp_edge_seal.[Location] LIKE '%-EDGE_SEAL'
ORDER BY pp_edge_seal.TimeStamp DESC

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_laminator','U') IS NOT NULL BEGIN DROP TABLE  #pp_laminator END
SELECT TOP 1
				pp_laminator.id AS subid
				,pp_laminator.Location AS Laminator_Location
				,pp_laminator.TimeStamp AS Laminator_TimeStamp
				,LAM_POS.Position AS Laminator_Position
INTO			#pp_laminator
FROM			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] AS pp_laminator 
LEFT JOIN		[ODS].[mfg].[ProcessHistoryLaminatorProcessHeader] AS LAM_POS
				ON pp_laminator.id = LAM_POS.SubId
				AND LAM_POS.Step = 1
				AND LAM_POS.ReadTime = (
					SELECT Max(ReadTime) FROM [ODS].[mfg].[ProcessHistoryLaminatorProcessHeader] AS LAM_POS2
						WHERE LAM_POS2.SubId = pp_laminator.id AND LAM_POS2.Step = 1)
WHERE			pp_laminator.ID = @subid
				AND pp_laminator.[Location] LIKE '%-Laminator' 
ORDER BY		pp_laminator.TimeStamp DESC

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_BSA','U') IS NOT NULL BEGIN DROP TABLE  #pp_BSA END
SELECT 
				pp_BSA.id AS subid
				,pp_BSA.Location AS BSA_Location
				,pp_BSA.TimeStamp AS BSA_TimeStamp
INTO			#pp_BSA
FROM			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] AS pp_BSA 
WHERE			pp_BSA.ID = @subid
				AND pp_BSA.[Location] LIKE '%-BSA'


/* -----------------------*/
IF OBJECT_ID('tempdb..##Final','U') IS NOT NULL BEGIN DROP TABLE  ##Final END
SELECT 
							subid.subid
							,ARC_BGD.ScrapReason
							,ARC_BGD.Operator
							,ARC_BGD.ModuleReturn
							,ARC_BGD.Comment
							,ARC_BGD.ReadTime
							,ARC_BGD.ARC_BGD_Equipment
							,pp_edge_seal.Edge_Seal_Location
							,pp_edge_seal.Edge_Seal_TimeStamp
							,DATEDIFF(minute,pp_edge_seal.Edge_Seal_TimeStamp,ARC_BGD.ReadTime) AS Edge_Seal_Time_To_ARC

							,pp_laminator.Laminator_Location
							,pp_laminator.Laminator_TimeStamp
							,pp_laminator.Laminator_Position
							,DATEDIFF(minute,pp_laminator.Laminator_TimeStamp,ARC_BGD.ReadTime) AS Laminator_Time_To_ARC

							,pp_BSA.BSA_Location
							,pp_BSA.BSA_TimeStamp
							,DATEDIFF(minute,pp_BSA.BSA_TimeStamp,ARC_BGD.ReadTime) AS BSA_Time_To_ARC

INTO						##Final
FROM #subid					AS subid
LEFT JOIN #ARC_BGD			AS ARC_BGD 
							ON subid.subid = ARC_BGD.subid
LEFT JOIN #pp_edge_seal		AS pp_edge_seal 
							ON subid.subid = pp_edge_seal.subid
LEFT JOIN #pp_laminator		AS pp_laminator 
							ON subid.subid = pp_laminator.subid
LEFT JOIN #pp_BSA			AS pp_BSA 
							ON subid.subid = pp_BSA.subid

SELECT * FROM ##Final


