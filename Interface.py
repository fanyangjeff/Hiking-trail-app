import graphs
import tkinter as tk
import re
import urllib.request
import json
import threading
from collections import defaultdict
from tkinter import messagebox as tkmb
import queue
import os
import sys
from tkinter.font import Font




import numpy as np

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib

matplotlib.use('TkAgg')  # tell matplotlib to work with Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Canvas widget
import matplotlib.pyplot as plt  # normal import of pyplot to plot
import sqlite3

# Additional code for running GUI application on Mac
# these modules and the code below will be covered in module 4
import sys
import os



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





MAXDISTANCE = 7
MAXRESULTS = 10
MAXLENGTH = 0
MINSTARS = 0

LEVEL_DIFFICULTY = {'greenBlue':(1, 'Easy'),
                    'green':(2, 'Easy/Intermediate'),
                    'blue':(3,'Intermediate') ,
                    'blueBlack':(4, 'Intermediate/Difficult'),
                    'black':(5, 'Difficult'),
                    'dblack':(6, 'Extremely Difficult'),
                    'missing':(0, 'None')}



API_KEY_GOOGLE = 'AIzaSyASyM3IdilzuHe_6lbDBpC7L1WDkuWCres'
API_KEY_HIKING = '200392139-ae0b007a125d0284aaf36fd7a5ec783b'





def getData(place_name, outputQ, e, maxdistance, maxresults, minlength, minstars):
    e.set()
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=' + place_name + '&key=' + API_KEY_GOOGLE)
    page = urllib.request.urlopen(url)
    data = json.load(page)

    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']

    hikingurl = 'https://www.hikingproject.com/data/get-trails?lat=' + str(lat) + '&lon=' + str(lng) + \
                '&maxDistance='+ str(maxdistance) + \
                '&maxResults=' + str(maxresults) +\
                '&minLength=' + str(minlength)+\
                '&minStars=' + str(minstars) + '&key=' + API_KEY_HIKING


    hikingpage = urllib.request.urlopen(hikingurl)
    hikingdata = json.load(hikingpage)

    hiking_dict = defaultdict(list)

    if len(hikingdata['trails']) == 0:
        outputQ.put('none')
        e.clear()
        return

    for data in hikingdata['trails']:
        hiking_dict[data['name']].append(data['stars'])
        hiking_dict[data['name']].append(LEVEL_DIFFICULTY[data['difficulty']][1])
        hiking_dict[data['name']].append(data['length'])
        s = data['summary']
        if len(s) > 90:
            position = s.find(' ', len(s) // 2)
            s = s[0: position] + '\n' + s[position + 1:]    #split in two lines, in case the summary is too long, which will be hard to put into the box
        hiking_dict[data['name']].append(s)
        hiking_dict[data['name']].append(data['location'])
        hiking_dict[data['name']].append(data['conditionStatus'])
        hiking_dict[data['name']].append(data['conditionDate'])
        hiking_dict[data['name']].append(data['high'])
        hiking_dict[data['name']].append(data ['low'])
        hiking_dict[data['name']].append(data['type'])
        hiking_dict[data['name']].append(data['id'])
        hiking_dict[data['name']].append(data['type'])
        hiking_dict[data['name']].append(data['starVotes'])
        hiking_dict[data['name']].append(data['url'])
        hiking_dict[data['name']].append(data['longitude'])
        hiking_dict[data['name']].append(data['latitude'])
        hiking_dict[data['name']].append(LEVEL_DIFFICULTY[data['difficulty']][0])    #which allows the user to search by difficulty level



        outputQ.put((data['name'], hiking_dict[data['name']]))

    e.clear()


class mainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("420x300")
        self.title("Hiking app")
        search_button = tk.Button(self, text = "search", command = lambda: Search_Interface(self))
        search_button.pack(side = tk.TOP)

        stats_button = tk.Button(self, text = "Hiking stats of Bay area", command = lambda :Graph_Window(self))
        stats_button.pack(side = tk.BOTTOM)





class Search_Interface(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.constrcutWindow()
        self.title('Welcome to Hiking trail app')


    def constrcutWindow(self):
        self.geometry("420x300")
        self.textvar = tk.StringVar()
        self.textvar.set('')
        L1 = tk.Label(self, text="Please enter either a city or a county name to search")

        L1.grid(row=0, columnspan=4)

        entry_name = tk.Entry(self, textvariable = self.textvar)
        entry_name.grid(column = 0, row = 2, columnspan = 2)
        entry_name.bind('<Return>', self.Create_List_DialogWindow)

        frame_for_search = tk.Frame(self)
        frame_for_search.grid(column = 0, row = 3, columnspan = 2, rowspan = 2)

        regular_search_button = tk.Button(frame_for_search, text = "Regular search", command = lambda: DialogWindow_List(self))
        regular_search_button.grid(column = 0, row = 0, rowspan = 2 , sticky = 'w')   #we can search in both ways


        advanced_search_button = tk.Button(frame_for_search, text = "Advanced search", command = lambda: AdvancedSearch(self))
        advanced_search_button.grid(column = 1, row = 0, rowspan = 2, sticky = 'e')



    def Create_List_DialogWindow(self, event):
        if self.textvar.get() != '':
            self.d = DialogWindow_List(self)

class AdvancedSearch(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        if self.master.textvar.get() == '':     #in case there's nothing in the textbox
            self.destroy()
            return

        self.title("Advanced search for " + self.master.textvar.get())
        self.master = master
        self.textvar_name = self.master.textvar.get()
        self.master.textvar.set('')                 #reset master
        self.textvar_distance = tk.StringVar()
        self.textvar_results = tk.StringVar()
        self.textvar_length = tk.StringVar()
        self.textvar_rating = tk.StringVar()
        Label2 = tk.Label(self, text = "maximum radius: ")
        Label3 = tk.Label(self, text = "maximum results: ")
        Label4 = tk.Label(self, text = "minimum length (route): ")
        Label5 = tk.Label(self, text = "minimum rating: ")

        E2 = tk.Entry(self, textvariable = self.textvar_distance)
        E3 = tk.Entry(self, textvariable=self.textvar_results)
        E4 = tk.Entry(self, textvariable=self.textvar_length)
        E5 = tk.Entry(self, textvariable=self.textvar_rating)

        Label2.grid(column = 0, row = 1)
        E2.grid(column=1, row=1)
        Label3.grid(column=0, row=2)
        E3.grid(column=1, row=2)
        Label4.grid(column=0, row=3)
        E4.grid(column=1, row=3)
        Label5.grid(column=0, row=4)
        E5.grid(column=1, row=4)

        E2.bind('<Return>', self.create_dialogwindow_list)
        E3.bind('<Return>', self.create_dialogwindow_list)
        E4.bind('<Return>', self.create_dialogwindow_list)
        E5.bind('<Return>', self.create_dialogwindow_list)

        frame_buttons = tk.Frame(self)
        frame_buttons.grid(sticky = 's')

        ConfirmButton = tk.Button(frame_buttons, text = 'ok', command = lambda: DialogWindow_List(self, 'advanced'))
        ConfirmButton.grid(row = 0, column = 0, columnspan = 2)

        clearButton = tk.Button(frame_buttons, text = 'clear', command = self.clear_entries)
        clearButton.grid(row = 0, column = 2, columnspan = 2)

    def create_dialogwindow_list(self, event):
        self.d = DialogWindow_List(self, 'advanced')

    def clear_entries(self):
        self.textvar_distance.set('')
        self.textvar_results.set('')
        self.textvar_length.set('')
        self.textvar_rating.set('')

class DialogWindow_List(tk.Toplevel):
    def __init__(self, master, search_mode = 'regular'):

        super().__init__(master)
        self.master = master
        self.data_list = []


        self.__scrollbar = tk.Scrollbar(self)  # build the scrollbar
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.mylist = tk.Listbox(self, height=15, width=65, yscrollcommand=self.__scrollbar.set)

        self.mylist.configure(font = 'Courier')
        self.mylist.pack(fill=tk.BOTH)

        self.__scrollbar.config(command=self.mylist.yview)
        self.mylist.bind("<ButtonRelease-1>", self.showInfo)

        frame_sort_buttons = tk.Frame(self)
        frame_sort_buttons.pack(side = tk.BOTTOM)

        self.RatingButton = tk.Button(frame_sort_buttons, text = "By ratings", command = self.sort_by_ratings)
        self.RatingButton.grid(row = 0, column = 0)
        self.LengthButton = tk.Button(frame_sort_buttons, text = "By Length", command = self.sort_by_length)
        self.LengthButton.grid(row = 0, column = 1)
        self.DifficultyButton_difficult = tk.Button(frame_sort_buttons, text = "Difficulty(hard)", command = lambda :self.sort_by_difficulty(True))
        self.DifficultyButton_difficult.grid(row=0, column=2)
        self.DifficultyButton_easy = tk.Button(frame_sort_buttons, text = "Difficulty(easy)", command = lambda :self.sort_by_difficulty(False))
        self.DifficultyButton_easy.grid(row=0, column=3)

        self.fixedlen = 10
        self.args_list = []
        self.outputQ = queue.Queue()
        self.e = threading.Event()

        self.update()


        if search_mode == 'regular':
            if self.master.textvar.get() == '':     #in case there's nothing in the textbox
                self.destroy()
                return
            self.target = re.sub(' ', '', self.master.textvar.get())  # remove all the spaces. Otherwise, API won't work
            self.create_regular_list()
        else:
            self.target = re.sub(' ', '', self.master.textvar_name)

            if self.master.textvar_distance.get() != '':
                try:
                    #self.distance = float(self.master.textvar_distance.get())
                    self.args_list.append(float(self.master.textvar_distance.get()))
                except ValueError:
                    tkmb.showerror("Value Error", 'Max Distance needs to be a number')
                    self.master.textvar_distance.set('')
                    self.destroy()
                    return
            else:
                self.args_list.append(MAXDISTANCE)    #default


            if self.master.textvar_results.get() != '':
                try:
                    self.args_list.append(int(self.master.textvar_results.get()))
                except ValueError:
                    tkmb.showerror("Value Error", 'Max results needs to be a number')
                    self.master.textvar_results.set('')
                    self.destroy()
                    return
            else:
                self.args_list.append(10)     #default


            if self.master.textvar_length.get() != '':
                try:
                    self.args_list.append(float(self.master.textvar_length.get()))
                except ValueError:
                    tkmb.showerror("Value Error", 'Max length needs to be a number')
                    self.master.textvar_length.set('')
                    self.destroy()
                    return
            else:
                self.args_list.append(MAXLENGTH)     #default


            if self.master.textvar_rating.get() != '':
                try:
                    self.args_list.append(float(self.master.textvar_rating.get()))

                except ValueError:
                    tkmb.showerror("Value Error", 'Max length needs to be a number')
                    self.master.textvar_rating.set('')
                    self.destroy()
                    return
            else:
                self.args_list.append(MINSTARS)

            self.create_advanced_list()



    def create_regular_list(self):
        self.master.textvar.set('')

        self.t = threading.Thread(target=getData, args=(self.target, self.outputQ, self.e, MAXDISTANCE, MAXRESULTS, MAXLENGTH, MINSTARS))
        self.t.start()
        self.e.wait()

        while self.e.is_set() or (not self.outputQ.empty()):
            temp = self.outputQ.get()
            if temp == 'none':
                tkmb.showerror("No matching result", "There is hiking trail found")
                self.destroy()
                return

            self.data_list.append((temp[0], temp[1]))


        for item in self.data_list:
            if item[1][0] == 0:            #in case there's no rating for some places
                star = 'none'
            else:
                star = str(item[1][0]) + ' stars'

            s = ("{:<30s}"+(self.fixedlen-len(item[0]))*" " +"{:<15s}"+(self.fixedlen-10)*" " +"{:<15s}"+(self.fixedlen-10)*" ").format(item[0], star ,str(item[1][2]) + 'miles')
            self.mylist.insert(tk.END, s)


    def create_advanced_list(self):
        self.t = threading.Thread(target = getData, args=(self.target, self.outputQ, self.e, *self.args_list,))
        self.t.start()
        self.e.wait()
        while self.e.is_set() or (not self.outputQ.empty()):
            temp = self.outputQ.get()
            if temp == 'none':
                tkmb.showerror("No matching result", "There is hiking trail found")
                self.destroy()
                return
            self.data_list.append((temp[0], temp[1]))



        for item in self.data_list:
            if item[1][0] == 0:
                star = 'none'
            else:
                star = str(item[1][0]) + ' stars'

            s = ("{:<30s}" + (self.fixedlen - len(item[0])) * " " + "{:<15s}" + (self.fixedlen - 10) * " " + "{:<15s}" + (self.fixedlen - 10) * " ").format(item[0], star, str(item[1][2]) + 'miles')
            self.mylist.insert(tk.END, s)



    def sort_by_ratings(self):
        self.mylist.delete(0, tk.END)
        self.data_list = sorted(self.data_list, key = lambda t:t[1][0], reverse = True)

        for item in self.data_list:
            if item[1][0] == 0:
                star = 'none'
            else:
                star = str(item[1][0]) + ' stars'
            s = ("{:<30s}" + (self.fixedlen - len(item[0])) * " " + "{:<15s}" + (self.fixedlen - 10) * " ").format(item[0], star)
            self.mylist.insert(tk.END, s)



    def sort_by_length(self):

        self.mylist.delete(0, tk.END)
        self.data_list = sorted(self.data_list, key=lambda t: t[1][2], reverse = True)
        for item in self.data_list:
            s = ("{:<30s}" + (self.fixedlen - 10) * " " + "{:<15s}" + (self.fixedlen - 10) * " ").format(item[0], str(item[1][2]) + 'miles')
            self.mylist.insert(tk.END, s)


    def sort_by_difficulty(self, reverse_difficulty):
        self.mylist.delete(0, tk.END)
        self.data_list = sorted(self.data_list, key=lambda t: t[1][-1], reverse=reverse_difficulty)
        for item in self.data_list:
            s = ("{:<30s}" + (self.fixedlen - 10) * " " + "{:<20s}" + (self.fixedlen - 10) * " ").format(item[0], item[1][1])
            self.mylist.insert(tk.END, s)




    def showInfo(self, event):
        info_window = Info_DialogWindow(self)


class Info_DialogWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        index = int(self.master.mylist.curselection()[0])

        self.trail_name = self.master.data_list[index][0]


        self.title("Info of " + self.trail_name)
        self.geometry("520x360")
        self.master = master

        Label1 = tk.Label(self, text = "Name: " + self.trail_name)
        Label1.grid(row = 0, column = 0, sticky = 'w')

        Label2 = tk.Label(self, text = "Rating:" + str(self.master.data_list[index][1][0]))
        Label2.grid(row=1, column=0, sticky = 'w')

        Label3 = tk.Label(self, text = "Difficulty level: " + self.master.data_list[index][1][1])
        Label3.grid(row=2, column=0, sticky='w')

        Label4 = tk.Label(self, text = "Length: " + str(self.master.data_list[index][1][2]) + "miles")
        Label4.grid(row=3, column=0, sticky='w')

        Label5 = tk.Label(self, text = "Location: " + self.master.data_list[index][1][4])
        Label5.grid(row = 4, column = 0, sticky = 'w')

        Label6 = tk.Label(self, text = "Type: "+ self.master.data_list[index][1][9])
        Label6.grid(row=5, column=0, sticky='w')

        Label7 = tk.Label(self, text = "Condition status: " + self.master.data_list[index][1][5])
        Label7.grid(row=6, column=0, sticky='w')

        Label8 = tk.Label(self, text = "Altitude: " + str(self.master.data_list[index][1][7]) + ' feet')
        Label8.grid(row=7, column=0, sticky='w')

        Label9 = tk.Label(self, text = "Elevation: " + str(self.master.data_list[index][1][7] - self.master.data_list[index][1][8]) + ' feet')
        Label9.grid(row = 8, column = 0, sticky = 'w')

        Label10 = tk.Label(self, text = "Longitude: " + str(self.master.data_list[index][1][14]))
        Label10.grid(row=9, column=0, sticky='w')

        Label11 = tk.Label(self, text="Latitude: " + str(self.master.data_list[index][1][15]))
        Label11.grid(row=10, column=0, sticky='w')

        Frame = tk.LabelFrame(self)               #for summary
        Frame.grid(row=11, column=0, columnspan = 2, rowspan = 3, sticky='w')

        Label1_inFrame = tk.Label(Frame, text = "Summary: ")
        Label1_inFrame.grid(row=0, column=0, sticky='w')

        Label2_inFrame = tk.Label(Frame, text = self.master.data_list[index][1][3])
        Label2_inFrame.grid(row = 1, column = 0, rowspan = 2, sticky = 'w')






'''
Mary

'''



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



if __name__ == '__main__':
    gui2fg()
    root = mainWindow()
    root.mainloop()
    #conn.close()




