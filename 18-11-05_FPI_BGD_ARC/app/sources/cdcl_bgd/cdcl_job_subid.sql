/*
679673740	9	DMT11A-VTD_COATER	2021-08-03 19:59:13.9500000	210804650518	DMT11A-VTD_COATER	0	1	0	2021-08-03 19:59:46.7666667	MFG\zSvc_MesDMT1	2021-08-04 02:59:13.9500000
0_DMT11ACdClBGD_210804650518_0_2021-08-04_03-02-07.FPI
*/

SET NOCOUNT ON

DECLARE @mode INT = 0
DECLARE @subid VARCHAR(20) 
--declare @datetime DATETIME

IF @mode = 0
BEGIN
	SET @subid		= 'var_subids'
	--set @datetime	= 'var_datetime'
END
ELSE IF @mode = 1
BEGIN
	SET @subid		= '221106760170'
	--set @datetime	= '2021-08-04 03:02:07'

END
PRINT(@subid)
--print(@datetime)


IF OBJECT_ID('tempdb..#subid_table','U') IS NOT NULL BEGIN DROP TABLE #subid_table END
SELECT 
					MS.Subid
					,SR.Reason AS ScrapReason
					,MS.ModuleReturn
					,MS.comment
					,MS.ReadTime
					,GE.name AS BGD_Equipment
					
INTO				#subid_table
FROM				ModuleAssembly.History.Scrap_ModuleScrap AS MS
INNER JOIN			ods.mfg.ScrapReason AS SR
					ON MS.ScrapReasonId = SR.ReasonId
JOIN				ods.mfg.GlobalEquipment AS GE
					ON MS.EquipmentId = ge.equipmentid
WHERE			
					--cast(ms.readTime as datetime2(0)) = @datetime
					(ms.subid = @subid )
					--AND GE.Name LIKE '%-CDCL2_ROLLCOAT_BGD'
					AND MS.HistoryAction IN ('U', 'I')
					-- AND ods.mfg.fn_Plant() = substring(GE.name,1,4)
					AND ms.ModuleReturn =0
/*
select * from #subid_table

IF OBJECT_ID('tempdb..#subid_table','U') IS NOT NULL BEGIN DROP TABLE #subid_table END
select
				base_table.input_subid 
				,base_table.input_datetime 
				,base_table.Subid
				,base_table.ModuleReturn
				,base_table.comment
				,base_table.ReadTime
				,base_table.BGD_Equipment
				,base_table.flag_subid_recover
into			#subid_table
from			##base_table  as base_table
where			flag_subid_recover = 'trust_subid'
				or base_table.date_diff = (select min(base_table2.date_diff) from ##base_table as base_table2)
order by		readtime desc
*/

/* *************************************************
***************************************************/
/*
if 'trust_subid' = (select max(flag_subid_recover) from #subid_table where flag_subid_recover = 'trust_subid')
begin
	print('trust_subid')
	Delete from #subid_table where flag_subid_recover like 'corrected_subid from %'
end
else
begin
	print('corrected_subid')
end

select * from #subid_table
*/
/* -----------------------*/
/*
IF OBJECT_ID('tempdb..#cdcl_scrap','U') IS NOT NULL BEGIN DROP TABLE #cdcl_scrap END
select 
				MS.Subid
				,MS.ModuleReturn
				,MS.comment
				,MS.ReadTime
				,GE.name as BGD_Equipment

INTO			#cdcl_scrap
from			ModuleAssembly.History.Scrap_ModuleScrap AS MS
INNER JOIN		ods.mfg.ScrapReason AS SR
				ON MS.ScrapReasonId = SR.ReasonId
INNER JOIN		ods.mfg.GlobalProcess AS GP
				ON MS.ProcessId = GP.ProcessId
INNER JOIN		ods.mfg.GlobalEquipment AS GE
				ON MS.EquipmentId = GE.EquipmentId
INNER JOIN		ods.mfg.ScrapCategory AS SC
				ON MS.ScrapCategoryId = SC.CategoryId
INNER JOIN		ods.mfg.GlobalUnit as GU
				ON MS.UnitId = GU.UnitId
INNER JOIN		ods.mfg.GlobalPlant as GPL
				ON GU.PlantId = GPL.PlantId
INNER JOIN		ods.mfg.GlobalSite as GS
				ON GPL.SiteId = GS.SiteId
WHERE
				ms.SubId in (select Subid from #subid_table)
				AND GE.Name LIKE '%-CDCL2_ROLLCOAT_BGD'
				AND MS.HistoryAction in ('U', 'I')
				AND ods.mfg.fn_Plant() = GPL.DisplayName
				AND ms.ModuleReturn =0
select * from #cdcl_scrap
*/


/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_VTD_COATER','U') IS NOT NULL BEGIN DROP TABLE  #pp_VTD_COATER END
SELECT  TOP 1
				 PP.id AS subid
				,PP.Location AS Location
				,PP.TimeStamp AS TimeStamp
INTO			#pp_VTD_COATER
FROM			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] AS PP 
WHERE			PP.ID IN (SELECT Subid FROM #subid_table)
				AND PP.[Location] LIKE '%-VTD_COATER'
/*
select * from #pp_VTD_COATER
*/

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_VTD_COATER_ACCUM','U') IS NOT NULL BEGIN DROP TABLE  #pp_VTD_COATER_ACCUM END
SELECT			TOP 1
				pp_VTD_COATER_ACCUM.id AS subid
				,pp_VTD_COATER_ACCUM.Location AS Location
				,pp_VTD_COATER_ACCUM.TimeStamp AS TimeStamp
INTO			#pp_VTD_COATER_ACCUM
FROM			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] AS pp_VTD_COATER_ACCUM 
WHERE			pp_VTD_COATER_ACCUM.ID IN (SELECT Subid FROM #subid_table)
				AND pp_VTD_COATER_ACCUM.[Location] LIKE '%-PRE_VTD_COATER_ACCUM%'
/*
select * from #pp_VTD_COATER_ACCUM
*/

/* -----------------------*/
IF OBJECT_ID('tempdb..##Final','U') IS NOT NULL BEGIN DROP TABLE  ##Final END
SELECT 
							subid.subid
							,subid.ScrapReason
							,subid.ModuleReturn
							,subid.Comment
							,subid.ReadTime
							,subid.BGD_Equipment

							,pp_VTD_COATER.Location AS VTD_COATER_Location
							,pp_VTD_COATER.TimeStamp AS VTD_COATER_TimeStamp
							,datediff(minute,pp_VTD_COATER.TimeStamp,subid.ReadTime) AS VTD_COATER_Time_To_CDCL

							,pp_VTD_COATER_ACCUM.Location AS VTD_COATER_ACCUM_Location
							,pp_VTD_COATER_ACCUM.TimeStamp AS VTD_COATER_ACCUM_TimeStamp
							,datediff(minute,pp_VTD_COATER_ACCUM.TimeStamp,subid.ReadTime) AS VTD_COATER_ACCUM_Time_To_CDCL

INTO						##Final
FROM						#subid_table			AS subid
LEFT JOIN					#pp_VTD_COATER	AS pp_VTD_COATER 
							ON subid.subid = pp_VTD_COATER.subid
LEFT JOIN					#pp_VTD_COATER_ACCUM	AS pp_VTD_COATER_ACCUM 
							ON subid.subid = pp_VTD_COATER_ACCUM.subid
/*
select * from ##Final

*/
