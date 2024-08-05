brew list libvmaf
find "outputPath" -name "vmaf_v0.6.1.pkl"
ffmpeg -i input.mp4 -i output.mp4 -lavfi libvmaf="model_path=/path/model/vmaf_v0.6.1.pkl" -f null -
