Scripts that modify your photo, used for organized folder name.

# Requirements
[ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/)

For Windows users, you might need to install WSL or Git Bash to run the bash script. This script has not been tested on Windows.

# Usage
1. Create a base folder and name your subfolder in the format "YYYYMMDD title".
2. Grant permission and run the script:
   ```
   chmod 755 /path/to/script.sh
   /path/to/script.sh "/base/folder/name"
   # Optional: Rename files. Change the '-DEVICE_MODEL' to your model or delete the string 
   exiftool -d %Y%m%d_%H%M%S%%-c'-DEVICE_MODEL'.%%e "-filename<DateTimeOriginal" -fileorder DateTimeOriginal FILE/FOLDER
   ```
Enjoy the organized EXIF dates!

Notes: 
1. Modifications are based on the DateTimeOriginal in EXIF. If absent, we use CreateDate instead.
2. Ensure there is a backup for your pictures. You can delete the "-overwrite_original" to reserve original photo.
3. Nested subfolders are not supported.


# Convert Folder Ascending Time

Ordered by filename ([source]((https://photo.stackexchange.com/questions/60342/how-can-i-incrementally-date-photos))).
```
# Set all photos to same date.
exiftool -overwrite_original -datetimeoriginal='2022:06:14 14:10:00' -filemodifydate='2022:06:14 14:10:00' DIR
# Increase time for each file by 10s ordered by file name.
exiftool -overwrite_original '-datetimeoriginal+<0:0:${filesequence}0' '-filemodifydate+<0:0:${filesequence}0' -fileorder filename DIR
```


# Useful Commands

## 1. Basic Usage
Increment 20 seconds by filename
```
exiftool -overwrite_original '-FileModifyDate+<0:0:${FileSequence; $_*=20}' -FileOrder Filename
```

Loose display
```
exiftool -s1 FILE/DIR
```

Only display specified info
```
exiftool -DateTimeOriginal FILE/DIR
```

Assign date to other date
```
exiftool -r -if '$DateTimeOriginal' -P "-AllDates<DateTimeOriginal"  "-FileModifyDate<DateTimeOriginal" FILE
```

## 2. Copying EXIF
Copy exif info from [another file](https://exiftool.org/forum/index.php?topic=11385.0)
```
exiftool.exe -tagsFromFile source.mpeg -FileModifyDate destination.mp4
```

**Compare the Metadata of two Files**
[Source](https://exiftool.org/forum/index.php?topic=3276.0)
```
exiftool a.jpg b.jpg -a -G1 -w txt
diff a.txt b.txt
```

**Copy all tags from another file**
[Source](https://exiftool.org/forum/index.php?topic=12962.msg)
```
exiftool -tagsfromfile A.jpg -all:all B.jpg
```

Copy exif info from another folder with [same name](https://exiftool.org/forum/index.php?topic=10322.0)
```
exiftool -TagsFromFile c:\exiftool\mpg\%f.mpg -FileCreateDate -FileModifyDate c:\exiftool\mp4
```

Copying example from official website: https://exiftool.org/exiftool_pod.html#COPYING-EXAMPLES.

## 3. Other Commands
**Rename file by dates**
```
# Good naming policy avoids EXIF missing forever
exiftool -d %Y%m%d_%H%M%S%%-c'-DEVICE_MODEL'.%%e "-filename<DateTimeOriginal" -fileorder DateTimeOriginal FILE/FOLDER
```

[Categorize by device model](https://exiftool.org/forum/index.php?topic=12361.0)
Surprisingly useful for managing photos from different phones.
```
exiftool "-directory<%d/${model;}" -r .
```