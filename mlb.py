import pandas as pd
import requests
import bs4
import re
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DataScraper:
    #pulled from https://github.com/BenKite/baseball_data/blob/master/baseballReferenceScrape.py
    def pullTable(self, url, tableID):
        res = requests.get(url)
        ## Work around comments
        comm = re.compile("<!--|-->")
        soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
        tables = soup.findAll('table', id = tableID)
        data_rows = tables[0].findAll('tr')
        data_header = tables[0].findAll('thead')
        data_header = data_header[0].findAll("tr")
        data_header = data_header[0].findAll("th")
        game_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])]
            for i in range(len(data_rows))
            ]
        data = pd.DataFrame(game_data)
        header = []
        for i in range(len(data.columns)):
            header.append(data_header[i].getText())
        data.columns = header
        data = data.loc[data[header[0]] != header[0]]
        data = data.reset_index(drop = True)
        return(data)


class Graphical:

    def __init__(self, battingDF, pitchingDF, fieldingDF, qualbattingDF, qualpitchingDF):

        self.battingButtons = []
        self.pitchingButtons = []
        self.fieldingButtons = []
        self.mainButtons = []

        self.currentDF = "BATTING"

        self.dfDict = {"BATTING":  (battingDF, self.battingButtons),
              "PITCHING": (pitchingDF, self.pitchingButtons),
              "FIELDING": (fieldingDF, self.fieldingButtons),
              "QUALONLYBATTING": (qualbattingDF, self.battingButtons),
              "QUALONLYPITCHING": (qualpitchingDF, self.pitchingButtons)}


        self.root = tk.Tk()
        self.root.title("MLB Dashboard")
        self.root.geometry("1400x1000")
        self.figure = plt.Figure(figsize=(10,10), dpi=100)
        self.bar = FigureCanvasTkAgg(self.figure, self.root)
        self.ax1 = self.figure.add_subplot(1, 1, 1)

        self.T = tk.Label(self.root, text = "CURRENT DF IS: " + self.currentDF)

    def plotNew(self, category):
        self.ax1.clear()
        self.bar.get_tk_widget().pack()
        df = self.dfDict[self.currentDF][0].sort_values(by = category, ascending = False)
        df = df[:25]
        x_ticks = df['Name'].values
        df.plot('Name', category, kind = 'barh', ax = self.ax1)
        self.ax1.invert_yaxis()
        self.ax1.set_title(category)
        self.figure.tight_layout()

        #add values to bars
        for i in self.ax1.patches:
            self.ax1.text(i.get_width(), i.get_y()+.38, \
            str(round((i.get_width()), 3)), fontsize=8, color='dimgrey')

        self.figure.canvas.draw()

    def switchDF(self, text):
        #hide buttons first then update df then place new buttons
        self.hideVariableButtons(self.currentDF)
        self.currentDF = text
        self.showVariableButtons(self.currentDF)
        self.showCurrentDF()

    def showCurrentDF(self):
        self.T.place_forget()
        self.T['text'] = "CURRENT DF IS: " + self.currentDF
        self.T.place(x = 5, y = 5)

    def showMainButtons(self):
        dfbuttons = ['BATTING', 'PITCHING', 'FIELDING', 'QUALONLYBATTING', 'QUALONLYPITCHING']
        yval = 50
        for item in dfbuttons:
            self.mainButtons.append(tk.Button(self.root, text = item, command = lambda item=item : self.switchDF(item)))

        for button in self.mainButtons:
            button.place(x = 30, y = yval)
            yval += 100

    def showVariableButtons(self, df):
        yval = 10
        #create the buttons if they haven't been made yet
        if(len(self.dfDict[df][1]) == 0):
            for col in self.dfDict[df][0].columns.tolist()[5:-1]:
                cur = tk.Button(self.root, text = col, command = lambda col=col : self.plotNew(col))
                self.dfDict[df][1].append(cur)
                cur.place(x = 1250, y = yval)
                yval += 30
        #if they've been made replace them from stored list
        else:
            for button in self.dfDict[df][1]:
                button.place(x = 1250, y = yval)
                yval += 30

    def hideVariableButtons(self, df):
        #hide buttons in list
        for button in self.dfDict[df][1]:
            button.place_forget()


    def display(self):
        self.showMainButtons()
        self.showVariableButtons(self.currentDF)
        self.showCurrentDF()
        self.root.mainloop()


if __name__ == '__main__':
    scraper = DataScraper()
    fieldingDF = scraper.pullTable('https://www.baseball-reference.com/leagues/MLB/2020-standard-fielding.shtml',
    'players_players_standard_fielding_fielding')
    fieldingDF = fieldingDF[:-1].apply(pd.to_numeric, errors='ignore')

    battingDF = scraper.pullTable('https://www.baseball-reference.com/leagues/MLB/2020-standard-batting.shtml',
    'players_standard_batting')
    battingDF = battingDF[:-1].apply(pd.to_numeric, errors='ignore')

    qualbattingDF = battingDF[battingDF['PA'] / 60 >= 3.1]

    pitchingDF = scraper.pullTable('https://www.baseball-reference.com/leagues/MLB/2020-standard-pitching.shtml',
    'players_standard_pitching')
    pitchingDF = pitchingDF[:-1].apply(pd.to_numeric, errors='ignore')

    qualpitchingDF = pitchingDF[pitchingDF['IP'] / 60 >= 1]

    gui = Graphical(battingDF, pitchingDF, fieldingDF, qualbattingDF, qualpitchingDF)
    gui.display()
