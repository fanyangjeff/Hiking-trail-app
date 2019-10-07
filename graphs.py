import numpy as np

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib

matplotlib.use('TkAgg')  # tell matplotlib to work with Tkinter
import tkinter as tk  # normal import of tkinter for GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Canvas widget
import matplotlib.pyplot as plt  # normal import of pyplot to plot
import sqlite3

# Additional code for running GUI application on Mac
# these modules and the code below will be covered in module 4
import sys
import os

import tkinter as tk



def gui2fg():
    """Brings tkinter GUI to foreground on Mac
    Call gui2fg() after creating main window and before mainloop() start
    """
    if sys.platform == 'darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is %d to true'
        os.system("/usr/bin/osascript -e '%s'" % (tmpl % os.getpid()))


DB_FILENAME = "trails.db"
COUNTY_LIST = []

conn = sqlite3.connect(DB_FILENAME)
cur = conn.cursor()



class Graph_Window(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.geometry("420x300")
        self.title("Hiking stats")

        scatter_plot_button = tk.Button(self, text = "scatter plot by counties", command = self.scatterPlotByCounty)
        draw_top_10_cities = tk.Button(self, text = "Highly rated trails in top 10 cities", command = self.drawTop10Cities)
        trails_by_counties = tk.Button(self, text = "Trails by counties", command = self.drawTrailbyCounty)

        scatter_plot_button.grid(row = 0, column = 0, columnspan = 2)
        draw_top_10_cities.grid(row = 1, column = 0, columnspan = 2)
        trails_by_counties.grid(row = 2, column = 0, columnspan = 2)





    def scatterPlotByCounty(self):
        countyList = []
        xyList = []
        colorDict = {"Alameda": "Red", "Napa": "Green", "Contra Costa": "Pink", "San Mateo": "Purple", "Marin": "Cyan",
                     "Solano": "Blue", "Santa Clara": "Brown", "Sonoma": "Magenta", "San Francisco": "Orange"}
        sizeDict = {}

        cur.execute('SELECT C.COUNTY,LONGITUDE,LATITUDE FROM TRAIL T LEFT OUTER JOIN CITY C ON T.CITY_ID = C.ID')
        for record in cur.fetchall():
            countyList.append(record[0])
            xyTuple = (record[1], record[2])
            xyList.append(xyTuple)
        # print(len(countyList))

        cur.execute('SELECT COUNTY, SUM(SQ_MI) FROM CITY GROUP BY COUNTY ORDER BY SUM(SQ_MI) ')
        for record in cur.fetchall():
            sizeDict[record[0]] = record[1]
        # print(sizeDict)

        npArrCounty = np.array(countyList)
        npArrXY = np.array(xyList)

        order = np.arange(len(npArrCounty))
        # print(order)

        # Create an empty numpy color array
        npColors = np.empty(len(npArrCounty), dtype=object)  # Initialize array to hold color

        for k, v in colorDict.items():
            npColors[npArrCounty == k] = v  # Assign each trail with their corresponding County color

        # print(npColors)

        plt.figure(figsize=(6, 6))
        plt.scatter(npArrXY[order, 0], npArrXY[order, 1], s=10, linewidths=0, color=npColors[order], marker="o");
        plt.legend(colorDict)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Scatter Plots of Trails in Bay Area", fontsize=10)

        # create a legend by plotting empty lists with the desired size and label
        for k, v in sizeDict.items():
            plt.scatter([], [], c=colorDict[k], alpha=1, s=10, label=k)
        plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title='County', loc="best")

        # for i in order:
        #    plt.annotate(countyList[i], xy=(npArrXY[i,0],npArrXY[i,1]))

        plt.show()

    def drawTop10Cities(self):
        """
        Draw bar graph of top 10 cities along with the number of trails where stars rating is equal or above 4.0 and number of votes equal or above 2
        """
        cityList = []
        numTrailList = []
        cur.execute('''SELECT C.NAME, COUNT(*)
                        FROM TRAIL T
                            LEFT OUTER JOIN CITY C ON T.CITY_ID = C.ID
                        WHERE STARS>=4.0 AND STARVOTES >=2
                        GROUP BY C.NAME
                        ORDER BY COUNT(*) DESC  
                        LIMIT 10;''')
        for record in cur.fetchall():
            cityList.append(record[0])
            numTrailList.append(record[1])

        plt.figure(figsize=(8, 5))
        barlist = plt.bar(cityList, numTrailList, width=0.5, color='blue')

        # create alternating blue/green for bar colors
        for i in range(10):
            if (i % 2 == 0):
                barlist[i].set_color('green')

        plt.title("Top Cities")
        plt.xlabel("City", size=10)
        plt.ylabel("Number of Trails", size=10)
        plt.xticks(cityList, size=7)
        plt.show()

    def drawTrailbyCounty(self):
        countyList = []
        numTrailList = []

        cur.execute('''SELECT C.COUNTY, COUNT(*)
                        FROM TRAIL T
                            LEFT OUTER JOIN CITY C ON T.CITY_ID = C.ID
                        GROUP BY C.COUNTY
                        --ORDER BY COUNT(*) DESC
                        ''')
        for record in cur.fetchall():
            countyList.append(record[0])
            numTrailList.append(record[1])

        fig1, ax1 = plt.subplots()
        ax1.pie(numTrailList, labels=countyList, autopct='%1i%%',
                shadow=False, startangle=45)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        # ax1.title('% Trails by County')
        plt.show()

