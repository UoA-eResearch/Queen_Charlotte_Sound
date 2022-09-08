#!/usr/bin/env python3

# This script uses Dropbox's Python API to fetch shared links for each file in a shared folder

from dropbox import Dropbox
from dropbox.files import SharedLink, FolderMetadata
import os
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

# From https://www.dropbox.com/developers/apps
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]
SHARED_LINK = "https://www.dropbox.com/sh/ct1wvq1ujz44nsz/AADGZHF3HVaUYiZfzGY0iTZua?dl=0"
dbx = Dropbox(DROPBOX_TOKEN)

files = []
def get_files(folder = ""):
    folder_result = dbx.files_list_folder(folder, shared_link = SharedLink(SHARED_LINK))
    print(f"Found {len(folder_result.entries)} files in {folder}")
    assert not folder_result.has_more
    for item in folder_result.entries:
        if type(item) == FolderMetadata:
            get_files("/" + folder + "/" + item.name)
        else:
            files.append(folder + "/" + item.name)

get_files()

def get_shared_link(file):
    return dbx.sharing_get_shared_link_metadata(SHARED_LINK, file).url.replace("https://www", "https://dl") + "\n"

results = thread_map(get_shared_link, files)
with open("dropbox_links.txt", "w") as f:
    f.writelines(results)