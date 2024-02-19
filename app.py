import pandas
from math import isnan
from matplotlib import pyplot
import tkinter
import tkinter.filedialog
import tkinter.messagebox

POINT_VALUES = {
    "auto_leave": 2,
    "ampNotes": 1,
    "auto_ampNotes": 2,
    "speakerNotes": 2,
    "auto_speakerNotes": 5,
    "ampSpeakerNotes": 5,
    "trapNotes": 5
}

def replaceDataFrameWithPointValue(data, pointValue, dataType):
    if dataType == "bool":
        if data == True:
            return pointValue
        else:
            return 0
    if dataType == "int64":
        return data * pointValue

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

def mergeCsvFiles():
    global dataFrame
    global pointDataFrame
    global filesToMerge
    dataFrame = pandas.read_csv(filesToMerge[0])
    for i in range(1, len(filesToMerge)):
        data = pandas.read_csv(filesToMerge[i])
        dataFrame = pandas.concat([dataFrame, data], ignore_index=True)
    dataFrame.sort_values("roundNum", inplace=True)
    pointDataFrame = dataFrame.copy(deep=True)
    for column in pointDataFrame.columns:
        if column in POINT_VALUES:
            pointDataFrame[column] = pointDataFrame[column].apply(replaceDataFrameWithPointValue, args=(POINT_VALUES[column], pointDataFrame[column].dtypes,))
        elif column != "teamNum" and column != "roundNum" and column != "noShow":
            pointDataFrame.drop(columns=column, inplace=True)
    initalizeDataWindow()

def exportMergedCsv():
    fileName = tkinter.filedialog.asksaveasfilename(parent=dataWindow, filetypes=[("CSV File", "*.csv")], initialfile="data.csv")
    if len(fileName) > 0:
        filterDataFrame(True, False).to_csv(fileName, index=False)

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
    global teamsToFilterListboxValues
    if addTeamToFilterEntry.get().isnumeric():
        if int(addTeamToFilterEntry.get()) in dataFrame["teamNum"].values:
            teamsToFilterListboxValues.append(int(addTeamToFilterEntry.get()))
            teamsToFilterListbox.configure(listvariable=tkinter.StringVar(value=teamsToFilterListboxValues))
            addTeamToFilterEntry.delete(0, tkinter.END)
        else:
            tkinter.messagebox.showerror("Illegal Value", "There is no data for this team")
    else:
        tkinter.messagebox.showerror("Illegal Value", "Must be a number greater than zero")

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
    dataWindow.title("Coalition Intelligence Analysis App")
    dataWindow.geometry("800x500")
    dataWindow.columnconfigure(0, weight=1)
    dataWindow.rowconfigure(1, weight=1)
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
    exportMergedButton = tkinter.Button(upperFrame, text="Export as CSV", command=exportMergedCsv)
    exportMergedButton.grid(row=0, column=3)
    noShowCountLabel = tkinter.Label(upperFrame)
    noShowCountLabel.grid(row=1, column=0, columnspan=4)
    upperFrame.grid(row=0, column=0, sticky="NEW")
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
    mainContainer.grid(row=1, column=0, sticky="NESW")
    selectValue()
    dataWindow.mainloop()

def initalizeMergeWindow():
    global filesToMerge
    global mergeWindow
    global csvFileListbox
    filesToMerge = []
    mergeWindow = tkinter.Tk()
    mergeWindow.title("Merge CSV Files")
    mergeWindow.geometry("500x300")
    mergeWindow.columnconfigure(0, weight=1)
    mergeWindow.rowconfigure(0, weight=1)
    csvFileListbox = tkinter.Listbox(mergeWindow)
    csvFileListbox.grid(row=0, column=0, sticky="NESW", columnspan=3)
    addCsvFileButton = tkinter.Button(mergeWindow, text="Add CSV file", command=addCsvFile)
    addCsvFileButton.grid(row=1, column=1)
    #TODO Display an error message when there is no data or CSV files selected
    displayDataButton = tkinter.Button(mergeWindow, text="Done", command=mergeCsvFiles)
    displayDataButton.grid(row=1, column=2)
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
    teamsToFilterListbox.grid(row=0, column=0, sticky="NESW", columnspan=4)
    addTeamToFilterEntry = tkinter.Entry(filterWindow)
    addTeamToFilterEntry.grid(row=2, column=0, sticky="EW")
    addTeamToFilterButton = tkinter.Button(filterWindow, text="Add team", command=addTeamToFilter)
    addTeamToFilterButton.grid(row=2, column=1)
    saveTeamToFilterButton = tkinter.Button(filterWindow, text="Save", command=saveTeamsToFilter)
    saveTeamToFilterButton.grid(row=2, column=2)
    showAllTeamsToFilterButton = tkinter.Button(filterWindow, text="Show all teams", command=showAllTeams)
    showAllTeamsToFilterButton.grid(row=2, column=3)

initalizeMergeWindow()