from urllib.parse import quote
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import os
import bypass_arvancloud

def display_movie_table(movie_data):
    table = PrettyTable()
    table.field_names = ["ID", "Type", "Title"]

    for i, movie_id in enumerate(movie_data.keys(), start=1):
        movie_type = movie_data[movie_id]["type"]
        movie_title = movie_data[movie_id]["title"]
        table.add_row([i, movie_type, movie_title])

    print(table)


def get_movie_list(movie_name):
    query = quote(movie_name)
    url = f"https://subf2m.co/subtitles/searchbytitle?query={query[:60]}&l="
    response = bypass_arvancloud.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    movie_id = 0
    
    if response.status_code == 200:
        search_results = soup.find('div', {'class': 'search-result'})
        if search_results:
            movie_data = {}
            for h2 in search_results.find_all('h2'):
                result_type = h2.text.strip()

                # nothing found
                if result_type == "No results found":
                    return None

                for list_item in h2.findNext('ul').find_all('li'):
                    movie_url = "https://subf2m.co" + list_item.findNext('div', {'class': 'title'}).a.get("href")
                    movie_name = list_item.findNext('div', {'class': 'title'}).a.text.strip()
                    movie_data[movie_id] = {"type": result_type, "link": os.path.basename(movie_url), "title": movie_name}
                    movie_id += 1
            return movie_data

    return None


def search_movie(name="", forced='n'):
    while True:
        if not name or forced == 'n':
            name = input(f"Please enter a valid movie name manually:\nName: ").strip().lower()
        movie_data = get_movie_list(name)
        if movie_data:
            if len(movie_data) > 1:
                print("Multiple movies found. Please select one:")
                while True:
                    display_movie_table(movie_data)
                    try:
                        selected_index = int(input("Enter the index of the movie you want to select (0 to cancel): ")) - 1
                    except Exception as e:
                        # invalid selection
                        selected_index = -2

                    if selected_index >= 0 and selected_index < len(movie_data):
                        selected_movie_id = list(movie_data.keys())[selected_index]
                        selected_movie = movie_data[selected_movie_id]
                        return selected_movie
                    elif selected_index == -1:
                        return None
                    else:
                        print("Invalid selection.")
            else:
                selected_movie_id = list(movie_data.keys())[0]
                selected_movie = movie_data[selected_movie_id]
                return selected_movie
        else:
            print("Movie not found.")
            # stop failed forced movie
            forced="n"