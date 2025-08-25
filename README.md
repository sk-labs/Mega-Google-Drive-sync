Hi there! Thank you for visiting this repository

---

# Mega-to-Google-Drive
This repository provides a Python script to transfer files from MEGA to Google Drive.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sk-labs/Mega-Google-Drive-sync/blob/master/Mega_Google_Drive_sync.ipynb)

## Quick start (Google Colab)
1. Open [Google Colab](https://colab.research.google.com)
2. Upload the `Transfer_files_from_Mega_to_Google_Drive.py` file (File → Upload)
3. Edit the `URL` and `OUTPUT_PATH` variables at the top and run the cells
4. Or copy-paste the script content into a new Colab notebook

## Quick start (Local)
```bash
python Transfer_files_from_Mega_to_Google_Drive.py --url "YOUR_MEGA_LINK" --out "downloads"
```  

Notes:
- The script installs MEGAcmd inside Colab and attempts to start its background service; if the service fails in the current Colab runtime the script prints debug logs and automatically tries a megatools fallback.
- For local usage, run `python Transfer_files_from_Mega_to_Google_Drive.py --url <MEGA_LINK> --out <output_path>` after installing MEGAcmd locally.

---

Original project and author credits retained: repository originally shared by the previous username.
