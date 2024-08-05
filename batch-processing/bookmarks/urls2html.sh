#!/bin/bash
#
# Run this script on a file named urls.txt with all your URLs and pipe the output to an HTML file.
# Example: ./convert_url_file.sh > bookmarks.html
# Based on changes from Jan van den Berg: https://j11g.com/2019/08/15/create-a-chrome-bookmark-html-file-to-import-list-of-urls/

echo "<!DOCTYPE NETSCAPE-Bookmark-file-1>"
echo '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
echo '<TITLE>Bookmarks</TITLE>'
echo '<H1>Bookmarks</H1>'
echo '<DL><p>'
  cat urls.txt |
  while read L; do
    echo -n '    <DT><A HREF="';
        echo ''"$L"'">'"$L"'</A>';
  done
echo "</DL><p>"