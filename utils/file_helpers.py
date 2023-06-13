import os
import colorama
from colorama import Fore, Style
import shutil
import subprocess
import re


def is_movie_file(file_path):
    movie_extensions = ['.avi', '.mkv', '.mp4', '.wmv', '.mov', '.flv', '.m4v', '.mpg', '.mpeg', '.3gp', '.vob', '.ts', '.webm', '.ogv', '.m2ts', '.mpe', '.mpv']  
    return any(file_path.lower().endswith(ext) for ext in movie_extensions)

def get_clean_filename(file_path):
	# Split the file name and extension
	name = file_path.strip().lower()
	# replace dot and hyphon with space for readability
	space_list = [".", "-","(", ")",","]
	for word in space_list:
	    name = name.replace(word, " ")
	# possible name that must be removed
	remove_list = ["1080p", "1080","720p", "720","480p", "480","bluray", "brrip","dvdrip", "hdrip","web dl", "hdtv","x264", "x265","yify", "yts","etrg", "ganool","pahe", "rarbg","mkvcage", "amzn", "nf","aac", "ac3","h264","hevc","2ch","subbed"]
	for word in remove_list:
	    name = name.replace(f" {word}", "")

	# Use regular expressions to extract the movie name and year
	match = re.search(r'^(.*?)\s*(\d{4})', name)

	if match:
	    name = f"{match.group(1)} {match.group(2)}"

	return name

def get_year_from_movie_name(name):
	# Use regular expressions to extract the movie name and year
	match = re.search(r'\b\d{4}\b', name)

	if match:
	    return int(match.group())
	
	return None

def get_parent_folder(path):
    return os.path.dirname(path) 


def get_formatted_path_with_merging_check(source_path, formatted_name):
    formatted_parts = formatted_name.split(os.path.sep)
    source_path = get_parent_folder(source_path)

    if check_folder_existence(source_path, formatted_parts[0], 2 ):
        formatted_path = os.path.join(get_parent_folder(get_parent_folder(source_path)), formatted_name)
    elif check_folder_existence(source_path, formatted_parts[0], 1 ):
        formatted_path = os.path.join(get_parent_folder(source_path), formatted_name)
    else:
        formatted_path = os.path.join(source_path, formatted_name)
    return formatted_path


def check_folder_existence(path, folder_name, level):
    # Get the two top-level parent folders
    for i in range(level):
        path = os.path.dirname(path)
        pass

    # Check if the specific folder exists in either of the two parent folders
    folder_path = os.path.join(path, folder_name)

    if os.path.exists(folder_path):
        return True
    return False


def rename_and_move_to_new_path(old_path, new_path):
    # Renamed and moved
    print(f"file renamed and moved to: {new_path}")
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    shutil.move(old_path, new_path)

def create_file_at(folder_path, file_name, file_content):
    try:
        new_file = os.path.join(folder_path, file_name )
        with open(new_file, "a") as f:
            f.write(file_content)
    except Exception as e:
        print(e)

def hide_file(folder_path, file_name):
    try:
        file = os.path.join(folder_path, file_name )
        subprocess.check_call(["attrib", "+H", file])
    except Exception as e:
        print(e)

def file_already_exist(file_path):
    if os.path.exists(file_path):
        return True
    return False

def read_file_contents(file_path):
	with open(os.path.join(folder_path, file_path), "r") as f:
		return f.read().splitlines()

def check_file_already_contains(file_path, content):
    if file_already_exist(file_path):
        contents = read_file_contents(file_path)
        if content in contents:
            return True
    return False

# check if first file is added sooner than the second file
# sometime user may add another movie to another movie folder that has a valid 
# metadata file. so if movie added after metadata file then this movie must be checked again.
def file_added_sooner(file_path, metadata_path):
	return int(os.path.getctime(file_path)) <= int(os.path.getctime(metadata_path))