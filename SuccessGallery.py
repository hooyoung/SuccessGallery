#!/usr/bin/python

# A440 = key 49
# middle C = key 40

import sys, pygame
import os
import glob
from numpy import *
import random

bag = {}
def get(fn):
  if fn not in bag:
    im = pygame.image.load(fn)
    bag[fn] = pygame.transform.smoothscale(im, im.get_rect().fit(screenrect).size)
  return bag[fn]
def getfiles(fn):
  try:
    for fn2 in sorted(os.listdir(fn)):
      fn2 = os.path.join(fn,fn2)
      if os.path.isdir(fn2):
        for fn3 in getfiles(fn2):
          yield fn3
      elif fn2.endswith('.jpg'):
        yield fn2
  except GeneratorExit: return

pygame.init()
screen = pygame.display.set_mode((800,800))
pygame.display.set_caption('Success Gallery')
screenrect = screen.get_rect()

#imcache = []
#ims = lazyfiles([os.path.join(os.getcwd(),fn) for fn in sys.argv[1:]] or [os.getcwd()])
def seldir():
  global reset, next, prev
  pos = [-1]
  fns = list(getfiles('.'))
  print fns
  def reset():
    pos[0] = -1
  def next():
    pos[0] += 1
    while pos[0] < len(fns):
      try:
        return get(fns[pos[0]])
      except:
        del fns[pos[0]]
    return None
  def prev(k):
    pos[0] = max(0,pos[0]-k)
    return get(fns[pos[0]])
  reset()

wavs = {}

def mywav(note):
  if note not in wavs:
    freq = 440 * 2**((note - 49)/12.)
    omega = 2*pi*freq/44100.
    buf = sin(arange(44100*1)*omega) * exp(-arange(44100*1)/(44100/3.))
    buf = buffer((buf*.5*32767).astype(int16).tostring())
    wavs[note] = pygame.mixer.Sound(buf)
  return wavs[note]

major = [2,2,1,2,2,2,1]

names = ['unison', 'minor second', 'major second', 'minor third', 'major third', 'perfect fourth', \
  'tritone', 'perfect fifth', 'minor sixth', 'major sixth', 'minor seventh', 'major seventh', 'perfect octave']
ans = 'zqwertyuiop[]asdfghjkl;\'/'
helpstr = """Press the key corresponding to the most recent interval 
z = unison
q,w,...,] = ascending minor second, major second, ...
a,s,...,',/ = descending minor second, major second, ..."""
val = range(13)+range(-1,-13,-1)
aord = [ord(c) for c in ans]
dic = dict(zip(aord,val))

pygame.mixer.init(44100,-16,2,4096)

channel = pygame.mixer.Channel(0)
#channel.set_endevent(pygame.USEREVENT)
c1 = pygame.mixer.Channel(1)
c2 = pygame.mixer.Channel(2)

font = pygame.font.Font(None, 36)

easy = False

notes = [40-12]
for x in [2,2,1,2,2,2,1,2,2,1,2,2,2,1]:
  notes.append(notes[-1]+x)

def advance(good):
  global answer, tone
  #screen.fill((0,255,0) if good else (255,0,0))
  if not good:
    prev(1)
    screen.fill((255,0,0))
    ansstr = '%s%s' % ('ascending ' if answer>0 else ('' if answer==0 else 'descending '), names[abs(answer)])
    text = font.render(ansstr, True, (255,255,255))
    screen.blit(text, text.get_rect(center=screenrect.center))
    pygame.display.flip()
    pygame.time.wait(500)
  screen.fill((0,0,0))
  pygame.display.flip()
  if easy:
    answer = random.randrange(7,13)
    tone = random.randrange(35,50-answer)
  else:
    #nexttone = random.randrange(max(tone-5,20),
    #                            min(tone+5,60)+1)
    nexttone = -1
    while not (tone-9 <= nexttone <= tone+9):
      nexttone = random.choice(notes)
    answer,tone = nexttone-tone,nexttone
  showplay()

def showplay(quiet=False):
  im = next()
  if im is None:
    print 'GOOD JOB'
    sys.exit(0)
  screen.blit(im, im.get_rect(center=screenrect.center))
  top,left = 0,0
  texts = []
  right = 0
  for line in helpstr.split('\n'):
    text = font.render(line, True, (255,255,255))
    rect = text.get_rect(top=top,left=left)
    #screen.blit(text, rect)
    texts.append((text,rect))
    top = rect.bottom + 10
    right = max(right,rect.right)
  screen.fill((255,0,0),pygame.Rect(0,0,right,top))
  for text,rect in texts:
    screen.blit(text,rect)

  pygame.display.flip()
  if not quiet:
    channel.play(mywav(tone))
    if easy:
      pygame.time.wait(1000)
      channel.play(mywav(tone+answer))

def restart():
  seldir()
  if not easy:
    global answer, tone
    answer,tone = 0,random.choice(notes)
    showplay()
    pygame.time.wait(1000)
  advance(True)
  pygame.event.clear(pygame.KEYUP)

restart()

while True:
  e = pygame.event.wait()
  if e.type == pygame.QUIT: sys.exit()
  if e.type == pygame.KEYUP:
    if e.key == 27: sys.exit()
    if e.key == ord('='): restart()
    elif e.key in dic:
      advance(dic[e.key] == answer)
    #elif e.key == ord(' '):
    #  showplay(quiet=True)
    elif e.key == ord('1'):
      if easy:
        c1.play(mywav(tone))
        c2.play(mywav(tone+answer))
      else:
        c1.play(mywav(tone-answer))
    elif e.key == ord('2'):
      c2.play(mywav(tone))
  if e.type == pygame.USEREVENT:
    pass

