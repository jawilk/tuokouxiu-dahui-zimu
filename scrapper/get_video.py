from pytube import YouTube


URL = ''

yt = YouTube(URL)
stream = yt.streams.get_highest_resolution()
stream.download()
