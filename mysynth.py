#!/usr/bin/env python

import cStringIO
import numpy as np
import wave


def freq(note):
  """convenience function to return frequency associated with a keyboard note"""
  return 440 * 2**((note-49)/12.)

def wav(ns, f):
  """return a buffer containing a wav of ns nanos at frequency f"""
  a = gen(ns, f)
  io = cStringIO.StringIO()
  f = wave.open(io,'w')
  try:
    f.setparams((1,2,44100,0,'NONE','not compressed'))
    f.writeframes(np.int16(a).tostring())
    return buffer(io.getvalue())
  finally:
    f.close()

def tone(ns, f, vol=4000):
  period = 44100 / float(f)
  omega = np.pi * 2 / period
  return vol * np.sin(np.arange(ns) * omega)

def gen(ns, f):
  harm_max = 4.
  lf = np.log(f)
  lf_fac = (lf-3)/harm_max
  harm = max(0., 2*(1-lf_fac))
  decay = 2/lf
  t = (lf-3)/5.5
  volfac = 1 + .8*t*np.cos(np.pi/5.3*(lf-3))
  z = tone(ns,f)
  z += tone(ns,f*2) * harm
  z += tone(ns,f*4) * .5 * harm
  fac = np.hstack((
    np.arange(100)/80.,
    1.25-np.arange(200)/800.,
    np.ones((ns-700,)),
    1.-np.arange(400)/400.))
  dfac = 1 - np.arange(ns)/ns*(1-decay)
  return z * fac * dfac * volfac

