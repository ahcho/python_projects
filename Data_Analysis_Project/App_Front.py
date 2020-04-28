'''
Author: Anna Cho

An application that shows comparisons between home value and 
1. household income, and 2. public school rating among the user chosen zip codes.
'''

import tkinter as tk
import tkinter.filedialog
import  tkinter.messagebox  as  tkmb
import json
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg') 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import matplotlib.pyplot as plt
import Plot

JSON_FNAME = "facts.json"

class MainWin(tk.Tk) :
    def __init__(self) :
        super().__init__()
        self.geometry('300x680')
        self.dataDict = self._createDictionary()
        self.zipcodes_by_city = self._getCityZipcodeDict() 
        self.cityList = sorted(self._getCityList()) 
    
        self.title("Santa Clara County") 
        self.protocol("WM_DELETE_WINDOW", self._close)
        
        F = tk.Frame(self)
        F2 = tk.Frame(self)
        F3 = tk.Frame(self)
        F4 = tk.Frame(self)
        
        F2.grid(row = 1)
        F3.grid(row = 2)
        F4.grid(row = 3,  sticky = 'w')
        F.grid(row = 4)
        tk.Label(F2, text = "1. Please choose a city").grid(row = 0)
        tk.Label(F3, text = "2. Please choose 2-5 zip codes").grid(row = 0)
        tk.Label(F4, text = "Chosen zip codes").grid(row = 0)
        tk.Button(F, text = "Compare", command = self._buttonClick).grid(padx=10, pady=10)         
        
        self.City_S = tk.Scrollbar(F2)
        S = tk.Scrollbar(F3) 
        
        self.City_LB = tk.Listbox(F2, 
                                  background = "lightgrey",
                                  selectbackground="lightblue",
                                  height = 10,
                                  width = 30,
                                  yscrollcommand = self.City_S.set,
                                  exportselection = False)
        
        tk.Button(F3, text = "Add", command = self._addButtonClick).grid(row = 3, padx=10, pady=10)
        
        self.City_LB.insert(tk.END, *self.cityList)
        self.City_LB.grid(column = 0)      
        self.City_S.grid(row = 1, column = 1, sticky = 'ns')
        
        self.Zip_LB = tk.Listbox(F3, 
                                 background = "lightgrey",
                                 selectbackground="lightblue",
                                 selectmode='multiple', 
                                 height = 10, 
                                 width = 30, 
                                 yscrollcommand = S.set)
        
        
        tk.Button(F4, text = "Delete", command = self._deleteButtonClick).grid(row = 3, padx = 60, pady= 10, sticky = 'w')
        tk.Button(F4, text = "Delete All", command = self._deleteAllButton).grid(row=3, padx = 50, pady= 10, sticky = 'e' ) 

        self.City_S.config(command = self.Zip_LB.yview)        
        
        
        self.Zip_LB.grid(row = 1, column = 0)
        
        self.Selection_LB =  tk.Listbox(F4, 
                                        background = "lightgrey",
                                        selectbackground="lightblue",
                                        selectmode='multiple',
                                        height = 5, 
                                        width = 30)
                                    
        self.Selection_LB.grid(row=1, column = 0)  
        
        S.grid(row = 1, column = 1, sticky ='ns')
        S.config(command = self.Zip_LB.yview)
        
        self.City_LB.bind('<ButtonRelease-1>', self._displayZipcodes)
                
       
    def _addButtonClick(self) :
        '''adds a list of chosen zipcodes from 2nd list box to 3rd list box'''
        linesList = [ line for line in self.Selection_LB.get(0, tk.END)]
        currentLB_list = set([ line.split(' ')[0] for line in linesList])   
        newZipList = set([self.Zip_LB.get(idx) for idx in self.Zip_LB.curselection()])
        self.Zip_LB.delete(0, tk.END) 
        self.Zip_LB.insert(tk.END, *self.zipCodes_list) 

        if len(newZipList) == 1 and len(newZipList.intersection(currentLB_list)) == 1 :
            tkmb.showinfo(" ", "This zip code is already chosen")
        elif len(newZipList) == 0 :
            tkmb.showinfo(" ", "Please choose a zip code!")
        else : 
            if (len(currentLB_list) + len(newZipList) <= 5 ) :   
                addList = newZipList.difference(currentLB_list)
                for zipcode in addList :
                    info = zipcode + ' ' + self.dataDict[zipcode]['city']
                    self.Selection_LB.insert(tk.END, info)   
            else :
                tkmb.showinfo(" ", "You may choose up to 5 zip codes")
                
    def _displayinfo(self, event) :
        '''display info about the selected zipcode'''
        line = self.Selection_LB.get(self.Selection_LB.curselection())
        zipcode = line.split(' ')[0]    
        info = 'Population: ' + self.dataDict[zipcode]['population']['total']
        
    def _deleteAllButton(self) :
        '''deletes everything in the selection list box'''
        return self.Selection_LB.delete(0, tk.END)  
    
    def _deleteButtonClick(self) :
        '''delete user chosen zipcodes from 3rd list box'''
        chosenList = [self.Selection_LB.get(idx) for idx in self.Selection_LB.curselection()]
        if len(chosenList) == 0 :
            tkmb.showinfo(" ", "Please choose a zip code to delete!")
        del_zip_list = [ chosenList[0].split(' ')[0] for line in chosenList ]
        idxs = map( int, self.Selection_LB.curselection())
        for idx in idxs :
            self.Selection_LB.delete(idx)
        
    def _displayZipcodes(self, event):
        '''when a city is chosen in the upper listbox, list of zipcode print in the 2nd listbox'''
        self.Zip_LB.delete(0, tk.END)
        self.cityIndex = self.City_LB.curselection()
        self.zipCodes_list = sorted(self.zipcodes_by_city[self.cityList[self.cityIndex[0]]])
        self.Zip_LB.insert(tk.END, *self.zipCodes_list)

    def _buttonClick(self) : 
        '''returns tuple of user chosen zipcode index'''
        
        linesList = [ line for line in self.Selection_LB.get(0, tk.END)]
        self.finalSelection_list = [ line.split(' ')[0] for line in linesList]    
        P = Plot.plotting()
        if (len(self.finalSelection_list) < 2 ) :
            tkmb.showerror("too little!", "Please select at least 2 zip codes to compare!", parent = self) 
        elif(len(self.finalSelection_list) > 5) :
            tkmb.showerror("too many!", "Please choose fewer than 5 zip codes!", parent = self)
        else:
            PlotWin(self, P.Plotting, self.finalSelection_list)
  
            self.finalSelection_list = []            
       
        
    def _createDictionary(self) :
        '''create a dictionary from json file'''
        with open(JSON_FNAME, 'r') as f : 
            dataDict = json.load(f)
        return dataDict 
        
    def showPlot(self) :
        '''show plot window makes comparions'''
        return plotwin(self, self.values)

    def _close(self) : 
        '''ask the user if the user wants to close the app'''
        if  tkmb.askokcancel(" ", "Do you want to close the app?") :
            self.destroy()
            
    def _getZipcodes(self) :
        '''from json file return a list of zipcodes'''
        return list(self.dataDict.keys())
    
    def _getCityZipcodeDict(self) :
        '''creates a dictionary{cityName:[list of zipcode]}'''
        zipcodes_by_city = defaultdict(list)
        for zipcode, val in self.dataDict.items():
            zipcodes_by_city[val["city"]].append(zipcode)    
        return zipcodes_by_city
    
    def _getCityList(self) :
        '''returns list of city names'''
        return list(self.zipcodes_by_city.keys())

        
class PlotWin(tk.Toplevel) :
    def __init__(self, master, plotFct, *args, **kwargs) :
        '''creates toplevel window with plots'''
        super().__init__(master)
        self.transient(master)
        P = Plot.plotting()
        fig = plt.figure(figsize=(12,6))
        self.title("Comparisons") 
        P.Plotting(*args, **kwargs)
        self.canvas = FigureCanvasTkAgg(fig, master = self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.draw()
        fig.tight_layout()
        self.bind('<Configure>', lambda e: self._resize())
        
    
    def _resize(self):
        self.canvas.get_tk_widget().pack_forget()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



   
if __name__=='__main__' :
    app = MainWin()
    app.mainloop()
