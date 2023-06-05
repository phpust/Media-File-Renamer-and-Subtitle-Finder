# Media-File-Renamer-and-Subtitle-Finder
Media File Renamer and Subtitle Finder is free software that basicly is a python scrapper for renaming movies and finding subtitles.

# Installation On Windows
1. create a folder called `subtitle` inside C:/ and extract all files inside it. like follow
![Folder Structure](/Images/1.PNG)
2. type `shell:sendto` inside run and hit enter. copy `renameMovieName.cmd` file from Batches folder into sendto folder. make sure `SCRIPT_PATH` inside the `renameMovieName.cmd` is correct
3. open `http://www.omdbapi.com/apikey.aspx` and get a free api key. ( it will be sent to your email address ). copy apikey to config.env file and replace it with [your-api-key-for-omdb] and save. final result must be like :
`OMDB_API_KEY=sdfksdfn54`
4. right click on a movie file and choose `renameMovieName`. it will show you the available options.