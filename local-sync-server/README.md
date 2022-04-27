To set the cronjobs in the device (Coral Dev Board)
1. cd to `local-sync-server` and run: `pwd`
2. run `which python3`
3. With the previous paths in handy, run `crontab -e`. At the end of the file, paste: the time of the cronjobs + the full path of python3 + the full path of the python scripts.
   **You should end up with something like this:**
- \* * * * * /home/joaquinf/.pyenv/shims/python3 /home/joaquinf/Desktop/tic6/local-sync-server/sync_live_metrics.py
- 0 * * * * /home/joaquinf/.pyenv/shims/python3 /home/joaquinf/Desktop/tic6/local-sync-server/sync_hourly_metrics.py
- 0 0 * * * /home/joaquinf/.pyenv/shims/python3 /home/joaquinf/Desktop/tic6/local-sync-server/sync_daily_metrics.py

_Note: times are given in `times.txt` file._