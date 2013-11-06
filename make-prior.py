#!/usr/bin/env python
"""generates prior from data"""
N=50
if __name__=="__main__":
	from pickle import load,dump
	from sys import argv
	from numpy import *
	from scipy.stats import linregress
	data={}
	with open(argv[1])as f:
		for ent in load(f):
			start=ent['data'][0]['t']*1.5-.5*ent['data'][1]['t']
			t=[]
			v=[]
			for sample in ent['data']:
				t.append(sample['t']-start)
				v.append(sample['v'])
			t=array(t)
			v=array(v)
			weight=zeros(N+1)
			vals=[]
			dx=1
			for start in xrange(0,N,dx):
				i=(start<=t)&(t<start+dx)
				m_t,b_t,_,_,sigma_t=linregress(arange(len(t))[i],t[i])
				m_v,b_v,_,_,sigma_v=linregress(t[i],v[i])
				var_t=(sigma_t*m_v)**2+1e-1
				var_v=sigma_v**2+1e-1
				w=1/(var_t+var_v)
				vals.append((m_v*start+b_v,m_v*(start+1)+b_v,w))
				weight[start]+=w
				weight[start+1]+=w
			i=arange(N+1)
			sigma=weight**-.5

			mu=zeros(N+1)
			for i,(left,right,w)in enumerate(vals):
				mu[dx*i]+=left*w
				mu[dx*(i+1)]+=right*w
			mu/=weight
			data[ent['irp']]={
				'mu':map(float,mu),
				'sigma':map(float,sigma),
			}
	with open(argv[2],'w')as f:
		dump(data,f)
