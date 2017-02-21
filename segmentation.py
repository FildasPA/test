#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
-- Object : Découpe et rassemble des segments d'un fichier audio dans un seul
            fichier.
-- By : Julien Boge
-- Last modification : 20.02.17
-- Usage : python Segmentator.py fichier.mp4 segments.txt


"""

import sys
import os.path
from pydub import AudioSegment

SUMMARY_FILE = "_summary"
CUT          = "cut"
EXTENSION    = "mp4"


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

#============================================================================
# ~~~~ Audio ~~~~
#============================================================================

def get_audio_from_file(filepath):
    """ Retourne un objet AudioSegment à partir du fichier audio. N'accepte que
    les fichiers mp4 (pour l'instant).
    """
    print "Get audio content from " + filepath + "..."
    if not EXTENSION in filepath:
        print "Incorrect audio file type"
        sys.exit(1)
    return AudioSegment.from_file(filepath,EXTENSION)

def get_segments_from_file(filepath):
    """ Retourne un array à partir du fichier contenant les segments audio à
    extraire, sous la forme "debut fin", temps en millisecondes.
    Le fichier doit donc se presenter sous la forme:
    0 10000
    35000 48000
    ...
    """
    print "Get segments from " + filepath + "..."
    file = open(filepath,'r')
    content = file.readlines()
    segments = [line.strip().split(' ') for line in content]
    return segments

def get_segment_from_audio(audio,start,end):
    """ Retourne un segment du fichier audio correspondant à l'intervalle de
    temps specifié.
    """
    print "  from " + str(start) + " to " + str(end)
    return audio[start:end]

def get_segments_from_audio(segments_time,audio_origin):
    """ Recupère, assemble et renvoie tous les segments audio specifiés """
    print "Catching audio segments..."
    segments = []
    for time in segments_time:
        segments.append(get_segment_from_audio(audio_origin,int(time[0]),int(time[1])))

    audio_sum = segments[0]
    for segment in segments[1:]:
        audio_sum = audio_sum + segment
    return audio_sum

def main(argv):

    audio_filepath  = argv[0]                               # fichier audio d'origine
    audio_file_name = os.path.basename(audio_filepath)      # nom du fichier
    audio_file_dir  = os.path.dirname(audio_filepath)       # nom du dossier
    audio_file_ext  = os.path.splitext(audio_filepath)[1]   # extension du fichier
    summary_file    = audio_file_name + "-summary" + audio_file_ext
    segments_filepath = argv[1]

    # print "file path: " + audio_filepath
    # print "file name: " + audio_file_name
    # print "file dir: "  + audio_file_dir
    # print "file ext:  " + audio_file_ext
    # print "summary file: " + summary_file

    # Verifie que les fichiers existent
    os.path.isfile(audio_filepath)
    os.path.isfile(segments_filepath)

    # Lit les segments à recuperer
    segments = get_segments_from_file(segments_filepath)

    # Récupère le contenu audio
    audio = get_audio_from_file(audio_filepath)

    # Récupère et assemble les segments audio selectionnés
    audio_summary = get_segments_from_audio(segments,audio)

    # Affiche la durée totale du nouveau contenu audio
    print "new file duration: " + str(audio_summary.duration_seconds)

    # Enregistre le nouveau fichier audio
    print "Saving audio summary into " + summary_file + "..."
    audio_summary.export(summary_file,format=EXTENSION)
    print "Saved!"


if __name__ == "__main__":
    main(sys.argv[1:])
