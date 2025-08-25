Hi there! Thank you for visiting this repository

---

# Mega-to-Google-Drive
This repository provides a Colab-friendly Python script to transfer files from MEGA to Google Drive.

[Open in Colab](https://colab.research.google.com/github/sk-labs/Mega-Google-Drive-sync/blob/master/Transfer_files_from_Mega_to_Google_Drive.py)

## Quick start
1. Click the "Open in Colab" link above.  
2. In Colab, edit the `URL` and `OUTPUT_PATH` variables at the top of the opened file and run the cells.  
3. If you want to save downloads to your Google Drive, mount Drive first (there's a cell explaining how in the file).  

Notes:
- The script installs MEGAcmd inside Colab and attempts to start its background service; if the service fails in the current Colab runtime the script prints debug logs and automatically tries a megatools fallback.
- For local usage, run `python Transfer_files_from_Mega_to_Google_Drive.py --url <MEGA_LINK> --out <output_path>` after installing MEGAcmd locally.

---

Original project and author credits retained: repository originally shared by the previous username.
