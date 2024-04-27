USE [FAC]
GO

/****** Object:  Table [dbo].[BgdBacklog]    Script Date: 1/22/2022 10:24:25 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[BgdBacklog](
	[ID]						[int] IDENTITY(1,1),
	--Paths
	[FpiSourcePath]				[varchar](500) NOT NULL,
	[ResultRootPath]			[varchar](500),
	--Flags
	[SubIdCorrected]			[varchar](20),
	[FlagFpiDestPath]			[Int],
	[FlagImagePath]				[Int],
	[FlagCAPath]				[Int],
	[FlagTraceabilityPath]		[Int],
	/* [FpiDestPath]				[varchar](256),
	[ImagePath]					[varchar](256),
	[ImagePath01]				[varchar](256),
	[ImagePathScreenShoot]		[varchar](256),
	[TraceabilityPath]			[varchar](256),
	[CommonalityAnalysisPath]	[varchar](256),*/
	--Extraction
	[ExtractSubId]				[varchar](20), 
	[ExtractFpiSize]			[int],
	[ExtractAlarmName]			[varchar](20),
	[ExtractSitePlant]			[varchar](5),
	[ExtractEquipment]			[varchar](50),
	[ExtractTimeStamp]			[datetime],
	[ExtractModifiedTimeUTC]	[datetime],
	[ExtractIsDummyMode]		[Bit],
	--auto generate
	[TimeStamp]					[datetime]	default getdate(),
	[TimeStampUtc]				[datetime]	default getutcdate(),
	[ModifiedTimeStampUtc]		[datetime]

 CONSTRAINT [PK_BgdBacklog] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[BgdBacklog] ADD CONSTRAINT U_FpiSourcePath UNIQUE([FpiSourcePath])
GO

Create TRIGGER [dbo].[trg_BgdBacklog_UpdateModifiedDate]
ON [dbo].[BgdBacklog]
AFTER UPDATE, Insert
AS
Begin
	
	UPDATE dbo.BgdBacklog
	SET [ModifiedTimeStampUtc] = getutcdate()
	WHERE ID IN (SELECT DISTINCT ID FROM inserted);

end
Go




