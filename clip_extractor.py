#!/usr/bin/env python3

import argparse
import glob
import os
import subprocess

def LOG(message):
    print(message)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str, help='Source folder to process', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output folder to create clips in', required=True)
    parser.add_argument('--name-pattern', type=str, default='{name}.mp4',
        help='Pattern used for the clip filenames. Allowed tokens are "{source}", "{name}", "{start_time}" and "{end_time}"')
    parser.add_argument('-e', '--encoding-mode', choices=['copy-codecs', 're-encode'], default='re-encode',
        help='The mode ffmpeg uses to encode the output clips, copy-codecs is faster but may cause issues with some video players')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Show ffmpeg output')
    parser.set_defaults(verbose=False)
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
        return glob.glob(os.path.join(source_folder, '**/*.clips'), recursive=True)

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
        extentions_to_try = ['.mp4', '.mov', '.MP4', '.MOV']
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
        output_file_path = os.path.join(self.arguments.output, output_file_name)
        output_file_path = self.index_output_file_path(output_file_path)
        return output_file_path

    def index_output_file_path(self, output_file_path):
        path, extention = os.path.splitext(output_file_path)
        index = 0
        while os.path.isfile(output_file_path):
            index += 1
            output_file_path = f'{path}_{index:03}{extention}'
        return output_file_path

    def convert_clip(self, clip, input_file_path, output_file_path):
        start_seconds = timestamp_to_seconds(clip.start_time)
        end_seconds = timestamp_to_seconds(clip.end_time) + 1
        command = ['ffmpeg', '-i', input_file_path,  '-ss', str(start_seconds) , '-to', str(end_seconds)]
        if self.arguments.encoding_mode == 'copy-codecs':
            command += ['-vcodec', 'copy', '-acodec', 'copy']
        if not self.arguments.verbose:
            command += ['-v', 'quiet']
        command.append(output_file_path)
        subprocess.run(command)

    def write_manifest(self):
        with open(os.path.join(self.arguments.output, 'manifest.txt'), 'w') as file:
            for entry in self.manifest:
                file.write(f'{entry}\n')

if __name__ == '__main__':
    ClipExtractor(parse_arguments()).extract_clips()
