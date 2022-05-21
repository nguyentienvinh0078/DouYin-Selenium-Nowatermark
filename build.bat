echo build titok Download
pyinstaller download_one.py --onefile --icon=logo.ico
pyinstaller download_multi.py --onefile --icon=logo.ico
pyinstaller VingDownload.py --onefile --icon=logo.ico
pyinstaller TiktokDownload.py --onefile --icon=logo.ico
pyinstaller TiktokDownload_backup.py --onefile --icon=logo.ico
pyinstaller DownloadAPP.py --onefile --icon=logo.ico --noconsole
