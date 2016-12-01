import ffmpy

# folder should contain images like: "imageIdentifier0001.png"
def encodeToVideo(imagesLoc, imageIdentifier, file):
    ff = ffmpy.FFmpeg(inputs={"-r 60 -i " + imageIdentifier + "%04d.png -vcodec mpeg4": None}, outputs={file: None})
    ff.run()

