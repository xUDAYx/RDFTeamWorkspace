@echo off
setlocal enabledelayedexpansion

REM Set the repository URL
set "repo_url=https://github.com/xUDAYx/RDFTeamWorkspace.git"

REM Get the directory of the batch file
set "local_dir=%~dp0"

REM Remove trailing backslash from local_dir
if %local_dir:~-1%==\ set "local_dir=%local_dir:~0,-1%"

echo Local directory: %local_dir%

REM Check if Git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed or not in the system PATH.
    pause
    exit /b 1
)

REM Check if the local directory is a Git repository
if not exist "%local_dir%\.git" (
    echo This directory is not a Git repository. Initializing and cloning the repository...
    git init "%local_dir%"
    git remote add origin %repo_url%
    git fetch origin
    git checkout -b main origin/main
) else (
    REM Change to the local directory
    pushd "%local_dir%"
    
    REM Fetch the latest changes from the remote repository
    git fetch origin
    
    REM Compare local and remote branches
    for /f "tokens=1,2" %%a in ('git rev-list --left-right --count HEAD...origin/main') do (
        set "behind=%%a"
        set "ahead=%%b"
    )
    
    if !behind! gtr 0 (
        echo Updates available. Pulling changes...
        git pull origin main
        echo Local files updated successfully.
    ) else (
        echo Your local repository is up to date.
    )
    
    REM Return to the original directory
    popd
)

echo Script completed.
pause