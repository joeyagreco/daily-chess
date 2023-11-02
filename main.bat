@echo off

IF "%1"=="fmt" (
    REM format code
    call :run_fmt
) ELSE IF "%1"=="up-reqs" (
    REM update requirements.txt file automatically
    call :run_up_reqs
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