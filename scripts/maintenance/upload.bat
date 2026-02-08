@echo off
cd /d C:\comptext-codex
twine upload dist/comptext_codex-5.0.1.tar.gz dist/comptext_codex-5.0.1-py3-none-any.whl
echo Upload completed with exit code: %ERRORLEVEL%
pause
