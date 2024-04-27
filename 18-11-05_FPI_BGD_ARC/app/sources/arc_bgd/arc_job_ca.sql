declare @mode INT = 0
declare @var_end_time DATETIME
declare @var_end_time_temp DATETIME

if @mode = 0
begin
	set @var_end_time_temp	= 'var_datetime' --argument here 2021-08-04 03:02:07 var_datetime
	if @var_end_time_temp ='' or @var_end_time_temp ='var_datetime'
	begin
		print('var_end_time_temp = blank')
		set @var_end_time	= getdate()
	end
	else
	begin
		print('var_end_time_temp = not black')
		set @var_end_time	= dateadd(minute,30,@var_end_time_temp)
	end
End
else if @mode = 1
begin
	set @var_end_time	= '2021-08-04 03:02:07'
End
print(@var_end_time)

/*-------------last_24_Hours-------------------------*/
IF OBJECT_ID('tempdb..#base_table','U') IS NOT NULL BEGIN DROP TABLE #base_table END
select			
				MS.Subid
				,MS.ModuleReturn
				,MS.comment
				,MS.ReadTime
				,GE.name as ARC_BGD_Equipment

				,pp_edge_seal.Location as Edge_Seal_location
				,pp_edge_seal.TimeStamp as Edge_Seal_TimeStamp
				,datediff(minute,pp_edge_seal.TimeStamp,MS.ReadTime) as Edge_Seal_Time_To_ARC

				,pp_laminator.Location as Laminator_Location
				,pp_laminator.TimeStamp as Laminator_TimeStamp
				,LAM_POS.Position as Laminator_Position
				,datediff(minute,pp_laminator.TimeStamp,MS.ReadTime) as Laminator_Time_to_arc

				,pp_BSA.Location as BSA_Location
				,pp_BSA.TimeStamp as BSA_TimeStamp
				,datediff(minute,pp_BSA.TimeStamp,MS.ReadTime) as BSA_Time_To_ARC
INTO			#base_table
from			ModuleAssembly.History.Scrap_ModuleScrap as MS
join			ods.mfg.GlobalEquipment AS GE
				on MS.EquipmentId = ge.equipmentid
left join		[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_edge_seal 
				on MS.SubId = pp_edge_seal.ID
				and pp_edge_seal.TimeStamp = (
					select max(TimeStamp) from [ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_edge_seal2 
					where pp_edge_seal2.ID = MS.SubId  and pp_edge_seal2.[Location] like '%-EDGE_SEAL')
left join		[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_laminator
				on MS.SubId = pp_laminator.ID
				and pp_laminator.TimeStamp = (
					select max(TimeStamp) from [ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_laminator2
					where pp_laminator2.ID = MS.SubId  and pp_laminator2.[Location] like '%-Laminator')		
left join		[ODS].[mfg].[ProcessHistoryLaminatorProcessHeader] as LAM_POS
				on MS.SubId = LAM_POS.SubId
				and pp_laminator.id = LAM_POS.Subid
				and LAM_POS.ReadTime = (
					select Max(ReadTime) from [ODS].[mfg].[ProcessHistoryLaminatorProcessHeader] as LAM_POS2
						where LAM_POS2.SubId = MS.SubId and pp_laminator.id = LAM_POS.Subid and LAM_POS2.Step = 1)
										
left join		[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_BSA 
				on MS.SubId = pp_BSA.ID
				and pp_BSA.TimeStamp = (
					select Max(TimeStamp) from [ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_BSA2 
					where pp_BSA2.ID = MS.SubId and pp_BSA2.[Location] like '%-BSA' )			

where 
				MS.ReadTime between dateadd(hour,-24,@var_end_time) and @var_end_time
				AND GE.Name LIKE '%-ARC_POST_WASHER_BGD'
				AND MS.HistoryAction in ('U', 'I')
				AND ods.mfg.fn_Plant() = substring(GE.name,1,4)
				AND ms.ModuleReturn =0


IF OBJECT_ID('tempdb..##es','U') IS NOT NULL BEGIN DROP TABLE ##es END
select				hour24.Edge_Seal_Location as location
					,hour01.qty as last_01h
					,hour03.qty as last_03h
					,hour06.qty as last_06h
					,hour12.qty as last_12h
					,hour24.qty as last_24h
into				##es	
from				(select		base.Edge_Seal_Location
					,count(base.SubID) as Qty
					from		#base_table as base
					Group by			Edge_Seal_Location) as hour24
full outer join		(select		base.Edge_Seal_Location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-12,@var_end_time) and @var_end_time
					Group by			base.Edge_Seal_Location) as hour12
					on hour24.Edge_Seal_Location = hour12.Edge_Seal_Location
full outer join		(select		base.Edge_Seal_Location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-6,@var_end_time) and @var_end_time
					Group by			base.Edge_Seal_Location) as hour06
					on hour24.Edge_Seal_Location = hour06.Edge_Seal_Location
full outer join		(select		base.Edge_Seal_Location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-03,@var_end_time) and @var_end_time
					Group by			base.Edge_Seal_Location) as hour03
					on hour24.Edge_Seal_Location = hour03.Edge_Seal_Location
full outer join		(select		base.Edge_Seal_Location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-01,@var_end_time) and @var_end_time
					Group by			base.Edge_Seal_Location) as hour01
					on hour24.Edge_Seal_Location = hour01.Edge_Seal_Location



IF OBJECT_ID('tempdb..##lam','U') IS NOT NULL BEGIN DROP TABLE ##lam END
/* ---------------laminator_location------------------ */
select				hour24.laminator_location as location
					,hour24.Laminator_Position as position	
					,hour01.qty as last_01h
					,hour03.qty as last_03h
					,hour06.qty as last_06h
					,hour12.qty as last_12h
					,hour24.qty as last_24h
into				##lam
from				(select	distinct	base.laminator_location, base.Laminator_Position
					,count(base.SubID) as Qty
					from		#base_table as base
					Group by			laminator_location, base.Laminator_Position) as hour24
LEFT join		(select	distinct	base.laminator_location, base.Laminator_Position
					,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-12,@var_end_time) and @var_end_time
					Group by			base.laminator_location, base.Laminator_Position) as hour12
					on hour24.laminator_location = hour12.laminator_location and hour24.Laminator_Position = hour12.Laminator_Position
LEFT join		(select	distinct	base.laminator_location, base.Laminator_Position
					,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-06,@var_end_time) and @var_end_time
					Group by			base.laminator_location, base.Laminator_Position) as hour06
					on hour24.laminator_location = hour06.laminator_location and hour24.Laminator_Position = hour06.Laminator_Position
LEFT join		(select	distinct	base.laminator_location, base.Laminator_Position
					,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-03,@var_end_time) and @var_end_time
					Group by			base.laminator_location, base.Laminator_Position) as hour03
					on hour24.laminator_location = hour03.laminator_location and hour24.Laminator_Position = hour03.Laminator_Position
LEFT join		(select	distinct	base.laminator_location, base.Laminator_Position
					,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-01,@var_end_time) and @var_end_time
					Group by			base.laminator_location, base.Laminator_Position) as hour01
					on hour24.laminator_location = hour01.laminator_location and hour24.Laminator_Position = hour01.Laminator_Position


IF OBJECT_ID('tempdb..##bsa','U') IS NOT NULL BEGIN DROP TABLE ##bsa END
/* ---------------bsa_location------------------ */
select				hour24.bsa_location as location
					,hour01.qty as last_01h
					,hour03.qty as last_03h
					,hour06.qty as last_06h
					,hour12.qty as last_12h
					,hour24.qty as last_24h
into				##bsa
from				(select		base.bsa_location
					,count(base.SubID) as Qty
					from		#base_table as base
					Group by			bsa_location) as hour24
full outer join		(select		base.bsa_location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-12,@var_end_time) and @var_end_time
					Group by			base.bsa_location) as hour12
					on hour24.bsa_location = hour12.bsa_location
full outer join		(select		base.bsa_location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-06,@var_end_time) and @var_end_time
					Group by			base.bsa_location) as hour06
					on hour24.bsa_location = hour06.bsa_location
full outer join		(select		base.bsa_location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-03,@var_end_time) and @var_end_time
					Group by			base.bsa_location) as hour03
					on hour24.bsa_location = hour03.bsa_location
full outer join		(select		base.bsa_location,count(base.SubID) as Qty
					from		#base_table as base
					where		base.ReadTime between dateadd(hour,-01,@var_end_time) and @var_end_time
					Group by			base.bsa_location) as hour01
					on hour24.bsa_location = hour01.bsa_location

					

/*
IF OBJECT_ID('tempdb..##final','U') IS NOT NULL BEGIN DROP TABLE ##final END
select * into ##final from (
select * from ##es
union all
select * from ##lam
union all
select * from ##bsa
) as a
order by location
*/

/* 

select Laminator_Location,Laminator_Position ,count(base.SubID) as Qty
from #base_table as base
where		base.ReadTime between dateadd(hour,-12,'2021-07-31 17:31:58') and '2021-07-31 17:31:58'
group by Laminator_Location,Laminator_Position

select distinct * from ##es order by location

select distinct * from ##lam order by location, position

select distinct * from ##bsa order by location

select * from ##final

*/


