# mkdir -p ../output

for file in *.mov; do
    ffmpeg -i "$file" -c:v libx265 -tag:v hvc1 -crf 28 "../output/${file%.mov}.mp4"
done
