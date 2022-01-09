from py_vollib.black_scholes.greeks.numerical import delta

stdev = 0.015648686525647205 * (365) ** 0.5
dte = 32
risk_free_rate = 0.01767  # 10 year treasuries
d = delta("p", S=172.17, K=145, t=dte / 365, r=risk_free_rate, sigma=stdev)
print(d)
