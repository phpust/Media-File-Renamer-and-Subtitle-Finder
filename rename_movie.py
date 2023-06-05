import requests
from urllib.parse import quote
import os
from pathlib import Path
import shutil
import re
from dotenv import load_dotenv

# Get the absolute path of the current Python file
python_file_path = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the config.env file
load_dotenv(os.path.join(python_file_path, "config.env"))

def clean_filename(filename):
    # Define the pattern to match the unwanted characters
    pattern = r'[\\/:*?"<>|]'

    # Use re.sub() to replace the matched characters with an empty string
    cleaned_filename = re.sub(pattern, '', filename)

    return cleaned_filename

def format_film_name_omdb(film_id):
    api_key = os.getenv("OMDB_API_KEY")
    url = f"http://www.omdbapi.com/?apikey={api_key}&i={film_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        film_data = response.json()
        title = film_data.get("Title")
        year = film_data.get("Year")
        director = film_data.get("Director")
        
        formatted_name = clean_filename(f"{title} ({year})")
        if director:
            formatted_name += os.path.sep + clean_filename(f"{title} ({year}, {director})")
        return formatted_name
    
    return None

def search_film_id_imdb(old_name):
    query = quote(old_name)
    url = f"https://v3.sg.media-imdb.com/suggestion/x/{query[:60]}.json"
    response = requests.get(url)
    if response.status_code == 200:
        search_results = response.json().get("d", [])
        if search_results:
            film_data = {}
            for result in search_results:
                film_id = result.get("id")
                film_name = result.get("l")
                film_year = result.get("y")
                film_data[film_id] = {"title": film_name, "year": film_year}
            return film_data
    
    return None


def get_two_top_folder(path):
    # Get the two top-level parent folders
    return os.path.dirname( os.path.dirname(path) )

def get_one_top_folder(path):
    # Get the one top-level parent folders
    return os.path.dirname(path) 

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

def get_formatted_path_with_merging_check(source_path, formatted_name):
    # Split the string by slashes to get individual parts
    formatted_parts = formatted_name.split(os.path.sep)
    source_path = get_one_top_folder(source_path)
    if check_folder_existence(source_path, formatted_parts[0], 2 ):
        formatted_path = os.path.join(get_two_top_folder(source_path), formatted_name)
    elif check_folder_existence(source_path, formatted_parts[0], 1 ):
        formatted_path = os.path.join(get_one_top_folder(source_path), formatted_name)
    else:
        formatted_path = os.path.join(source_path, formatted_name)
    print(f"formated path is {formatted_path}")
    return formatted_path

def rename_and_move_to_new_path(old_path, new_path):
    # Renamed and moved
    print(f"movie renamed and moved to: {new_path}")
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    shutil.move(old_path, new_path)

# fix and rename one movie. only call on movie.
def main(file_path):
    base=os.path.basename(file_path)
    old_name, old_name_extention = os.path.splitext(base)
    choice = input(f"Do you want to change {old_name} for query? (y/n)")
    if choice=="y":
        old_name = input(f"enter movie new name : ")
    film_data = search_film_id_imdb(old_name)
    if film_data:
        if len(film_data) > 1:
            print("Multiple films found. Please select one:")
            for i, film_id in enumerate(film_data.keys()):
                film_name = film_data[film_id]["title"]
                film_year = film_data[film_id]["year"]
                print(f"{i+1}. {film_name} ({film_year})")
            selected_index = int(input("Enter the index of the film you want to select: ")) - 1
            if selected_index >= 0 and selected_index < len(film_data):
                selected_film_id = list(film_data.keys())[selected_index]
                selected_film = film_data[selected_film_id]
                formatted_film_name = format_film_name_omdb(selected_film_id) + old_name_extention
                
                renamed_path = get_formatted_path_with_merging_check(file_path, formatted_film_name)
                rename_and_move_to_new_path(file_path, renamed_path)
            else:
                print("Invalid selection.")
        else:
            selected_film_id = list(film_data.keys())[0]
            selected_film = film_data[selected_film_id]
            formatted_film_name = format_film_name_omdb(selected_film_id) + old_name_extention
            
            renamed_path = get_formatted_path_with_merging_check(file_path, formatted_film_name)
            rename_and_move_to_new_path(file_path, renamed_path)
    else:
        print("Film not found.")