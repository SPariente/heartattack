@echo off
title Heart disease dashboard launcher
echo This will install the required python packages, download the dashboard script, and run it
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install pandas
python3 -m pip install numpy
python3 -m pip install matplotlib
python3 -m pip install plotly_express
python3 -m pip install dash
python3 -m pip install statsmodels
powershell -c "invoke-webrequest 'https://raw.githubusercontent.com/SPariente/heartattack/master/dashboard.py' -outfile ./dashboard.py"
start http://127.0.0.1:8050/
echo --------------------------------------------------
echo Once loaded, refresh the page to see the dashboard
echo --------------------------------------------------
python ./dashboard.py
pause