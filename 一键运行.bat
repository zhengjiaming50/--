@echo off
cd code
for %%f in (*.py) do (
    echo Running %%f...
    python %%f
)
pause