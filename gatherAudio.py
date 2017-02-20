#!/usr/bin/python
#-*- coding: utf-8 -*-

#==============================================================================
#
# Gather
# -- Objet : Rassemble des segments d'un fichier audio dans un seul fichier.
# -- Par : Julien Boge
# -- Dernière modification : 20.02.17
# -- Usage: python gather.py fichier.mp4 segments.txt
#
#==============================================================================

import sys
import os.path
from pydub import AudioSegment

SUMMARY_FILE = "_summary"
EXTENSION    = "mp4"

#============================================================================
# ~~~~ File utils ~~~~
#============================================================================

#----------------------------------------------------------------------------
# * File exists
#----------------------------------------------------------------------------
def file_exists(filepath):
	return os.path.isfile(filepath)

#----------------------------------------------------------------------------
# * Check file exists
#----------------------------------------------------------------------------
def check_file_exists(filepath):
	if not file_exists(filepath):
		print "'" + filepath + "' doesn't exists!"
		sys.exit(1)

#----------------------------------------------------------------------------
# * Get file name
#----------------------------------------------------------------------------
def get_file_name(filepath):
	return filepath.split('/')[-1].split('.')[:-1][0]

#----------------------------------------------------------------------------
# * Get file folder name
#----------------------------------------------------------------------------
def get_file_folder_name(filepath):
	return '/'.join(filepath.split('/')[:-1])

#----------------------------------------------------------------------------
# * Get file extension
#----------------------------------------------------------------------------
def get_file_ext(filepath):
	return '.'.join(filepath.split('.')[:-1])


#============================================================================
# ~~~~ Audio ~~~~
#============================================================================

#----------------------------------------------------------------------------
# * Get audio file
# Retourne un objet AudioSegment à partir du fichier audio. N'accepte que
# les fichiers mp4 (pour l'instant).
#----------------------------------------------------------------------------
def get_audio_from_file(filepath):
	print "Get audio content from " + filepath + "..."
	if not 'mp4' in filepath:
		print "Incorrect audio file type"
		sys.exit(1)
	return AudioSegment.from_file(filepath,EXTENSION)

#----------------------------------------------------------------------------
# * Get segments from file
# Retourne un array à partir du fichier contenant les segments audio à
# extraire, sous la forme "debut fin", temps en millisecondes.
# Le fichier doit donc se presenter sous la forme:
# 0 10000
# 35000 48000
# ...
#----------------------------------------------------------------------------
def get_segments_from_file(filepath):
	print "Get segments from " + filepath + "..."
	file = open(filepath,'r')
	content = file.readlines()
	segments = [line.strip().split(' ') for line in content]
	return segments

#----------------------------------------------------------------------------
# * Get segment from audio
# Retourne un segment du fichier audio correspondant à l'intervalle de temps
# specifié.
#----------------------------------------------------------------------------
def get_segment_from_audio(audio,start,end):
	print '  from ' + str(start) + " to " + str(end)
	return audio[start:end]

#----------------------------------------------------------------------------
# * Get segments from audio
# Recupère, assemble et renvoie tous les segments audio specifiés.
#----------------------------------------------------------------------------
def get_segments_from_audio(segments_time,audio_origin):
	print 'Catching audio segments...'
	segments = []
	for time in segments_time:
		segments.append(get_segment_from_audio(audio_origin,int(time[0]),int(time[1])))

	audio_sum = segments[0]
	for segment in segments[1:]:
		audio_sum = audio_sum + segment
	return audio_sum

#----------------------------------------------------------------------------
# * Main
#----------------------------------------------------------------------------
def main(argv):

	audio = {}
	audio['path'] = argv[0]                                  # fichier audio d'origine
	audio['name'] = get_file_name(audio.get('path'))         # nom du fichier
	audio['dir']  = get_file_folder_name(audio.get('path'))  # nom du dossier
	audio['ext']  = get_file_ext(audio.get('path'))          # extension du fichier

	for s in audio.values():
		print s

	# segments_filepath = argv[1]
	# segments_list

	# audio_file_name    = audio_filepath.split('/')[-1].split('.')[:-1][0]
	# audio_file_dir     = audio_filepath.
	# audio_type         = audio_filepath.split('.')[-1]
	# summary_file       = audio_file_name + "_summary." + audio_type

	# # Verifie que les fichiers existent
	# check_file_exists(audio_filepath)
	# check_file_exists(segments_filepath)

	# # Lit les segments à recuperer
	# segments = get_segments_from_file(segments_filepath)

	# # Récupère le contenu audio
	# audio = get_audio_from_file(audio_filepath)

	# # Récupère et assemble les segments audio selectionnés
	# audio_summary = get_segments_from_audio(segments,audio)

	# # Affiche la durée totale du nouveau contenu audio
	# print "new file duration: " + str(audio_summary.duration_seconds)

	# # Enregistre le nouveau fichier audio
	# print "Saving audio summary into " + summary_file + "..."
	# audio_summary.export(summary_file,format=EXTENSION)
	# print "Saved!"


#----------------------------------------------------------------------------
# * Execute program
#----------------------------------------------------------------------------
if __name__ == "__main__":
	main(sys.argv[1:])
