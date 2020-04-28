import  matplotlib.pyplot  as  plt 
import numpy as np
import json
import matplotlib
matplotlib.rcParams['figure.figsize'] = (20, 20)

with open('facts.json', 'r') as fh: 
    Data = json.load(fh)

class plotting:
    
    def __init__(self):
        self = self

    
    def GetData(self,SelectedZip, key):
        x = []
        for i in SelectedZip:
            S = Data.get(i)
            x.append(S.get(key))
        return x
    
    def GetPlotingValue(self,list1,key):
        x = []
        for i in list1:
            x.append(float(i.get(key)))
        x = np.asarray(x)
        return x


    def smallPlot(self, Selection):
        fig = plt.figure()
        plt.plot([1,2,3,4])
        plt.ylabel('some numbers')    
        fig.tight_layout()

    
    def Plotting(self, Selection): 
        yaxislist1 = self.GetData(Selection, "schoolPerformance")
        yaxislist2 = self.GetData(Selection, "medianHomeValue")
        yaxislist3 = self.GetData(Selection, "income")
        yaxislist4 = self.GetData(Selection, "education")
        
        
        cityname = self.GetData(Selection,"city")
        X = [str(cityname[i]) +"\n"+ str(Selection[i]) for i in range(len(cityname))]
        
        ax1 = plt.subplot(1,2,1)
        ax1.set_title("School Rating VS Median Home Value")
        
        median = self.GetPlotingValue(yaxislist1, "medianSchoolRating")
        mean = self.GetPlotingValue(yaxislist1,"meanSchoolRating") 
        
        

        '''
        ax1 and ax2 will plot out Median Home Price vs SchoolRating (left picture)
        '''      
        medianPrice = np.asarray(list(map(int,yaxislist2)))
        ax1.set_ylabel('Median Home Price')
        ax1.bar(Selection,medianPrice, align="center",zorder=1)
        ax1.tick_params(axis='y')
        ax1.axis( (-1, len(Selection), 300000, 2500000) ) 
        ax1.set_ylim(0,2500000)
        
        ax2 = ax1.twinx()    
        ax2.set_xlabel('Zip Codes')
        ax2.set_ylabel("School Rating")
    
        for label in (ax1.get_xticklabels()):
            label.set_fontsize(7)  
        
        ax2.plot(Selection, median, "or-" ,label = "Median School Rating",  color = 'orange',zorder=10)
        ax2.plot(Selection,mean, "or-",label = "Mean School Rating", color='cyan',zorder=5)
        ax2.legend(loc="best", prop={'size':6})
        ax2.axis( (-1, len(Selection), 500, max(mean)+200) ) 
        ax2.set_xticklabels(X)
        


        '''
        ax3 and ax4 will plot out Median Home Price vs MedianHouseholdIncome (middle picture)
        '''
        ax3 = plt.subplot(1,2,2)
        ax3.set_title("Household Income VS Median Home Value")
        median = self.GetPlotingValue(yaxislist3, "medianHouseholdIncome")
        mean = self.GetPlotingValue(yaxislist3,"meanHouseholdIncome") 
        

        ax3.set_ylabel('Median Home Price')
        ax3.bar(Selection,medianPrice, align="center",zorder=1)
        ax3.tick_params(axis='y')
        ax3.axis( (-1, len(Selection), 300000, 2500000) ) 
        ax3.set_ylim(0,2500000)  
        
        ax4 = ax3.twinx()
        ax4.set_xlabel('ZipCodes')
        ax4.set_ylabel("Household Income")
        #'''
        for label in (ax3.get_xticklabels()):
            label.set_fontsize(7)  
        #'''
        ax4.plot(Selection, median, "or-" ,label = "Median Household Income",  color = 'orange',zorder=10)
        ax4.plot(Selection,mean, "or-",label = "Mean Household Income", color='cyan',zorder=10)
        ax4.legend(loc="best", prop={'size': 6})
        ax4.axis( (-1, len(Selection), 0, max(mean)+20000)) 
        ax4.set_xticklabels(X)
