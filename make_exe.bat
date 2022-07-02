@echo off

ECHO --- Creating exe file ---
ECHO (make sure you have "venv" folder with pyinstaller in project root)


SET SCRIPTPATH=%~dp0

rem ECHO %SCRIPTPATH%
ECHO - removing old dist folder
rmdir /s /q "%SCRIPTPATH%\dist"

ECHO - generating executable, please wait ...
%SCRIPTPATH%\venv\Scripts\pyinstaller.exe label_maker.py -F --log-level=WARN --name label_maker > nul

rem copy the created executable
xcopy /i /y "%SCRIPTPATH%\dist\label_maker.exe" "%SCRIPTPATH%" > nul

rem remove build files
cd %SCRIPTPATH%
@RD /S /Q "%SCRIPTPATH%\dist" > nul
@RD /S /Q "%SCRIPTPATH%\build" > nul

ECHO -- Executable generated
