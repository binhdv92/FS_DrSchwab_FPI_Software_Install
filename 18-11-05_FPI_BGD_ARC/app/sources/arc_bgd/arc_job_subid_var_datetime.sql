/*
210630680577	0	BROKEN	2021-08-02 03:06:17.9370000	DMT21A-ARC_POST_WASHER_BGD	2021-08-02 03:06:17	2021-08-02 03:06:18
210727680600	0	BROKEN	2021-08-02 15:53:13.1370000	DMT21A-ARC_POST_WASHER_BGD	2021-08-02 15:53:13

*/

SET NOCOUNT ON

declare @mode INT = 0
declare @subid varchar(20) 
declare @datetime DATETIME

if @mode = 0
begin
	set @subid		= 'var_subids'
	set @datetime	= 'var_datetime'
End
else if @mode = 1
begin
	--set @subid		= '210712691753'
	--set @datetime	= '2021-07-31 17:49:22'

	--set @subid		= '210802723689'
	--set @datetime	= '2021-08-03 02:31:59'

	/*
	--pgt2
	--input1	input2	Subid	ModuleReturn	comment	ReadTime	ARC_BGD_Equipment	(No column name)	(No column name)
	--210803720566	2021-08-03 07:12:27.000	210803720566	0	BROKEN	2021-08-03 07:12:28.2670000	PGT21A-ARC_POST_WASHER_BGD	2021-08-03 07:12:28	2021-08-03 07:12:28
	*/
	--set @subid		= '210803720567'
	--set @datetime	= '2021-08-03 07:12:27'
	
	--pgt2
	--set @subid		= '210627610673'
	--set @datetime	= '2021-08-03 06:27:19'

	--dmt1
	--set @subid		= '210806660552'
	--set @datetime	= '2021-08-06 10:30:26'
	--set @datetime	= '0000-00-00 00:00:00'
	--set @datetime	= ''

	-- pgt1
	set @subid		= '210919771001'
	set @datetime	= '2021-09-20 08:44:14'
	
End
print(@subid)
print(@datetime)


IF OBJECT_ID('tempdb..##base_table','U') IS NOT NULL BEGIN DROP TABLE ##base_table END
select 
					@subid as 'input_subid'
					,@datetime as 'input_datetime'
					,MS.Subid
					,MS.ModuleReturn
					,MS.comment
					,MS.ReadTime
					,GE.name as ARC_BGD_Equipment
					,datediff(second,@datetime,MS.ReadTime) as date_diff
					,case 
						when MS.Subid=@subid then 'trust_subid'
						else concat('corrected_subid from ',@subid) end as flag_subid_recover
INTO				##base_table
from				ModuleAssembly.History.Scrap_ModuleScrap as ms
join				ods.mfg.GlobalEquipment AS GE
					on MS.EquipmentId = ge.equipmentid
where			
					--cast(ms.readTime as datetime2(0)) = @datetime
					(ms.subid = @subid or ms.ReadTime between dateadd(minute,-5,@datetime) and dateadd(minute,1,@datetime))
					AND GE.Name LIKE '%-ARC_POST_WASHER_BGD'
					AND MS.HistoryAction in ('U', 'I')
					AND ods.mfg.fn_Plant() = substring(GE.name,1,4)
					AND ms.ModuleReturn =0


IF OBJECT_ID('tempdb..#subid_table','U') IS NOT NULL BEGIN DROP TABLE #subid_table END
select
				base_table.input_subid 
				,base_table.input_datetime 
				,base_table.Subid
				,base_table.ModuleReturn
				,base_table.comment
				,base_table.ReadTime
				,base_table.ARC_BGD_Equipment
				,base_table.flag_subid_recover
into			#subid_table
from			##base_table  as base_table
where			flag_subid_recover = 'trust_subid'
				or base_table.date_diff = (select min(base_table2.date_diff) from ##base_table as base_table2)
order by		readtime desc


/* *************************************************
***************************************************/
if 'trust_subid' = (select max(flag_subid_recover) from #subid_table where flag_subid_recover = 'trust_subid')
begin
	print('trust_subid')
	Delete from #subid_table where flag_subid_recover like 'corrected_subid from %'
end
else
begin
	print('corrected_subid')
end

/* -----------------------*/
IF OBJECT_ID('tempdb..#ARC_BGD','U') IS NOT NULL BEGIN DROP TABLE #ARC_BGD END
select 
				MS.Subid
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
INNER JOIN		ods.mfg.GlobalUnit as GU
				ON MS.UnitId = GU.UnitId
INNER JOIN		ods.mfg.GlobalPlant as GPL
				ON GU.PlantId = GPL.PlantId
INNER JOIN		ods.mfg.GlobalSite as GS
				ON GPL.SiteId = GS.SiteId
WHERE
				ms.SubId in (select Subid from #subid_table)
				AND GE.Name LIKE '%-ARC_POST_WASHER_BGD%'
				AND MS.HistoryAction in ('U', 'I')
				AND ods.mfg.fn_Plant() = GPL.DisplayName
				AND ms.ModuleReturn =0

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_ARC_BGD','U') IS NOT NULL BEGIN DROP TABLE  #pp_ARC_BGD END
select 
				pp_ARC_BGD.id as subid
				,pp_ARC_BGD.Location as Edge_Seal_Location
				,pp_ARC_BGD.TimeStamp as Edge_Seal_TimeStamp
INTO			#pp_ARC_BGD
from			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_ARC_BGD 
where			pp_ARC_BGD.ID in (select Subid from #subid_table)
				and pp_ARC_BGD.[Location] like '%ARC_WASHER'

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_edge_seal','U') IS NOT NULL BEGIN DROP TABLE  #pp_edge_seal END
select 
				pp_edge_seal.id as subid
				,pp_edge_seal.Location as Edge_Seal_Location
				,pp_edge_seal.TimeStamp as Edge_Seal_TimeStamp
INTO			#pp_edge_seal
from			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_edge_seal 
where			pp_edge_seal.ID in (select Subid from #subid_table)
				and pp_edge_seal.[Location] like '%-EDGE_SEAL'

/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_laminator','U') IS NOT NULL BEGIN DROP TABLE  #pp_laminator END
select 
				pp_laminator.id as subid
				,pp_laminator.Location as Laminator_Location
				,pp_laminator.TimeStamp as Laminator_TimeStamp
				,LAM_POS.Position as Laminator_Position
INTO			#pp_laminator
from			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_laminator 
LEFT JOIN		[ODS].[mfg].[ProcessHistoryLaminatorProcessHeader] as LAM_POS
				on pp_laminator.id = LAM_POS.SubId
				and LAM_POS.Step = 1
				and LAM_POS.ReadTime = (
					select Max(ReadTime) from [ODS].[mfg].[ProcessHistoryLaminatorProcessHeader] as LAM_POS2
						where LAM_POS2.SubId = pp_laminator.id and LAM_POS2.Step = 1)
where			pp_laminator.ID in (select Subid from #subid_table)
				and pp_laminator.[Location] like '%-Laminator' 


/* -----------------------*/
IF OBJECT_ID('tempdb..#pp_BSA','U') IS NOT NULL BEGIN DROP TABLE  #pp_BSA END
select 
				pp_BSA.id as subid
				,pp_BSA.Location as BSA_Location
				,pp_BSA.TimeStamp as BSA_TimeStamp
INTO			#pp_BSA
from			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_BSA 
where			pp_BSA.ID in (select Subid from #subid_table)
				and pp_BSA.[Location] like '%-BSA'


/* -----------------------*/
IF OBJECT_ID('tempdb..##Final','U') IS NOT NULL BEGIN DROP TABLE  ##Final END
select 
							subid.subid
							,flag_subid_recover
							,ARC_BGD.ModuleReturn
							,ARC_BGD.Comment
							,ARC_BGD.ReadTime
							,ARC_BGD.ARC_BGD_Equipment
							,pp_edge_seal.Edge_Seal_Location
							,pp_edge_seal.Edge_Seal_TimeStamp
							,datediff(minute,pp_edge_seal.Edge_Seal_TimeStamp,ARC_BGD.ReadTime) as Edge_Seal_Time_To_ARC

							,pp_laminator.Laminator_Location
							,pp_laminator.Laminator_TimeStamp
							,pp_laminator.Laminator_Position
							,datediff(minute,pp_laminator.Laminator_TimeStamp,ARC_BGD.ReadTime) as Laminator_Time_To_ARC

							,pp_BSA.BSA_Location
							,pp_BSA.BSA_TimeStamp
							,datediff(minute,pp_BSA.BSA_TimeStamp,ARC_BGD.ReadTime) as BSA_Time_To_ARC
INTO						##Final
from  #subid_table			as subid
LEFT JOIN #ARC_BGD			as ARC_BGD 
							on subid.subid = ARC_BGD.subid
LEFT JOIN #pp_edge_seal		as pp_edge_seal 
							on subid.subid = pp_edge_seal.subid
LEFT JOIN #pp_laminator		as pp_laminator 
							on subid.subid = pp_laminator.subid
LEFT JOIN #pp_BSA			as pp_BSA 
							on subid.subid = pp_BSA.subid


select * from ##Final


