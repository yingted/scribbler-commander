from pickle import load
from numpy import arange, pi, exp, log, tan, arctan, linspace, around, ndarray, array, ones, zeros, meshgrid, searchsorted, hypot, arctan2, abs, isnan, isfinite, nan_to_num
try:
    from scipy.integrate import quad
    from scipy.interpolate import UnivariateSpline, pchip
except ImportError:
    pass
from util import memoize, xp_initialize, get_obstacle
from itertools import cycle, islice

def _floor_clip(v, lo, hi):
	if isinstance(v, ndarray):
		return v.astype('int').clip(lo, hi)
	return max(lo, min(hi, int(v)))
class Prior(object):
	_max_r = 1.23
	_max_t = 50
	_r_to_t = _max_t / _max_r
	_sigma_theta = pi / 24 #TODO measure
	_var_theta = _sigma_theta**2
	_max_v = 6400 #for opcode 157 with latency 400
	_N = 17
	_h = .15
	_points = tan(linspace(0, arctan(_max_r / _h), num=_N+1)) * _h
	_widths = map(float.__sub__, _points[1:], _points[:-1])
	_times = _points / _max_r * _max_t
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
		'''log of conditional distribution P(v|irp,r)'''
		t = r * self._r_to_t
		data = self.data[irp]

		i = min(self._N - 1, searchsorted(self._times, t, side='right'))
		dt = t - i
		mu1 = data['mu'][i]
		mu2 = data['mu'][i+1]
		sigma1 = data['sigma'][i]
		sigma2 = data['sigma'][i+1]
		mu = dt * mu2 + (1 - dt) * mu1
		sigma = abs(dt * sigma2 + (1 - dt) * sigma1)

		return ((v - mu)/sigma)**2 / -2 - log((2 * pi)**.5 * sigma)
	@memoize #XXX check memory usage
	def r(self, irp, r):
		'''log of distribution P(r)'''
		return log(exp(self.v_r(irp, arange(0, self._max_v + 1), r)).sum())
	@memoize
	def v(self, irp, v):
		'''log of distribution P(v)'''
		return log(quad(lambda r: exp(self.v_r(irp, v, r) - self.r(irp, r)), 0, self._max_r)[0])
	def __call__(self, irp, v, r):
		'''log P'''
		return self.v_r(irp, v, r) + self.r(irp, r)
	def theta(self, theta):
		'''log of distribution P(theta) in radians'''
		return -(theta**2/self._var_theta-log(2 * pi * self._var_theta))/2
class Map(object):
	def __init__(self, P, w, h):
		'''construct a grid map'''
		self.P = P
		self.w = w
		self.h = h
		self.s = 8.
		self.upsample = 3
		self.m_per_unit = self.s / 40. / self.upsample
		endpoint = (self.s - self.m_per_unit) / 2
		w *= self.upsample
		h *= self.upsample
		self._x, self._y = meshgrid(linspace(-endpoint, endpoint, num = w), linspace(-endpoint, endpoint, num = h))
		rho = .15
		self.log_rho = log(rho)
		self.lambd = .99
		self.d = zeros((w, h))
		self.r0 = .093
		self.R = tan(linspace(0, arctan(P._max_r / P._h), num=10 * P._N + 1)) * P._h
		self.cb = None
	def update(self, x0, y0, theta0, irp, v):
		'''update the map using sensor data
		x0, y0, theta0 are standard mathematics x, y, theta'''
		#self.d[~isfinite(self.d)] = self.log_rho
		self.d *= self.lambd
		# use P_r(r) as a cached for P(irp, v, r) 
		points = exp(array([self.P(irp, v, r) for r in self.R]))
		P_r = UnivariateSpline(self.R, points)
		P_r_i = pchip(self.R, array([0] + map(P_r.integral, self.R[:-1], self.R[1:])).cumsum())
		scaling = 1. / max(1, P_r_i(self.P._max_r))
		def prob(r):
			return min(1, max(0, P_r(r) * (1 - P_r_i(r) / scaling)))
		# calculate radii, set of radii and thetas
		if P_r_i(.1) > 1e-7 and self.cb:
			self.cb()
		x = self._x - x0
		y = self._y - y0
		radii = hypot(x, y) - self.r0
		thetas = (arctan2(y, x) - theta0 + pi) % (2 * pi) - pi
		H = self.P.v(irp, v) - .15
		shape = radii.shape
		E = nan_to_num(log(array([prob(x) for x in radii.flatten()]).clip(0, 1))).reshape(shape)
		if isnan(E.sum()):
			E = zeros(shape)#XXX salvage values
		k = 5.
		#print E - H
		self.d += exp(self.P.theta(thetas.flatten()).reshape(shape)) * (E - H).clip(-k, k) *((0 <= radii) & (radii <= self.P._max_r))
		#print v, self.d
	@property
	def x(self):
		return self._x[self.upsample/2::self.upsample,self.upsample/2::self.upsample]
	@property
	def y(self):
		return self._y[self.upsample/2::self.upsample,self.upsample/2::self.upsample]
	@property
	def p(self):
		'''returns probabilities'''
		factor = exp(self.d[self.upsample/2::self.upsample,self.upsample/2::self.upsample])
		#return factor / (1 + factor)
		factor = factor / (factor + 1.)
		#print "Z=",factor.sum(),"max=",factor.max(),factor
		return factor
	@property
	def _p(self):
		'''returns probabilities'''
		factor = exp(self.d)
		#return factor / (1 + factor)
		factor = factor / (factor + 1.)
		#print "Z=",factor.sum(),"max=",factor.max(),factor
		return factor
if __name__=='__main__':
	from myro import *
	from numpy import array, set_printoptions, dot
	#from matplotlib.pyplot import *
	from movement import moveforward, turnside
	from time import time
	import deadreckoning
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
			print 'dist:', dist
			hist.append(dist)
			yield dist
	burnin = 8
	d = iter(islice(distances(), burnin, None))
	target = 0., 1.
	margin_deg = 50.
	class DestinationReached(Exception): pass
	def getBearing():
		dist, bearing = deadreckoning.distTo(*target)
		#bearing = (bearing + pi) % (2 * pi) - pi
		#print 'heading', deadreckoning.robotHeading, 'distance', dist
		if dist < .1:
			print 'reached destination', dist
			raise DestinationReached
		return bearing
	def debug():
		stop()
		#print 'heading', deadreckoning.robotHeading / pi * 180, 'deg'
		#raw_input('press enter to continue: ')
	left_seconds = [0]
	def rotation(left): # assume only one value
		'''contract: this generator must complete'''
		left_seconds[0] -= time() * cmp(left, 0)
		motors(left, -left)
		yield None
		#left_seconds[0] += (time() + .12) * cmp(left, 0)
		left_seconds[0] += time() * cmp(left, 0)
		stop()
	try:
		while True:
			print 'moving to obstacle'
			irps[:] = 140,
			d.next()
			forward(.8)
			while d.next() > .25: getBearing()

			print 'turning until no obstacle'
			irps[:] = 146,
			for _ in rotation(.1):
				while d.next() < .34: pass
			print 'distance:', hist[-3]
			debug()

			print 'passing obstacle'
			#moveforward(hist[-3] + .15)
			forward(.8, (hist[-3] + .15) / .127)
			stop()

			while True:
				getBearing() # check if we arrived

				print 'locating obstacle'
				if d.next() < .32:
					for _ in rotation(.1):
						while d.next() < .32: pass
				else:
					exc = None
					for _ in rotation(-.1):
						#while d.next() >= .32: pass
						while d.next() >= .32:
							try:
								if getBearing() <= -margin_deg * pi / 180:
									break
							except DestinationReached, exc:
								break
					if exc:
						raise exc
				debug()

				print 'turning away from obstacle'
				#turnside(pi/4, left=False)
				for _ in rotation(.1):
					wait(margin_deg / 24.0)
				debug()

				bearing = getBearing()
				print 'bearing', bearing
				if bearing <= 0:
					break

				print 'wall following'
				#moveforward(.2)
				forward(.8, .2 / .127)

				stop()
				for _ in xrange(burnin): d.next()
			print 'turning towards target'
			turnside(-bearing, left=False)
	except KeyboardInterrupt:
		pass
	except DestinationReached:
		#turnside(deadreckoning.robotHeading, left=False)
		t = left_seconds[0]
		print 'rotated right for', t
		for _ in rotation(.1 * cmp(0, t)):
			#wait(abs(t) * 1.12)
			wait(abs(t))
		stop()
		beep(.1, 880)
		wait(.4)
		beep(.1, 880)
		wait(.4)
		beep(.5, 880)
	except Exception:
		stop()
		raise
	stop()
