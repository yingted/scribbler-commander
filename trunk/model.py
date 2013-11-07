import deadreckoning
from pickle import load
from numpy import arange, pi, exp, log, linspace, around, ndarray, array, ones
from scipy.integrate import quad
from util import memoize, xp_initialize, get_obstacle
from itertools import cycle, islice
def _floor_clip(v, lo, hi):
	if isinstance(v, ndarray):
		return v.astype('int').clip(lo, hi)
	return max(lo, min(hi, int(v)))
class Prior(object):
	_max_r = 1.23
	_max_t = 50
	_r_to_t = _max_t/_max_r
	_sigma_theta = pi/12 #TODO measure
	_max_v = 6400 #for opcode 157 with latency 400
	def __init__(self, inp='prior.pickle'):
		if isinstance(inp, file):
			self.data = load(inp)
		elif isinstance(inp, str):
			fd=open(inp)
			try:
				self.data = load(fd)
			finally:
				fd.close()
		else:
			self.data = inp
		for irp in self.data:
			for k in self.data[irp]:
				self.data[irp][k] = array(self.data[irp][k])
	def v_r(self, irp, v, r):
		"""log of conditional distribution P(v|irp,r)"""
		t = r * self._r_to_t
		data = self.data[irp]

		i = _floor_clip(t, 0, self._max_t - 1)
		dt = t - i
		mu1 = data['mu'][i]
		mu2 = data['mu'][i+1]
		sigma1 = data['sigma'][i]
		sigma2 = data['sigma'][i+1]
		mu = dt * mu2 + (1 - dt) * mu1
		sigma = dt * sigma2 + (1 - dt) * sigma1

		return ((v - mu)/sigma)**2 / -2 - log((2 * pi)**.5 * sigma)
	@memoize #XXX check memory usage
	def r(self, irp, r):
		"""log of distribution P(r)"""
		return log(exp(self.v_r(irp, arange(0, self._max_v + 1), r)).sum())
	@memoize
	def v(self, irp, v):
		"""log of distribution P(v)"""
		return log(quad(lambda r: exp(self.v_r(irp, v, r) - self.r(irp, r)), 0, self._max_r)[0])
	def __call__(self, irp, v, r):
		"""log P"""
		return self.v_r(irp, v, r) + self.r(irp, r)
if __name__=='__main__':
	from myro import *
	from numpy import array, set_printoptions, dot
	from matplotlib.pyplot import *
	from movement import moveforward, turnside
	P=Prior()
	#R = linspace(0, P._max_r, num=300)
	R = linspace(0, P._max_r, num=100)
	#ion()
	#ax = axes(xlim=(0, 1.23), ylim=(0, 1))
	#line, = ax.plot([], [])

	set_printoptions(precision=1, suppress=True)
	#print quad(lambda r: P.r(134, r), 0, P._max_r)[0]
	#print sum(P.v(134, i) for i in xrange(1, P._max_v+1))
	#print P.r(134, .2)
	#print P.v(134, 1000)
	#print [P(134, 1000, (i+.5)/5.*.3+.2) for i in xrange(5)]
	xp_initialize()
	irps = [125, 131, 137, 143, 146]
	hist = []
	def distances():
		rho = .15
		log_rho = log(rho)
		d = ones(len(R)) * log_rho
		lambd = .6
		while True:
			irp = irps[0]
			irps[:] = irps[1:] + irps[:1]
			setIRPower(irp)
			d = (d - log_rho) * lambd + log_rho
			v = get_obstacle('center')
			H = P.v(irp, v)
			E = array([P(irp, v, r) for r in R])
			d += E - H
			#print v, d
			Z = exp(d).sum()
			if Z!=0:
				p = exp(d) / Z
				#line.set_data(R, p)
				#draw()
				dist = dot(R, p)
			#print 'dist:', dist
			hist.append(dist)
			yield dist
	d = iter(islice(distances(), 8, None))
	#target = 0., 1.
	target = 0., 2.
	class DestinationReached(Exception): pass
	def getBearing():
		dist, bearing = deadreckoning.distTo(*target)
		print 'heading', deadreckoning.robotHeading
		if dist < .2:
			print 'reached destination', dist
			raise DestinationReached
		return bearing
	try:
		while True:
			print 'moving to obstacle'
			irps[:] = 140,
			d.next()
			forward(.8)
			while d.next() > .24: getBearing()

			print 'turning until no obstacle'
			irps[:] = 146,
			motors(.1, -.1)
			while d.next() < .32: pass
			print 'distance:', hist[-3]

			print 'passing obstacle'
			moveforward(hist[-3] + .15)

			while True:
				getBearing() # check if we arrived

				print 'locating obstacle'
				if d.next() < .32:
					motors(.1, -.1)
					while d.next() < .32: pass
				else:
					motors(-.1, .1)
					while d.next() >= .32: pass

				print 'turning away from obstacle'
				turnside(pi/4, left=False)

				bearing = getBearing()
				print 'bearing', bearing
				if bearing <= 0:
					break

				print 'wall following'
				moveforward(.2)

			print 'turning towards target'
			turnside(-bearing, left=False)
	except KeyboardInterrupt:
		pass
	except DestinationReached:
		pass
	stop()
