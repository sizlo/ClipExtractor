#!/usr/bin/env python3

import argparse
import glob
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def LOG(message):
    print(message)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, help='Source folder to process', required=True)
    parser.add_argument('--output', type=str, help='Output folder to create clips in', required=True)
    parser.add_argument('--name-pattern', type=str, default='{name}.mp4',
        help='Pattern used for the clip filenames. Allowed tokens are "{source}", "{name}", "{start_time}" and "{end_time}"')
    return parser.parse_args()

def timestamp_to_seconds(time_stamp):
    minutes, seconds = time_stamp.split(':')
    return (int(minutes) * 60) + int(seconds)

class Clip:
    def __init__(self, string_definition):
        self.name, self.start_time, self.end_time = string_definition.split(' ')

    def __str__(self):
        return f'name: {self.name}, start_time: {self.start_time}, end_time: {self.end_time}'

class ManifestEntry:
    def __init__(self, output_file, source_file, clip):
        self.output_file = output_file
        self.source_file = source_file
        self.clip = clip

    def __str__(self):
        result = ''
        result += f'{self.output_file}\n'
        result += f'  source: {self.source_file}\n'
        result += f'  name: {self.clip.name}\n'
        result += f'  start_time: {self.clip.start_time}\n'
        result += f'  end_time: {self.clip.end_time}\n'
        return result

class ClipExtractor:
    def __init__(self, arguments):
        self.arguments = arguments
        self.manifest = []

    def extract_clips(self):
        if not os.path.isdir(self.arguments.output):
            os.makedirs(self.arguments.output)
        meta_files = self.find_meta_files(self.arguments.source)
        self.process_files(meta_files)
        self.write_manifest()

    def find_meta_files(self, source_folder):
        return glob.glob(source_folder + '**/*.clips', recursive=True)

    def process_files(self, files):
        for file in files:
            self.process_file(file)

    def process_file(self, meta_file_path):
        LOG(f'Processing file {meta_file_path}')
        clips = self.get_clips_from_file(meta_file_path)
        video_file_path = self.find_video_file(meta_file_path)
        for clip in clips:
            self.process_clip(clip, video_file_path)

    def get_clips_from_file(self, file_path):
        with open(file_path) as file:
            lines = file.read().splitlines()
        return [Clip(line) for line in lines]

    def find_video_file(self, meta_file_path):
        extentions_to_try = ['.mp4', '.mov']
        for extention in extentions_to_try:
            video_file_path = os.path.splitext(meta_file_path)[0] + extention
            if os.path.isfile(video_file_path):
                return video_file_path

    def process_clip(self, clip, input_file_path):
        LOG(f'  Processing clip <{clip}>')
        output_file_path = self.get_output_file_path(clip, input_file_path)
        self.convert_clip(clip, input_file_path, output_file_path)
        self.manifest.append(ManifestEntry(output_file_path, input_file_path, clip))

    def get_output_file_path(self, clip, input_file_path):
        source_file_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_name = self.arguments.name_pattern.replace('{source}', source_file_name).replace('{name}', clip.name).replace('{start_time}', clip.start_time).replace('{end_time}', clip.end_time)
        return os.path.join(self.arguments.output, output_file_name)

    def convert_clip(self, clip, input_file_path, output_file_path):
        ffmpeg_extract_subclip(input_file_path,
            timestamp_to_seconds(clip.start_time),
            timestamp_to_seconds(clip.end_time),
            targetname=output_file_path)

    def write_manifest(self):
        with open(os.path.join(self.arguments.output, 'manifest.txt'), 'w') as file:
            for entry in self.manifest:
                file.write(f'{entry}\n')

if __name__ == '__main__':
    ClipExtractor(parse_arguments()).extract_clips()
