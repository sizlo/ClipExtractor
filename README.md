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

## Local
You can run this tool locally by installing Python and ffmpeg using the dependency above.
`./clip_extractor.py --source SOURCE_FOLDER --output OUTPUT_FOLDER [--name-pattern NAME_PATTERN] [--encoding-mode ENCODING_MODE] [--verbose]`

`SOURCE_FOLDER` (-s) is the folder which will be searched recursively for `.clips` files.

`OUTPUT_FOLDER` (-o) is the folder where the clips and manifest file will be written.

`NAME_PATTERN` is an optional pattern which will be used when creating the clip file names. The tokens `{source}`, `{name}`, `{start_time}` and `{end_time}` will be replaced with the source video file name, the name of the clip, the start time stamp of the clip and the end time stamp of the clip respectively. The default is `{name}.mp4`.

`ENCODING_MODE` (-e) specifies how ffmpeg will encode the output clips. Allowed values are `copy-codecs` which will copy the audio and video codecs from the source video, and `re-encode` which will encode the clip as an entirely new video file. `copy-codecs` will be faster but may cause issues in some video players, explanation [here](https://stackoverflow.com/a/18449609). The default mode is `re-encode`.

`--verbose` (-v) is used to show the output of ffmpeg, which is hidden by default.

### Example
`./clip_extractor.py --source ~/Videos/MySnowboardingHoliday --output ~/Videos/SnowboardingClips`

## Docker
Alternatively this tool has been adapted slightly to run inside a docker container. This removes the requirement to install Python and ffmpeg locally and can be run inside the container instead. For this to work you need to bind a volume in docker (using the -v) and pairing your local directory to another one mounted in the docker machine. You can then run these through and write files. The only downside to running it this way is that the output need to go inside the main videos folder, although this can be put inside a subfolder if desired.

### Example
In order to build the docker image you can run the following:
`docker build . -t clip-extractor`

Then finally you can run the script to extract clips from your footage:
`docker run -v ~/Videos/MySnowboardingHoliday:/videos clip-extractor -o /videos/output -s /videos`