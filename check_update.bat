@echo off

REM Print starting message
echo Starting the update process...

REM Print the current directory
echo Current directory: %cd%

REM Check for updates and pull the latest changes
echo Fetching and merging updates from the remote repository...
git pull https://github.com/xUDAYx/RDFTeamWorkspace.git

REM Check the exit code of the git pull command
if %errorlevel% neq 0 (
    echo Error: Failed to update the repository.
    pause
    exit /b %errorlevel%
)

REM Print a success message
echo Repository has been successfully updated.

REM Print completion message
echo Update process completed.

pause
