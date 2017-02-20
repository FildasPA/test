# Rapport - Julien Boge

# Découper et assembler des segments d'un fichier audio dans un nouveau fichier

Libraire utilisée: https://github.com/jiaaro/pydub

Voir l'[installation](https://github.com/jiaaro/pydub#installation)

Paramètres du programme:
- le chemin vers le fichier audio
- le chemin vers un fichier contenant les intervalles de temps à récupérer. Cet intervalle est de la forme `debut fin`, debut et fin en millisecondes.

Sortie:
Le nouveau fichier audio est enregistré dans le répertoire courant avec pour nom le nom du fichier audio d'origine plus '_summary' avant l'extension.

Exemple d'utilisation:

```
python gather.py chemin_fichier_audio.mp4 segments.txt
```
Le fichier segments.txt qui se trouve plus bas récupère les segments allant de 4s à 10s, de 20 à 30s, et de 45,26 à 49,01s. Le fichier en sortie sera: chemin_fichier_audio_summary.mp4

