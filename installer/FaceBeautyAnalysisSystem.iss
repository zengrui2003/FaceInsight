[Setup]
AppId={{7A3C23A8-3D8D-4B24-9B77-1A03B4A8B6F1}
AppName=人脸颜值数据分析系统
AppVersion=1.1.0
DefaultDirName={localappdata}\FaceBeautyAnalysisSystem
DefaultGroupName=人脸颜值数据分析系统
OutputDir=output
OutputBaseFilename=FaceBeautyAnalysisSystemSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[InstallDelete]
Type: files; Name: "{app}\config.local.json"
Type: files; Name: "{app}\beauty_analysis.db"

[Files]
Source: "..\dist\FaceBeautyAnalysisSystem\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\人脸颜值数据分析系统"; Filename: "{app}\FaceBeautyAnalysisSystem.exe"
Name: "{userdesktop}\人脸颜值数据分析系统"; Filename: "{app}\FaceBeautyAnalysisSystem.exe"