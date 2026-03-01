#!/usr/bin/env python3
"""
Generate all M3 Challenge 2026 figures as PNG files.
Mirrors exactly what the MATLAB code produces.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import openpyxl, math, os

XLSX = '/Users/aaryapatel/m3/M3-Challenge-Problem-Data-2026.xlsx'
OUT  = '/Users/aaryapatel/m3/figures'
DPI  = 180

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
    'axes.edgecolor': '#cccccc',
    'grid.color': '#dddddd',
    'grid.linestyle': '--',
    'grid.alpha': 0.7,
})

wb = openpyxl.load_workbook(XLSX, data_only=True)

def pv(ws, r, c):
    v = ws.cell(r, c).value
    if v is None: return 0.0
    if isinstance(v, (int, float)):
        return 0.0 if (isinstance(v, float) and math.isnan(v)) else float(v)
    try: return float(str(v).replace(',', ''))
    except: return 0.0

# ======================== DATA LOADING ========================
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

# ======================== MODEL FUNCTIONS ========================
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
    return Y - E, Y, E

def gamblingOutcome(p):
    DI = DI_full(p['salary'], p['age'], p['hhsize'], p['country'], p['region'])[0]
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

def DI_CI(S, age, h, country, region):
    """Return (DI, DI_lo, DI_hi) with 95% CI from parameter uncertainty."""
    DI, Y, E = DI_full(S, age, h, country, region)
    cv_E = math.sqrt(0.20**2 + 0.10**2 + 0.15**2)  # ~0.269
    E_lo = max(E * (1 - 1.96 * cv_E), 0)
    E_hi = min(E * (1 + 1.96 * cv_E), Y)
    DI_hi = max(Y - E_lo, 0)
    DI_lo = max(Y - E_hi, 0)
    return DI, DI_lo, DI_hi

def impactRate(R_in, L, k, Rmid):
    R_in = np.asarray(R_in, dtype=float)
    return L / (1 + np.exp(-k * (R_in - Rmid)))

# ======================== MONTE CARLO ========================
print("Running Monte Carlo (N=2000) ...")
rng = np.random.RandomState(42)
N = 2000

countries_list = ['US','UK']
us_regs = ['Northeast','Midwest','South','West']
uk_regs = ['England','Wales','Scotland','Northern Ireland']
genders_list = ['male','female']
ed_list = ['nocollege','college']
risk_list = ['low','medium','high']
style_list = ['conservative','mixed','highrisk']

pop_ages = np.zeros(N)
pop_genders = []
pop_countries = []
pop_regions = []
pop_losses = np.zeros(N)
pop_DIs = np.zeros(N)
pop_salaries = np.zeros(N)

for i in range(N):
    p = {
        'salary': 20000 + rng.rand() * 180000,
        'age': rng.randint(18, 76),
        'hhsize': rng.randint(1, 6),
        'country': rng.choice(countries_list),
        'gender': rng.choice(genders_list),
        'education': rng.choice(ed_list),
        'riskTolerance': rng.choice(risk_list),
        'style': rng.choice(style_list),
    }
    p['region'] = rng.choice(us_regs if p['country']=='US' else uk_regs)

    expL, DI = gamblingOutcome(p)
    pop_ages[i] = p['age']
    pop_genders.append(p['gender'])
    pop_countries.append(p['country'])
    pop_regions.append(p['region'])
    pop_losses[i] = expL
    pop_DIs[i] = DI
    pop_salaries[i] = p['salary']

pop_genders = np.array(pop_genders)
pop_countries = np.array(pop_countries)
pop_regions = np.array(pop_regions)

# R calculation
R_all = np.full(N, np.nan)
valid_mask = pop_DIs > 0
R_all[valid_mask] = -pop_losses[valid_mask] / pop_DIs[valid_mask]
Rv = R_all[np.isfinite(R_all) & (R_all > 0)]

print(f"  Mean R: {100*np.mean(Rv):.2f}%")
print(f"  High-risk (R>=15%): {100*np.sum(Rv>=0.15)/len(Rv):.1f}%")

fignum = 0

# ================================================================
# FIGURE 1 — Q1: DI vs Salary with 95% CI bands
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q1 — DI vs Salary with 95% CI ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
salaries = np.linspace(20000, 200000, 300)
hh_sizes = [1, 2, 4]
colors_q1 = ['#1f77b4', '#d62728', '#2ca02c']

for j, h in enumerate(hh_sizes):
    di_mid = np.zeros(len(salaries))
    di_lo  = np.zeros(len(salaries))
    di_hi  = np.zeros(len(salaries))
    for k, s in enumerate(salaries):
        di_mid[k], di_lo[k], di_hi[k] = DI_CI(s, 35, h, 'US', 'West')

    ax.fill_between(salaries/1000, di_lo/1000, di_hi/1000,
                    color=colors_q1[j], alpha=0.15)
    ax.plot(salaries/1000, di_mid/1000, color=colors_q1[j], linewidth=2.2,
            label=f'h = {h}')

ax.set_xlabel('Annual Gross Salary ($k)')
ax.set_ylabel('Disposable Income ($k)')
ax.set_title('Q1: Disposable Income vs Salary with 95% CI (US West, Age 35)')
ax.legend(framealpha=0.9)
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q1_DI_vs_Salary.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 1b — Q1: CI width across salary range (standalone)
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q1 — CI Width by Salary ...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

# Left: CI for US regions at h=2
us_regions_ci = ['Northeast', 'Midwest', 'South', 'West']
reg_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for j, reg in enumerate(us_regions_ci):
    mid = np.array([DI_CI(s, 35, 2, 'US', reg)[0] for s in salaries])
    lo  = np.array([DI_CI(s, 35, 2, 'US', reg)[1] for s in salaries])
    hi  = np.array([DI_CI(s, 35, 2, 'US', reg)[2] for s in salaries])
    ax1.fill_between(salaries/1000, lo/1000, hi/1000, color=reg_colors[j], alpha=0.12)
    ax1.plot(salaries/1000, mid/1000, color=reg_colors[j], linewidth=2, label=reg)

ax1.set_xlabel('Annual Gross Salary ($k)')
ax1.set_ylabel('Disposable Income ($k)')
ax1.set_title('Q1: DI with 95% CI by US Region (h=2, age 35)')
ax1.legend(framealpha=0.9)
ax1.grid(True)

# Right: CI for UK regions at h=2
uk_regions_ci = ['England', 'Wales', 'Scotland', 'Northern Ireland']
uk_colors = ['#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
for j, reg in enumerate(uk_regions_ci):
    mid = np.array([DI_CI(s, 35, 2, 'UK', reg)[0] for s in salaries])
    lo  = np.array([DI_CI(s, 35, 2, 'UK', reg)[1] for s in salaries])
    hi  = np.array([DI_CI(s, 35, 2, 'UK', reg)[2] for s in salaries])
    ax2.fill_between(salaries/1000, lo/1000, hi/1000, color=uk_colors[j], alpha=0.12)
    ax2.plot(salaries/1000, mid/1000, color=uk_colors[j], linewidth=2, label=reg)

ax2.set_xlabel('Annual Gross Salary ($k)')
ax2.set_ylabel('Disposable Income ($k)')
ax2.set_title('Q1: DI with 95% CI by UK Region (h=2, age 35)')
ax2.legend(framealpha=0.9)
ax2.grid(True)

fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q1_DI_CI_by_Region.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 2 — Q2: Expected Annual Loss Histogram
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q2 — Loss Histogram ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
losses_nonzero = pop_losses[pop_losses < -0.5]
ax.hist(losses_nonzero, bins=50, color='#4c72b0', edgecolor='white', alpha=0.85)
ax.set_xlabel('Expected Annual Net Outcome ($)')
ax.set_ylabel('Count')
ax.set_title('Q2: Distribution of Expected Annual Gambling Losses')
ax.axvline(np.mean(losses_nonzero), color='#d62728', linestyle='--', linewidth=1.5,
           label=f'Mean = ${np.mean(losses_nonzero):,.0f}')
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q2_Loss_Histogram.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 3 — Q2: DI vs Annual Loss scatter
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q2 — DI vs Loss Scatter ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
mask_sc = pop_DIs > 0
ax.scatter(pop_DIs[mask_sc]/1000, -pop_losses[mask_sc]/1000,
           s=12, alpha=0.35, c='#4c72b0', edgecolors='none')
ax.set_xlabel('Disposable Income ($k)')
ax.set_ylabel('Expected Annual Loss ($k)')
ax.set_title('Q2: Disposable Income vs Expected Annual Loss')
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q2_DI_vs_Loss_Scatter.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 4 — Q3-1: R Distribution
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — R Distribution ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.hist(100*Rv, bins=50, color='#3399dd', edgecolor='white', alpha=0.85)
ax.axvline(100*np.mean(Rv), color='#d62728', linestyle='--', linewidth=1.5,
           label=f'Mean R = {100*np.mean(Rv):.2f}%')
ax.axvline(15, color='#ff7700', linestyle=':', linewidth=1.5,
           label='High-risk threshold (15%)')
ax.set_xlabel('R = Gambling Loss as % of Disposable Income')
ax.set_ylabel('Count')
ax.set_title('Q3: Distribution of R = Gambling Expense / DI')
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_1_R_Distribution.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# Q3 projection setup
# ================================================================
years = np.arange(2024, 2035)
nYears = len(years)
annualGrowth = 0.09
growthCurve = (1 + annualGrowth) ** np.arange(nYears)

ageEdges = [18, 30, 45, 65, 76]
ageLabels = ['18-29', '30-44', '45-64', '65+']
nAG = len(ageLabels)
ageSens = [1.25, 1.10, 0.95, 0.80]

# ================================================================
# FIGURE 5 — Q3-2: R over time by Age Group
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — R Over Time by Age ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
age_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

for g in range(nAG):
    mask = np.isfinite(R_all) & (R_all > 0) & (pop_ages >= ageEdges[g]) & (pop_ages < ageEdges[g+1])
    baseR = np.mean(R_all[mask]) if np.sum(mask) > 0 else np.mean(Rv)
    proj = baseR * growthCurve * ageSens[g]
    ax.plot(years, 100*proj, '-o', linewidth=2.2, color=age_colors[g],
            markersize=5, label=ageLabels[g])

ax.set_xlabel('Year')
ax.set_ylabel('R (%)')
ax.set_title('Q3: Projected Gambling-to-DI Ratio by Age Group')
ax.legend(framealpha=0.9)
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_2_R_by_Age.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 6 — Q3-3: R over time by Gender
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — R Over Time by Gender ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
genderSens = [1.15, 0.85]
gen_colors = ['#2660a4', '#d94f04']

for g, (label, sens) in enumerate(zip(['Male', 'Female'], genderSens)):
    gkey = label.lower()
    mask = np.isfinite(R_all) & (R_all > 0) & (pop_genders == gkey)
    baseR = np.mean(R_all[mask]) if np.sum(mask) > 0 else np.mean(Rv)
    proj = baseR * growthCurve * sens
    marker = 's' if g == 0 else 'D'
    ax.plot(years, 100*proj, f'-{marker}', linewidth=2.2, color=gen_colors[g],
            markersize=5, label=label)

ax.set_xlabel('Year')
ax.set_ylabel('R (%)')
ax.set_title('Q3: Projected Gambling-to-DI Ratio by Gender')
ax.legend(framealpha=0.9)
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_3_R_by_Gender.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 7 — Q3-4: R over time by Country/Region
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — R Over Time by Region ...")
allRegions = ['Northeast','Midwest','South','West',
              'England','Wales','Scotland','Northern Ireland']
regSens = [1.05, 0.95, 1.10, 1.12, 1.08, 0.90, 0.95, 0.88]

fig, ax = plt.subplots(figsize=(10, 6))
reg_colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728',
              '#9467bd','#8c564b','#e377c2','#7f7f7f']
lstyles = ['-','-','-','-','--','--','--','--']
markers = ['o','s','D','^','o','s','D','^']

for j, (reg, sens) in enumerate(zip(allRegions, regSens)):
    mask = np.isfinite(R_all) & (R_all > 0) & (pop_regions == reg)
    baseR = np.mean(R_all[mask]) if np.sum(mask) > 0 else np.mean(Rv)
    proj = baseR * growthCurve * sens
    ax.plot(years, 100*proj, linestyle=lstyles[j], marker=markers[j],
            linewidth=1.8, color=reg_colors[j], markersize=4, label=reg)

ax.set_xlabel('Year')
ax.set_ylabel('R (%)')
ax.set_title('Q3: Projected R by Country / Region')
ax.legend(framealpha=0.9, ncol=2, fontsize=9)
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_4_R_by_Region.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# Outcome definitions
# ================================================================
outcomes = [
    ('Debt',           0.40, 25, 0.12),
    ('Depression',     0.45, 22, 0.13),
    ('Divorce',        0.30, 28, 0.14),
    ('Drug Addiction', 0.25, 30, 0.15),
    ('School Decline', 0.50, 25, 0.10),
]
nOut = len(outcomes)
oColors = ['#d62728','#2ca02c','#9467bd','#8c564b','#e377c2']

# ================================================================
# FIGURE 8 — Q3-5: Dose-Response Curves
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — Dose-Response Curves ...")
fig, ax = plt.subplots(figsize=(9, 5.5))
Rsweep = np.linspace(0, 0.30, 300)

for j, (name, L, k, Rmid) in enumerate(outcomes):
    y = 100 * impactRate(Rsweep, L, k, Rmid)
    ax.plot(100*Rsweep, y, linewidth=2.5, color=oColors[j], label=name)

ax.set_xlabel('R = Gambling Expense / DI (%)')
ax.set_ylabel('Probability of Harm (%)')
ax.set_title('Q3: How Gambling Ratio Drives Social Harm')
ax.legend(framealpha=0.9)
ax.set_xlim(0, 30)
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_5_Dose_Response.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 9 — Q3-6: Current Harm Rates by Age Group
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — Harm by Age Group ...")
fig, ax = plt.subplots(figsize=(10, 5.5))
harmByAge = np.zeros((nAG, nOut))
for g in range(nAG):
    mask = np.isfinite(R_all) & (R_all > 0) & (pop_ages >= ageEdges[g]) & (pop_ages < ageEdges[g+1])
    if np.sum(mask) == 0: continue
    mR = np.mean(R_all[mask])
    for j, (name, L, k, Rmid) in enumerate(outcomes):
        harmByAge[g, j] = 100 * float(impactRate(mR, L, k, Rmid))

x = np.arange(nAG)
width = 0.15
for j in range(nOut):
    ax.bar(x + j*width - (nOut-1)*width/2, harmByAge[:, j], width,
           color=oColors[j], label=outcomes[j][0], edgecolor='white', linewidth=0.5)

ax.set_xticks(x)
ax.set_xticklabels(ageLabels)
ax.set_xlabel('Age Group')
ax.set_ylabel('Estimated Harm Rate (%)')
ax.set_title('Q3: Social Harm Rates by Age Group (Current R)')
ax.legend(framealpha=0.9, fontsize=9)
ax.grid(True, axis='y')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_6_Harm_by_Age.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 10 — Q3-7: Intervention Effect on R
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — Intervention on R ...")
interventions = [
    ('Spending\nCaps', 0.30),
    ('Self-\nExclusion', 0.25),
    ('Ad\nBans', 0.15),
    ('Education', 0.10),
    ('Combined', 0.60),
]
nInt = len(interventions)
R_baseline = float(np.mean(Rv))
R_after = [R_baseline * (1 - red) for _, red in interventions]

fig, ax = plt.subplots(figsize=(9, 5.5))
x = np.arange(nInt)
w = 0.35
bars1 = ax.bar(x - w/2, [100*R_baseline]*nInt, w, color='#d94f04',
               label='Before', edgecolor='white')
bars2 = ax.bar(x + w/2, [100*r for r in R_after], w, color='#2ca02c',
               label='After', edgecolor='white')

ax.set_xticks(x)
ax.set_xticklabels([name for name, _ in interventions])
ax.set_ylabel('Mean R (%)')
ax.set_title('Q3: Gambling Ratio Before vs After Intervention')
ax.legend(framealpha=0.9)
ax.grid(True, axis='y')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_7_Intervention_R.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 11 — Q3-8: Cascaded Outcome Improvement
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — Cascaded Improvement ...")
R_combined = R_baseline * 0.40
harm_before = [100*float(impactRate(R_baseline, L, k, Rm)) for _, L, k, Rm in outcomes]
harm_after  = [100*float(impactRate(R_combined, L, k, Rm))  for _, L, k, Rm in outcomes]

fig, ax = plt.subplots(figsize=(10, 5.5))
x = np.arange(nOut)
w = 0.35
ax.bar(x - w/2, harm_before, w, color='#d94f04', label='Before (current R)',
       edgecolor='white')
ax.bar(x + w/2, harm_after,  w, color='#2ca02c', label='After (60% R reduction)',
       edgecolor='white')

for i in range(nOut):
    diff = harm_before[i] - harm_after[i]
    ax.annotate(f'-{diff:.1f}pp', xy=(x[i], max(harm_before[i], harm_after[i]) + 0.3),
                ha='center', fontsize=8, color='#555555')

ax.set_xticks(x)
ax.set_xticklabels([name for name, *_ in outcomes])
ax.set_ylabel('Estimated Harm Rate (%)')
ax.set_title('Q3: Social Harm Before vs After Combined Intervention')
ax.legend(framealpha=0.9)
ax.grid(True, axis='y')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_8_Cascaded_Improvement.png'), dpi=DPI)
plt.close(fig)

# ================================================================
# FIGURE 12 — Q3-9: Harm Trajectories Over Time (2x3 subplots)
# ================================================================
fignum += 1
print(f"Figure {fignum}: Q3 — Harm Trajectories ...")
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes_flat = axes.flatten()

for j, (name, L, k, Rmid) in enumerate(outcomes):
    ax = axes_flat[j]
    R_t_none = R_baseline * growthCurve
    R_t_int  = R_combined * growthCurve
    h_none = 100 * impactRate(R_t_none, L, k, Rmid)
    h_int  = 100 * impactRate(R_t_int, L, k, Rmid)
    ax.plot(years, h_none, '-o', linewidth=2, color='#d94f04', markersize=3,
            label='No action')
    ax.plot(years, h_int,  '-s', linewidth=2, color='#2ca02c', markersize=3,
            label='Combined intervention')
    ax.set_title(name, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Rate (%)')
    ax.grid(True)
    if j == 0:
        ax.legend(fontsize=7, framealpha=0.9)

axes_flat[-1].set_visible(False)
fig.suptitle('Q3: Projected Social-Harm Trajectories (2024-2034)',
             fontsize=14, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'Q3_9_Harm_Trajectories.png'), dpi=DPI,
            bbox_inches='tight')
plt.close(fig)

# ================================================================
wb.close()
print(f"\nDone — {fignum} figures saved to {OUT}/")
for f in sorted(os.listdir(OUT)):
    if f.endswith('.png'):
        print(f"  {f}")
