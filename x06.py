#!/usr/bin/env python
#program to decode x06 Mazielka
import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose
from scipy import fft
from time import sleep, time
import signal
def sigHandler(s, fr):
   stream.stop_stream()
   stream.close()
   exit(0)
signal.signal(signal.SIGINT, sigHandler)
SENSITIVITY= 0.4
BANDWIDTH = 12
SAMPLES = 1048
RATE = 11025
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=RATE,
                 input=True,
                 frames_per_buffer=SAMPLES)
DETECT = [815, 845, 875, 910, 950, 990]
scores = [0,0,0,0,0,0]
scoreIndex = 0
msg = ""
showErrors = False
def processMsg(m):
   n = "";l = ""
   for x in m:
      if x == l: continue
      n+=x;l=x
   return n
sigFound = False
print "listening for code.."
nc = 0
while True:
   while stream.get_read_available()< SAMPLES: sleep(0.05)
   audioData  = fromstring(stream.read(
         stream.get_read_available()), dtype=short)[-SAMPLES:]
   normalizedData = audioData / 32768.0
   intensity = abs(fft(normalizedData))[:SAMPLES/2]
   frequencies = linspace(0.0, float(RATE)/2, num=SAMPLES/2)
   maxScoreIndex = scores.index(max(scores))
   maxScore = max(scores)
   tf = False
   for tone in DETECT:
      try:
          a = max(intensity[(frequencies < tone+BANDWIDTH) &
                            (frequencies > tone-BANDWIDTH )])
          b = intensity[(frequencies < tone-100) &
                        (frequencies > tone-200)]
          if not len(b): continue
          b = max(b) + SENSITIVITY
          if a>b:
              tf = True
              scoreIndex = DETECT.index(tone)
              scores[scoreIndex] += 1
              if maxScore >= 2:
                 msg+=str(maxScoreIndex + 1)
                 scores = [0,0,0,0,0,0]
              if not sigFound:
                 print "signal detected"
                 sigFound = True
      except Exception as e:
          print "error.." + str(e)
          pass
   if not tf:
      nc+=1
   if nc>=10:
      print processMsg(msg)
      nc = 0
      msg = ""
      scores = [0,0,0,0,0,0]
