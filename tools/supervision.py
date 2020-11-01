#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import numpy
import time
import datetime
import matplotlib.pyplot     
import matplotlib.animation
import mpl_toolkits.mplot3d
from .fields import *
from .mechanics import *

    #========= RENDERING =================================================#

class Rendering:
    """Facilitates dynamic or static rendering of trajectories and fields."""

    ordains = {"f":"Force (N)", "t":"Torque (N.m)",
               "s":"Speed (m/s)", "av":"Angular velocity (rad/s)"}

    defSet = {"nameFig": "Rendering",                 # figure name
              "nameAxe": ["x (m)", "y (m)", "z (m)"], # axis names
              "coloDef": "white",                     # default color
              "timeFra": 10,                          # frame duration (ms)
              "dispAxe": True,                        # display the axes
              "coloFie": "grey",                      # field quivers color
              "normFie": False,                       # normalize the quivers
              "dispCon": True,                        # display configuration
              "dispPos": True,                        # display path
              "dispFor": True,                        # display net force
              "dispTor": True,                        # display net torque
              "sizeDef": None,                        # size of the solid axes
              "coloTra": [],                          # colors of the solids
              "coloAxe": ["green", "green", "green"], # axis colors
              "coloFor": "red",                       # force color
              "coloTor": "blue",                      # torque color
              "coloEnv": [],                          # object colors
              "dispGra": True,                        # display the graphics
              "listGra": ["s", "av"]}                 # choice of graphics
        
    def __init__(self, display=[], settings=None, comment=None):
        self.field, self.trajectories, self.environment = None, [], []
        self.classify(display)
        self.settings, self.comment = settings, comment
        if settings is None:
            self.settings = Rendering.defSet.copy()
        checkType([self.settings], dict)
        if comment is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.comment = ["Date: "+date]
        checkType(self.comment, str)
        
    def classify(self, item):
        """Classify the items to display."""
        if isinstance(item, list):
            for element in item:
                self.classify(element)
        elif isinstance(item, Field):
            self.field = item
        elif isinstance(item, Trajectory):
            self.trajectories.append(item)
        elif isinstance(item, (Solid, Path, Volume)):
            self.environment.append(item)
        elif item is not None:
            raise TypeError(str(type(item))+" can not be displayed")

    def __repr__(self):
        display = repr([self.field, self.trajectories, self.environment])
        settings = repr(self.settings)
        comment = repr(self.comment)
        return "Rendering("+display+", "+settings+", "+comment+")"

    def plotGraphic(self, name, graphic):
        """Plot the graphic of ordains 'name'."""
        if not name in self.ordains:
            raise ValueError(str(name)+" is not a valid graphic name")
        graphic.set_ylabel(self.ordains[name])
        for i in range(len(self.trajectories)):
            t = self.trajectories[i]
            graphic.plot([a.magnitude for a in t.data["times"]],
                         [norm(s).magnitude for s in t.data[name]],
                         color=self.settings["coloTra"][i])

    def normCoef(self, a):
        """Return the normalization coefficient for the values in 'a'."""
        def aux(b):
            """Recursive reading."""
            if isinstance(b, Quantity):
                return norm(b).magnitude
            if isinstance(b, (list, Storage)):
                return max([aux(c) for c in b])
            raise TypeError("normCoef not defined on "+str(type(a)))
        m = aux(a)
        if m == 0:
            return 1
        return 1/m

    def size(self, item):
        """Return the characteristic size of the item."""
        if isinstance(item, Solid):
            return norm(item.cfg.position).magnitude+self.size(item.shp)
        if isinstance(item, Volume):
            return max(d.magnitude/2 for d in item.size)
        if isinstance(item, Path):
            return max([norm(p).magnitude for p in item])
        else:
            raise TypeError("size not defined on "+str(type(item)))

    def prepareData(self, show=False):
        """Prepare the data before displaying."""
        if self.field is None:
            nF, sF = float('inf'), 0
        else:
            nF, self.quivLen = self.field.n[3], self.field.spg
            sF = self.field.spg.magnitude*max(self.field.n[0:2])/2
        if len(self.trajectories) is 0:
            nT, sT = float('inf'), 0
        else:
            nT = min([len(t.data["times"]) for t in self.trajectories])
            p = [self.size(t.solid.shp) for t in self.trajectories]
            sT = max([max([norm(v).magnitude + p[i]
                           for v in self.trajectories[i].data["p"]])
                           for i in range(len(self.trajectories))])
        if len(self.environment) is 0:
            sE = 0
        else:
            sE = max([self.size(item) for item in self.environment])

        # axes size
        self.sizeAxe = max(sF, sT, sE)

        # number of frames
        if self.field is None and len(self.trajectories) is 0:
            self.numbFra = 1
        else:
            self.numbFra = min(nF, nT)

        # size coef
        if self.settings['sizeDef'] is None:
            coefSiz = 0.05*self.sizeAxe
        else:
            coefSiz = self.settings['sizeDef']

        # colors
        n1 = len(self.environment)-len(self.settings["coloEnv"])
        n2 = len(self.trajectories)-len(self.settings["coloTra"])
        if n1 > 0:
            self.settings["coloEnv"].extend(n1*[self.settings["coloDef"]])
        if n2 > 0:
            self.settings["coloTra"].extend(n2*[self.settings["coloDef"]])

        # normalization
        if len(self.trajectories) is not 0 and self.settings["dispFor"]:
            coefFor = self.normCoef([t.data["f"] for t in self.trajectories])
            coefFor = 2*coefSiz*coefFor
        if len(self.trajectories) is not 0 and self.settings["dispTor"]:
            coefTor = self.normCoef([t.data["t"] for t in self.trajectories])
            coefTor = 2*coefSiz*coefTor
        if self.field is not None:
            if self.settings["normFie"]:
                coefFie = 1
            else:
                coefFie = self.normCoef(self.field.stg)

        # canvas 3D settings
        matplotlib.pyplot.style.use('dark_background')
        name, size = self.settings["nameFig"], (19.20, 10.80)
        self.figure = matplotlib.pyplot.figure(name, figsize=size)
        self.axes = matplotlib.pyplot.subplot(121, projection='3d')
        self.axes.set_xlim(-self.sizeAxe/1.5 ,self.sizeAxe/1.5)
        self.axes.set_ylim(-self.sizeAxe/1.5 ,self.sizeAxe/1.5)
        self.axes.set_zlim(-self.sizeAxe/1.5 ,self.sizeAxe/1.5)
        self.axes.set_xlabel(self.settings["nameAxe"][0])
        self.axes.set_ylabel(self.settings["nameAxe"][1])
        self.axes.set_zlabel(self.settings["nameAxe"][2])
        self.axes.grid(False)
        self.axes.xaxis.pane.fill = False
        self.axes.yaxis.pane.fill = False
        self.axes.zaxis.pane.fill = False
        if self.settings["dispAxe"]:
            matplotlib.pyplot.axis('on')
        else:
            matplotlib.pyplot.axis('off')

        # graphics
        if len(self.trajectories) is not 0 and self.settings["dispGra"]:
            self.graphic1 = matplotlib.pyplot.subplot(222)
            self.graphic2 = matplotlib.pyplot.subplot(224)
            self.plotGraphic(self.settings["listGra"][0], self.graphic1)
            self.plotGraphic(self.settings["listGra"][1], self.graphic2)
            self.graphic1.set_xlabel('Time (s)')
            self.graphic2.set_xlabel('Time (s)')
            start = self.trajectories[0].data["times"][0].magnitude
            end = self.trajectories[0].data["times"][-1].magnitude
            self.dur = (end-start)/10

        # trajectories data conversion
        self.dataTraAxe, self.dataTraPos = [], []
        self.dataTraFor, self.dataTraTor = [], []
        for i in range(len(self.trajectories)):

            # configurations
            if self.settings["dispCon"]:
                l = []
                for k in range(self.numbFra):
                    mBtoE = self.trajectories[i].data["mBtoE"][k]
                    mEtoB = self.trajectories[i].data["mEtoB"][k]
                    o = self.trajectories[i].data["p"][k].magnitude
                    c = Configuration(o, Basis(mBtoE, mEtoB))
                    p = []
                    axes = [add(mul(mBtoE[0], coefSiz), o).magnitude,
                            add(mul(mBtoE[1], coefSiz), o).magnitude,
                            add(mul(mBtoE[2], coefSiz), o).magnitude]
                    for v in axes:
                        x, y = numpy.array([[o[0], v[0]], [o[1], v[1]]])
                        z = numpy.array([[o[2], v[2]], [o[2], v[2]]])
                        p.append([x, y, z])
                    l.append(p)
                self.dataTraAxe.append(l)

            # paths
            if self.settings["dispPos"]:
                l = []
                for k in range(self.numbFra):
                    positions = [self.trajectories[i].data["p"][j].magnitude
                                 for j in range(k)]
                    x, y = numpy.array([[m[0] for m in positions],
                                        [m[1] for m in positions]])
                    z = numpy.array([[m[2] for m in positions],
                                     [m[2] for m in positions]])
                    l.append([x, y, z])
                self.dataTraPos.append(l)

            # forces
            if self.settings["dispFor"]:
                l = []
                for k in range(self.numbFra):
                    f = mul(coefFor, self.trajectories[i].data["f"][k])
                    p = self.trajectories[i].data["p"][k]
                    f, p = f.magnitude, p.magnitude
                    x, y = numpy.array([[p[0], p[0]+f[0]], [p[1], p[1]+f[1]]])
                    z = numpy.array([[p[2], p[2]+f[2]], [p[2], p[2]+f[2]]])
                    l.append([x, y, z])
                self.dataTraFor.append(l)

            # torques
            if self.settings["dispTor"]:
                l = []
                for k in range(self.numbFra):
                    t = mul(coefTor, self.trajectories[i].data["t"][k])
                    p = self.trajectories[i].data["p"][k]
                    t, p = t.magnitude, p.magnitude
                    x, y = numpy.array([[p[0], p[0]+t[0]], [p[1], p[1]+t[1]]])
                    z = numpy.array([[p[2], p[2]+t[2]], [p[2], p[2]+t[2]]])
                    l.append([x, y, z])
                self.dataTraTor.append(l)

        # field data conversion
        self.dataFiePos = []
        self.dataFieVal = []
        if self.field is not None:
            if self.field.stg.magType is Vector:
                x, y, z = numpy.meshgrid(numpy.arange(0, self.field.n[1], 1.0),
                                         numpy.arange(0, self.field.n[0], 1.0),
                                         numpy.arange(0, self.field.n[2], 1.0))

                # positions
                for i in range(len(x)):
                    for j in range(len(x[0])):
                        for k in range(len(x[0][0])):
                            position = self.field.position(i, j, k)
                            x[i][j][k] = position.magnitude[0]
                            y[i][j][k] = position.magnitude[1]
                            z[i][j][k] = position.magnitude[2]
                self.dataFiePos = [x, y, z]

                # values
                for t in range(self.numbFra):
                    u = 0*numpy.array(x)
                    v = 0*numpy.array(y)
                    w = 0*numpy.array(z)
                    for i in range(self.field.n[0]):
                        for j in range(self.field.n[1]):
                            for k in range(self.field.n[2]):
                                sample = self.field.value(i, j, k, t)
                                sample = mul(coefFie, sample)
                                u[i][j][k] = sample.magnitude[0]
                                v[i][j][k] = sample.magnitude[1]
                                w[i][j][k] = sample.magnitude[2]
                    self.dataFieVal.append([u, v, w])

        # initialization
        x, y = numpy.array([[],[]])
        z = numpy.array([[],[]])
        if len(self.trajectories) is not 0:
            self.plotTraFor = [self.axes.plot_wireframe(x, y, z) 
                               for i in range(len(self.trajectories))]
            self.plotTraTor = [self.axes.plot_wireframe(x, y, z) 
                               for i in range(len(self.trajectories))]
            self.plotTraPos = [self.axes.plot_wireframe(x, y, z) 
                               for i in range(len(self.trajectories))]
            self.plotTraAxe = [[self.axes.plot_wireframe(x, y, z),
                                self.axes.plot_wireframe(x, y, z),
                                self.axes.plot_wireframe(x, y, z)]
                               for i in range(len(self.trajectories))]
        if self.field is not None:
            self.quivers = self.axes.quiver(x, y, z, x, y, z)

        # animation
        if self.numbFra is not 1:
            self.animation = matplotlib.animation.FuncAnimation(self.figure,
                                 self.update, frames=self.numbFra,
                                 interval=self.settings["timeFra"])
        # snapshot
        else:
            self.update(0)
        
        # environment
        for i in range(len(self.environment)):
            self.draw(self.environment[i], self.settings["coloEnv"][i])

        # show
        if show:
            matplotlib.pyplot.show()

    def display(self, items=[]):
        """Start displaying data."""
        self.classify(items)
        infos = "\n".join(["(i) "+a for a in self.comment])
        print("\n[INFORMATIONS]\n"+infos)
        self.prepareData(True)

    def update(self, k):
        """Update function for matplotlib animation."""
        if len(self.trajectories) is not 0 and self.settings["dispGra"]:
            end = self.trajectories[0].data["times"][k].magnitude
            start = end - self.dur
            self.graphic1.set_xlim(start, end)
            self.graphic2.set_xlim(start, end)
        for i in range(len(self.trajectories)):
            if self.settings["dispCon"]:
                for j in range(3):
                    x, y, z = self.dataTraAxe[i][k][j]
                    self.axes.collections.remove(self.plotTraAxe[i][j])
                    self.plotTraAxe[i][j] = self.axes.plot_wireframe(x, y, z,
                                            color=self.settings["coloAxe"][j])
            if self.settings["dispPos"]:
                x, y, z = self.dataTraPos[i][k]
                self.axes.collections.remove(self.plotTraPos[i])
                self.plotTraPos[i] = self.axes.plot_wireframe(x, y, z,
                                            color=self.settings["coloTra"][i])
            if self.settings["dispFor"]:
                x, y, z = self.dataTraFor[i][k]
                self.axes.collections.remove(self.plotTraFor[i])
                self.plotTraFor[i] = self.axes.plot_wireframe(x, y, z,
                                            color=self.settings["coloFor"])
            if self.settings["dispTor"]:
                x, y, z = self.dataTraTor[i][k]
                self.axes.collections.remove(self.plotTraTor[i])
                self.plotTraTor[i] = self.axes.plot_wireframe(x, y, z,
                                            color=self.settings["coloTor"])
        if self.field is not None:
            x, y, z = self.dataFiePos
            u, v, w = self.dataFieVal[k]
            self.axes.collections.remove(self.quivers)
            self.quivers = self.axes.quiver(x, y, z, u, v, w,
                                            length=self.quivLen.magnitude,
                                            normalize=self.settings["normFie"],
                                            linewidth=.5,
                                            color=self.settings["coloFie"])

    def draw(self, item, color='white', f=None):
        """Draw 'item' on axes."""
        if isinstance(item, Solid):
            self.draw(item.shp, color, item.cfg.outside)
        elif isinstance(item, Path):
            if callable(f):
                vectors = [f(v) for v in item]
            else:
                vectors = [v for v in item]
            x, y = numpy.array([[v.magnitude[0] for v in vectors],
                                [v.magnitude[1] for v in vectors]])
            z = numpy.array([[v.magnitude[2] for v in vectors],
                             [v.magnitude[2] for v in vectors]])
            self.axes.plot_wireframe(x, y, z, color=color)
        else:
            raise Exception(str(type(item))+" can not be displayed")

    #========= USEFUL FUNCTIONS ==========================================#

def console(path):
    """Menu to choose and display saved data."""
    def menu1():
        while True:
            print("\n[FILES]\n|0| Quit")
            files = os.listdir(path)
            n = len(str(len(files)))
            for i in range(len(files)):
                print("|"+(n-len(str(i+1)))*" "+str(i+1)+"| "+files[i])
            choice = int(input(">>> Choice: "))
            if choice is 0:
                break
            menu2(eval(load(path+'/'+files[int(choice-1)])))
    def menu2(item):
        while True:
            print("\n[ACTION]\n|0| Back\n|1| Display\n|2| Export")
            choice = int(input(">>> Choice: "))
            if choice is 0:
                break
            if choice is 1:
                item.display()
            if choice is 2:
                menu3(item)
    def menu3(item):
        settings = [0, 0, 0]
        item.prepareData()
        while True:
            print("\n[SETTINGS]")
            print("(i) Number of frames: "+str(item.numbFra))
            print("|0| Back")
            print("|1| Vertical angle: "+str(settings[0])+"\u00B0")
            print("|2| Horizontal angle: "+str(settings[1])+"\u00B0")
            print("|3| Frame: "+str(settings[2])+" (for PDF)")
            print("|4| Export as PDF")
            print("|5| Export as MP4")
            choice = int(input(">>> Choice: "))
            if choice is 0:
                break
            if choice in [1, 2, 3]:
                settings[choice-1] = int(input(">>> New value: "))
            date = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            item.axes.view_init(settings[0], settings[1])
            if choice is 4:
                item.update(settings[2])
                item.figure.savefig(date+".pdf")
            if choice is 5:
                Writer = matplotlib.animation.writers['ffmpeg']
                writer = Writer(fps=24)
                item.animation.save(date+".mp4", writer=writer)
    menu1()

class Timer:
    """Gives an estimate of the remaining calculation time."""

    def __init__(self, n):
        self.n = n # number of sequences
        self.c = 0 # counter
        self.dt = 0 # average duration of a sequence
        self.rm = 0 # remaining minutes
        self.rh = 0 # remaining hours

    def before(self):
        """Must be called at the beginning of the sequence."""
        self.t1 = time.time()
        
    def after(self):
        """Must be called at the end of the sequence."""
        self.dt = (self.c*self.dt + time.time()-self.t1)/(self.c+1)
        self.c += 1
        newRM = int(self.dt*(self.n-self.c)/60)+1
        if newRM >= 60:
            newRH = newRM//60 + 1
            if newRH != self.rh:
                self.rh = newRH
                if self.rh is 1:
                    print("(i) ", self.rh, "hour")
                else:
                    print("(i) ", self.rh, "hours")
        elif newRM is not self.rm and self.n is not 1:
            self.rm = newRM
            if self.rm is 1:
                print("(i)", self.rm, "minute")
            else:
                print("(i)", self.rm, "minutes")

    #========= SORTS =====================================================#

def mergeSort(compare=lambda a, b: a < b):
    """Not in-place and stable."""
    def merge(L1, L2):
        L, i1, i2, n1, n2 = [], 0, 0, len(L1), len(L2)
        for i in range(n1+n2):
            if n2 == i2 or i1 < n1 and compare(L1[i1], L2[i2]):
                L.append(L1[i1])
                i1 += 1
            else:
                L.append(L2[i2])
                i2 += 1
        return L
    def sort(L):
        if len(L) <= 1:
            return L[:]
        m = len(L)//2
        return merge(sort(L[:m]), sort(L[m:]))
    return sort

def quickSort(compare=lambda a, b: a < b):
    """In-place and not stable."""
    def partition(L, g, d):
        pivot , m = L[g], g
        for i in range(g+1, d):
            if compare(L[i], pivot):
                m += 1
                if i > m:
                    L[i], L[m] = L[m], L[i]
        if m > g:
            L[m], L[g] = L[g], L[m]
        return m
    def sort(L):
        def aux(g, d):
            if g < d-1:
                m = partition(L, g, d)
                aux(g, m)
                aux(m+1, d)
        aux(0, len(L))
        return(L)
    return sort
