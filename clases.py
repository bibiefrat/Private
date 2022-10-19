import StringIO
import re
from collections import defaultdict
data = """
Joy Division - Love Will Tear Us Apart
Joy Division - New Dawn Fades
Pixies - Where Is My Mind
Pixies - Hey
Genesis - Mama
"""

song_re = re.compile('(?P<artist>.*) - (?P<song>.*)')

class MusicFile:
    def __init__(self, input):
        self.artists_data = defaultdict(Artist)
        for line in StringIO.StringIO(input):
            data = song_re.search(line)
            if data is not None:
                artist = data.group('artist')
                song = data.group('song')
                self.artists_data[artist].add_song(song)

    def __getitem__(self, item):
        return self.artists_data[item]

    def artist(self, name):
        return self.artists_data[name]

class Artist:
    def __init__(self):
        self.songs = []

    def add_song(self, name):
        self.songs.append(name)


music = MusicFile(data)
print(music['Joy Division'].songs)













