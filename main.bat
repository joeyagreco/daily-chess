@echo off

IF "%1"=="fmt" (
    REM format code
    call :run_fmt
) ELSE IF "%1"=="up-reqs" (
    REM update requirements.txt file automatically
    call :run_up_reqs
) ELSE IF "%1"=="docker-build" (
    REM build docker image
    call :run_docker_build
) ELSE IF "%1"=="docker" (
    REM run docker image
    call :run_docker
) ELSE (
    echo Invalid flag. Please specify a valid flag.
)

:run_fmt
black --config=pyproject.toml .
autoflake --config=pyproject.toml .
REM isort automatically looks for pyproject.toml
isort .
exit /b

:run_up_reqs
pipreqs . --force
exit /b

:run_docker_build
docker build -t daily_chess .
exit /b

:run_docker
docker run daily_chess
exit /b