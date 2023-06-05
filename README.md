# Media-File-Renamer-and-Subtitle-Finder
Media File Renamer and Subtitle Finder is free software that basicly is a python scrapper for renaming movies and finding subtitles.
تغییر دهنده نام فیلم ها و زیرنویس یاب یه نرم افزار رایگانه که در اصل اسکرپری هستش که با پایتون نوشته شده.

# Installation On Windows
- create a folder called `subtitle` inside C:/ and extract all files inside it. like follow
- یک پوشه به نام `subtitle` تو درایو C درست کنین و محتوای این ریپازیتوری رو توش بریزید. مثل تصویر زیر:
- 
![Folder Structure](/Images/1.PNG)

- type `shell:sendto` inside run and hit enter. copy `renameMovieName.cmd` file from Batches folder into sendto folder. make sure `SCRIPT_PATH` inside the `renameMovieName.cmd` is correct
- run رو باز کنین . دستور `shell:sendto` رو اجرا کنین تا پوشه مورد نظر باز بشه. فایل  `renameMovieName.cmd` رو از پوشه Batches کپی کنید و تو پوشه sendto بریزید. فایل  `renameMovieName.cmd` رو باز کنین و ببینید آدرس اسکریپت درست باشه.
- open `http://www.omdbapi.com/apikey.aspx` and get a free api key. ( it will be sent to your email address ). copy apikey to config.env file and replace it with [your-api-key-for-omdb] and save. final result must be like :
`OMDB_API_KEY=sdfksdfn54`
- سایت `http://www.omdbapi.com/apikey.aspx` رو بازکنین و درخواست یه apikey بدید تا براتون ایمیل بشه. از تو ایمیل کپی کنین و به جای [your-api-key-for-omdb] تو فایل config.env قرار بدید.  
- right click on a movie file and choose `renameMovieName`. it will show you the available options.
- رو فیلم مورد نظر کلیک راست کنین و از گزینه sendto  گزینه renameMovieName رو انتخاب کنید و بقیه گزینه ها رو اسکریپت ازتون سوال می کنه.
- موفق باشید
