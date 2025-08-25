#!/usr/bin/env python3
"""
Transfer_files_from_Mega_to_Google_Drive.py

Colab-friendly Python script that can be opened directly in Google Colab (Colab will display .py files as notebooks).

Usage in Colab:
 - Open this file in Colab via the repo link or the README badge.
 - Edit the URL and OUTPUT_PATH variables in the first code cell and run the cells.

This script contains the same robust installation and server-start logic as the notebook but as a script so the repo does not need to keep an .ipynb file.
"""

# %% [markdown]
# # Mega → Google Drive (Colab)
#
# Open this file in Google Colab (File -> Open notebook -> GitHub or use the README badge).
# Edit the `URL` and `OUTPUT_PATH` variables below and run the cells.

# %%
# Colab: Mount Google Drive (optional)
# If you open this file in Google Colab and want downloads saved to Drive,
# run this cell. When not in Colab, this will print a helpful message and continue.
try:
    from google.colab import drive  # type: ignore
    print('Mounting Google Drive at /content/drive')
    drive.mount('/content/drive', force_remount=True)
except Exception as e:
    # Not running inside Colab or google.colab not available.
    print('google.colab not available (not running in Colab):', e)

# %%
import os
import sys
import time
import shutil
import shlex
import subprocess
import contextlib
import urllib.request
from typing import Optional

HOME = os.path.expanduser('~')

# Colab-editable variables: set your MEGA public URL and desired output path here
# In Colab, edit these values and run the cell.
URL: str = ""  # <-- paste MEGA public link here
OUTPUT_PATH: str = ""  # <-- e.g. '/content/drive/MyDrive/MegaDownloads' or leave empty for './downloads'

# %%
def sh(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout


def detect_repo() -> str:
    repo = None
    try:
        kv = {}
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    kv[k] = v.strip('"')
        distro = kv.get('ID', '').lower()
        ver = kv.get('VERSION_ID', '')
        if 'ubuntu' in distro:
            if ver.startswith('22'):
                repo = 'xUbuntu_22.04'
            elif ver.startswith('20'):
                repo = 'xUbuntu_20.04'
        if 'debian' in distro or distro == 'debian':
            if ver.startswith('12'):
                repo = 'Debian_12.0'
            elif ver.startswith('11'):
                repo = 'Debian_11.0'
    except Exception:
        pass
    return repo or 'xUbuntu_22.04'


def install_megacmd():
    if shutil.which('mega-get') and shutil.which('mega-cmd-server'):
        return
    print('Installing MEGAcmd ...')
    repo = detect_repo()
    sh('sudo apt-get update -y')
    sh('sudo apt-get install -y gnupg2 ca-certificates curl apt-transport-https lsb-release')
    sh(f"curl -fsSL https://mega.nz/linux/repo/{repo}/Release.key | gpg --dearmor | sudo tee /usr/share/keyrings/meganz-archive-keyring.gpg >/dev/null")
    sh(f"echo 'deb [signed-by=/usr/share/keyrings/meganz-archive-keyring.gpg] https://mega.nz/linux/repo/{repo}/ ./' | sudo tee /etc/apt/sources.list.d/megacmd.list")
    sh('sudo apt-get update -y')
    out = sh('sudo apt-get install -y megacmd')
    print(out)


def install_megatools():
    if shutil.which('megatools') or shutil.which('megatools-dl'):
        return
    print('Installing megatools (fallback)...')
    sh('sudo apt-get update -y')
    sh('sudo apt-get install -y megatools')


LOG_DIR = '/root/.megaCmd'
LOG_FILE = f'{LOG_DIR}/megacmdserver.log'


def start_megacmd_server(timeout_s: int = 25) -> bool:
    os.makedirs(LOG_DIR, exist_ok=True)
    # Cleanup stale sockets/locks and fix perms
    sh(f'rm -f {LOG_DIR}/megacmd* {LOG_DIR}/*.sock 2>/dev/null || true')
    sh(f'chmod 700 {LOG_DIR} || true')
    sh('pkill -f mega-cmd-server || true')
    env = os.environ.copy()
    env['MEGACMD_CODEPAGE'] = 'UTF-8'
    with open(LOG_FILE, 'a') as lf:
        subprocess.Popen(['bash', '-lc', 'mega-cmd-server --debug-full'], stdout=lf, stderr=lf, env=env)
    t0 = time.time()
    last = ''
    pid_ok = False
    while time.time() - t0 < timeout_s:
        pgrep = subprocess.run(['bash', '-lc', 'pgrep -f "mega-cmd-server( |$)" || true'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        pid_ok = bool(pgrep.stdout.strip())
        p = subprocess.run(['mega-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        last = p.stdout
        if (p.returncode == 0 or 'MEGAcmd' in last) and pid_ok:
            return True
        time.sleep(0.5)
    try:
        tail = sh(f'tail -n 200 {LOG_FILE}')
        print('MEGAcmd server not ready. Log tail:\n', tail)
    except Exception as e:
        print('Could not read server log:', e)
    return False


def unbuffered(proc, stream='stdout'):
    stream = getattr(proc, stream)
    with contextlib.closing(stream):
        newlines = ['\n', '\r\n', '\r']
        while True:
            out = []
            last = stream.read(1)
            if last == '' and proc.poll() is not None:
                break
            while last not in newlines:
                if last == '' and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = ''.join(out)
            yield out


def run_mega_get(url: str, out_path: str) -> int:
    cmd = ["mega-get", url, out_path]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    for line in unbuffered(proc):
        print(line)
    proc.wait()
    return proc.returncode


def transfare(url: str, outpath: str) -> None:
    if not url:
        print('Please provide a MEGA public URL.')
        return
    os.makedirs(outpath, exist_ok=True)
    rc = run_mega_get(url, outpath)
    if rc == 0:
        print('Download completed successfully.')
        return
    print('\nmega-get failed (rc=', rc, '). Retrying after restarting MEGAcmd server...')
    start_megacmd_server()
    rc2 = run_mega_get(url, outpath)
    if rc2 == 0:
        print('Download completed successfully on retry.')
        return
    print('\nMEGAcmd still failing. Trying megatools fallback...')
    install_megatools()
    dl_bin = 'megatools-dl' if shutil.which('megatools-dl') else 'megatools'
    cmd = f"{dl_bin} --path {shlex.quote(outpath)} {shlex.quote(url)}"
    print('Running fallback:', cmd)
    out = sh(cmd)
    print(out)


def main(argv: Optional[list] = None) -> None:
    # CLI-friendly but also works in Colab by editing the URL/OUTPUT_PATH variables above.
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='MEGA public link')
    parser.add_argument('--out', help='Output path', default='downloads')
    args = parser.parse_args(argv)
    url = args.url or URL
    outp = args.out or OUTPUT_PATH or 'downloads'

    # If running in Colab, attempt to install and start MEGAcmd
    if shutil.which('mega-get') is None:
        try:
            install_megacmd()
        except Exception as e:
            print('install_megacmd failed:', e)
    start_megacmd_server()
    transfare(url, outp)


if __name__ == '__main__':
    main()
