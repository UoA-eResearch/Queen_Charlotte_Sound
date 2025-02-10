#!/usr/bin/env python3

# This script uses Dropbox's Python API to fetch shared links for each file in a folder, recursively

from dropbox import Dropbox
from dropbox.files import FolderMetadata
from dropbox.common import PathRoot
import os
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map, process_map
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# Use rclone to generate a bearer token
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]
dbx = Dropbox(DROPBOX_TOKEN)
print(dbx.users_get_current_account().root_info)
root_namespace_id = dbx.users_get_current_account().root_info.root_namespace_id
print(root_namespace_id)
dbx = dbx.with_path_root(PathRoot.root(root_namespace_id))

files = []

def handle_result(folder, folder_result):
    for item in folder_result.entries:
        if type(item) == FolderMetadata:
            get_files(item.path_display)
        else:
            files.append(item.path_display)

def get_files(folder):
    folder_result = dbx.files_list_folder(folder)
    print(f"Got {len(folder_result.entries)} files from {folder}")
    handle_result(folder, folder_result)
    while folder_result.has_more:
        folder_result = dbx.files_list_folder_continue(folder_result.cursor)
        handle_result(folder, folder_result)

get_files("/Cumulative-effects-data---QCS/Final info")
files = pd.Series(files)
print(files)

def get_shared_link(file):
    return dbx.sharing_create_shared_link(file).url + "&raw=1"

links = thread_map(get_shared_link, files)
df = pd.DataFrame({"path": files, "link": links})
print(df)
df.to_csv("dropbox_links.csv", index=False)