set csvData to "Filename,CreationDate" & linefeed

tell application "Photos"
	set photoList to every media item
	
	repeat with photo in photoList
		set photoName to filename of photo
		set creationDate to date of photo
		
		set creationDateStr to my formatDate(creationDate)
		set csvData to csvData & "\"" & photoName & "\"" & "," & creationDateStr & linefeed
	end repeat
end tell

set filePath to (path to desktop as text) & "photos_metadata.csv"
do shell script "echo " & quoted form of csvData & " > " & quoted form of POSIX path of filePath

-- Handler to format the date as ISO8601 string
on formatDate(thisDate)
	set {year:y, month:m, day:d, hours:h, minutes:min, seconds:s} to thisDate
	set m to text -2 thru -1 of ("0" & (m as integer))
	set d to text -2 thru -1 of ("0" & d)
	set h to text -2 thru -1 of ("0" & h)
	set min to text -2 thru -1 of ("0" & min)
	set s to text -2 thru -1 of ("0" & s)
	return (y & "-" & m & "-" & d & "T" & h & ":" & min & ":" & s)
end formatDate
