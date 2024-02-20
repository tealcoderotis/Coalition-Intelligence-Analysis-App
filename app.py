import pandas
from math import isnan
from matplotlib import pyplot
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import json
import sys
import os

try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

def replaceDataFrameWithPointValue(data, pointValue, dataType):
    if dataType == "bool":
        if data == True:
            return pointValue
        else:
            return 0
    if dataType == "int64":
        if type(pointValue) == list:
            return pointValue[data]
        else:
            return data * pointValue
    
def replaceDataFrameWithDropdownValue(data, dropdownList):
    return dropdownList[data]

def filterDataFrame(hideNoShow, usePointDataFrame):
    global teamsToFilter
    global filteredDataFrame
    global filteredPointDataFrame
    global showNoShowTeamsCheckboxVariable
    if teamsToFilter != None:
        if usePointDataFrame:
            dataFrameToUse = filteredPointDataFrame
        else:
            dataFrameToUse = filteredDataFrame
    else:
        if usePointDataFrame:
            dataFrameToUse = pointDataFrame
        else:
            dataFrameToUse = dataFrame
    if hideNoShow == True and showNoShowTeamsCheckboxVariable.get() == 0:
        dataFrameToDisplay = dataFrameToUse[dataFrameToUse["noShow"].values == False]
        return dataFrameToDisplay
    else:
        return dataFrameToUse

def addCsvFile():
    global filesToMerge
    files = tkinter.filedialog.askopenfilenames(parent=mergeWindow, filetypes=[("CSV File", "*.csv")])
    for file in files:
        filesToMerge.append(file)
    csvFileListbox.configure(listvariable=tkinter.StringVar(value=filesToMerge))

def removeCsvFile():
    global filesToMerge
    try:
        del filesToMerge [csvFileListbox.curselection()[0]]
        csvFileListbox.configure(listvariable=tkinter.StringVar(value=filesToMerge))
    except:
        pass

def mergeCsvFiles():
    global dataFrame
    global pointDataFrame
    global filesToMerge
    if len(filesToMerge) > 0:
        try:
            dataFrame = pandas.read_csv(filesToMerge[0])
            for i in range(1, len(filesToMerge)):
                data = pandas.read_csv(filesToMerge[i])
                dataFrame = pandas.concat([dataFrame, data], ignore_index=True)
            dataFrame.sort_values("roundNum", inplace=True)
            pointDataFrame = dataFrame.copy(deep=True)
            for column in pointDataFrame.columns:
                if column in pointValues:
                    pointDataFrame[column] = pointDataFrame[column].apply(replaceDataFrameWithPointValue, args=(pointValues[column], pointDataFrame[column].dtypes,))
                elif column != "teamNum" and column != "roundNum" and column != "noShow":
                    pointDataFrame.drop(columns=column, inplace=True)
            for column in dataFrame.columns:
                if column in dropdownValues:
                    dataFrame[column] = dataFrame[column].apply(replaceDataFrameWithDropdownValue, args=(dropdownValues[column],))
            initalizeDataWindow()
        except:
            tkinter.messagebox.showerror("Error", "Failed to load one or more CSV files")
    else:
        tkinter.messagebox.showerror("Error", "No CSV files selected")

def exportCsv(usePointValues=False):
    fileName = tkinter.filedialog.asksaveasfilename(parent=dataWindow, filetypes=[("CSV File", "*.csv")], initialfile="data.csv")
    if len(fileName) > 0:
        filterDataFrame(True, usePointValues).to_csv(fileName, index=False)

def exportPointCsv():
    exportCsv(True)

def selectValue(*args):
    global rawValueDataText
    global pointRawValueDataText
    global variableDropdown
    global variableDropdownVariable
    global noShowCountLabel
    global standardDeviationLabel
    global pointStandardDeviationLabel
    global showNoShowTeamsCheckboxVariable
    dataFrameToUse = filterDataFrame(False, False)
    pointDataFrameToUse = filterDataFrame(False, True)
    noShowCount = dataFrameToUse[dataFrameToUse["noShow"] == True].shape[0]
    showCount = dataFrameToUse[dataFrameToUse["noShow"] == False].shape[0]
    totalShowCount = noShowCount + showCount
    noShowCountLabel.configure(text=f"{noShowCount} rounds without robot    {showCount} rounds with robot    {totalShowCount} rounds in total")
    if showNoShowTeamsCheckboxVariable.get() == 0:
        dataFrameToDisplay = dataFrameToUse[dataFrameToUse["noShow"].values == False]
        pointDataFrameToDisplay = pointDataFrameToUse[pointDataFrameToUse["noShow"].values == False]
    else:
        dataFrameToDisplay = dataFrameToUse
        pointDataFrameToDisplay = pointDataFrameToUse
    columnToDisplay = dataFrameToDisplay[variableDropdownVariable.get()]
    if columnToDisplay.dtypes == "int64":
        if isnan(columnToDisplay.std()):
            standardDeviationLabel.grid_remove()
        else:
            standardDeviationLabel.configure(text=f"Standard deviation: {columnToDisplay.std()}")
            standardDeviationLabel.grid()
        if columnToDisplay.shape[0] > 0:
            plotButtonContainer.grid()
        else:
            plotButtonContainer.grid_remove()
    else:
        standardDeviationLabel.grid_remove()
        plotButtonContainer.grid_remove()
    rawValueDataText.configure(state=tkinter.NORMAL)
    rawValueDataText.delete("1.0", tkinter.END)
    if showNoShowTeamsCheckboxVariable.get() == 0:
        rawValueDataText.insert(tkinter.END, dataFrameToDisplay[["roundNum", "teamNum", variableDropdownVariable.get()]].to_string(index=False))
    else:
        rawValueDataText.insert(tkinter.END, dataFrameToDisplay[["roundNum", "teamNum", "noShow", variableDropdownVariable.get()]].to_string(index=False))
    rawValueDataText.configure(state=tkinter.DISABLED)
    if variableDropdownVariable.get() in pointDataFrame.columns:
        pointColumnToDisplay = pointDataFrameToDisplay[variableDropdownVariable.get()]
        if pointColumnToDisplay.dtypes == "int64":
            if isnan(pointColumnToDisplay.std()):
                pointStandardDeviationLabel.grid_remove()
            else:
                pointStandardDeviationLabel.configure(text=f"Standard deviation: {pointColumnToDisplay.std()}")
                pointStandardDeviationLabel.grid()
            if pointColumnToDisplay.shape[0] > 0:
                pointPlotButtonContainer.grid()
            else:
                pointPlotButtonContainer.grid_remove()
        else:
            pointStandardDeviationLabel.grid_remove()
            pointPlotButtonContainer.grid_remove()
        pointRawValueDataText.configure(state=tkinter.NORMAL)
        pointRawValueDataText.delete("1.0", tkinter.END)
        if showNoShowTeamsCheckboxVariable.get() == 0:
            pointRawValueDataText.insert(tkinter.END, pointDataFrameToDisplay[["roundNum", "teamNum", variableDropdownVariable.get()]].to_string(index=False))
        else:
            pointRawValueDataText.insert(tkinter.END, pointDataFrameToDisplay[["roundNum", "teamNum", "noShow", variableDropdownVariable.get()]].to_string(index=False))
        pointRawValueDataText.configure(state=tkinter.DISABLED)
    else:
        pointStandardDeviationLabel.grid_remove()
        pointPlotButtonContainer.grid_remove()
        pointRawValueDataText.configure(state=tkinter.NORMAL)
        pointRawValueDataText.delete("1.0", tkinter.END)
        pointRawValueDataText.insert(tkinter.END, "This item has no scoring attached to it")
        pointRawValueDataText.configure(state=tkinter.DISABLED)

def showBoxPlot(usePointValues=False):
    dataFrameToDisplay = filterDataFrame(True, usePointValues)
    columnToDisplay = dataFrameToDisplay[variableDropdownVariable.get()]
    teams = dataFrameToDisplay["teamNum"].drop_duplicates().values
    if (len(teams) == 1):
        axies = pyplot.subplots(nrows=1, ncols=1)[1]
        columnToDisplay.plot.box(ax=axies)
        axies.set_title("Team" + str(teams[0]))
    else:
        axies = pyplot.subplots(nrows=1, ncols=len(teams) + 1)[1]
        columnToDisplay.plot.box(ax=axies[0])
        axies[0].set_title("All Teams")
        for i in range(len(teams)):
            teamDataFrame = dataFrameToDisplay[dataFrameToDisplay["teamNum"].isin([teams[i]])]
            columnToDisplay = teamDataFrame[variableDropdownVariable.get()]
            columnToDisplay.plot.box(ax=axies[i+1])
            axies[i+1].set_title("Team " + str(teams[i]))
    pyplot.get_current_fig_manager().set_window_title("Box Plot")
    pyplot.show()

def showPointBoxPlot():
    showBoxPlot(True)

def showLinePlot(usePointValues=False):
    dataFrameToDisplay = filterDataFrame(True, usePointValues)
    columnsToDisplay = dataFrameToDisplay[["roundNum", variableDropdownVariable.get()]]
    teams = dataFrameToDisplay["teamNum"].drop_duplicates().values
    if (len(teams) == 1):
        axies = pyplot.subplots(nrows=1, ncols=1)[1]
        columnsToDisplay.plot.line(ax=axies, x="roundNum", y=variableDropdownVariable.get())
        axies.set_title("Team" + str(teams[0]))
    else:
        axies = pyplot.subplots(nrows=1, ncols=len(teams) + 1)[1]
        columnsToDisplay.plot.line(ax=axies[0], x="roundNum", y=variableDropdownVariable.get())
        axies[0].set_title("All Teams")
        for i in range(len(teams)):
            teamDataFrame = dataFrameToDisplay[dataFrameToDisplay["teamNum"].isin([teams[i]])]
            columnsToDisplay = teamDataFrame[["roundNum", variableDropdownVariable.get()]]
            columnsToDisplay.plot.line(ax=axies[i+1], x="roundNum", y=variableDropdownVariable.get())
            axies[i+1].set_title("Team " + str(teams[i]))
    pyplot.get_current_fig_manager().set_window_title("Line Graph")
    pyplot.show()

def showPointLinePlot():
    showLinePlot(True)

def addTeamToFilter():
    global teamsToFilterListboxValues
    if addTeamToFilterEntry.get().isnumeric():
        if int(addTeamToFilterEntry.get()) in dataFrame["teamNum"].values:
            teamsToFilterListboxValues.append(int(addTeamToFilterEntry.get()))
            teamsToFilterListbox.configure(listvariable=tkinter.StringVar(value=teamsToFilterListboxValues))
            addTeamToFilterEntry.delete(0, tkinter.END)
        else:
            tkinter.messagebox.showerror("Illegal Value", "There is no data for this team")
    else:
        tkinter.messagebox.showerror("Illegal Value", "Must be a positive number")

def removeTeamFromFilter():
    global teamsToFilterListboxValues
    try:
        del teamsToFilterListboxValues[teamsToFilterListbox.curselection()[0]]
        teamsToFilterListbox.configure(listvariable=tkinter.StringVar(value=teamsToFilterListboxValues))
    except:
        pass

def saveTeamsToFilter():
    global teamsToFilterListboxValues
    global teamsToFilter
    global filteredDataFrame
    global filteredPointDataFrame
    if len(teamsToFilterListboxValues) > 0:
        teamsToFilter = teamsToFilterListboxValues.copy()
        filteredDataFrame = dataFrame[dataFrame["teamNum"].isin(teamsToFilter)]
        filteredPointDataFrame = pointDataFrame[dataFrame["teamNum"].isin(teamsToFilter)]
        filterWindow.destroy()
        selectValue()
    else:
        tkinter.messagebox.showerror("Error", "No teams selected")

def showAllTeams():
    global teamsToFilter
    global filteredDataFrame
    teamsToFilter = None
    filteredDataFrame = None
    filterWindow.destroy()
    selectValue()

def getIcon():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "icon.ico")
    else:
        return "icon.ico"

def initalizeDataWindow():
    global dataWindow
    global dataFrame
    global rawValueDataText
    global pointRawValueDataText
    global variableDropdown
    global variableDropdownVariable
    global showNoShowTeamsCheckboxVariable
    global noShowCountLabel
    global standardDeviationLabel
    global pointStandardDeviationLabel
    global plotButtonContainer
    global pointPlotButtonContainer
    global teamsToFilter
    global filteredDataFrame
    global filteredPointDataFrame
    teamsToFilter = None
    filteredDataFrame = None
    mergeWindow.destroy()
    dataWindow = tkinter.Tk()
    dataWindow.iconbitmap(default=getIcon())
    dataWindow.title("Coalition Intelligence Analysis App")
    dataWindow.geometry("800x500")
    dataWindow.columnconfigure(0, weight=1)
    dataWindow.rowconfigure(2, weight=1)
    upperFrame = tkinter.Frame()
    upperFrame.columnconfigure(0, weight=1)
    dataFrameColumns = list(dataFrame.columns)
    dataFrameColumns.remove("roundNum")
    dataFrameColumns.remove("teamNum")
    dataFrameColumns.remove("noShow")
    variableDropdownVariable = tkinter.StringVar(value=dataFrameColumns[0])
    variableDropdownVariable.trace_add("write", selectValue)
    variableDropdown = tkinter.OptionMenu(upperFrame, variableDropdownVariable, *dataFrameColumns)
    variableDropdown.grid(row=0, column=0, sticky="NEW")
    showNoShowTeamsCheckboxVariable = tkinter.IntVar(value=0)
    showNoShowTeamsCheckboxVariable.trace_add("write", selectValue)
    showNoShowTeamsCheckbox = tkinter.Checkbutton(upperFrame, text="Show rounds without robot", indicatoron=False, variable=showNoShowTeamsCheckboxVariable)
    showNoShowTeamsCheckbox.grid(row=0, column=1)
    selectTeamButton = tkinter.Button(upperFrame, text="Select teams", command=selectTeam)
    selectTeamButton.grid(row=0, column=2)
    exportButton = tkinter.Button(upperFrame, text="Export values as CSV", command=exportCsv)
    exportButton.grid(row=0, column=3)
    pointExportButton = tkinter.Button(upperFrame, text="Export scores as CSV", command=exportPointCsv)
    pointExportButton.grid(row=0, column=4)
    upperFrame.grid(row=0, column=0, sticky="NEW")
    noShowCountLabel = tkinter.Label(dataWindow)
    noShowCountLabel.grid(row=1, column=0)
    mainContainer = tkinter.PanedWindow(dataWindow, orient=tkinter.HORIZONTAL)
    valueContainer = tkinter.Frame()
    valueContainer.rowconfigure(0, weight=1)
    valueContainer.columnconfigure(0, weight=1)
    rawValueDataText = tkinter.Text(valueContainer, wrap=tkinter.NONE)
    rawValueDataText.grid(row=0, column=0, sticky="NESW")
    standardDeviationLabel = tkinter.Label(valueContainer, anchor=tkinter.NW, justify=tkinter.LEFT)
    standardDeviationLabel.grid(row=1, column=0, sticky="NEW")
    plotButtonContainer = tkinter.Frame(valueContainer)
    boxplotDisplayButton = tkinter.Button(plotButtonContainer, text="Show box plot", command=showBoxPlot)
    boxplotDisplayButton.grid(row=0, column=0)
    lineplotDisplayButton = tkinter.Button(plotButtonContainer, text="Show line graph", command=showLinePlot)
    lineplotDisplayButton.grid(row=0, column=1)
    plotButtonContainer.grid(row=2, column=0, sticky="NE")
    mainContainer.add(valueContainer, sticky="NESW")
    pointContainer = tkinter.Frame()
    pointContainer.rowconfigure(0, weight=1)
    pointContainer.columnconfigure(0, weight=1)
    pointRawValueDataText = tkinter.Text(pointContainer, wrap=tkinter.NONE)
    pointRawValueDataText.grid(row=0, column=0, sticky="NESW")
    pointStandardDeviationLabel = tkinter.Label(pointContainer, anchor=tkinter.NW, justify=tkinter.LEFT)
    pointStandardDeviationLabel.grid(row=1, column=0, sticky="NEW")
    pointPlotButtonContainer = tkinter.Frame(pointContainer)
    pointBoxplotDisplayButton = tkinter.Button(pointPlotButtonContainer, text="Show box plot", command=showPointBoxPlot)
    pointBoxplotDisplayButton.grid(row=0, column=0)
    pointLineplotDisplayButton = tkinter.Button(pointPlotButtonContainer, text="Show line graph", command=showPointLinePlot)
    pointLineplotDisplayButton.grid(row=0, column=1)
    pointPlotButtonContainer.grid(row=2, column=0, sticky="NE")
    mainContainer.add(pointContainer, sticky="NESW")
    mainContainer.grid(row=2, column=0, sticky="NESW")
    selectValue()
    dataWindow.mainloop()

def initalizeMergeWindow():
    global filesToMerge
    global mergeWindow
    global csvFileListbox
    global pointValues
    global dropdownValues
    filesToMerge = []
    mergeWindow = tkinter.Tk()
    mergeWindow.iconbitmap(default=getIcon())
    mergeWindow.title("Merge CSV Files")
    mergeWindow.geometry("500x300")
    mergeWindow.columnconfigure(0, weight=1)
    mergeWindow.rowconfigure(0, weight=1)
    csvFileListbox = tkinter.Listbox(mergeWindow)
    csvFileListbox.grid(row=0, column=0, sticky="NESW")
    lowerFrame = tkinter.Frame(mergeWindow)
    addCsvFileButton = tkinter.Button(lowerFrame, text="Add CSV file", command=addCsvFile)
    addCsvFileButton.grid(row=0, column=0)
    removeCsvFileButton = tkinter.Button(lowerFrame, text="Remove CSV file", command=removeCsvFile)
    removeCsvFileButton.grid(row=0, column=1)
    displayDataButton = tkinter.Button(lowerFrame, text="Done", command=mergeCsvFiles)
    displayDataButton.grid(row=0, column=2)
    lowerFrame.grid(row=1, column=0, sticky="E")
    try:
        jsonFile = open("config.json", mode="r")
        jsonValues = json.load(jsonFile)
        jsonFile.close()
        if "pointValues" in jsonValues:
            pointValues = jsonValues["pointValues"]
        else:
            pointValues = {}
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring and dropdown recognition may not work properly.")
        if "dropdownValues" in jsonValues:
            dropdownValues = jsonValues["dropdownValues"]
        else:
            dropdownValues = {}
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring and dropdown recognition may not work properly.")
    except:
        pointValues = {}
        dropdownValues = {}
        tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring and dropdown recognition may not work properly.")
    mergeWindow.mainloop()

def selectTeam():
    global addTeamToFilterEntry
    global teamsToFilterListboxValues
    global teamsToFilterListbox
    global teamsToFilter
    global filterWindow
    filterWindow = tkinter.Toplevel()
    filterWindow.title("Select Teams")
    filterWindow.geometry("500x300")
    filterWindow.grab_set()
    filterWindow.transient(dataWindow)
    filterWindow.columnconfigure(0, weight=1)
    filterWindow.rowconfigure(0, weight=1)
    teamsToFilterListbox = tkinter.Listbox(filterWindow)
    if teamsToFilter != None:
        teamsToFilterListboxValues = teamsToFilter.copy()
        teamsToFilterListbox.configure(listvariable=tkinter.StringVar(value=teamsToFilterListboxValues))
    else:
        teamsToFilterListboxValues = []
    teamsToFilterListbox.grid(row=0, column=0, sticky="NESW")
    lowerFrame = tkinter.Frame(filterWindow)
    lowerFrame.columnconfigure(0, weight=1)
    addTeamToFilterEntry = tkinter.Entry(lowerFrame)
    addTeamToFilterEntry.grid(row=0, column=0, sticky="EW")
    addTeamToFilterButton = tkinter.Button(lowerFrame, text="Add team", command=addTeamToFilter)
    addTeamToFilterButton.grid(row=0, column=1)
    removeTeamToFilterButton = tkinter.Button(lowerFrame, text="Remove team", command=removeTeamFromFilter)
    removeTeamToFilterButton.grid(row=0, column=2)
    saveTeamToFilterButton = tkinter.Button(lowerFrame, text="Save", command=saveTeamsToFilter)
    saveTeamToFilterButton.grid(row=0, column=3)
    showAllTeamsToFilterButton = tkinter.Button(lowerFrame, text="Show all teams", command=showAllTeams)
    showAllTeamsToFilterButton.grid(row=0, column=4)
    lowerFrame.grid(row=1, column=0, sticky="EW")

initalizeMergeWindow()