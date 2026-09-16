[Setup]
AppId={{7A3C23A8-3D8D-4B24-9B77-1A03B4A8B6F1}
AppName=人脸颜值数据洞察
AppVersion=0.1.0
DefaultDirName={localappdata}\FaceInsight
DefaultGroupName=人脸颜值数据洞察
OutputDir=output
OutputBaseFilename=FaceInsightSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "..\dist\FaceInsight\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\人脸颜值数据洞察"; Filename: "{app}\FaceInsight.exe"
Name: "{userdesktop}\人脸颜值数据洞察"; Filename: "{app}\FaceInsight.exe"
