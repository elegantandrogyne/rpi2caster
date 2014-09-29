#! /usr/bin/python
import select, os
gpiofilename='/sys/class/gpio/gpio14/value'
f = open(gpiofilename, 'r')

po = select.epoll()
po.register(f, select.POLLPRI)

while 1:
  events = po.poll(10)
  if not events:
    print('timeout')
    exit()
  else:
    f.seek(0)
    state_last=f.read()
    print 'waiting'