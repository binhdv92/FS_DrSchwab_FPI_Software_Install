
/*
679673740	9	DMT11A-VTD_COATER	2021-08-03 19:59:13.9500000	210804650518	DMT11A-VTD_COATER	0	1	0	2021-08-03 19:59:46.7666667	MFG\zSvc_MesDMT1	2021-08-04 02:59:13.9500000
0_DMT11ACdClBGD_210804650518_0_2021-08-04_03-02-07.FPI
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
	--set @subid		= '210804650518'
	--set @datetime	= '2021-08-04 03:02:07'
	-- 201020770741 : pgt12

	--set @subid		= '210919771001'
	--set @datetime	= '2021-09-20 08:44:14'

	-- PGT1
	--set @subid		= '210927610864'
	--set @datetime	= '2021-09-27 09:46:57'

	-- 2021-11-09 pgt2 , missing CA info
	set @subid		= '220124620931'
	set @datetime	= '2022-01-24 06:11:09'

	-- 2021-11-09 pgt2 , FS100 ROBOT
	--set @subid		= '211206730425'
	--set @datetime	= '2021-12-06 05:51:33'


	-- KMT2
	--set @subid		= '210920742427'
	--set @datetime	= '2021-09-20 23:38:23'
	
	--KMT1
	--set @subid		= '210920623487'
	--set @datetime	= '2021-09-20 20:01:41'
	
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
					,GE.name as BGD_Equipment
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
					AND (
						   GE.Name LIKE '%-CDCL2_ROLLCOAT' 
						or GE.Name LIKE '%-CDCL2_ROLLCOAT_BGD'
						or GE.Name LIKE '%-CVS02' 
						or GE.Name Like '%-PRE_CDCL2_ROLLCOAT_RIGHT_BGD' /* KMT */
						or GE.Name Like '%-PRE_CDCL2_ROLLCOAT_LEFT_BGD' /* KMT */
					)
					AND MS.HistoryAction in ('U', 'I')
					AND ods.mfg.fn_Plant() = substring(GE.name,1,4)
					AND ms.ModuleReturn =0

-- select * from ##base_table

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
/* --------CA-------------*/
/* -----------------------*/
	IF OBJECT_ID('tempdb..#workflow','U') IS NOT NULL BEGIN DROP TABLE  #workflow END
	select 
			A.SubId, A.ProcessName,A.Location, A.TimeStamp
			
	INTO	#workflow
	From (
			select 
						SubId, ProcessName,EquipmentName as Location, ReadTime as TimeStamp
						,rank() over (Partition by ProcessName order by ReadTime Desc) as rank_01
			from ods.mfg.workflow
			where 
					SubId = (select SubId from #subid_table)
					--SubId = '211128602929' 
					and ProcessId in 
						(
							61175 /*  BARCODE_MARKER		*/
							,61250 /* VTD_WASHER			*/
							,61381 /* PRE_VTD_COATER_ACCUM  */
							,61400 /* VTD_COATER			*/
						)
	) as A
	where A.rank_01 = 1
	/* select * from #workflow */

	/* -----------------------*/
	IF OBJECT_ID('tempdb..#PPE_ROBOT_FS100','U') IS NOT NULL BEGIN DROP TABLE  #PPE_ROBOT_FS100 END
	select 
					 PPE.subid as subid
					 ,'ROBOT_FS100' as ProcessName
					,PPE.SourceLocation as Location
					,PPE.TimeStamp as TimeStamp
	INTO			#PPE_ROBOT_FS100
	from			ModuleAssembly.ProcessHistory.PdrContainerContentEvent PPE
	where			PPE.subID in (select Subid from #subid_table)
					and PPE.[SourceLocation] like '%FS100%'
					and PPE.TimeStamp = (select max(TimeStamp) from ModuleAssembly.ProcessHistory.PdrContainerContentEvent PPE2 where PPE2.subID in (select Subid from #subid_table)
					and PPE2.[SourceLocation] like '%FS100%')
	/* select * from #PPE_ROBOT_FS100 */

	/* -----------------------*/
	IF OBJECT_ID('tempdb..#traceability','U') IS NOT NULL BEGIN DROP TABLE  #traceability END
	select	
				SubId, ProcessName,Location, TimeStamp
	into		#traceability
	from (
			select 
			SubId, ProcessName,Location, TimeStamp
			from #workflow
			UNION ALL
			select
			SubId, ProcessName,Location, TimeStamp
			from #PPE_ROBOT_FS100
	) as	A
	/* select	* from #traceability */

	
	/* -----------------------*/
	IF OBJECT_ID('tempdb..#traceability_pivot_Location','U') IS NOT NULL BEGIN DROP TABLE  #traceability_pivot_Location END
	select 
			SubId
			,BARCODE_MARKER		
			,VTD_WASHER			
			,PRE_VTD_COATER_ACCUM  
			,VTD_COATER	
			,ROBOT_FS100
	INTO	#traceability_pivot_Location
	from (select SubId, ProcessName,Location from #traceability) as a
	pivot
	(
		max(Location)
		for ProcessName in 
		(
			[BARCODE_MARKER]	
			,[VTD_WASHER]			
			,[PRE_VTD_COATER_ACCUM]  
			,[VTD_COATER]	
			,[ROBOT_FS100]
		)
	) as piv

	IF OBJECT_ID('tempdb..#traceability_pivot_TimeStamp','U') IS NOT NULL BEGIN DROP TABLE  #traceability_pivot_TimeStamp END
	select 
			SubId
			,BARCODE_MARKER		
			,VTD_WASHER			
			,PRE_VTD_COATER_ACCUM  
			,VTD_COATER	
			,ROBOT_FS100
	INTO	#traceability_pivot_TimeStamp
	from (select SubId, ProcessName, TimeStamp from #traceability) as a
	pivot
	(
		max(TimeStamp)
		for ProcessName in 
		(
			[BARCODE_MARKER]	
			,[VTD_WASHER]			
			,[PRE_VTD_COATER_ACCUM]  
			,[VTD_COATER]	
			,[ROBOT_FS100]
		)
	) as piv
	
	IF OBJECT_ID('tempdb..##final','U') IS NOT NULL BEGIN DROP TABLE  ##final END
	Select 
			C.subid
			,C.flag_subid_recover
			,C.ModuleReturn
			,C.Comment
			,C.ReadTime
			,C.BGD_Equipment
			,A.BARCODE_MARKER			as 	BARCODE_MARKER_Location
			,B.BARCODE_MARKER			as  BARCODE_MARKER_TimeStamp
			,datediff(minute,B.BARCODE_MARKER,C.ReadTime) as [BARCODE_MARKER to CDCL (min)]
			,A.VTD_WASHER				as	VTD_WASHER_Location		
			,B.VTD_WASHER				as	VTD_WASHER_TimeStamp
			,datediff(minute,B.VTD_WASHER,C.ReadTime) as [VTD_WASHER to CDCL  (min)]
			,A.PRE_VTD_COATER_ACCUM  	as	PRE_VTD_COATER_ACCUM_Location
			,B.PRE_VTD_COATER_ACCUM  	as	PRE_VTD_COATER_ACCUM_TimeStamp
			,datediff(minute,B.PRE_VTD_COATER_ACCUM,C.ReadTime) as [PRE_VTD_COATER_ACCUM to CDCL  (min)]
			,A.VTD_COATER				as	VTD_COATER_Location
			,B.VTD_COATER				as	VTD_COATER_TimeStamp
			,datediff(minute,B.VTD_COATER,C.ReadTime) as [VTD_COATER to CDCL  (min)]
			,A.ROBOT_FS100				as	ROBOT_FS100_Location
			,B.ROBOT_FS100				as	ROBOT_FS100_TimeStamp
			,datediff(minute,B.ROBOT_FS100,C.ReadTime) as [ROBOT_FS100 to CDCL  (min)]
	INTO	##final
	from	#subid_table as C
	LEFT JOIN	#traceability_pivot_Location as A
			ON C.SubId = A.SubId
	LEFT JOIN	#traceability_pivot_TimeStamp as B
			on C.SubId = B.SubId							

/*

select * from ##Final

select * from ##base_table

select * from #subid_table

select * from #PPE_BARCODE_MARKER

select * from #PPE_VTD_COATER
select * from #PPE_ROBOT_FS050

select * from #PPE_VTD_WASHER

select * from #PPE_PRE_VTD_COATER_ACCUM

IF OBJECT_ID('tempdb..#PPE_BARCODE_MARKER','U') IS NOT NULL BEGIN DROP TABLE  #PPE_BARCODE_MARKER END
	select 
					PPE.id as subid
					,PPE.Location as Location
					,PPE.TimeStamp as TimeStamp
	INTO			#PPE_BARCODE_MARKER
	from			[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as PPE
	where			PPE.ID in (select Subid from #subid_table)
					--and PPE.[Location] like '%-BARCODE_MARKER'


select * from #PPE_BARCODE_MARKER



select * from ModuleAssembly.History.Scrap_ModuleScrap  ms
join				ods.mfg.GlobalEquipment AS GE
		on MS.EquipmentId = ge.equipmentid
where 
subid in ('210920742427','210920742438','210920742401','210920623487','210920621895','210920761566','210920760989','210920620917')

--ms.processID = '10365' 
--ge.name like '%CDCL%'
--and ReadTime between getdate()-14 and getdate()

*/

	