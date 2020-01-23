'''
Created on 08.09.2018

@author: Phil
'''
from pocketsphinx.pocketsphinx import *
from multiprocessing import Pipe
import os

# These will need to be modified according to where the pocketsphinx folder is
MODELDIR = "/home/pi/Lexia/model"

class DecoderCore():
    #### This is the Key function of the whole System 
    def __init__(self,dic = 'de-de/de.dic', lm = 'de-de/de.lm' , lang = 'de-de/de-de'):
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(MODELDIR, lang))
        config.set_string('-lm', os.path.join(MODELDIR, lm ))
        config.set_string('-dict', os.path.join(MODELDIR, dic))
        self.decoder = Decoder(config) #### Configuring the Pocketsphinx Voice Recognition
        self.pipe_open , self.pipe_end = Pipe() #### Mulitprocessing Communication Object

    def decode(self,buf):
        self.pipe_open.send(buf)

    def get_words(self):
        return self.pipe_open.recv()

    def get_pipe_end(self):
        return self.pipe_end

    def run_decoder(self,pipe_end):
        print("Decoder started. ")
        self.decoder.start_utt()
        buf = pipe_end.recv() # receving audiobuffer
        while (buf != 0):
            self.decoder.process_raw(buf, False, False)
            buf = pipe_end.recv() # receving audiobuffer
        self.decoder.end_utt()  # Starting audio translation
        self.words = []
        [self.words.append(seg.word) for seg in self.decoder.seg()] # Reading words
        string = ""
        for word in self.words:
            if (word != '<sil>' and word != '<s>' and word != '</s>'): # Removing non words
                string = string + " " + word
        pipe_end.send(string) # Sending words to the mainprocess
        print("Decoder finished.")

