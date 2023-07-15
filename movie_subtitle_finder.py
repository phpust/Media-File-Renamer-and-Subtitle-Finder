import requests
from bs4 import BeautifulSoup
import colorama
from colorama import Fore, Style
import zipfile
import io
from prettytable import PrettyTable
import textwrap
import sys
import os
import re
import imageio
import shutil
import subprocess
from utils import file_helpers
import search_movie
import bypass_arvancloud

def get_subtitles_list(movie_slug, language):
    # Create movie URL
    search_url = f"https://subf2m.co/subtitles/{movie_slug}/{language}"
    
    # Send a GET request to the search URL
    response = bypass_arvancloud.get(search_url)
    if response.status_code == 503:
        # movie does not found
        raise Exception("movie does not found") 
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        subtitle_entries = soup.find("ul", "larglist").find_all("li", "item")
    except Exception as e:
        # movie found but there is no subtitle for this language
        subtitle_entries = []
    

    subtitles = []
    for index, row in enumerate(subtitle_entries):
        # Extract subtitle details: title and download link
        title = ' | '.join(x.text.strip() for x in row.find("ul", "scrolllist").find_all("li"))
        download_link = "https://subf2m.co" + row.find("a", "download").get("href")
        subtitles.append((index + 1, title, download_link))

    return subtitles

def choose_subtitles(subtitles, fixed_subtitle_choice, language):

    selected_subtitles = []
    error_in_fixed_subtitle_choice = False

    while True:
        # Create a table to display the available subtitles
        table = PrettyTable()
        table.field_names = ["ID", "Title"]
        table.align["ID"] = "l"
        table.align["Title"] = "l"
        maximun_width = 100

        for index, subtitle in enumerate(subtitles):
            # Determine the color for the row based on the index
            row_color = Fore.CYAN if index % 2 == 0 else Fore.GREEN

            # Wrap the title based on the "|" character and Create a multiline string for the wrapped title
            multiline_title = subtitle[1].split("| ")

            # Add the row to the table with the appropriate color
            if len(multiline_title) > 1:
                # If the title is wrapped into multiple lines
                for line_index, line in enumerate(multiline_title):
                    # Colorize each line with the row color
                    if line_index==0:
                        colored_line1 = f"{row_color}{str(subtitle[0])}{Style.RESET_ALL}"
                    else:
                        colored_line1 = ""
                    colored_line2 = f"{row_color}{line}{Style.RESET_ALL}"
                    table.add_row([colored_line1, colored_line2])

            else:
                # If the title is not wrapped, add the row with the row color
                table.add_row([row_color + str(subtitle[0]) + Style.RESET_ALL, row_color + str(subtitle[1]) + Style.RESET_ALL ])

            # Add a dashed line after each row (except the last row)
            if index < len(subtitles) - 1:
                table.add_row([ "-" * 3 , "-" * (maximun_width + 3) ])

        if fixed_subtitle_choice and fixed_subtitle_choice != "q" and not error_in_fixed_subtitle_choice:
            choice = fixed_subtitle_choice
        else:
            print(table)

            print(f"\nSelected subtitles: {', '.join([subtitle[1] for subtitle in selected_subtitles])}")

            print(f"\nSelect the subtitles you want to download {language}:")
            print("Enter the IDs separated by commas (e.g., 1, 3, 4), or choose:")
            print("a. All subtitles")
            print("q. Quit")
            choice = input("Your choice: ").strip().lower()

        if choice == "a":
            selected_subtitles = subtitles.copy()
            break

        if choice == "q":
            break

        try:
            ids = [int(id.strip()) for id in choice.split(",")]
            selected_subtitles.extend([subtitle for subtitle in subtitles if subtitle[0] in ids and subtitle not in selected_subtitles])
            if not selected_subtitles:
                raise ValueError("not valid ids") 
            break
        except ValueError:
            print ( f"{choice} is not a valid choice" )
            error_in_fixed_subtitle_choice = True
        pass

    return selected_subtitles

def get_parent_folder(path):
    # Get the one top-level parent folders
    return os.path.dirname(path) 

def download_subtitle(download_link_id, language, movie_file_path, download_history_choice):
    # Check if the subtitle has already been downloaded
    downloaded_subtitles = set()
    downloaded_file = os.path.join(get_parent_folder(movie_file_path), f".{language}.downloaded" )
    
    if os.path.exists(downloaded_file):
        with open(downloaded_file, "r") as f:
            downloaded_subtitles = set(f.read().splitlines())

    # [skip] already downloaded
    if download_history_choice=="s" and download_link_id in downloaded_subtitles:
        print(f"{Fore.GREEN}[Skipping] -> Subtitle {download_link_id} already downloaded.{Style.RESET_ALL}")
        return

    # [ask] do you want to download again?
    if download_history_choice=="q" and download_link_id in downloaded_subtitles:
        print(f"{Fore.YELLOW}Already downloaded. should i SKIP downloading {download_link_id} again ?(y/n){Style.RESET_ALL}")
        choice = input(f"Yourn Choice?").strip().lower()
        if choice == "y":
            return

    # Send a GET request to the subtitle download link
    response = bypass_arvancloud.get(download_link_id)
    soup = BeautifulSoup(response.content, "html.parser")
    download_link = "https://subf2m.co" + soup.find("div", "download").a.get("href")

    response = bypass_arvancloud.get(download_link)
    # Extract the subtitle file name from the response headers
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        filename_start = content_disposition.index("filename=") + len("filename=") + 1
        filename = content_disposition[filename_start:]
    else:
        filename = "subtitle.zip"

    # Create a temporary directory to extract the subtitle files
    movie_folder_path = os.path.dirname(movie_file_path);
    temp_dir = os.path.join(movie_folder_path, "__temp__")
    os.makedirs(temp_dir, exist_ok=True)
    subtitle_file_path = os.path.join(temp_dir, filename)

    # Save the subtitle file
    with open(subtitle_file_path, "wb") as f:
        f.write(response.content)

    print(f"Subtitle downloaded: {filename}")

    # Extract the subtitle files from the zip
    try:
        with zipfile.ZipFile(subtitle_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Remove the ZIP file
        os.remove(subtitle_file_path)
    except Exception as e:
        print(f"Unable to extract {subtitle_file_path}. Do it Yourself.")



    # Rename the extracted files
    for extracted_file in os.listdir(temp_dir):
        extracted_file_path = os.path.join(temp_dir, extracted_file)
        if os.path.isfile(extracted_file_path):
            new_file_name = "["+language+"] "+ extracted_file
            new_file_path = os.path.join(temp_dir, new_file_name)
            os.rename(extracted_file_path, new_file_path)

    # Move the renamed subtitle files to the movie directory
    for renamed_file in os.listdir(temp_dir):
        renamed_file_path = os.path.join(temp_dir, renamed_file)
        if os.path.isfile(renamed_file_path):
            renamed_dest_path = os.path.join(movie_folder_path, renamed_file)
            shutil.move(renamed_file_path, renamed_dest_path)
            print(f"Subtitle file moved to: {renamed_dest_path}")

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    # Save the downloaded subtitle link
    if download_link_id not in downloaded_subtitles:
        with open(downloaded_file, "a") as f:
            f.write(download_link_id + "\n")
    

    # make sure file is hidden in windows
    subprocess.check_call(["attrib", "+H", downloaded_file])

def get_languages():
    selected_languages = []
    language_choices = [
        "1. farsi_persian", "2. english", "3. arabic", "4. bengali", "5. dutch",
        "6. french", "7. german", "8. hebrew", "9. korean", "10. polish",
        "11. spanish", "12. vietnamese", "13. turkish"
    ] 

    print("Available languages:")
    for language in language_choices:
        print(language)
    choice = input("Please enter the numbers of the languages you want to download subtitles for "
                   "(separated by comma), or 'all' to download all languages, or 'q' to exit: ")

    if choice.lower() == "all":
        selected_languages = [language.split('. ')[1] for language in language_choices]

    if choice.lower() == "q":
        sys.exit(1)

    selected_indices = [int(index) for index in choice.split(",") if index.isdigit()]
    selected_languages.extend([language_choices[index-1].split('. ')[1] for index in selected_indices if 0 < index <= len(language_choices)])


    return selected_languages


def check_movie_file_already_downloaded(folder_name, movie_file_path):
    return file_helpers.check_file_already_contains( file_helpers.get_downloading_file_path(folder_name) , movie_file_path)

def save_downloaded_movie_file(folder_name, movie_file_path):
    try:
        db_for_downloading_file = os.path.join(folder_name, ".downloading")
        file_helpers.hide_file(file_helpers.get_parent_folder(db_for_downloading_file), ".downloading")
        with open(db_for_downloading_file, "a") as f:
            f.write(movie_file_path + "\n")
    except Exception as e:
        print(e)

# args[0] = folder_path
# args[1] = languages
# args[2] = fixed_subtitle_choice
# args[3] = download_history_choice
def handle_movie_and_save_to_dl_list(file_path, *args):
    if file_helpers.is_movie_file(file_path):
        # if there is downloading file then maybe it is downloaded already
        if check_movie_file_already_downloaded(args[0], file_path):
            print(f"[Ignoring] file {file_path} already downloaded.")
            return False
        
        # add movie to downloaded list
        if automated_main(file_path, args[1], args[2], args[3]):
            save_downloaded_movie_file(args[0], file_path)
        
        elif input("do you want to add this movie to downloaded list (y/n): ").strip().lower()=="y":
            save_downloaded_movie_file(args[0], file_path)
    return False

def process_all_files_in_directory(folder_path):
    # check if we were in middle of download and continue
    if file_helpers.file_already_exist_in(folder_path, ".downloading"):
        print("Look like you were in middle of download.")
        print("c. Continue previous downloading")
        print("i. Ignore it and start fresh")
        if input("Your choice: ").strip().lower()=="i":
            # remove downloading file
            file_helpers.delete_file_from(folder_path, ".downloading")

    # default it will download all files
    # check if there is any .downloaded db in folder to ask user about what should we do
    download_history_choice = "a"
    if file_helpers.walk_through(folder_path, file_helpers.is_subtitle_file_downloaded):
        print("Some Movies have download history. choose what to do :")
        print("a. Download subtitles again")
        print("s. Skip them")
        print("q. Ask Every time")
        download_history_choice = input("Your choice: ").strip().lower()

    languages = get_languages()

    print("\nSelect the subtitles you want to download:")
    print("Enter the IDs separated by commas (e.g., 1, 3, 4), or choose:")
    print("a. All subtitles")
    print("q. Ask Every time")

    fixed_subtitle_choice = input("Your choice: ").strip().lower()

    # this will handle folders of movies 
    file_helpers.walk_through(folder_path, handle_movie_and_save_to_dl_list, folder_path, languages, fixed_subtitle_choice, download_history_choice)

    if file_helpers.is_movie_file(folder_path):
        file_path = folder_path
        automated_main(file_path, languages, fixed_subtitle_choice, download_history_choice)
    else:
        print(f"\"{folder_path}\" is not valid.")

def get_movie_page_slug(file_path):
    movie_name=""
    filename =  get_movie_id_from_folder(file_path)
    # Define the regular expression pattern to match the movie name
    pattern = r"^(.*?)\s\(\d{4},.*?\)"
    # Extract the movie name using the pattern
    match = re.search(pattern, filename)
    
    if match:
        movie_name = match.group(1)
    
    movie_slug = get_movie_name_from_user(file_path, movie_name.replace(".", " ").replace("(", " ").replace(")", " ").replace(",", " ").replace("-", " "))
    if not movie_slug:
        # becouse movie not found then finish this search for all languages
        raise Exception("movie not found")

    print(f"movie suggestion {movie_slug}")
    return movie_slug ;

def get_movie_id_from_folder(folder_path):
    return os.path.basename(folder_path)

def get_movie_name_from_user(file_path, movie_name):
    print(f"file full path if helps [ {file_path} ] [ movie name : \"{movie_name}\"]")

    search_result = search_movie.search_movie(movie_name, "forced")
    
    if search_result:
        search_result = search_result['link']
    
    return search_result

def automated_main(file_path, languages, fixed_subtitle_choice, download_history_choice):
    # Initialize colorama on Windows
    colorama.init()
    try:
        movie_slug = get_movie_page_slug(file_path).strip().lower()
    except Exception as e:
        return False
    
    founded = False
    # find the movie url
    for language in languages:
        # Search for subtitles
        subtitles = get_subtitles_list(movie_slug, language)

        if subtitles:
            founded = True
            # Let the user choose subtitles to download
            selected_subtitles = choose_subtitles(list(reversed(subtitles)), fixed_subtitle_choice, language)

            if selected_subtitles:
                # Download and extract the selected subtitles
                for subtitle in selected_subtitles:
                    try:
                        download_subtitle(subtitle[2], language, file_path, download_history_choice)
                    except Exception as e:
                        print(f"CRASHED . IGNORING THIS SUBTITLE.")

            else:
                print(f"No subtitles selected for {movie_name} in {language}.")
        else:
            print("No subtitles found for the given movie and language.")
    return founded