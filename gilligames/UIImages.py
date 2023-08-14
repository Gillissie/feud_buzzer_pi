from tkinter import *

# Since tkinter/PhotoImage requires that a referene to loaded images be kept (or else they get garbage collected I guess),
# this class acts as a loader for all images used in the UI, and serves up images.
# This allows us to load an image only once, no matter how many times it's used.
# Usage is simple - call UIImages.get("Filename.png") to load & retrieve an image.

class UIImages(object):

    images = {}
    
    @staticmethod
    def get(filename):
        if filename not in UIImages.images:
            UIImages.images[filename] = PhotoImage(file="ui_images/{}".format(filename))
            
        return UIImages.images[filename];