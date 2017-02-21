#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
-- Object : Découpe et rassemble des segments d'un fichier audio dans un seul
            fichier.
-- By : Julien Boge
-- Last modification : 20.02.17
-- Usage : python segmentator.py fichier.mp4 segments.txt


"""

import sys
import os
import shutil
import subprocess

SUMMARY_FILE      = "_summary"
# CUT               = "cut"
DEFAULT_EXTENSION = "mp4"
SEGMENT_FILES_LIST = "._segment_files_list.txt"


def file_exists(filepath):
    """ File exists """
    return os.path.isfile(filepath)

def check_file_exists(filepath):
    """ Check file exists """
    if not file_exists(filepath):
        print "'" + filepath + "' doesn't exists!"
        sys.exit(1)

def get_file_name(filepath):
    """ Get file name """
    return filepath.split('/')[-1].split('.')[:-1][0]

def get_file_folder_name(filepath):
    """ Get file folder name """
    return '/'.join(filepath.split('/')[:-1])

def get_file_ext(filepath):
    """ Get file extension """
    return filepath.split('.')[-1]

def get_segments_times(filepath):
    """ Retourne un array à partir du fichier contenant les segments audio à
    extraire, sous la forme "debut fin", temps en millisecondes.
    """
    print "Get segments from " + filepath + "..."
    file = open(filepath,'r')
    content = file.readlines()
    segments_times = [line.strip().split(' ') for line in content]
    segments_times = [[int(i) for i in segment] for segment in segments_times]
    return segments_times

def get_segment(filepath,output_file,ext,start_time,end_time):
    """ Retourne un segment du média correspondant à l'intervalle de
    temps specifié.
    """
    # duration = end_time - start_time

    print "Extract from {} to {} (ms)".format(start_time, end_time)

    command = 'ffmpeg -loglevel panic -i {input} -ss {start} -c copy -to {end} -f {ext} {output}'.\
        format(input=filepath, start=start_time,
               end=end_time, ext=ext, output=output_file)

    print command
    # print "into: " + output_file

    try:
        subprocess.check_call(command.split())  # Must split all the arguments.
    except subprocess.CalledProcessError as exp:
        print('Exception caught: {}'.format(exp))

def get_segments_from_audio(segments_time,audio_origin):
    """ Recupère, assemble et retourne tous les segments audio specifiés """
    print "Catching audio segments..."
    segments = []
    for time in segments_time:
        segments.append(get_segment_from_audio(audio_origin,int(time[0]),int(time[1])))

    audio_sum = segments[0]
    for segment in segments[1:]:
        audio_sum = audio_sum + segment
    return audio_sum


def get_segments(filepath,folder,ext,segments_times):
    """ Récupère les segments du média dans des fichiers temporaires
    sauvegardés dans le dossier folder, avant de les assembler dans
    un seul fichier
    """
    segments = []
    for segment_times in segments_times:
        output_file = folder + "/cut" + str(len(segments)) + "." + ext
        segment = get_segment(filepath,output_file,ext,segment_times[0],segment_times[1])
        segments.append(segment)
    return segments

def concat_segments(folder,output_file):
    """ Fusionne les fichiers contenant les segments """
    segments_list = ["file '" + folder + "/" + file + "'"\
                     for file in list(reversed(os.listdir(folder)))]

    # print "files:\n" + segments_list

    file = open("tmp_segments_files","w")
    for segment in segments_list:
        file.write(segment + "\n")
    file.close()

    command = 'ffmpeg -loglevel panic -f concat -i {list} -c copy {output}'.\
        format(list="tmp_segments_files",output=output_file)
    # print "Command:\n" + command
    try:
        subprocess.check_call(command.split())  # Must split all the arguments.
    except subprocess.CalledProcessError as exp:
        print('Exception caught: {}'.format(exp))

    # Supprime le fichier contenant la liste des chemins vers les segments
    if os.path.isfile("tmp_segments_files"):
        os.remove("tmp_segments_files")

def main(argv):

    audio_filepath  = argv[0]                               # fichier audio d'origine
    audio_file_dir  = os.path.dirname(audio_filepath)       # nom du dossier
    ext  = os.path.splitext(audio_filepath)[1][1:]          # extension du fichier
    if not ext:
        ext = DEFAULT_EXTENSION
        audio_file_name = os.path.basename(audio_filepath)
    else:
        audio_file_name = os.path.basename(audio_filepath).split("."+ext)[0] # nom du fichier sans l'extension
    summary_file    = audio_file_name + "-summary." + ext
    segments_filepath = argv[1]
    tmp_dir = "._tmp_segmentation_files_" + audio_file_name

    print "file path: " + audio_filepath
    print "file name: " + audio_file_name
    print "file dir:  "  + audio_file_dir
    print "file ext:  " + ext
    print tmp_dir
    # print "summary file: " + summary_file

    # Verifie que les fichiers existent
    os.path.isfile(audio_filepath)
    os.path.isfile(segments_filepath)

    # Lit les temps des segments à recuperer
    segments_times = get_segments_times(segments_filepath)
    # print segments_times

    # Quitte si aucun segment n'est sélectionné
    if(len(segments_times) == 0):
        print "No segment selected!"
        sys.exit(1)

    # Supprime le dossier temporaire s'il était resté
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    # Crée un nouveau dossier temporaire
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)


    # Récupère le contenu audio
    # audio = get_audio_from_file(audio_filepath)

    # Récupère et assemble les segments audio selectionnés
    # Récupère les segments
    get_segments(audio_filepath,tmp_dir,ext,segments_times)
    concat_segments(tmp_dir,summary_file)

    # audio_summary = get_segments_from_audio(segments,audio)

    # Affiche la durée totale du nouveau contenu audio
    # print "new file duration: " + str(audio_summary.duration_seconds)

    # # Enregistre le nouveau fichier audio
    # print "Saving audio summary into " + summary_file + "..."
    # audio_summary.export(summary_file,format=EXTENSION)
    # print "Saved!"

    # Supprime le dossier temporaire
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
