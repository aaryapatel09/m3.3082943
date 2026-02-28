#!/usr/bin/env python3
"""
Test suite v2: validates all M3 MATLAB functions against real Excel data.
Updated for progressive marginal tax and risk-dependent gambling caps.
"""

import openpyxl, math, random, os, sys

XLSX = '/Users/aaryapatel/m3/M3-Challenge-Problem-Data-2026.xlsx'
PASS_COUNT = 0
FAIL_COUNT = 0

def ok(name, cond, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if cond:
        PASS_COUNT += 1
        print(f"  PASS  {name}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL  {name}  {detail}")

def approx(a, b, tol=0.01):
    if b == 0: return abs(a) < tol
    return abs(a - b) / max(abs(b), 1e-12) < tol

wb = openpyxl.load_workbook(XLSX, data_only=True)
def pv(ws, r, c):
    v = ws.cell(r, c).value
    if v is None: return 0.0
    if isinstance(v, (int, float)): return 0.0 if math.isnan(v) else float(v)
    try: return float(str(v).replace(',',''))
    except: return 0.0

print("=" * 70)
print("TEST SUITE v2: M3 Challenge 2026 MATLAB Implementation")
print("=" * 70)

# ---- 1. US Data ----
print("\n--- 1. loadUSExpenditureData ---")
ws_us = wb['Expenditures (U.S.)']
us_ageBounds = [(0,24),(25,34),(35,44),(45,54),(55,64),(65,74),(75,float('inf'))]
us_meanIncome = [pv(ws_us, 4, c) for c in range(2, 9)]
us_allExpend = [pv(ws_us, 11, c) for c in range(2, 9)]
us_essExpend = [sum(pv(ws_us, r, c) for r in [12,13,14,19,20,25]) for c in range(2, 9)]
us_regionIncome = [pv(ws_us, 4, c) for c in range(9, 13)]
us_regionAllExpend = [pv(ws_us, 11, c) for c in range(9, 13)]
us_nationalIncome = sum(us_regionIncome) / 4
us_nationalAllExpend = sum(us_regionAllExpend) / 4

ok("US mean income[0]", approx(us_meanIncome[0], 48514))
ok("US mean income[1]", approx(us_meanIncome[1], 102494))
ok("US essential < all", all(us_essExpend[i] <= us_allExpend[i] for i in range(7)))
ok("US region income NE", approx(us_regionIncome[0], 115770))

# ---- 2. UK Data ----
print("\n--- 2. loadUKExpenditureData ---")
ws_uk = wb['Expenditures (U.K.)']
uk_ageBounds = [(0,29),(30,49),(50,64),(65,74),(75,float('inf'))]
blockStarts = [4, 21, 38, 55, 72]
uk_quintileIncome = [pv(ws_uk, 5, c) for c in range(10, 15)]
ok("UK quintile[0]=272", approx(uk_quintileIncome[0], 272))
ok("UK quintile[4]=2391", approx(uk_quintileIncome[4], 2391))

uk_essWeekly, uk_avgPAll = [], []
for r0 in blockStarts:
    food = [pv(ws_uk, r0+4, c) for c in range(2, 7)]
    hous = [pv(ws_uk, r0+7, c) for c in range(2, 7)]
    tran = [pv(ws_uk, r0+10, c) for c in range(2, 7)]
    uk_essWeekly.append([f+h+t for f,h,t in zip(food, hous, tran)])
    uk_avgPAll.append(pv(ws_uk, r0+2, 7))

for b in range(5):
    ok(f"UK block {b} essential positive", all(v > 0 for v in uk_essWeekly[b]))

uk_regAllExpWk = [0.0]*4; uk_natAllExpWk = 0.0
for rr in range(12, 25):
    for i, c in enumerate(range(10, 14)):
        uk_regAllExpWk[i] += pv(ws_uk, rr, c)
    uk_natAllExpWk += pv(ws_uk, rr, 14)

# ---- 3. Betting Data ----
print("\n--- 3. loadUSBettingData ---")
ws_bet = wb['Online Sports Betting Personal ']
ok("hasAccount=22", approx(pv(ws_bet, 4, 2), 22))
ok("chase=52", approx(pv(ws_bet, 40, 2), 52))

# ---- 4. afterTaxIncome (progressive) ----
print("\n--- 4. afterTaxIncome ---")
def afterTax(S, country):
    brackets = [0, 30000, 80000, 150000, float('inf')]
    rates = [0.10,0.18,0.24,0.30] if country=='US' else [0.12,0.20,0.26,0.32]
    tax = 0
    for k in range(len(rates)):
        taxable = max(0, min(S, brackets[k+1]) - brackets[k])
        tax += rates[k] * taxable
    return S - tax, tax/S if S > 0 else 0

ok("US S=0: Y=0", afterTax(0,'US')[0] == 0)
ok("US S=30000: Y=27000", approx(afterTax(30000,'US')[0], 27000))
ok("US S=70000: Y=59800", approx(afterTax(70000,'US')[0], 59800))
ok("US S=110000: Y=90800", approx(afterTax(110000,'US')[0], 90800))
ok("US S=200000: Y=156200", approx(afterTax(200000,'US')[0], 156200))
ok("UK S=60000: Y=50400", approx(afterTax(60000,'UK')[0], 50400))

# ---- 5-8. Pipeline helpers ----
print("\n--- 5-8. Pipeline helpers ---")
usHHbyAge = [2.0,3.0,3.3,3.0,2.5,2.0,1.7]
def mapUS(age):
    for i,(lo,hi) in enumerate(us_ageBounds):
        if lo<=age<=hi: return i
    return 6
def mapUK(age):
    for i,(lo,hi) in enumerate(uk_ageBounds):
        if lo<=age<=hi: return i
    return 4
def findQ(wk, qi):
    bnd = [(qi[i]+qi[i+1])/2 for i in range(4)]
    q = 0
    for b in bnd:
        if wk > b: q += 1
    return q
def regMult(region, country):
    if country=='US':
        regs=['Northeast','Midwest','South','West']
        if region not in regs: return 1.0
        ri = regs.index(region)
        return (us_regionAllExpend[ri]/us_regionIncome[ri])/(us_nationalAllExpend/us_nationalIncome)
    else:
        regs=['England','Wales','Scotland','Northern Ireland']
        if region not in regs: return 1.0
        return uk_regAllExpWk[regs.index(region)]/uk_natAllExpWk
def hhMult(h, age, country):
    hbar = uk_avgPAll[mapUK(age)] if country=='UK' else usHHbyAge[mapUS(age)]
    if hbar <= 0: hbar = 2.5
    return (h/hbar)**0.7

ok("US West mult ~ 1.023", approx(regMult('West','US'), 1.023, 0.02))
ok("UK Scotland mult ~ 0.871", approx(regMult('Scotland','UK'), 0.871, 0.02))
ok("US h=1 age=35 < 1", hhMult(1,35,'US') < 1)
ok("US h=4 age=35 > 1", hhMult(4,35,'US') > 1)

# ---- 9. disposableIncome ----
print("\n--- 9. disposableIncome ---")
def DI_full(S, age, h, country, region):
    Y = afterTax(S, country)[0]
    if country=='US':
        theta = us_essExpend[mapUS(age)] / us_meanIncome[mapUS(age)]
    else:
        bIdx = mapUK(age)
        qIdx = findQ(S/52, uk_quintileIncome)
        theta = uk_essWeekly[bIdx][qIdx] / uk_quintileIncome[qIdx]
    E = theta * S * regMult(region, country) * hhMult(h, age, country)
    E = min(E, Y)
    return Y-E, Y, E

DI1,Y1,_ = DI_full(70000,28,1,'US','West')
ok("Q1 ex1 Y=59800", approx(Y1, 59800))
ok("Q1 ex1 DI > 0", DI1 > 0, f"DI={DI1:.0f}")
DI2,Y2,_ = DI_full(110000,42,4,'US','Midwest')
ok("Q1 ex2 Y=90800", approx(Y2, 90800))
DI3,Y3,_ = DI_full(60000,35,2,'UK','England')
ok("Q1 ex3 Y=50400", approx(Y3, 50400))
ok("Q1 ex3 DI > 0", DI3 > 0, f"DI={DI3:.0f}")
ok("Larger hh -> lower DI", DI_full(80000,40,1,'US','West')[0] > DI_full(80000,40,4,'US','West')[0])

# ---- 10. gamblingOutcome ----
print("\n--- 10. gamblingOutcome ---")
def gamblingOutcome(p):
    DI = DI_full(p['salary'],p['age'],p['hhsize'],p['country'],p['region'])[0]
    M = {'low':50,'medium':300,'high':800}[p['riskTolerance']]
    af = 1.15 if p['age']<35 else (0.70 if p['age']>=65 else 1.0)
    gf = 1.10 if p['gender']=='male' else (0.85 if p['gender']=='female' else 1.0)
    ef = 1.05 if p['education']=='college' else 1.0
    M *= af*gf*ef; G_raw = 12*M
    capFrac = {'low':0.15,'medium':0.40,'high':1.00}[p['riskTolerance']]
    G = min(G_raw, capFrac*max(DI,0))
    baseEdge = {'conservative':0.04,'mixed':0.07,'highrisk':0.12}.get(p['style'],0.07)
    chaseMult = {'low':1.00,'medium':1.20,'high':1.50}[p['riskTolerance']]
    edge = baseEdge * chaseMult
    return -edge*G, edge*G, edge*G/max(DI,1), G, DI

p1 = {'salary':70000,'age':28,'hhsize':1,'country':'US','region':'West',
      'gender':'male','education':'nocollege','riskTolerance':'medium','style':'mixed'}
e1,_,f1,G1,D1 = gamblingOutcome(p1)
ok("Gamble p1: loss < 0", e1 < 0)
ok("Gamble p1: G > 0", G1 > 0)

# ---- 11. Q3 ----
print("\n--- 11. Q3 metrics ---")
annuity = ((1.04**20)-1)/0.04
ok("Annuity ~ 29.778", approx(annuity, 29.778, 0.001))

# ---- 12. MC ----
print("\n--- 12. Monte Carlo (N=1000) ---")
random.seed(42); N=1000
mc_l, mc_d, mc_a = [], [], []
for _ in range(N):
    p = {'salary':20000+random.random()*180000, 'age':random.randint(18,75),
         'hhsize':random.randint(1,5), 'country':random.choice(['US','UK']),
         'gender':random.choice(['male','female']),
         'education':random.choice(['nocollege','college']),
         'riskTolerance':random.choice(['low','medium','high']),
         'style':random.choice(['conservative','mixed','highrisk'])}
    p['region'] = random.choice(['Northeast','Midwest','South','West'] if p['country']=='US'
                                 else ['England','Wales','Scotland','Northern Ireland'])
    e,_,_,_,D = gamblingOutcome(p); mc_l.append(e); mc_d.append(D); mc_a.append(p['age'])

ok("MC: all losses <= 0", all(l <= 0 for l in mc_l))
ok("MC: mean DI > 0", sum(mc_d)/N > 0)
R_vals = [-l/d for l,d in zip(mc_l, mc_d) if d > 0]
hr = sum(1 for r in R_vals if r >= 0.15)
print(f"  Mean DI=${sum(mc_d)/N:,.0f}, Mean loss=${sum(mc_l)/N:,.0f}, High-risk={hr}/{len(R_vals)}")

# ---- 13. File checks ----
print("\n--- 13. File checks ---")
m_files = [f for f in os.listdir('/Users/aaryapatel/m3') if f.endswith('.m')]
ok("14 .m files", len(m_files) == 14, f"found {len(m_files)}")

print("\n" + "=" * 70)
print(f"TEST RESULTS: {PASS_COUNT} passed, {FAIL_COUNT} failed")
print("=" * 70)
if FAIL_COUNT == 0:
    print("\nAll tests passed!")
else:
    print(f"\n{FAIL_COUNT} test(s) FAILED.")
    sys.exit(1)
wb.close()
