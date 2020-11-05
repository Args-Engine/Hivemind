@echo off

IF NOT DEFINED VS_BASE_PATH (
	FOR /F "tokens=*" %%g IN ('vswhere -latest -property "installationPath"') do (SET VS_BASE_PATH=%%g)
)

IF NOT DEFINED IS_DEVENV (
	@call "%VS_BASE_PATH%\Common7\Tools\vsdevcmd.bat" /no_logo && SET IS_DEVENV=1
)

%*