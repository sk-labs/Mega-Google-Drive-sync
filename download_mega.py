#!/usr/bin/env python3
"""
download_mega.py - small local helper to download a MEGA public link using MEGAcmd.
Usage: python download_mega.py <mega-link> [output_path]
"""
import sys
import os
import subprocess
import shutil


def sh(cmd):
    return subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_mega.py <mega-link> [output_path]")
        return
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'downloads'
    os.makedirs(out, exist_ok=True)
    if not shutil.which('mega-get'):
        print('MEGAcmd (mega-get) not found on PATH. Install from https://mega.nz/cmd and try again.')
        return
    print('Starting download...')
    print(sh(f"mega-get {url} {out}"))


if __name__ == '__main__':
    main()
