@echo off
cd /d C:\comptext-codex
git tag -a v5.0.1 -m "v5.0.1 - Agent Teams Ready"
git push origin v5.0.1 --force
echo Tag v5.0.1 created and pushed!
