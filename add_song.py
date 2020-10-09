#!/usr/bin/env python3
import argparse
import logging
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET


# Configure these to your preference
WORKING_DIR="/home/ishaheen/temp"  # this dir is created and deleted with every run
MUSIC_DIR="/home/ishaheen/Music/TotesFavMusic"  # final destination of downloaded file
PLAYLIST_LOCATION="/home/ishaheen/Music/TotesFavMusic.xspf"  # location of music playlist


def main():
    args = parse_args()
    setup_logging(args.v)
    download_song(args.url, args.k, args.v)
    insert_into_playlist()
    clean_up()


def parse_args():
    parser = argparse.ArgumentParser(description="Download song at given url and add to playlist")
    parser.add_argument("url", help="url for the song")
    parser.add_argument("-v", action="store_true", help="output more detailed logging statements")
    parser.add_argument("-k", action="store_true", help="keep the video of the song")

    return parser.parse_args()


def setup_logging(verbose):
    logging.getLogger().setLevel("INFO")
    if verbose:
        logging.getLogger().setLevel("DEBUG")


def download_song(url, keep_video, verbose):
    logging.info("Downloading song...")
    
    youtube_dl_args= ["youtube-dl", "--output", f"{WORKING_DIR}/%(title)s.%(ext)s", url]
    if not keep_video:
        youtube_dl_args.extend(["--extract-audio", "--audio-format", "mp3"])
    
    stdout_arg = {"stdout": subprocess.DEVNULL}
    if verbose:
        stdout_arg = {}

    download_process = subprocess.run(youtube_dl_args, **stdout_arg)
   
    if download_process.returncode:
        logging.error("Download failed")
    else:
        logging.info("Download successful")


def insert_into_playlist():
    song_name = next(os.scandir(WORKING_DIR)).name
    song_destination = f"{MUSIC_DIR}/{song_name}"
    shutil.copyfile(f"{WORKING_DIR}/{song_name}", song_destination) 

    ET.register_namespace("", "http://xspf.org/ns/0/")
    playlist = ET.parse(PLAYLIST_LOCATION)
    tracklist = playlist.getroot().find("{http://xspf.org/ns/0/}trackList")
    track = ET.SubElement(tracklist, "track")
    tracklist.insert(0, track)
    location = ET.SubElement(track, "location")
    location.text = f"file://{song_destination}"
    
    playlist.write(PLAYLIST_LOCATION)
    logging.info(f"Inserted {song_name} into playlist")


def clean_up():
    shutil.rmtree(WORKING_DIR)


if __name__ == "__main__":
    main()
