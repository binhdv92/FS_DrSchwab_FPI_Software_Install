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
				,GE.name as BGD_Equipment

				,pp_VTD_COATER.Location as VTD_COATER_Location
				,pp_VTD_COATER.TimeStamp as VTD_COATER_TimeStamp
				,datediff(minute,pp_VTD_COATER.TimeStamp,MS.ReadTime) as VTD_COATER_Time_To_ARC

				,datediff(hour,MS.ReadTime,@var_end_time) as diff_hour

INTO			#base_table
from			ModuleAssembly.History.Scrap_ModuleScrap as MS
join			ods.mfg.GlobalEquipment AS GE
				on MS.EquipmentId = ge.equipmentid
left join		[ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_VTD_COATER 
				on MS.SubId = pp_VTD_COATER.ID
				and pp_VTD_COATER.TimeStamp = (
					select max(TimeStamp) from [ODS].[mfg].[ProcessHistoryPdrPartProducedEvent] as pp_VTD_COATER2 
					where pp_VTD_COATER2.ID = MS.SubId  and pp_VTD_COATER2.[Location] like '%-VTD_COATER')

where 
				MS.ReadTime between dateadd(hour,-24,@var_end_time) and @var_end_time
				AND GE.Name LIKE '%-CDCL2_ROLLCOAT_BGD'
				AND MS.HistoryAction in ('U', 'I')
				AND ods.mfg.fn_Plant() = substring(GE.name,1,4)
				AND ms.ModuleReturn =0


/*******************##VTD_COATER***********************************/
IF OBJECT_ID('tempdb..##VTD_COATER','U') IS NOT NULL BEGIN DROP TABLE ##VTD_COATER END
select				hour24.VTD_COATER_Location as location
					,hour01.qty as last_01h
					,hour03.qty as last_03h
					,hour06.qty as last_06h
					,hour12.qty as last_12h
					,hour24.qty as last_24h
into				##VTD_COATER	
from				(select		VTD_COATER_Location, count(*) as Qty
					from		#base_table
					Group by	VTD_COATER_Location) as hour24
full outer join		(select		VTD_COATER_Location,count(*) as Qty
					from		#base_table
					where		ReadTime between dateadd(hour,-12,@var_end_time) and @var_end_time
					Group by	VTD_COATER_Location) as hour12
					on hour24.VTD_COATER_Location = hour12.VTD_COATER_Location
full outer join		(select		VTD_COATER_Location,count(*) as Qty
					from		#base_table
					where		ReadTime between dateadd(hour,-6,@var_end_time) and @var_end_time
					Group by	VTD_COATER_Location) as hour06
					on hour24.VTD_COATER_Location = hour06.VTD_COATER_Location
full outer join		(select		VTD_COATER_Location,count(*) as Qty
					from		#base_table
					where		ReadTime between dateadd(hour,-03,@var_end_time) and @var_end_time
					Group by	VTD_COATER_Location) as hour03
					on hour24.VTD_COATER_Location = hour03.VTD_COATER_Location
full outer join		(select		VTD_COATER_Location,count(*) as Qty
					from		#base_table
					where		ReadTime between dateadd(hour,-01,@var_end_time) and @var_end_time
					Group by	VTD_COATER_Location) as hour01
					on hour24.VTD_COATER_Location = hour01.VTD_COATER_Location


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

select distinct * from ##VTD_COATER order by location

*/


