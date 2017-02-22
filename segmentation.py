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

DESCRIPTION = """
Extract and join segments of audio and/or video file into one single file.

List of segments times must be specified in milliseconds, either
into a list or into a file looking as follow:
0 10340
25789 36400
...
"""

# Flags
PRINT_STEPS            = True
PRINT_COMMANDS         = False
PRINT_COMMANDS_OUTPUT  = False

DEFAULT_FORMAT         = "mp4"
FINAL_FILE_SUFFIX      = "-summary"
FINAL_FILE_DESTINATION = ""
TEMP_DIR_PREFIX        = "._tmp_segmentation_files_"
SEGMENTS_FILES_LIST    = "segment_files_list.txt"
FFMPEG_SILENT          = "-loglevel panic"
FORCE_OVERWRITING      = ""


def printerror(message):
    print "Error: {}".format(message)

def printwarning(message):
    print "Warning: {}".format(message)

def check_file_exists(filepath):
    """ Si le fichier n'existe pas, affiche un message d'erreur
    et quitte le programme """
    if not os.path.isfile(filepath):
        printerror("file '{}' doesn't exist".format(filepath))
        sys.exit(1)

def get_segments_times(file):
    """ Retourne une liste à partir du fichier contenant les
    intervalles de temps des segments à extraire. """
    if PRINT_STEPS:
        print "Get segments from '{}'...".format(file.name)

    times = []
    for line in file:
        line = line.strip().split(' ')
        if not line[0]:
            continue
        line = [float(n)/1000 for n in line]
        times.append([line[0],line[1]])
    return times

def extract_segment(filepath,output_file,format,start_time,end_time):
    """ Sauvegarde dans un fichier à part un extrait du média
    correspondant à l'intervalle de temps specifié. """
    if PRINT_STEPS:
        print "  Extracting from {} to {} (s)...".format(start_time, end_time)

    command = ("ffmpeg {silent} {force} -i {input} -ss {start} -c copy -to {end}"
               " -f {format} {output}").\
        format(silent=FFMPEG_SILENT, force=FORCE_OVERWRITING,
               input=filepath, start=start_time, end=end_time,
               format=format, output=output_file)

    if(PRINT_COMMANDS):
        print command

    try:
        subprocess.check_call(command.split())
    except subprocess.CalledProcessError as e:
        print('Exception caught: {}'.format(e))

def extract_segments(filepath,folder,ext,segments_times):
    """ Créer un dossier temporaire et y stocke les extraits. """
    if PRINT_STEPS:
        print "Extracting segments from '{}'...".format(filepath)

    # Supprime le dossier temporaire existant
    if os.path.exists(folder):
        shutil.rmtree(folder)
    # Crée un nouveau dossier temporaire
    if not os.path.exists(folder):
        os.makedirs(folder)

    number = 0
    for times in segments_times:
        output_file = folder + "/cut" + str(number) + "." + ext
        extract_segment(filepath,output_file,ext,times[0],times[1])
        number += 1
    return number

def concat_segments(folder,number,ext,output_file):
    """ Fusionne les fichiers contenant les segments dans un seul fichier """
    if PRINT_STEPS:
        print "Saving media summary into '{}'...".format(output_file)

    segments_list = folder + "_" + SEGMENTS_FILES_LIST

    # Supprime le fichier contenant la liste des chemins vers les segments
    if os.path.isfile(segments_list):
        os.remove(segments_list)

    segments = ["file '" + folder + "/cut" + str(i) + "." + ext\
                for i in range(0, number)]

    file = open(segments_list,"w")
    file.write('\n'.join(segments))
    file.close()

    command = 'ffmpeg {silent} {force} -f concat -i {list} -c copy {output}'.\
        format(silent=FFMPEG_SILENT,force=FORCE_OVERWRITING,
               list=segments_list,output=output_file)

    if(PRINT_COMMANDS):
        print command

    try:
        subprocess.check_call(command.split())
    except subprocess.CalledProcessError as e:
        print('Exception caught: {}'.format(e))

    if PRINT_STEPS:
        print "Saved!"

    # Supprime le fichier contenant la liste des chemins vers les segments
    if os.path.isfile(segments_list):
        os.remove(segments_list)

    # # Supprime le dossier temporaire
    if os.path.exists(folder):
        shutil.rmtree(folder)

def main(filepath,segments_times):
    # Définition des variables
    fileformat = os.path.splitext(filepath)[1][1:] # extension du fichier (sans le '.')
    if fileformat:
        filename = os.path.basename(filepath).split("." + fileformat)[0]
    else:
        fileformat = DEFAULT_FORMAT
        filename   = os.path.basename(filepath)

    global FINAL_FILE_DESTINATION

    if not FINAL_FILE_DESTINATION:
        FINAL_FILE_DESTINATION = filename + FINAL_FILE_SUFFIX + "." + fileformat
    tmp_dir = TEMP_DIR_PREFIX + filename

    # Verifie que le fichier existe
    check_file_exists(filepath)

    # Quitte si aucun segment n'est sélectionné
    if(len(segments_times) == 0):
        printerror("No segment selected for {}!".format(filepath))
        sys.exit(1)

    if(len(segments_times) == 1):
        extract_segment(audio_filepath, FINAL_FILE_DESTINATION, fileformat,
                        segments_times[0][0], segments_times[0][1])
        return

    # Extrait les segments
    number = extract_segments(audio_filepath,tmp_dir,fileformat,segments_times)

    # Assemble les extraits
    concat_segments(tmp_dir,number,fileformat,FINAL_FILE_DESTINATION)


if __name__ == "__main__":
    """ Traite les arguments & options """
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('audiofile', nargs=1,
                        help='Specify the audio file')
    parser.add_argument('-f','--force', action="store_true",
                        help='Force overwriting existing file')
    parser.add_argument('--file', type=argparse.FileType('r'),
                        help='Specify the file containing segments times')
    parser.add_argument('--list', nargs=1,
                        help='Specify the list containing segments times !! NOT FUNCTIONNAL YET !!')
    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help='Display all informations, steps, and commands')
    parser.add_argument('-q', '--quiet', action="store_true", default=False,
                        help='Program will display only errors')
    parser.add_argument('-d', '--destination', nargs=1,
                        help='Define result file destination')
    parser.add_argument('-s', '--suffix', nargs=1,
                        help='Define a suffix for final file name')
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
        FORCE_OVERWRITING="-y"

    if not args['file'] and not args['list']:
        printerror("Must specify a file or a list argument containing times segments")
        sys.exit(1)
    elif args['file']:
        segments_times = get_segments_times(args['file'])
    else:
        printerror("Segments times sent as list argument isn't currently functionnal. Exit.")
        sys.exit(1)
        # segments_times = ast.literal_eval(args['list'])

    if args['destination']:
        FINAL_FILE_DESTINATION = args['destination']
    if args['suffix']:
        FINAL_FILE_SUFFIX = args['suffix']

    audio_filepath = ''.join(args['audiofile'])  # nom du fichier audio d'origine

    main(audio_filepath,segments_times)
