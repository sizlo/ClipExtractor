Clip Extractor
==============

Tool to extract clips from many video files.

Given an input folder, the tool searches recursively for `.clips` files which contain a list of clips to process. The name of the clips file should correspond to the name of the video file it defines clips in, e.g `some_video_file.clips` defines clips from `some_video_file.mp4`.

Each clips file consists of lines of clip definitions. A clip definition is a name, the start time stamp in seconds, and the end time stamp in seconds e.g `my_video_clip 03:12 04:43`.

A manifest file will also be written with the video clips which lists the source video, start timestamp and end timestamp for each clip.

# Dependencies
This tool runs [ffmpeg](https://www.ffmpeg.org/) commands. To install with brew use:

`brew install ffmpeg`

# Usage
`./clip_extractor.py --source SOURCE_FOLDER --output OUTPUT_FOLDER [--name-pattern NAME_PATTERN]`

`SOURCE_FOLDER` is the folder which will be searched recursively for `.clips` files.

`OUTPUT_FOLDER` is the folder where the clips and manifest file will be written.

`NAME_PATTERN` is an optional pattern which will be used when creating the clip file names. The tokens `{source}`, `{name}`, `{start_time}` and `{end_time}` will be replaced with the source video file name, the name of the clip, the start time stamp of the clip and the end time stamp of the clip respectively. The default is `{name}.mp4`.

# Example
`./clip_extractor.py --source ~/Videos/MySnowboardingHoliday --output ~/Videos/SnowboardingClips`