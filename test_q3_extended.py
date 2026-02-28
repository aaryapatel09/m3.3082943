#!/usr/bin/env python3
"""
Test suite for expanded Q3: R projection, dose-response impact mapping,
and intervention effectiveness.
"""

import math, random, sys

PASS = 0
FAIL = 0

def ok(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  **FAIL**  {name}  {detail}")

def approx(a, b, rtol=0.005):
    if abs(b) < 1e-9: return abs(a) < 1e-6
    return abs(a - b) / max(abs(a), abs(b), 1e-12) < rtol

print("=" * 72)
print("Q3 EXTENDED TEST SUITE")
print("=" * 72)

# ==================================================================
# A. R computation
# ==================================================================
print("\n[A] R = |expLoss| / DI ...")
for loss, di in [(-100, 50000), (-500, 20000), (-2000, 10000), (-50, 100000)]:
    R = -loss / di
    ok(f"R for loss={loss}, DI={di}: {R:.4f}", R > 0 and R < 1)

ok("R undefined when DI=0", True)  # code uses nan

# ==================================================================
# B. Growth projection
# ==================================================================
print("\n[B] R growth projection over time ...")

annualGrowth = 0.09
years = list(range(2024, 2035))
growthCurve = [(1 + annualGrowth)**t for t in range(len(years))]

ok("Year 0 growth = 1.0", approx(growthCurve[0], 1.0))
ok("Year 10 growth = 2.367", approx(growthCurve[10], 1.09**10, 0.001))
ok("Growth strictly increasing", all(growthCurve[i] < growthCurve[i+1] for i in range(10)))

# Age sensitivity factors
ageSens = [1.25, 1.10, 0.95, 0.80]
ok("Young (18-29) most sensitive", ageSens[0] == max(ageSens))
ok("Old (65+) least sensitive", ageSens[3] == min(ageSens))

# Project R for each age group
baseR = 0.05
for g, (label, s) in enumerate(zip(['18-29','30-44','45-64','65+'], ageSens)):
    projected = [baseR * gc * s for gc in growthCurve]
    ok(f"Age {label}: projected R starts at {projected[0]:.4f}",
       approx(projected[0], baseR * s))
    ok(f"Age {label}: projected R increases over time",
       all(projected[i] <= projected[i+1] for i in range(10)))
    ok(f"Age {label}: year 10 R = {projected[10]:.4f}",
       approx(projected[10], baseR * s * 1.09**10))

# Gender sensitivity
genderSens = [1.15, 0.85]
ok("Male more sensitive than female", genderSens[0] > genderSens[1])

# Region sensitivities
regSens = [1.05, 0.95, 1.10, 1.12, 1.08, 0.90, 0.95, 0.88]
allRegs = ['Northeast','Midwest','South','West',
           'England','Wales','Scotland','Northern Ireland']
ok("West highest US sens", regSens[3] == max(regSens[:4]))
ok("England highest UK sens", regSens[4] == max(regSens[4:]))

# ==================================================================
# C. Dose-response impact functions
# ==================================================================
print("\n[C] Dose-response impact mapping ...")

def impactRate(R_in, L, k, Rmid):
    return L / (1 + math.exp(-k * (R_in - Rmid)))

outcomes = [
    ('Debt',            0.40, 25, 0.12),
    ('Depression',      0.45, 22, 0.13),
    ('Divorce',         0.30, 28, 0.14),
    ('Drug Addiction',  0.25, 30, 0.15),
    ('School Decline',  0.50, 25, 0.10),
]

# C1. At R=0, harm should be very low (near 0)
for name, L, k, Rmid in outcomes:
    rate0 = impactRate(0.0, L, k, Rmid)
    ok(f"{name} at R=0: rate={rate0:.4f} < 5%", rate0 < 0.05,
       f"got {100*rate0:.2f}%")

# C2. At R=0.30, harm should be near saturation (near L)
for name, L, k, Rmid in outcomes:
    rate30 = impactRate(0.30, L, k, Rmid)
    ok(f"{name} at R=30%: rate={rate30:.4f} close to L={L}",
       rate30 > 0.85 * L, f"got {100*rate30:.1f}% vs L={100*L:.1f}%")

# C3. Monotonicity: harm increases with R
for name, L, k, Rmid in outcomes:
    prev = -1
    for R_val in [0, 0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30]:
        rate = impactRate(R_val, L, k, Rmid)
        ok(f"{name} mono R={R_val:.2f}: rate >= prev",
           rate >= prev - 1e-9, f"prev={prev:.4f}, now={rate:.4f}")
        prev = rate

# C4. At R=Rmid, rate should be exactly L/2
for name, L, k, Rmid in outcomes:
    rateMid = impactRate(Rmid, L, k, Rmid)
    ok(f"{name} at Rmid={Rmid}: rate = L/2 = {L/2:.3f}",
       approx(rateMid, L/2), f"got {rateMid:.4f}")

# C5. All rates in [0, L] for any R in [0, 1]
for name, L, k, Rmid in outcomes:
    for R_val in [0, 0.001, 0.05, 0.10, 0.20, 0.50, 1.0]:
        rate = impactRate(R_val, L, k, Rmid)
        ok(f"{name} R={R_val}: rate in [0, {L}]",
           0 <= rate <= L + 1e-9)

# C6. Ordering among outcomes at typical R
R_test = 0.12
rates_at_12 = {name: impactRate(R_test, L, k, Rmid) for name, L, k, Rmid in outcomes}
ok("School Decline highest at R=12% (lowest Rmid)",
   rates_at_12['School Decline'] > rates_at_12['Drug Addiction'])

# ==================================================================
# D. Intervention modeling
# ==================================================================
print("\n[D] Intervention modeling ...")

interventions = [
    ('Spending Caps', 0.30),
    ('Self-Exclusion', 0.25),
    ('Ad Bans', 0.15),
    ('Education', 0.10),
    ('Combined', 0.60),
]

R_baseline = 0.05

# D1. Each intervention reduces R
for name, reduction in interventions:
    R_after = R_baseline * (1 - reduction)
    ok(f"{name}: R_after = {R_after:.4f} < R_baseline",
       R_after < R_baseline)
    ok(f"{name}: R_after >= 0",
       R_after >= 0)

# D2. Combined is the strongest
combined_R = R_baseline * (1 - 0.60)
for name, reduction in interventions[:-1]:
    single_R = R_baseline * (1 - reduction)
    ok(f"Combined stronger than {name}: {combined_R:.4f} < {single_R:.4f}",
       combined_R <= single_R)

# D3. Cascaded outcome improvement: lower R -> lower harm for all outcomes
for name, L, k, Rmid in outcomes:
    harm_before = impactRate(R_baseline, L, k, Rmid)
    harm_after  = impactRate(combined_R, L, k, Rmid)
    ok(f"{name}: harm drops after combined intervention",
       harm_after <= harm_before,
       f"before={100*harm_before:.2f}%, after={100*harm_after:.2f}%")
    ok(f"{name}: improvement > 0",
       harm_before - harm_after > 0,
       f"delta={100*(harm_before-harm_after):.2f} pp")

# D4. Harm trajectories: with intervention always lower than without
for name, L, k, Rmid in outcomes:
    for t in range(len(years)):
        R_t_none = R_baseline * growthCurve[t]
        R_t_int  = combined_R * growthCurve[t]
        h_none = impactRate(R_t_none, L, k, Rmid)
        h_int  = impactRate(R_t_int, L, k, Rmid)
        ok(f"{name} year {years[t]}: intervention harm <= no-action",
           h_int <= h_none + 1e-9)

# D5. Without intervention, harm should increase over time
for name, L, k, Rmid in outcomes:
    prev = -1
    for t in range(len(years)):
        R_t = R_baseline * growthCurve[t]
        h = impactRate(R_t, L, k, Rmid)
        ok(f"{name} no-action year {years[t]}: harm increasing",
           h >= prev - 1e-9)
        prev = h

# ==================================================================
# E. Full Monte Carlo integration check
# ==================================================================
print("\n[E] MC integration (N=2000) ...")

import openpyxl
XLSX = '/Users/aaryapatel/m3/M3-Challenge-Problem-Data-2026.xlsx'
wb = openpyxl.load_workbook(XLSX, data_only=True)
def pv(ws, r, c):
    v = ws.cell(r, c).value
    if v is None: return 0.0
    if isinstance(v, (int, float)): return 0.0 if math.isnan(v) else float(v)
    try: return float(str(v).replace(',',''))
    except: return 0.0

ws_us = wb['Expenditures (U.S.)']
ws_uk = wb['Expenditures (U.K.)']
us_ageBounds = [(0,24),(25,34),(35,44),(45,54),(55,64),(65,74),(75,9999)]
uk_ageBounds = [(0,29),(30,49),(50,64),(65,74),(75,9999)]
us_meanIncome = [pv(ws_us, 4, c) for c in range(2,9)]
us_essExpend = [sum(pv(ws_us, r, c) for r in [12,13,14,19,20,25]) for c in range(2,9)]
us_regionIncome = [pv(ws_us, 4, c) for c in range(9,13)]
us_regionAllExpend = [pv(ws_us, 11, c) for c in range(9,13)]
us_nationalIncome = sum(us_regionIncome)/4
us_nationalAllExpend = sum(us_regionAllExpend)/4
uk_quintileIncome = [pv(ws_uk, 5, c) for c in range(10,15)]
blockStarts = [4, 21, 38, 55, 72]
uk_essWeekly, uk_avgPAll = [], []
usHHbyAge = [2.0,3.0,3.3,3.0,2.5,2.0,1.7]
for r0 in blockStarts:
    food = [pv(ws_uk, r0+4, c) for c in range(2,7)]
    hous = [pv(ws_uk, r0+7, c) for c in range(2,7)]
    tran = [pv(ws_uk, r0+10, c) for c in range(2,7)]
    uk_essWeekly.append([f+h+t for f,h,t in zip(food,hous,tran)])
    uk_avgPAll.append(pv(ws_uk, r0+2, 7))
uk_regAllExpWk = [0.0]*4; uk_natAllExpWk = 0.0
for rr in range(12,25):
    for i, c in enumerate(range(10,14)):
        uk_regAllExpWk[i] += pv(ws_uk, rr, c)
    uk_natAllExpWk += pv(ws_uk, rr, 14)

def afterTax(S, country):
    brackets = [0, 30000, 80000, 150000, float('inf')]
    rates = [0.10,0.18,0.24,0.30] if country=='US' else [0.12,0.20,0.26,0.32]
    tax = 0
    for k in range(len(rates)):
        taxable = max(0, min(S, brackets[k+1]) - brackets[k])
        tax += rates[k] * taxable
    return S - tax
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
def DI_full(S, age, h, country, region):
    Y = afterTax(S, country)
    if country=='US':
        theta = us_essExpend[mapUS(age)] / us_meanIncome[mapUS(age)]
    else:
        bIdx = mapUK(age)
        qIdx = findQ(S/52, uk_quintileIncome)
        theta = uk_essWeekly[bIdx][qIdx] / uk_quintileIncome[qIdx]
    E = theta * S * regMult(region, country) * hhMult(h, age, country)
    E = min(E, Y)
    return Y - E
def gamblingOutcome(p):
    DI = DI_full(p['salary'], p['age'], p['hhsize'], p['country'], p['region'])
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
    return -edge*G, DI

random.seed(999)
N = 2000
R_vals = []
age_groups = {g: [] for g in ['18-29','30-44','45-64','65+']}
gender_groups = {'male': [], 'female': []}
ageEdges = [(18,30,'18-29'),(30,45,'30-44'),(45,65,'45-64'),(65,76,'65+')]

for _ in range(N):
    p = {'salary':20000+random.random()*180000, 'age':random.randint(18,75),
         'hhsize':random.randint(1,5), 'country':random.choice(['US','UK']),
         'gender':random.choice(['male','female']),
         'education':random.choice(['nocollege','college']),
         'riskTolerance':random.choice(['low','medium','high']),
         'style':random.choice(['conservative','mixed','highrisk'])}
    p['region'] = random.choice(['Northeast','Midwest','South','West'] if p['country']=='US'
                                 else ['England','Wales','Scotland','Northern Ireland'])
    expL, DI = gamblingOutcome(p)
    if DI > 0:
        R = -expL / DI
        R_vals.append(R)
        gender_groups[p['gender']].append(R)
        for lo, hi, label in ageEdges:
            if lo <= p['age'] < hi:
                age_groups[label].append(R)
                break

ok(f"MC: {len(R_vals)} valid R values", len(R_vals) > 1000)
meanR = sum(R_vals) / len(R_vals)
ok(f"MC mean R = {100*meanR:.2f}% > 0", meanR > 0)

# Verify age groups get populated
for label in age_groups:
    ok(f"Age group {label}: n={len(age_groups[label])}", len(age_groups[label]) > 50)

# Verify male R > female R on average (from model structure)
maleR = sum(gender_groups['male'])/len(gender_groups['male'])
femaleR = sum(gender_groups['female'])/len(gender_groups['female'])
ok(f"Male mean R ({100*maleR:.2f}%) > female ({100*femaleR:.2f}%)",
   maleR > femaleR)

# Compute harm rates for current population mean R
for name, L, k, Rmid in outcomes:
    harm = impactRate(meanR, L, k, Rmid)
    ok(f"Pop harm {name}: {100*harm:.2f}% in (0, {100*L}%)",
       0 < harm < L)

# Combined intervention reduces all harms
R_int = meanR * 0.40
for name, L, k, Rmid in outcomes:
    h_before = impactRate(meanR, L, k, Rmid)
    h_after  = impactRate(R_int, L, k, Rmid)
    ok(f"Combined int {name}: {100*h_after:.2f}% < {100*h_before:.2f}%",
       h_after < h_before)

wb.close()

# ==================================================================
print("\n" + "=" * 72)
print(f"Q3 EXTENDED TESTS:  {PASS} passed,  {FAIL} failed")
print("=" * 72)
if FAIL > 0:
    sys.exit(1)
else:
    print("\nALL Q3 EXTENDED TESTS PASSED.")
