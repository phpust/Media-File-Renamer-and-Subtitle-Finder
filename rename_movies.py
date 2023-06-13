import requests
from requests.exceptions import Timeout, RequestException
from urllib.parse import quote
import os
from pathlib import Path
import shutil
import re
from dotenv import load_dotenv
from utils import file_helpers
from utils import displayable_path
import colorama
from colorama import init
init()
from colorama import Fore, Style

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

def format_movie_name_omdb(movie_id):
    api_key = os.getenv("OMDB_API_KEY")
    url = f"http://www.omdbapi.com/?apikey={api_key}&i={movie_id}"
    response = requests.get(url)
    
    if response is not None and response.status_code == 200:
        movie_data = response.json()
        title = movie_data.get("Title")
        year = movie_data.get("Year")
        director = movie_data.get("Director")
        
        formatted_name = clean_filename(f"{title} ({year})")
        if director:
            formatted_name += os.path.sep + clean_filename(f"{title} ({year}, {director})")
        return formatted_name
    
    return None

def search_movie_id_imdb(old_name):
    query = quote(old_name)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language" : "en-US,en;q=0.5",
        "Accept-Encoding":"gzip, deflate, br",
        "Connection":"keep-alive",
        "Upgrade-Insecure-Requests":"1",
        "Sec-Fetch-Dest":"document",
        "Sec-Fetch-Mode":"navigate",
        "Sec-Fetch-Site":"none",
        "Sec-Fetch-User":"?1",
        "TE":"trailers"
    }
    url = f"https://v3.sg.media-imdb.com/suggestion/x/{query}.json"
    retry_count = 3
    response = None

    for i in range(retry_count):
        try:
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()  # Check for any HTTP errors
            break  # Exit loop if successful
        except Timeout:
            print("Connection timed out. Retrying...")
            continue  # Try again if timeout occurs
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break  # Exit loop if an error occurs

    year = file_helpers.get_year_from_movie_name(old_name)
    if response is not None and response.status_code == 200:
        search_results = response.json().get("d", [])
        if search_results:
            movie_data = {}
            movie_data_without_year = {}
            for result in search_results:
                # filter only movies
                if result.get("qid") in ["movie", "video", "short", "tvMovie"]:
                    movie_id = result.get("id")
                    movie_name = f"{result.get('l')} ( {result.get('qid')} ) "
                    movie_year = result.get("y")
                    if year is not None and year==movie_year:
                        movie_data[movie_id] = {"title": movie_name, "year": movie_year}
                    else:
                        movie_data_without_year[movie_id] = {"title": movie_name, "year": movie_year}

            movie_data.update(movie_data_without_year)
            return movie_data
    
    return None

# fix and rename one movie. only call on movie.
def one_movie(file_path, automatic=False):
    base=os.path.basename(file_path)
    print(f"{Fore.GREEN}  File Name : {base}  {Style.RESET_ALL}")
    old_name, old_name_extention = os.path.splitext(base)
    old_name = file_helpers.get_clean_filename(old_name)
    if not automatic:
        print(f"Do you want to change movie name for better result (current name : \"{old_name}\") ?")
        print(f"choose between this three option :")
        print(f"1. change movie name")
        print(f"2. skip it. move to next movie")
        print(f"Anything else would be default search")
        choice = input("Your choice: ").strip().lower()
        if choice=="1":
            old_name = input(f"Enter movie name : ")
        elif choice=="2":
            print(f"Renaming movie {old_name} skipped.")
            return
    movie_data = search_movie_id_imdb(old_name)
    if movie_data:
        if len(movie_data) > 1:
            print("Multiple movies found. Please select one:")
            for i, movie_id in enumerate(movie_data.keys()):
                movie_name = movie_data[movie_id]["title"]
                movie_year = movie_data[movie_id]["year"]
                print(f"{i+1}. {movie_name} ({movie_year})")
            selected_index = input("Enter the index of the movie you want to select: ")
            if len(selected_index) > 0 :
                selected_index = int(selected_index) - 1
            else:
                selected_index = -1
        else:
            # select the only existing result automaticaly
            selected_index = 0

        if selected_index >= 0 and selected_index < len(movie_data):
            selected_movie_id = list(movie_data.keys())[selected_index]
            selected_movie = movie_data[selected_movie_id]
            formatted_movie_name = format_movie_name_omdb(selected_movie_id) + old_name_extention
            
            renamed_path = file_helpers.get_formatted_path_with_merging_check(file_path, formatted_movie_name)
            if file_helpers.rename_and_move_to_new_path(file_path, renamed_path) :
                # add imdbID file to metadata file.
                file_helpers.create_file_at(file_helpers.get_parent_folder(renamed_path), ".metadata", selected_movie_id)
                file_helpers.hide_file(file_helpers.get_parent_folder(renamed_path), ".metadata")
        else:
            print("Invalid selection.")
    else:
        print("movie not found.")



def main(folder_path):
    print(f"How do you want to do rename ?")
    print(f"choose between this three option :")
    print(f"1. Automaticaly ")
    print(f"2. Supervision")
    print(f"3. Show File Tree")
    choice = input("Your choice: ").strip().lower()
    if choice=="1":
        choice = True
    elif choice=="2":
        choice = False
    else:
        paths = displayable_path.DisplayablePath.make_tree(Path(folder_path), criteria=file_helpers.is_not_hidden_and_is_movie)
        for path in paths:
            print(path.displayable())
        return
    # handle folder of movies
    if os.path.isdir(folder_path):
        for root, directories, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                metadata_path = os.path.join(root, ".metadata")
                if file_helpers.is_movie_file(file_path):
                    print(f"{Fore.GREEN} *********************** Analyzing... *********************** {Style.RESET_ALL}")
                    # if metadata does exist and created after movie created.
                    if file_helpers.file_already_exist(metadata_path) and file_helpers.file_added_sooner(file_path, metadata_path):
                        print(f"{file_path} Already processed. Ignoring.")
                        continue
                    one_movie(file_path, choice)
    # handle only one movie file
    elif file_helpers.is_movie_file(folder_path):
        file_path = folder_path
        metadata_path = os.path.join(file_helpers.get_parent_folder(file_path), ".metadata")

        # if metadata does exist and created after movie created.
        if file_helpers.file_already_exist(metadata_path) and file_helpers.file_added_sooner(file_path, metadata_path):
            print(f"{file_path} Already processed. Ignoring.")
            return
        one_movie(file_path, choice)
    # selected file is not valid movies
    else:
        print(f"\"{folder_path}\" is not valid movie.")