for file in *.mov; do
  base="${file%.mov}"
  ffmpeg -y -i "$file" -c:v libx265 -b:v 1500k -x265-params pass=1 -an -f null /dev/null && \
  ffmpeg -i "$file" -c:v libx265 -b:v 1500k -x265-params pass=2 -c:a copy "../output/${base}.mp4"
done
