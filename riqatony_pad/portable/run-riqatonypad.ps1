$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& python (Join-Path $Root "app.py") @args
exit $LASTEXITCODE
