@echo off
REM Define the GitHub repository URL
set "REPO_URL=https://github.com/xUDAYx/RDFTeamWorkspace.git"

REM Initialize an empty Git repository in the current directory
git init

REM Set the remote repository URL
git remote add origin "%REPO_URL%"

REM Pull the contents of the repository into the current directory
git pull origin main

REM Pause to keep the command prompt window open after execution
pause
