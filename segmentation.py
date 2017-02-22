#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
-- Objet : Découpe et rassemble des segments d'un fichier audio dans un seul
           fichier.
-- Par : Julien Boge
-- Dernière modification : 21.02.17
"""

import sys
import pdb
import os
import shutil
import ast
import argparse
from argparse import RawTextHelpFormatter
import subprocess

sys.tracebacklimit    = 1

# Flags
PRINT_STEPS            = True
PRINT_COMMANDS         = False
PRINT_COMMANDS_OUTPUT  = False

DEFAULT_FORMAT         = "mp4"

FORMAT                 = ""
OUTPUT_FILE_NAME       = ""
OUTPUT_FILE_SUFFIX     = "-summary"
TEMP_DIR_PREFIX        = "._tmp_segmentation_files_"
FORCE_OVERWRITING      = ""

EXTRACTS_LIST          = "extracts.txt"
EXTRACT_PREFIX         = "cut"
FFMPEG_SILENT          = "-loglevel panic "

SEGMENTS_TIMES         = ""
ORIGIN_AUDIO_FILE      = ""
TEMP_DIR               = ""


DESCRIPTION = """
Extract and join segments of audio and/or video file into one single file.

List of segments times must be specified in milliseconds, either
into a list or into a file looking as follow:
0 10340
25789 36400
...
"""

def printerror(message):
    print "Error: {}".format(message)

def printwarning(message):
    print "Warning: {}".format(message)

def execute_command(command):
    if PRINT_COMMANDS:
        print command
    try:
        subprocess.check_call(command.split())
        return True
    except subprocess.CalledProcessError as e:
        print('Exception caught: {}'.format(e))
        return False

def read_segments_times(file):
    """ Retourne une liste à partir du fichier contenant les
    intervalles de temps des segments à extraire. """
    if PRINT_STEPS:
        print "Read segments times from '{}'...".format(file.name)

    times = []
    for line in file:
        line = line.strip().split(' ')
        if not line[0]:
            continue
        line = [float(n)/1000 for n in line]
        times.append({'start': line[0],'end': line[1]})
    return times

def extract_segment(output_file, start_time, end_time):
    """ Sauvegarde dans un fichier à part un extrait du média
    correspondant à l'intervalle de temps specifié. """
    if PRINT_STEPS:
        print "  Extracting from {} to {} (s) ...".\
            format(start_time, end_time)

    command = ("ffmpeg {silent}{force}-i {input} -ss {start} -c copy -to {end}"
               " -f {format} {output}").\
        format(silent=FFMPEG_SILENT, force=FORCE_OVERWRITING,
               input=ORIGIN_AUDIO_FILE, start=start_time, end=end_time,
               format=FORMAT, output=output_file)

    execute_command(command)

def extract_segments(segments_times):
    """ Récupère et sauvegarde les extraits dans le dossier temporaire """
    if PRINT_STEPS:
        print "Extracting from '{}'...".format(OUTPUT_FILE_NAME)

    for i, times in enumerate(segments_times):
        output_file = "{folder}/{name}{id}.{ext}".\
            format(folder=TEMP_DIR, name=EXTRACT_PREFIX, id=i, ext=FORMAT)
        extract_segment(output_file, times['start'], times['end'])

def concat_segments(extracts_number):
    """ Fusionne les fichiers contenant les segments dans un seul fichier """
    if PRINT_STEPS:
        print "Saving media summary into '{}'...".format(OUTPUT_FILE_NAME)

    extracts_list = os.path.abspath("{}/{}".format(TEMP_DIR,EXTRACTS_LIST))

    extracts = ["file '{folder}/{name}{id}.{ext}'".\
                    format(folder=os.path.abspath(TEMP_DIR),
                           name=EXTRACT_PREFIX,
                           id=i, ext=FORMAT)
                 for i in range(0, extracts_number)]

    file = open(extracts_list,"w")
    file.write('\n'.join(extracts))
    file.close()

    command = 'ffmpeg {silent}{force}-f concat -safe 0 -i {file_list} -c copy {output}'.\
        format(silent=FFMPEG_SILENT,force=FORCE_OVERWRITING,
               file_list=extracts_list,output=OUTPUT_FILE_NAME)

    if execute_command(command) and PRINT_STEPS:
        print "Saved!"

def ini():
    # Supprime le dossier temporaire existant
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    # Crée un nouveau dossier temporaire
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def terminate():
    # Supprime le dossier temporaire
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

def main(segments_times):
    # Définition des variables
    fileformat = os.path.splitext(ORIGIN_AUDIO_FILE)[1][1:] # extension du fichier, sans le '.'
    if fileformat:
        filename   = os.path.basename(ORIGIN_AUDIO_FILE).split("." + fileformat)[0]
    else:
        filename   = os.path.basename(ORIGIN_AUDIO_FILE)
        fileformat = FORMAT

    global OUTPUT_FILE_NAME
    global TEMP_DIR

    if OUTPUT_FILE_NAME:
        OUTPUT_FILE_NAME = "{filename}.{format}".\
            format(filename=OUTPUT_FILE_NAME, format=FORMAT)
    else:
        OUTPUT_FILE_NAME = "{filename}{suffix}.{format}".\
            format(filename=filename, suffix=FINAL_FILE_SUFFIX, format=fileformat)

    TEMP_DIR = TEMP_DIR_PREFIX + filename

    ini()
    segments_times = read_segments_times(segments_times)

    # Quitte si aucun segment n'est sélectionné
    if(len(segments_times) == 0):
        printerror("No segment selected for {}!".format(ORIGIN_AUDIO_FILE))
        sys.exit(1)

    # Extrait les segments
    extract_segments(segments_times)

    if len(segments_times) == 1:
        shutil.move("{folder}/{filename}0.{format}".\
                        format(TEMP_DIR,EXTRACTS_NAME,fileformat),
                    OUTPUT_FILE_NAME)
    else:
        concat_segments(len(segments_times))

    terminate()


if __name__ == "__main__":
    """ Traite les arguments & options """
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('audio_file', type=file,
                        help="Specify the audio file to segment")
    parser.add_argument('segments_times', type=argparse.FileType('r'),
                        help="Specify the file containing segments times")
    parser.add_argument('-f','--force', action="store_true",
                        help="Force overwriting existing file")
    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help="Display all informations, steps, and commands")
    parser.add_argument('-q', '--quiet', action="store_true", default=False,
                        help="Program will display only errors")
    parser.add_argument('-n', '--name',
                        help="Define output file name. Erase suffix name")
    parser.add_argument('-s', '--suffix',
                        help="Define the ouput file name's suffix")
    parser.add_argument('--format', default=DEFAULT_FORMAT,
                        help="Define the ouput file format")
    args = vars(parser.parse_args())

    if args['quiet'] and args['verbose']:
        printwarning("can't define both quiet and verbose flags as True."
                     " Will use default flags.")
    elif args['quiet']:
        PRINT_STEPS = PRINT_COMMANDS = PRINT_COMMANDS_OUTPUT = False
    elif args['verbose']:
        PRINT_STEPS = PRINT_COMMANDS = PRINT_COMMANDS_OUTPUT = True
        FFMPEG_SILENT = ""

    if args['force']:
        FORCE_OVERWRITING="-y "

    if args['name']:
        OUTPUT_FILE_NAME   = args['name']
        OUTPUT_FILE_SUFFIX = ""

    if args['suffix'] and args['name']:
        printwarning("can't define both name and suffix, suffix will be ignored")
    elif args['suffix']:
        OUTPUT_FILE_SUFFIX = args['suffix']

    if args['format']:
        FORMAT = args['format']

    ORIGIN_AUDIO_FILE = args['audio_file'].name

    main(args['segments_times'])
