# BTD5-Lite v2 for the TI-84 Evo (TI-Python)
# 13 towers x 3 paths x 5 tiers, 5 maps, 3 difficulties, 11 bloon types,
# targeting modes, freeze/glue/village buffs, 3 save slots + autosave.
# CURSOR CONTROLS: arrows move the yellow box, ENTER selects the cell.
#   First run asks you to press each key once (saved to btd5.key).
#   'menu' key opens a typed prompt (save/load/new/etc); Enter there returns.
#   If key reading doesn't work, answer n to the cursor question and type cells.
# TYPED CONTROLS: type a map cell like  a3  (col a, row 3)
#   empty cell -> pick a tower from the menu to build
#   tower cell -> tower menu: 1/2/3 upgrade, t target, s sell
#  g = next round   m map   l list   h prices   new   save [1-3]   load [1-3]   q
try:
    import ti_draw as D
except:
    D = None

W, H, C, TOP = 16, 10, 20, 20   # grid cols/rows, cell px, HUD px

MAPS = [
 ("Meadow",   [(0,1),(13,1),(13,4),(2,4),(2,7),(14,7),(14,9)]),
 ("Zigzag",   [(0,0),(14,0),(14,2),(1,2),(1,4),(14,4),(14,6),(1,6),(1,8),(15,8)]),
 ("Spiral",   [(0,0),(15,0),(15,9),(1,9),(1,2),(13,2),(13,7),(4,7),(4,4),(10,4)]),
 ("Shortcut", [(0,2),(8,2),(8,7),(15,7)]),
 ("Hairpin",  [(0,9),(14,9),(14,6),(3,6),(3,3),(12,3),(12,0)]),
]
# name, lives, cash, price mult, win round
DIFFS = [("Easy",60,800,.85,30), ("Normal",40,650,1.0,40), ("Hard",25,500,1.15,50)]

PATH = []; PCELL = set()

def setmap(m):
    del PATH[:]; PCELL.clear()
    wp = MAPS[m][1]
    for i in range(len(wp)-1):
        x0, y0 = wp[i]; x1, y1 = wp[i+1]
        n = max(abs(x1-x0), abs(y1-y0))
        for k in range(n*4):
            PATH.append((x0+(x1-x0)*k/(n*4), y0+(y1-y0)*k/(n*4)))
        for k in range(n+1):
            PCELL.add((x0+(x1-x0)*k//n, y0+(y1-y0)*k//n))
    PATH.append(wp[-1])

# ---- bloons ----  [type, hp, dist(1/4 cells), camo, freeze, slow]
CH = {'R':[],'B':['R'],'G':['B'],'Y':['G'],'P':['Y'],'K':['P','P'],'W':['P','P'],
      'L':['K','K'],'Z':['K','W'],'C':['Z','Z'],'M':['C','C','C','C']}
HP = {'C':10,'M':200}
SPD = {'R':.08,'B':.10,'G':.12,'Y':.16,'P':.18,'K':.14,'W':.15,'L':.09,'Z':.15,'C':.15,'M':.09}
COL = {'R':(230,30,30),'B':(40,90,240),'G':(40,190,50),'Y':(240,220,30),'P':(255,120,200),
       'K':(20,20,20),'W':(240,240,240),'L':(120,120,130),'Z':(150,150,150),
       'C':(170,100,40),'M':(40,60,160)}
ORDER = 'RBGYPKWLZCM'
START = [1,3,6,9,12,16,20,24,28,34,40]
MULT = [1.0,.9,.8,.7,.6,.45,.4,.3,.25,.2,.05]
VAL = {}
def val(t):
    if t not in VAL: VAL[t] = HP.get(t,1) + sum(val(c) for c in CH[t])
    return VAL[t]

def wave(n):
    sp = []
    for i in range(len(ORDER)):
        if n < START[i] or (i < 6 and n > START[i]+14): continue
        cnt = min(60, int((n-START[i]+2)*4*MULT[i]))
        gap = max(2, int(8-n/6))
        for k in range(cnt):
            cam = 1 if (n >= 14 and i < 9 and k % (3 if n < 30 else 2) == 0) else 0
            sp.append((i*5+k*gap, ORDER[i], cam))
    sp.sort()
    return sp

# ---- towers ----
DEF = dict(d=0,cd=10,r=3.0,p=1,sh=1,sp=0,cam=0,lead=0,inc=0,sharp=0,boom=0,
           frz=0,glue=0,vcd=1,vr=0,vcam=0)
MULK = ('cd','vcd'); SETK = ('cam','lead','vcam')
def B(**k):
    s = dict(DEF); s.update(k); return s
def U(n, c, **k): return (n, c, k)

TW = {
'd': ("Dart Monkey",170,B(d=1,cd=9,r=3.0,p=2,sharp=1),[
  [U("Sharp Shots",140,p=1),U("Razor Sharp",220,p=2),U("Spike-o-pult",500,d=1,p=6),
   U("Juggernaut",1800,d=3,p=8,lead=1),U("Ultra-Juggernaut",15000,d=8,p=10)],
  [U("Quick Shots",120,cd=.8),U("Very Quick",190,cd=.8),U("Triple Shot",400,sh=2),
   U("Fan Club",8000,cd=.3,sh=1),U("Plasma Fan Club",20000,cd=.3,d=2)],
  [U("Long Range",90,r=1),U("Eyesight",120,r=1,cam=1),U("Crossbow",500,d=2,r=2,cd=.8),
   U("Sharp Shooter",2200,d=3,cd=.7),U("Crossbow Master",14000,d=8,cd=.4)]]),
't': ("Tack Shooter",280,B(d=1,cd=14,r=2.0,p=6,sharp=1),[
  [U("Faster Shooting",150,cd=.85),U("Even Faster",250,cd=.85),U("Hyper Fast",600,cd=.75),
   U("Ring of Fire",2500,d=1,cd=.7,lead=1),U("Inferno Ring",12000,d=3,cd=.5)],
  [U("Long Range Tacks",100,r=.5),U("Super Range",225,r=.6),U("Blade Shooter",550,d=1,p=4,lead=1),
   U("Blade Maelstrom",2800,p=6,d=1),U("Super Maelstrom",14000,d=3,p=10)],
  [U("More Tacks",150,p=2),U("Even More Tacks",250,p=2),U("Tack Sprayer",500,p=4),
   U("Overdrive",3000,cd=.6),U("The Tack Zone",15000,p=10,d=2,cd=.7)]]),
's': ("Sniper Monkey",350,B(d=2,cd=20,r=99,lead=1),[
  [U("Full Metal Jacket",350,d=1),U("Point Five Oh",900,d=3),U("Deadly Precision",3200,d=10),
   U("Cripple MOAB",6000,d=25),U("Elite Sniper",20000,d=60)],
  [U("Fast Firing",300,cd=.7),U("Faster Firing",800,cd=.7),U("Semi-Auto",3000,cd=.4),
   U("Full Auto",8000,cd=.5,sh=1),U("Machine Gun Nest",20000,cd=.5,sh=2)],
  [U("Night Vision",250,cam=1),U("Shrapnel",700,p=2),U("Bouncing Bullet",1800,p=4,d=1),
   U("Supply Drop",3500,inc=250),U("Elite Defender",12000,inc=700,d=4,cd=.5)]]),
'b': ("Bomb Tower",600,B(d=1,cd=20,r=3.2,sp=1.2,lead=1,boom=1),[
  [U("Bigger Bombs",200,sp=.5),U("Heavy Bombs",400,d=1),U("Really Big Bombs",900,sp=.7,d=1),
   U("Bloon Impact",3200,d=3,sp=.5),U("Bloon Crush",14000,d=12,sp=1)],
  [U("Faster Reload",250,cd=.8),U("Missile Launcher",400,cd=.8,r=1),U("MOAB Mauler",900,d=3),
   U("MOAB Assassin",3000,d=10,cd=.8),U("MOAB Eliminator",18000,d=40,cd=.6)],
  [U("Extra Range",150,r=1),U("Frag Bombs",400,p=2),U("Cluster Bombs",800,sp=.4,p=3),
   U("Recursive Cluster",3500,p=6,d=1),U("Bomb Blitz",12000,p=12,cd=.5)]]),
'i': ("Ice Tower",300,B(cd=30,r=2.2,p=99,frz=8),[
  [U("Enhanced Freeze",200,frz=4),U("Deep Freeze",350,frz=6),U("Arctic Wind",2200,frz=8,r=.5),
   U("Snap Freeze",3000,frz=10,cd=.7),U("Absolute Zero",8000,frz=16,r=1,cd=.5)],
  [U("Larger Radius",100,r=.5),U("Re-Freeze",400,cd=.7),U("Cryo Cannon",1500,d=1),
   U("Icicles",2500,d=2,cd=.8),U("Icicle Impale",7000,d=5)],
  [U("Wider Freeze",150,r=.4),U("Even Wider",300,r=.6),U("Ice Shards",900,d=1),
   U("Blizzard",3000,cd=.6),U("Ice Age",9000,frz=10,r=1)]]),
'g': ("Glue Gunner",270,B(cd=14,r=3.0,p=2,glue=35),[
  [U("Glue Soak",200,p=3),U("Glue Splatter",300,p=4),U("Glue Hose",1500,cd=.5),
   U("Corrosive Glue",3000,d=1),U("Glue Strike",8000,d=2,p=10)],
  [U("Bigger Globs",100,r=.5),U("Stickier Glue",250,glue=25),U("Super Glue",800,glue=40),
   U("Glue Storm",3000,p=10,cd=.8),U("Glue Hurricane",12000,p=25,cd=.6,glue=30)],
  [U("Acid Splash",300,d=1),U("Bloon Dissolver",1600,d=1,cd=.8),U("Liquefier",4500,d=2,lead=1),
   U("Acid Pool",9000,d=4,p=4),U("Dissolve All",18000,d=8,cd=.5)]]),
'm': ("Mortar",700,B(d=1,cd=45,r=99,sp=1.5,lead=1,boom=1),[
  [U("Bigger Blast",250,sp=.3),U("Bigger Still",500,sp=.4),U("Heavy Shells",1500,d=2),
   U("Artillery Battery",6000,d=4,p=1),U("Pop and Awe",18000,d=15,p=2)],
  [U("Faster Reload",300,cd=.8),U("Rapid Reload",600,cd=.7),U("Shell Shock",1800,d=1,cd=.8),
   U("Burny Stuff",5000,d=3),U("Blitz",16000,cd=.4,d=5)],
  [U("Night Targeting",400,cam=1),U("Cluster Shells",800,p=2),U("Hunter Shells",2500,p=3),
   U("Supply Shells",4000,inc=250),U("Rain of Fire",15000,p=8,d=3)]]),
'n': ("Ninja Monkey",500,B(d=1,cd=7,r=3.3,cam=1,sharp=1),[
  [U("Discipline",300,cd=.75),U("Sharp Shurikens",350,p=2),U("Double Shot",850,sh=1),
   U("Bloonjitsu",2800,sh=2,cd=.8),U("Grandmaster",14000,d=4,sh=3)],
  [U("Seeking Shuriken",300,r=1),U("Distraction",400,p=1),U("Flash Bomb",900,sp=1.0),
   U("Sticky Bomb",3000,sp=.5,d=2),U("Sabotage",12000,cd=.5,d=3)],
  [U("Sharper Blades",300,d=1),U("Tracking",300,r=1),U("Cursed Blades",1200,d=2,lead=1),
   U("Death Blossom",3500,p=5,sh=1),U("Shadow Clone",14000,sh=3,d=3)]]),
'r': ("Boomerang",330,B(d=1,cd=12,r=3.5,p=4,sharp=1),[
  [U("Improved Rangs",200,p=3),U("Glaives",280,d=1,p=2),U("Ricochet",1500,p=6,d=1),
   U("M.O.A.R Glaives",3500,d=4,lead=1),U("Glaive Lord",14000,d=10,p=10)],
  [U("Faster Throw",200,cd=.8),U("Bionic Rang",400,cd=.6),U("Turbo Charge",1800,cd=.5,sh=1),
   U("Perma-Charge",4000,cd=.3),U("Ultra Charge",15000,cd=.3,d=3)],
  [U("Long Range Rangs",100,r=1),U("Red Hot Rangs",300,d=1,lead=1),U("Kylie Rang",1200,d=2,p=3),
   U("MOAB Press",3000,d=5),U("MOAB Domination",12000,d=15)]]),
'k': ("Spike Factory",550,B(d=1,cd=25,r=3.0,p=4,sharp=1),[
  [U("Bigger Stacks",250,p=4),U("White Hot Spikes",400,d=1,lead=1),U("Spiked Balls",1200,d=2,p=4),
   U("Spiked Mines",2800,sp=1.2,d=3),U("Super Mines",12000,sp=1.5,d=10)],
  [U("Faster Production",300,cd=.8),U("Even Faster",500,cd=.75),U("MOAB-SHREDR",1500,d=3),
   U("Spike Storm",3500,cd=.4),U("Carpet of Spikes",14000,cd=.3,p=10,d=2)],
  [U("Long Reach",200,r=.7),U("Smart Spikes",400,cam=1),U("Perma Spikes",1300,d=1,p=3),
   U("Spike Clog",3000,p=6),U("Super Perma",15000,d=4)]]),
'f': ("Banana Farm",500,B(p=0,r=0,inc=60),[
  [U("More Bananas",250,inc=40),U("Plantation",600,inc=100),U("Research",2500,inc=250),
   U("Banana Central",7000,inc=600),U("Banana Empire",18000,inc=1500)],
  [U("Long Life",200,inc=25),U("Valuable",500,inc=50),U("Monkey Bank",2000,inc=150),
   U("IMF Loan",5000,inc=250),U("Monkey-Nomics",14000,inc=800)],
  [U("Coupons",150,inc=20),U("Fertilizer",400,inc=45),U("Greenhouse",1800,inc=120),
   U("Banana Cartel",4500,inc=300),U("Fruit Baron",13000,inc=700)]]),
'v': ("Monkey Village",1200,B(p=0,r=3.0,vcd=.9),[
  [U("Bigger Radius",400,r=.5),U("Jungle Drums",1500,vcd=.8),U("Primary Training",3500,vr=.5),
   U("Mentoring",9000,vcd=.8),U("Expertise",20000,vr=1,vcd=.7)],
  [U("Radar Scanner",800,vcam=1),U("Wider Net",1000,r=.7),U("Call to Arms",3000,vcd=.85),
   U("Homeland Defense",6000,vr=1),U("Monkey Aces",18000,vcd=.7,vr=1)],
  [U("Large Village",400,r=.5),U("Better Training",900,vr=.5),U("Overclock",2500,vcd=.85),
   U("Monkey City",7000,r=1,vr=.5),U("Elite Village",19000,vcd=.6,vr=1,vcam=1)]]),
'x': ("Super Monkey",2500,B(d=1,cd=2.5,r=4.5,cam=1,sharp=1),[
  [U("Laser Blasts",3500,d=1,lead=1),U("Plasma Blasts",4500,d=2),U("Sun God",15000,d=8,p=4),
   U("Temple",40000,d=25,p=4),U("True Sun God",80000,d=60,p=8)],
  [U("Super Range",1500,r=1),U("Epic Range",2000,r=1.5),U("Robo Monkey",6500,sh=1,cd=.7),
   U("Tech Terror",15000,cd=.5,sh=2),U("Dart Storm",50000,cd=.3,sh=3)],
  [U("Knockback",1200,cd=.85),U("Dark Knight",5000,d=2,p=3),U("Dark Champion",14000,d=4,p=5,cd=.7),
   U("Shadow King",35000,d=12,p=8),U("Void Lord",70000,d=30,p=12,cd=.7)]]),
}
TCOL = {'d':(140,90,40),'t':(200,60,60),'s':(40,120,60),'b':(60,60,70),'i':(100,200,240),
        'g':(150,220,60),'m':(90,90,40),'n':(70,30,110),'r':(220,140,40),'k':(130,130,130),
        'f':(240,210,40),'v':(180,60,180),'x':(30,30,200)}

G = {'c':650,'l':40,'r':0,'best':0,'m':0,'d':1}
TOWERS = []   # [kind,col,row,[a,b,c],spent,cooldown,stats,targeting]
HEX = '0123456789abcdef'
CUR = [0, 0]; USECUR = [False]; KEYS = {}
KN = ('up','down','left','right','enter','go','menu')
KL = ('UP arrow','DOWN arrow','LEFT arrow','RIGHT arrow','SELECT (enter)','START ROUND (any key, e.g. +)','MENU (any key, e.g. mode)')
def rawkey():
    import ti_system as T
    if hasattr(T, 'wait_key'): return str(T.wait_key())
    while True:
        k = T.get_key()
        if k: return str(k)
def readkey():
    k = rawkey()
    for n in KEYS:
        if KEYS[n] == k: return n
    return None
def calibrate():
    for i in range(len(KN)):
        print('Press', KL[i]); KEYS[KN[i]] = rawkey()
    try:
        f = open('btd5.key', 'w'); f.write('|'.join([KEYS[n] for n in KN])); f.close()
    except: pass
def setup_keys():
    try:
        import ti_system
    except:
        return False
    try:
        f = open('btd5.key', 'r'); v = f.read().split('|'); f.close()
        if len(v) == len(KN):
            for i in range(len(KN)): KEYS[KN[i]] = v[i]
            return True
    except: pass
    try:
        calibrate(); return True
    except: return False

def price(x): return int(x*DIFFS[G['d']][3])

def stats(tw):
    s = dict(TW[tw[0]][2])
    for p in range(3):
        for t in range(tw[3][p]):
            for k, v in TW[tw[0]][3][p][t][2].items():
                if k in MULK: s[k] *= v
                elif k in SETK: s[k] = 1
                else: s[k] += v
    tw[6] = s

def refresh():
    for t in TOWERS: stats(t)
    for v in TOWERS:
        if v[0] != 'v': continue
        vs = v[6]; r2 = vs['r']*vs['r']
        for t in TOWERS:
            if t is v or t[0] == 'v': continue
            dx = t[1]-v[1]; dy = t[2]-v[2]
            if dx*dx+dy*dy <= r2:
                s = t[6]; s['cd'] *= vs['vcd']; s['r'] += vs['vr']
                if vs['vcam']: s['cam'] = 1

def allowed(tiers, p):
    t = list(tiers); t[p] += 1
    if t[p] > 5: return False
    t.sort(reverse=True)
    return t[2] == 0 and t[1] <= 2

# ---- drawing ----
def px(c): return int(c*C)
def py(r): return int(TOP+r*C)

def draw(bl=None, note=''):
    hud = 'R%d $%d L%d %s' % (G['r'],G['c'],G['l'],note)
    if USECUR[0]:
        j = tower_at(CUR[0], CUR[1])
        hud = 'R%d $%d L%d %s%d %s' % (G['r'],G['c'],G['l'],HEX[CUR[0]],CUR[1],TW[TOWERS[j][0]][0] if j >= 0 else '')
    if D is None:
        g = [['.' if (c,r) in PCELL else ' ' for c in range(W)] for r in range(H)]
        for t in TOWERS: g[t[2]][t[1]] = t[0].upper()
        if USECUR[0]: g[CUR[1]][CUR[0]] = '@'
        if bl:
            for b in bl:
                i = int(b[2])
                if i < len(PATH)-1: g[int(PATH[i][1]+.5)][int(PATH[i][0]+.5)] = b[0]
        print('   ' + HEX[:W])
        for r in range(H): print(' %d ' % r + ''.join(g[r]))
        print(hud); return
    D.use_buffer()
    D.set_color(90,170,80); D.fill_rect(0,0,320,240)
    D.set_color(200,170,110)
    for (c,r) in PCELL: D.fill_rect(px(c),py(r),C,C)
    D.set_color(60,60,60)
    for c in range(W): D.draw_text(px(c)+6,py(H-1)+14,HEX[c])
    for r in range(H): D.draw_text(2,py(r)+14,str(r))
    for i, t in enumerate(TOWERS):
        D.set_color(*TCOL[t[0]]); D.fill_circle(px(t[1])+10,py(t[2])+10,8)
        D.set_color(255,255,255); D.draw_text(px(t[1])+5,py(t[2])+14,str(i))
    if bl:
        for b in bl:
            i = int(b[2])
            if i < len(PATH)-1:
                x = px(PATH[i][0])+10; y = py(PATH[i][1])+10
                D.set_color(*COL[b[0]]); D.fill_circle(x,y,8 if b[0]=='M' else 4)
                if b[3]: D.set_color(0,100,0); D.draw_circle(x,y,6)
                if b[4] > 0: D.set_color(120,230,255); D.draw_circle(x,y,5)
    if USECUR[0]:
        D.set_color(255,255,0)
        D.draw_rect(px(CUR[0]),py(CUR[1]),C,C); D.draw_rect(px(CUR[0])+1,py(CUR[1])+1,C-2,C-2)
    D.set_color(0,0,0); D.fill_rect(0,0,320,TOP)
    D.set_color(255,255,255); D.draw_text(2,14,hud)
    D.paint_buffer()

# ---- combat ----
def hit(b, d, bl):
    if b[1] > d:
        b[1] -= d; return 0
    d -= b[1]; b[1] = -1
    if b in bl: bl.remove(b)
    cash = 1
    for k, t in enumerate(CH[b[0]]):
        c = [t, HP.get(t,1), max(0, b[2]-k*1.5), b[3], 0, 0]
        bl.append(c)
        if k == 0 and d > 0: cash += hit(c, d, bl)
    return cash

def ok(b, s):
    if b[3] and not s['cam']: return False
    if b[0] == 'L' and s['sharp'] and not s['lead']: return False
    return True

def fire(tw, bl):
    s = tw[6]; x = tw[1]; y = tw[2]; r2 = s['r']*s['r']; last = len(PATH)-1
    cands = []
    for b in bl:
        i = int(b[2])
        if i > last: continue
        dx = PATH[i][0]-x; dy = PATH[i][1]-y
        if dx*dx+dy*dy <= r2 and ok(b, s): cands.append(b)
    if not cands: return False
    m = tw[7]
    if m == 0: cands.sort(key=lambda b: -b[2])
    elif m == 1: cands.sort(key=lambda b: b[2])
    else: cands.sort(key=lambda b: -val(b[0]))
    got = 0
    for b in cands[:int(s['p'])]:
        if s['frz'] and b[0] not in 'WZ': b[4] = s['frz']
        if s['glue']: b[5] = s['glue']
        if s['d'] <= 0: continue
        for _ in range(int(s['sh'])):
            if b[1] < 0: break
            i = min(int(b[2]), last); bx = PATH[i][0]; by = PATH[i][1]
            got += hit(b, s['d'], bl)
            if s['sp'] > 0:
                sr = s['sp']*s['sp']
                for o in list(bl):
                    if o[1] < 0 or (s['boom'] and o[0] == 'K'): continue
                    j = int(o[2])
                    if j > last: continue
                    ex = PATH[j][0]-bx; ey = PATH[j][1]-by
                    if ex*ex+ey*ey <= sr: got += hit(o, s['d'], bl)
    G['c'] += got
    return True

def run_wave():
    sp = wave(G['r']); bl = []; t = 0; si = 0; last = len(PATH)-1
    for tw in TOWERS: tw[5] = 0
    while si < len(sp) or bl:
        t += 1
        while si < len(sp) and sp[si][0] <= t:
            bl.append([sp[si][1], HP.get(sp[si][1],1), 0.0, sp[si][2], 0, 0]); si += 1
        for b in list(bl):
            if b[4] > 0: b[4] -= 1; continue
            v = SPD[b[0]]*4
            if b[5] > 0: b[5] -= 1; v *= .5
            b[2] += v
            if b[2] >= last:
                G['l'] -= val(b[0]); bl.remove(b)
        if G['l'] <= 0: return False
        for tw in TOWERS:
            if tw[6]['p'] < 1: continue
            if tw[5] > 0: tw[5] -= 1
            elif fire(tw, bl): tw[5] = max(1, tw[6]['cd'])
        if t % 3 == 0: draw(bl, 'wave')
    return True

# ---- save / load ----
def pack():
    s = '%d,%d,%d,%d,%d,%d' % (G['r'],G['c'],G['l'],G['best'],G['m'],G['d'])
    for t in TOWERS:
        s += ';%s,%d,%d,%d,%d,%d,%d,%d' % (t[0],t[1],t[2],t[3][0],t[3][1],t[3][2],t[4],t[7])
    return s

def unpack(s):
    a = s.strip().split(';'); h = [int(x) for x in a[0].split(',')]
    G.update(r=h[0],c=h[1],l=h[2],best=h[3],m=h[4] if len(h)>4 else 0,d=h[5] if len(h)>5 else 1)
    setmap(G['m']); del TOWERS[:]
    for x in a[1:]:
        f = x.split(',')
        TOWERS.append([f[0],int(f[1]),int(f[2]),[int(f[3]),int(f[4]),int(f[5])],int(f[6]),0,None,
                       int(f[7]) if len(f) > 7 else 0])
    refresh()

def fname(slot): return 'btd5_%s.sav' % slot

def save(slot):
    s = pack()
    try:
        f = open(fname(slot), 'w'); f.write(s); f.close()
        print('Saved slot', slot)
    except:
        print('No file access - copy this save code:'); print(s)

def load(slot, quiet=False):
    try:
        f = open(fname(slot), 'r'); s = f.read(); f.close()
    except:
        if quiet: return False
        s = input('No file. Paste save code (blank=cancel): ')
        if not s: return False
    try:
        unpack(s); return True
    except:
        print('Bad save'); return False

# ---- game flow ----
def newgame():
    print('Maps:')
    for i in range(len(MAPS)): print(' %d %s' % (i, MAPS[i][0]))
    try: m = int(input('Map #: '))
    except: m = 0
    for i in range(len(DIFFS)): print(' %d %s' % (i, DIFFS[i][0]))
    try: d = int(input('Difficulty #: '))
    except: d = 1
    m = m if 0 <= m < len(MAPS) else 0; d = d if 0 <= d < len(DIFFS) else 1
    best = G['best']
    G.update(r=0,c=DIFFS[d][2],l=DIFFS[d][1],m=m,d=d,best=best)
    del TOWERS[:]; setmap(m)

def shop():
    for k in TW: print('%s %s $%d' % (k, TW[k][0], price(TW[k][1])))

def info(i):
    t = TOWERS[i]; s = t[6]
    print('#%d %s %d/%d/%d sell $%d tgt:%s' % (i, TW[t[0]][0], t[3][0], t[3][1], t[3][2],
          int(t[4]*.7), ('first','last','strong')[t[7]]))
    print('dmg%d cd%.1f rng%.1f tg%d x%d spl%.1f frz%d glue%d inc%d%s%s' % (s['d'], s['cd'], s['r'],
          s['p'], s['sh'], s['sp'], s['frz'], s['glue'], s['inc'],
          ' CAMO' if s['cam'] else '', ' LEAD' if s['lead'] else ''))
    for p in range(3):
        n = t[3][p]
        if n >= 5: print(' %d)  MAX' % (p+1)); continue
        u = TW[t[0]][3][p][n]
        cost = price(u[1])
        print(' %d)%s %s $%d%s' % (p+1, '*' if G['c'] >= cost and allowed(t[3], p) else ' ', u[0], cost,
              '' if allowed(t[3], p) else ' LOCKED'))

def cell(p):
    t = ''.join(p).lower()
    if len(t) == 2 and t[0] in HEX and t[1].isdigit() and int(t[1]) < H:
        return (HEX.index(t[0]), int(t[1]))
    return None

def tower_at(c, r):
    for i in range(len(TOWERS)):
        if TOWERS[i][1] == c and TOWERS[i][2] == r: return i
    return -1

def pick_tower():
    ks = list(TW.keys()); line = ''
    for n in range(len(ks)):
        k = ks[n]; cost = price(TW[k][1])
        line += '%s%d %s %d' % ('*' if G['c'] >= cost else ' ', n+1, TW[k][0].split()[0][:7], cost)
        if n % 2: print(line); line = ''
        else: line += ' |'
    if line: print(line)
    a = input('Tower # (* = affordable, Enter=cancel): ').strip().lower()
    if a.isdigit() and 1 <= int(a) <= len(ks): return ks[int(a)-1]
    return None

def build(col, row):
    k = pick_tower()
    if not k: return
    cost = price(TW[k][1])
    if G['c'] < cost: print('Need $%d' % cost); return
    G['c'] -= cost
    TOWERS.append([k,col,row,[0,0,0],cost,0,None,0]); refresh()
    draw(None, 'built ' + TW[k][0])

def tower_menu(i):
    while True:
        t = TOWERS[i]; info(i)
        a = input('1/2/3 upgrade  t target  s sell  Enter back: ').strip().lower()
        if a in ('1','2','3'):
            pa = int(a)-1
            if not allowed(t[3], pa): print('Locked (max 5 / 2 / 0)'); continue
            u = TW[t[0]][3][pa][t[3][pa]]; cost = price(u[1])
            if G['c'] < cost: print('Need $%d' % cost); continue
            G['c'] -= cost; t[4] += cost; t[3][pa] += 1; refresh(); draw(None, u[0])
        elif a == 't': t[7] = (t[7]+1) % 3
        elif a == 's':
            if input('Sell for $%d? (y/n) ' % int(t[4]*.7)) == 'y':
                TOWERS.pop(i); G['c'] += int(t[4]*.7); refresh(); draw(); return
        else: return

def do_round():
    G['r'] += 1
    if run_wave():
        G['c'] += 100 + G['r'] + sum(int(t[6]['inc']) for t in TOWERS)
        if G['r'] > G['best']: G['best'] = G['r']
        save('a'); draw(None, 'cleared')
        if G['r'] >= DIFFS[G['d']][4]: print('YOU WIN!'); return True
    else:
        print('Game over at round', G['r'])
        if G['r'] > G['best']: G['best'] = G['r']
        save('a'); newgame(); draw()
    return False

def pick_cell(rc):
    if rc in PCELL: print('That is the path'); return
    i = tower_at(rc[0], rc[1])
    if i >= 0: tower_menu(i)
    else: build(rc[0], rc[1])
    draw()

def command():
    p = input('cell/g/m/l/h/cur/keys/save/load/q (Enter=back)> ').split()
    if not p: return 0
    c = p[0].lower(); rc = cell(p)
    if rc: pick_cell(rc)
    elif c == 'l':
        for i in range(len(TOWERS)):
            t = TOWERS[i]; print(HEX[t[1]]+str(t[2]), TW[t[0]][0], t[3])
    elif c == 'm': draw()
    elif c == 'h': shop()
    elif c == 'new': newgame(); draw()
    elif c in ('g', 'go'):
        if do_round(): return 1
    elif c == 'cur':
        USECUR[0] = setup_keys(); print('Cursor', 'on' if USECUR[0] else 'unavailable'); draw()
    elif c == 'keys':
        try: calibrate(); USECUR[0] = True
        except: print('Key reading unavailable')
        draw()
    elif c == 'save': save(p[1] if len(p) > 1 else '1')
    elif c == 'load':
        if load(p[1] if len(p) > 1 else '1'): draw()
    elif c == 'q': return 1
    else: print('Type a cell (e.g. a3), g, m, l, h, cur, keys, new, save, load, q')
    return 0

def main():
    print('BTD5-Lite v4')
    if load('a', True) and input('Continue autosave? (y/n) ') == 'y': pass
    else: newgame()
    if input('Cursor controls? (y/n) ').lower() != 'n': USECUR[0] = setup_keys()
    draw()
    while True:
        try:
            if USECUR[0]:
                k = readkey()
                if k == 'up' and CUR[1] > 0: CUR[1] -= 1
                elif k == 'down' and CUR[1] < H-1: CUR[1] += 1
                elif k == 'left' and CUR[0] > 0: CUR[0] -= 1
                elif k == 'right' and CUR[0] < W-1: CUR[0] += 1
                elif k == 'enter': pick_cell((CUR[0], CUR[1])); continue
                elif k == 'go':
                    if do_round(): return
                    continue
                elif k == 'menu':
                    if command(): return
                    draw(); continue
                draw()
            elif command(): return
        except Exception as e:
            print('?', e)

if __name__ == '__main__':
    main()
