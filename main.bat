@echo off

IF "%1"=="fmt" (
    REM format code
    call :run_fmt
) ELSE (
    echo Invalid flag. Please specify a valid flag.
)

:run_fmt
black --config=pyproject.toml .
autoflake --config=pyproject.toml .
REM isort automatically looks for pyproject.toml
isort .
exit /b