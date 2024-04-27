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
	-- set @subid		= '210919771001'
	-- set @datetime	= '2021-09-20 08:44:14'

	-- dmt1 - arc
	set @subid = '220124662504'
	set @datetime	= '2022-01-24 16:39:58'

	-- dmt1 - cdcl
	set @subid = '220124672280'
	set @datetime	= '2022-01-24 22:13:30'
	
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
					AND (
						GE.Name LIKE '%-ARC_POST_WASHER_BGD'	
					)
					AND MS.HistoryAction in ('U', 'I')
					AND ods.mfg.fn_Plant() = substring(GE.name,1,4)
					AND ms.ModuleReturn =0


IF OBJECT_ID('tempdb..##subid_table','U') IS NOT NULL BEGIN DROP TABLE ##subid_table END
select
				base_table.input_subid 
				,base_table.input_datetime 
				,base_table.Subid
				,base_table.ModuleReturn
				,base_table.comment
				,base_table.ReadTime
				,base_table.ARC_BGD_Equipment
				,base_table.flag_subid_recover
into			##subid_table
from			##base_table  as base_table
where			flag_subid_recover = 'trust_subid'
				or base_table.date_diff = (select min(base_table2.date_diff) from ##base_table as base_table2)
order by		readtime desc


/* *************************************************
***************************************************/
if 'trust_subid' = (select max(flag_subid_recover) from ##subid_table where flag_subid_recover = 'trust_subid')
begin
	print('trust_subid')
	Delete from ##subid_table where flag_subid_recover like 'corrected_subid from %'
end
else
begin
	print('corrected_subid')
end

select * from ##subid_table