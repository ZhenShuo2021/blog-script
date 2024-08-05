ffmpeg -i "outputFile" -i "sourceFile" -lavfi libvmaf=log_fmt=json:log_path=output.json -f null -
