import sys
sys.path.append("D:/BME/_ur/2/proj/UBXparser/src")
import UBXparser
from UBXmessage import *
import logging
import time
import numpy as np
import re

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.widgets import Button

fid = open('D:/BME/_ur/2/proj/noaadata.txt')
for line in fid.readlines():
    if len(line) == 0:
        continue
    segments = re.split('\s+', line)
    noradId = segments[1]
    

exit()

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

#file = "d:/BME/_ur/2/proj/dump/TES1/TES1_2023-04-16-152706.UBX" # kicsi
file = "d:/BME/_ur/2/proj/dump/TES1/TES1_2023-04-16-153556.UBX" # nagy 2-13, 2-36, 6-24
#file = "d:/BME/_ur/2/proj/example.bin"
writeCsv = True

fid = open(file, 'br')
parser = UBXparser.UBXparser(fid)

msgs = {}
msgCnt = 0
for msg in parser.readFile():
    msgTypeId = type(msg).__name__
    if not msgTypeId in msgs:
        msgs[msgTypeId] = []
    msgs[msgTypeId].append(msg)
    msgCnt += 1

print("Found {} messages of {} types".format(msgCnt, len(msgs)))
for msgTypeId, msgList in msgs.items():
    print(type(msgList[0]).__name__, " - ", len(msgList))


satMsgName = "UBX_NAV_SAT"
systems = {}
#csvFile = open("d:/BME/_ur/2/proj/data.csv", "w")

if (satMsgName in msgs):
    satDatas = {}
    for satMsg in msgs.get(satMsgName):
        time = satMsg.data['iTOW']
        #csvFile.write(str(time) + ";")
        if time == 0:
            continue

        for meas in satMsg.data['measurements']:
            gnssId = meas['gnssId']
            satId = meas['svId']
            cno = meas['cno']
            elev = meas['elev']
            azim = meas['azim']

            if cno == 0:
                continue

            if elev < 0:
                continue

            if azim < 140 or azim > 260:
                continue

            if not gnssId in satDatas:
                satDatas[gnssId] = {}

            if not satId in satDatas[gnssId]:
                satDatas[gnssId][satId] = {"times": [], "cmos": [], "elevs": []}
            
            if not satId in systems:
                systems[satId] = gnssId
            
            satDatas[gnssId][satId]["times"].append(time)
            satDatas[gnssId][satId]["cmos"].append(cno)
            satDatas[gnssId][satId]["elevs"].append(elev)

            #csvFile.write(str(gnssId) + "_" + str(satId) + ";" + str(cno) + ";")

        #csvFile.write("\n")

    #csvFile.close()

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    plots = []
    graphs = {}
    
    for gnssId, gnssSatDatas in satDatas.items():
        for satId, satData in gnssSatDatas.items():
            #plt.figure()
            #plt.plot(satData["times"], satData["cmos"])
            avgs = []
            window = []
            for idx, time in enumerate(satData["times"]):
                window.append(satData["cmos"][idx])
                if (len(window) > 10):
                    window.pop(0)
                avgs.append(sum(window) / 10)

            #pl, = ax.plot(satData["times"], avgs, label=str(gnssId) + '-' + str(satId))
            pl, = ax.plot(satData["elevs"], satData["cmos"], 'o', label=str(gnssId) + '-' + str(satId))
            plots.append(pl)
    
    legend = ax.legend(ncol=12, loc='lower left', bbox_to_anchor=(0.0, -0.28))

    for i, lo in enumerate(legend.get_texts()):
        graphs[lo] = plots[i]
        lo.set_picker(True)

    def updateSeriesVisibility(legendEntry, visibility = -1):
        if visibility == -1:
            willBeVisible = not graphs[legendEntry].get_visible()
        else:
            willBeVisible = visibility

        legendEntry.set_alpha(1.0 if willBeVisible else 0.5)
        graphs[legendEntry].set_visible(willBeVisible)


    def on_pick(evt):
        legend = evt.artist
        updateSeriesVisibility(legend)
        fig.canvas.draw()

    plt.connect('pick_event', on_pick)

    def on_swap(evt):
        for legendEntry in graphs.keys():
            updateSeriesVisibility(legendEntry)
        fig.canvas.draw()

    axSwap = fig.add_axes([0.7, 0.05, 0.1, 0.075])
    btnSwap = Button(axSwap, 'Inv')
    btnSwap.on_clicked(on_swap)

    ax.ticklabel_format(useOffset=False, style='plain')
    #ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:.0f}'.format(x/1000) + 's'))
    #plt.tight_layout()
    plt.show()
        
else:
    print("No SAT messages in dump")