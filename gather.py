#!/usr/bin/python

#==============================================================================
#
# Gather
# -- Objet : Rassemble des segments d'un fichier audio dans un seul fichier.
# -- Par : Julien Boge
# -- Derniere modification : 20.02.17
# -- Usage: python gather.py fichier.mp4 segments.txt
#
#==============================================================================

import sys
import os.path
from pydub import AudioSegment

SUMMARY_FILE = "_summary"
EXTENSION    = "mp4"

#----------------------------------------------------------------------------
# * File exists
#----------------------------------------------------------------------------
def file_exists(file_path):
	return os.path.isfile(file_path)

#----------------------------------------------------------------------------
# * Check file exists
#----------------------------------------------------------------------------
def check_file_exists(file_path):
	if not file_exists(file_path):
		print "'" + file_path + "' doesn't exists!"
		sys.exit(1)

#----------------------------------------------------------------------------
# * Get audio file
# Retourne un objet AudioSegment a partir du fichier audio. N'accepte que
# les fichiers mp4 (pour l'instant).
#----------------------------------------------------------------------------
def get_audio_from_file(file_path):
	print "Get audio content from " + file_path + "..."
	if not 'mp4' in file_path:
		print "Incorrect audio file type"
		sys.exit(1)
	return AudioSegment.from_file(file_path,EXTENSION)

#----------------------------------------------------------------------------
# * Get segments from file
# Retourne un array a partir du fichier contenant les segments audio a
# extraire, sous la forme "debut fin", temps en millisecondes.
# Le fichier doit donc se presenter sous la forme:
# 0 10000
# 35000 48000
# ...
#----------------------------------------------------------------------------
def get_segments_from_file(file_path):
	print "Get segments from " + file_path + "..."
	file = open(file_path,'r')
	content = file.readlines()
	segments = [line.strip().split(' ') for line in content]
	return segments

#----------------------------------------------------------------------------
# * Get segment from audio
# Retourne un segment du fichier audio correspondant a l'intervalle de temps
# specifie.
#----------------------------------------------------------------------------
def get_segment_from_audio(audio,start,end):
	print '  from ' + str(start) + " to " + str(end)
	return audio[start:end]

#----------------------------------------------------------------------------
# * Get segments from audio
# Recupere, assemble et renvoi tous les segments audio specifies.
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
	audio_file_path    = argv[0]
	segments_file_path = argv[1]

	audio_file_name    = audio_file_path.split('/')[-1].split('.')[:-1][0]
	audio_file_dir     = audio_file_path.split(audio_file_name)[0]
	audio_type         = audio_file_path.split('.')[-1]
	summary_file       = audio_file_name + "_summary." + audio_type

	# Verifie que les fichiers existent
	check_file_exists(audio_file_path)
	check_file_exists(segments_file_path)

	# Lit les segments a recuperer
	segments = get_segments_from_file(segments_file_path)

	# Recupere le contenu audio
	audio = get_audio_from_file(audio_file_path)

	# Recupere et assemble les segments audio selectionnes
	audio_summary = get_segments_from_audio(segments,audio)

	# Affiche la duree totale du nouveau contenu audio
	print "new file duration: " + str(audio_summary.duration_seconds)

	# Enregistre le nouveau fichier audio
	print "Saving audio summary into " + summary_file + "..."
	audio_summary.export(summary_file,format=EXTENSION)
	print "Saved!"


#----------------------------------------------------------------------------
# * Execute program
#----------------------------------------------------------------------------
if __name__ == "__main__":
	main(sys.argv[1:])
