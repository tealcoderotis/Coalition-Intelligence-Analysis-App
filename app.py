import pandas
import matplotlib.pyplot as pyplot
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import json

def replaceDataFrameWithPointValue(data, pointValue, dataType):
    if dataType == "bool":
        if data == True:
            return pointValue
        else:
            return 0
    if dataType == "int64" or dataType == "float64":
        return data * pointValue
    if dataType == "object":
        return pointValue[data]
    
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
        dataFrameToUse = dataFrameToUse[dataFrameToUse["noShow"].values == False]
    if hideNoShow == True and showRobotStoppedTeamsCheckboxVariable.get() == 0:
        dataFrameToUse = dataFrameToUse[dataFrameToUse["robotStop"].values == "No stop"]
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
            if "preprocessed" not in dataFrame.columns:
                dataFrame["preprocessed"] = True
                for column in dataFrame.columns:
                    if column in dropdownValues:
                        dataFrame[column] = dataFrame[column].apply(replaceDataFrameWithDropdownValue, args=(dropdownValues[column],))
                for cycleCountValue, itemsToCount in cycleCountValues.items():
                    indexToAdd = dataFrame.columns.get_loc(itemsToCount[len(itemsToCount) - 1]) + 1
                    dataFrame.insert(loc=indexToAdd, column=cycleCountValue, value=addColumns(dataFrame, itemsToCount))
            pointDataFrame = pandas.DataFrame()
            pointDataFrame["roundNum"] = dataFrame["roundNum"]
            pointDataFrame["teamNum"] = dataFrame["teamNum"]
            pointDataFrame["noShow"] = dataFrame["noShow"]
            pointDataFrame["robotStop"] = dataFrame["robotStop"]
            for column, value in pointValues.items():
                    pointDataFrame[column] = dataFrame[column].apply(replaceDataFrameWithPointValue, args=(value, dataFrame[column].dtypes,))
        except:
            tkinter.messagebox.showerror("Error", "An error occured while trying to load the data")
        else:
            initalizeDataWindow()
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
    global countLabel
    global statisticsLabel
    global pointStatisticsLabel
    global showNoShowTeamsCheckboxVariable
    dataFrameToUse = filterDataFrame(False, False)
    noShowCount = dataFrameToUse[dataFrameToUse["noShow"].values == True].shape[0]
    showCount = dataFrameToUse[dataFrameToUse["noShow"].values == False].shape[0]
    robotStoppedCount = dataFrameToUse[dataFrameToUse["robotStop"].values != "No stop"].shape[0]
    noRobotStoppedCount = dataFrameToUse[dataFrameToUse["robotStop"].values == "No stop"].shape[0]
    totalCount = dataFrameToUse.shape[0]
    countLabel.configure(text=f"{noShowCount} rounds without robot    {showCount} rounds with robot    {robotStoppedCount} rounds with stopped robot    {noRobotStoppedCount} rounds without stopped robot    {totalCount} rounds total")
    dataFrameToDisplay = filterDataFrame(True, False)
    pointDataFrameToDisplay = filterDataFrame(True, True)
    if variableDropdownVariable.get() != "All values":
        columnToDisplay = dataFrameToDisplay[variableDropdownVariable.get()]
        if columnToDisplay.shape[0] > 0:
            mode = ", ".join(map(str, columnToDisplay.mode().to_list()))
            if columnToDisplay.dtypes == "int64" or columnToDisplay.dtypes == "float64":
                statisticsLabel.configure(text=f"Mean: {columnToDisplay.mean()}    Median: {columnToDisplay.median()}    Mode: {mode}    Standard deviation: {columnToDisplay.std(ddof=0)}")
                statisticsLabel.grid()
                plotButtonContainer.grid()
            else:
                statisticsLabel.configure(text=f"Mode: {mode}")
                statisticsLabel.grid()
                plotButtonContainer.grid_remove()
        else:
            statisticsLabel.grid_remove()
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
            if pointColumnToDisplay.shape[0] > 0:
                pointMode = ", ".join(map(str, pointColumnToDisplay.mode().to_list()))
                if pointColumnToDisplay.dtypes == "int64" or pointColumnToDisplay.dtypes == "float64":
                    pointStatisticsLabel.configure(text=f"Mean: {pointColumnToDisplay.mean()}    Median: {pointColumnToDisplay.median()}    Mode: {pointMode}    Standard deviation: {pointColumnToDisplay.std(ddof=0)}")
                    pointStatisticsLabel.grid()
                    pointPlotButtonContainer.grid()
                else:
                    pointStatisticsLabel.configure(text=f"Mode: {pointMode}")
                    pointStatisticsLabel.grid()
                    pointPlotButtonContainer.grid_remove()
            else:
                pointStatisticsLabel.grid_remove()
                pointPlotButtonContainer.grid_remove()
            pointRawValueDataText.configure(state=tkinter.NORMAL)
            pointRawValueDataText.delete("1.0", tkinter.END)
            if showNoShowTeamsCheckboxVariable.get() == 0:
                pointRawValueDataText.insert(tkinter.END, pointDataFrameToDisplay[["roundNum", "teamNum", variableDropdownVariable.get()]].to_string(index=False))
            else:
                pointRawValueDataText.insert(tkinter.END, pointDataFrameToDisplay[["roundNum", "teamNum", "noShow", variableDropdownVariable.get()]].to_string(index=False))
            pointRawValueDataText.configure(state=tkinter.DISABLED)
        else:
            pointStatisticsLabel.grid_remove()
            pointPlotButtonContainer.grid_remove()
            pointRawValueDataText.configure(state=tkinter.NORMAL)
            pointRawValueDataText.delete("1.0", tkinter.END)
            pointRawValueDataText.insert(tkinter.END, "This item has no scoring attached to it")
            pointRawValueDataText.configure(state=tkinter.DISABLED)
    else:
        statisticsLabel.grid_remove()
        plotButtonContainer.grid_remove()
        pointStatisticsLabel.grid_remove()
        pointPlotButtonContainer.grid_remove()
        rawValueDataText.configure(state=tkinter.NORMAL)
        rawValueDataText.delete("1.0", tkinter.END)
        columnsToDisplay = list(dataFrameToDisplay.columns)
        for valueToHide in valuesToHide:
                columnsToDisplay.remove(valueToHide)
        if showNoShowTeamsCheckboxVariable.get() == 0:
            columnsToDisplay.remove("noShow")
            rawValueDataText.insert(tkinter.END, dataFrameToDisplay[columnsToDisplay].to_string(index=False))
        else:
            rawValueDataText.insert(tkinter.END, dataFrameToDisplay[columnsToDisplay].to_string(index=False))
        rawValueDataText.configure(state=tkinter.DISABLED)
        pointRawValueDataText.configure(state=tkinter.NORMAL)
        pointRawValueDataText.delete("1.0", tkinter.END)
        pointColumnsToDisplay = list(pointDataFrameToDisplay.columns)
        if showNoShowTeamsCheckboxVariable.get() == 0:
            pointColumnsToDisplay.remove("noShow")
            pointRawValueDataText.insert(tkinter.END, pointDataFrameToDisplay[pointColumnsToDisplay].to_string(index=False))
        else:
            pointRawValueDataText.insert(tkinter.END, pointDataFrameToDisplay[pointColumnsToDisplay].to_string(index=False))
        pointRawValueDataText.configure(state=tkinter.DISABLED)

def showBoxPlot(usePointValues=False):
    dataFrameToDisplay = filterDataFrame(True, usePointValues)
    columnToDisplay = dataFrameToDisplay[variableDropdownVariable.get()]
    teams = dataFrameToDisplay.sort_values("teamNum")["teamNum"].drop_duplicates().values
    if (len(teams) == 1):
        axies = pyplot.subplots(nrows=1, ncols=1, sharey=True)[1]
        columnToDisplay.plot(kind="box", ax=axies)
        axies.set_title(teams[0])
    else:
        axies = pyplot.subplots(nrows=1, ncols=len(teams) + 1, sharey=True)[1]
        columnToDisplay.plot(kind="box", ax=axies[0])
        axies[0].set_title("All Teams")
        for i in range(len(teams)):
            teamDataFrame = dataFrameToDisplay[dataFrameToDisplay["teamNum"].isin([teams[i]])]
            columnToDisplay = teamDataFrame[variableDropdownVariable.get()]
            columnToDisplay.plot.box(ax=axies[i+1])
            axies[i+1].set_title(teams[i])
    pyplot.get_current_fig_manager().set_window_title("Box Plot")
    pyplot.show()

def showPointBoxPlot():
    showBoxPlot(True)

def showLinePlot(usePointValues=False):
    dataFrameToDisplay = filterDataFrame(True, usePointValues)
    columnsToDisplay = dataFrameToDisplay[["roundNum", variableDropdownVariable.get()]]
    teams = dataFrameToDisplay.sort_values("teamNum")["teamNum"].drop_duplicates().values
    if (len(teams) == 1):
        axies = pyplot.subplots(nrows=1, ncols=1, sharey=True, sharex=True)[1]
        columnsToDisplay.plot(kind="line", ax=axies, x="roundNum", y=variableDropdownVariable.get())
        axies.set_title(teams[0])
    else:
        axies = pyplot.subplots(nrows=1, ncols=len(teams) + 1, sharey=True, sharex=True)[1]
        columnsToDisplay.plot(kind="line", ax=axies[0], x="roundNum", y=variableDropdownVariable.get())
        axies[0].set_title("All Teams")
        for i in range(len(teams)):
            teamDataFrame = dataFrameToDisplay[dataFrameToDisplay["teamNum"].isin([teams[i]])]
            columnsToDisplay = teamDataFrame[["roundNum", variableDropdownVariable.get()]]
            columnsToDisplay.plot.line(ax=axies[i+1], x="roundNum", y=variableDropdownVariable.get())
            axies[i+1].set_title(teams[i])
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
    
def addColumns(dataFrame, columnsToAdd):
    dataFrame = dataFrame.copy(deep=True)
    series = dataFrame[columnsToAdd[0]]
    for i in range(1, len(columnsToAdd)):
        series = series.add(dataFrame[columnsToAdd[i]])
    return series

def convertToCSPFormat():
    if len(filesToMerge) > 0:
        try:
            oldDataFrame = pandas.read_csv(filesToMerge[0])
            for i in range(1, len(filesToMerge)):
                data = pandas.read_csv(filesToMerge[i])
                oldDataFrame = pandas.concat([oldDataFrame, data], ignore_index=True)
            oldDataFrame.sort_values("roundNum", inplace=True)
            dataFrame = pandas.DataFrame()
            for newValue, conversionValue in cspConverterValues.items():
                if type(conversionValue) == str:
                    if conversionValue != "":
                        dataFrame[newValue] = oldDataFrame[conversionValue]
                    else:
                        dataFrame[newValue] = ""
                elif type(conversionValue) == list:
                    dataFrame[newValue] = addColumns(oldDataFrame, conversionValue)
                elif type(conversionValue) == dict:
                    dataFrame[newValue] = oldDataFrame[conversionValue["value"]].apply(replaceDataFrameWithDropdownValue, args=(conversionValue["dropdownValues"],))
        except:
            tkinter.messagebox.showerror("Error", "An error occured while trying to load the data")
        else:
            fileName = tkinter.filedialog.asksaveasfilename(parent=mergeWindow, filetypes=[("CSV File", "*.csv")], initialfile="data.csv")
            if len(fileName) > 0:
                dataFrame.to_csv(fileName, index=False)
    else:
        tkinter.messagebox.showerror("Error", "No CSV files selected")

def initalizeDataWindow():
    global dataWindow
    global dataFrame
    global rawValueDataText
    global pointRawValueDataText
    global variableDropdown
    global variableDropdownVariable
    global showNoShowTeamsCheckboxVariable
    global showRobotStoppedTeamsCheckboxVariable
    global countLabel
    global statisticsLabel
    global pointStatisticsLabel
    global plotButtonContainer
    global pointPlotButtonContainer
    global teamsToFilter
    global filteredDataFrame
    global filteredPointDataFrame
    teamsToFilter = None
    filteredDataFrame = None
    mergeWindow.destroy()
    dataWindow = tkinter.Tk()
    dataWindow.iconbitmap("icon.ico")
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
    for valueToHide in valuesToHide:
        if valueToHide in dataFrameColumns:
            dataFrameColumns.remove(valueToHide)
    dataFrameColumns.insert(0, "All values")
    variableDropdownVariable = tkinter.StringVar(value=dataFrameColumns[0])
    variableDropdownVariable.trace_add("write", selectValue)
    variableDropdown = tkinter.OptionMenu(upperFrame, variableDropdownVariable, *dataFrameColumns)
    variableDropdown.grid(row=0, column=0, sticky="NEW")
    showNoShowTeamsCheckboxVariable = tkinter.IntVar(value=0)
    showNoShowTeamsCheckboxVariable.trace_add("write", selectValue)
    showNoShowTeamsCheckbox = tkinter.Checkbutton(upperFrame, text="Show rounds without robot", indicatoron=False, variable=showNoShowTeamsCheckboxVariable)
    showNoShowTeamsCheckbox.grid(row=0, column=1)
    showRobotStoppedTeamsCheckboxVariable = tkinter.IntVar(value=0)
    showRobotStoppedTeamsCheckboxVariable.trace_add("write", selectValue)
    showRobotStoppedTeamsCheckbox = tkinter.Checkbutton(upperFrame, text="Show rounds with stopped robot", indicatoron=False, variable=showRobotStoppedTeamsCheckboxVariable)
    showRobotStoppedTeamsCheckbox.grid(row=0, column=2)
    showTeamSummariesButton = tkinter.Button(upperFrame, text="Team summaries", command=initalizeTeamSummariesWindow)
    showTeamSummariesButton.grid(row=0, column=3)
    selectTeamButton = tkinter.Button(upperFrame, text="Select teams", command=selectTeam)
    selectTeamButton.grid(row=0, column=4)
    exportButton = tkinter.Button(upperFrame, text="Export values as CSV", command=exportCsv)
    exportButton.grid(row=0, column=5)
    pointExportButton = tkinter.Button(upperFrame, text="Export scores as CSV", command=exportPointCsv)
    pointExportButton.grid(row=0, column=6)
    upperFrame.grid(row=0, column=0, sticky="NEW")
    countLabel = tkinter.Label(dataWindow)
    countLabel.grid(row=1, column=0)
    mainContainer = tkinter.PanedWindow(dataWindow, orient=tkinter.HORIZONTAL)
    valueContainer = tkinter.Frame()
    valueContainer.rowconfigure(0, weight=1)
    valueContainer.columnconfigure(0, weight=1)
    rawValueDataText = tkinter.Text(valueContainer, wrap=tkinter.NONE)
    rawValueDataText.grid(row=0, column=0, sticky="NESW")
    statisticsLabel = tkinter.Label(valueContainer)
    statisticsLabel.grid(row=1, column=0)
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
    pointStatisticsLabel = tkinter.Label(pointContainer)
    pointStatisticsLabel.grid(row=1, column=0)
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
    global valuesToHide
    global cspConverterValues
    global cycleCountValues
    global robotAbilites
    filesToMerge = []
    mergeWindow = tkinter.Tk()
    mergeWindow.iconbitmap("icon.ico")
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
    convertToCspButton = tkinter.Button(lowerFrame, text="Convert to CSP format", command=convertToCSPFormat)
    convertToCspButton.grid(row=0, column=2)
    displayDataButton = tkinter.Button(lowerFrame, text="Done", command=mergeCsvFiles)
    displayDataButton.grid(row=0, column=3)
    lowerFrame.grid(row=1, column=0, sticky="E")
    try:
        jsonFile = open("config.json", mode="r")
        jsonValues = json.load(jsonFile)
        jsonFile.close()
        if "pointValues" in jsonValues:
            pointValues = jsonValues["pointValues"]
        else:
            pointValues = {}
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
        if "dropdownValues" in jsonValues:
            dropdownValues = jsonValues["dropdownValues"]
        else:
            dropdownValues = {}
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
        if "hideFromSelector" in jsonValues:
            valuesToHide = jsonValues["hideFromSelector"]
        else:
            valuesToHide = []
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
        if "CSPConverterValues" in jsonValues:
            cspConverterValues = jsonValues["CSPConverterValues"]
        else:
            cspConverterValues = []
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
        if "cycleCounts" in jsonValues:
            cycleCountValues = jsonValues["cycleCounts"]
        else:
            cycleCountValues = {}
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
        if "robotAbilites" in jsonValues:
            robotAbilites = jsonValues["robotAbilites"]
        else:
            robotAbilites = {}
            tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
    except:
        pointValues = {}
        dropdownValues = {}
        valuesToHide = []
        cspConverterValues = []
        cycleCountValues = {}
        robotAbilites = {}
        tkinter.messagebox.showerror("Error", "Failed to load config.json. Scoring, dropdown recognition, and the CSP converter may not work properly.")
    valuesToHide.append("preprocessed")
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

def exportTeamAbilites():
    fileName = tkinter.filedialog.asksaveasfilename(parent=dataWindow, filetypes=[("CSV File", "*.csv")], initialfile="data.csv")
    if len(fileName) > 0:
        if robotAbilitesDropdownVariable.get() == "Precentages":
            abilityPrecentagesDataFrame.to_csv(fileName, index=False)
        elif robotAbilitesDropdownVariable.get() == "Means":
            abilityMeansDataFrame.to_csv(fileName, index=False)

def selectTeamSummaryType(*args):
    robotAbilitesText.configure(state=tkinter.NORMAL)
    robotAbilitesText.delete("1.0", tkinter.END)
    if robotAbilitesDropdownVariable.get() == "Precentages":
        robotAbilitesMeanDropdown.grid_remove()
        robotAbilitesPrecentageDropdown.grid(row=0, column=1)
        robotAbilitesText.insert(tkinter.END, abilityPrecentagesDataFrame.to_string(index=False))
    elif robotAbilitesDropdownVariable.get() == "Means":
        robotAbilitesPrecentageDropdown.grid_remove()
        robotAbilitesMeanDropdown.grid(row=0, column=1)
        robotAbilitesText.insert(tkinter.END, abilityMeansDataFrame.to_string(index=False))
    robotAbilitesText.configure(state=tkinter.DISABLED)

def selectTeamPrecentageSorting(*args):
    robotAbilitesText.configure(state=tkinter.NORMAL)
    robotAbilitesText.delete("1.0", tkinter.END)
    if robotAbilitesPrecentageDropdownVariable.get() == "teamNum":
        abilityPrecentagesDataFrame.sort_values(robotAbilitesPrecentageDropdownVariable.get(), ascending=True, inplace=True)
    else:
        abilityPrecentagesDataFrame.sort_values(robotAbilitesPrecentageDropdownVariable.get(), ascending=False, inplace=True)
    robotAbilitesText.insert(tkinter.END, abilityPrecentagesDataFrame.to_string(index=False))
    robotAbilitesText.configure(state=tkinter.DISABLED)

def selectTeamMeanSorting(*args):
    robotAbilitesText.configure(state=tkinter.NORMAL)
    robotAbilitesText.delete("1.0", tkinter.END)
    if robotAbilitesMeanDropdownVariable.get() == "teamNum":
        abilityMeansDataFrame.sort_values(robotAbilitesMeanDropdownVariable.get(), ascending=True, inplace=True)
    else:
        abilityMeansDataFrame.sort_values(robotAbilitesMeanDropdownVariable.get(), ascending=False, inplace=True)
    robotAbilitesText.insert(tkinter.END, abilityMeansDataFrame.to_string(index=False))
    robotAbilitesText.configure(state=tkinter.DISABLED)

def initalizeTeamSummariesWindow():
    global robotAbilitesDropdownVariable
    global robotAbilitesText
    global abilityPrecentagesDataFrame
    global abilityMeansDataFrame
    global robotAbilitesDropdownVariable
    global robotAbilitesPrecentageDropdownVariable
    global robotAbilitesPrecentageDropdown
    global robotAbilitesMeanDropdownVariable
    global robotAbilitesMeanDropdown
    dataFrameToDisplay = filterDataFrame(True, False)
    teams = dataFrameToDisplay["teamNum"].drop_duplicates().values
    abilityPrecentagesDataFrame = pandas.DataFrame()
    abilityPrecentagesDataFrame["teamNum"] = pandas.Series(teams)
    abilityMeansDataFrame = pandas.DataFrame()
    abilityMeansDataFrame["teamNum"] = pandas.Series(teams)
    for ability, value in robotAbilites.items():
        abilityPrecentageList = []
        abilityMeanList = []
        for team in teams:
            teamDataFrame = dataFrameToDisplay[dataFrameToDisplay["teamNum"] == team]
            if type(value) == int:
                abilityPrecentage = teamDataFrame[teamDataFrame[ability].values > value].shape[0] / teamDataFrame.shape[0] * 100
                abilityMean = teamDataFrame[ability].mean()
                abilityMeanList.append(abilityMean)
            elif type(value) == list:
                abilityPrecentage = teamDataFrame[~teamDataFrame[ability].isin(value)].shape[0] / teamDataFrame.shape[0] * 100
            abilityPrecentageList.append(abilityPrecentage)
        if len(abilityPrecentageList) > 0:
            abilityPrecentagesDataFrame[ability] = pandas.Series(abilityPrecentageList, dtype="object")
        if len(abilityMeanList) > 0:
            abilityMeansDataFrame[ability] = pandas.Series(abilityMeanList, dtype="object")
    abilityPrecentagesDataFrame.sort_values("teamNum", ascending=True, inplace=True)
    abilityMeansDataFrame.sort_values("teamNum", ascending=True, inplace=True)
    teamAbilityWindow = tkinter.Toplevel()
    teamAbilityWindow.title("Team Summaries")
    teamAbilityWindow.geometry("500x300")
    teamAbilityWindow.grab_set()
    teamAbilityWindow.transient(dataWindow)
    teamAbilityWindow.columnconfigure(0, weight=1)
    teamAbilityWindow.rowconfigure(1, weight=1)
    teamAbilityUpperFrame = tkinter.Frame(teamAbilityWindow)
    teamAbilityUpperFrame.columnconfigure(0, weight=1)
    robotAbilitesDropdownVariable = tkinter.StringVar(value="Precentages")
    robotAbilitesDropdown = tkinter.OptionMenu(teamAbilityUpperFrame, robotAbilitesDropdownVariable, "Precentages", "Means", command=selectTeamSummaryType)
    robotAbilitesDropdown.grid(row=0, column=0, sticky="NEW")
    robotAbilitesPrecentageDropdownVariable = tkinter.StringVar(value="teamNum")
    robotAbilitesPrecentageDropdownVariable.trace_add("write", selectTeamPrecentageSorting)
    robotAbilitesPrecentageDropdown = tkinter.OptionMenu(teamAbilityUpperFrame, robotAbilitesPrecentageDropdownVariable, *list(abilityPrecentagesDataFrame.columns))
    robotAbilitesMeanDropdownVariable = tkinter.StringVar(value="teamNum")
    robotAbilitesMeanDropdownVariable.trace_add("write", selectTeamMeanSorting)
    robotAbilitesMeanDropdown = tkinter.OptionMenu(teamAbilityUpperFrame, robotAbilitesMeanDropdownVariable, *list(abilityMeansDataFrame.columns))
    robotAbilitesPrecentageDropdown.grid(row=0, column=1)
    exportRobotAbilitesButton = tkinter.Button(teamAbilityUpperFrame, text="Export as CSV", command=exportTeamAbilites)
    exportRobotAbilitesButton.grid(row=0, column=2)
    teamAbilityUpperFrame.grid(row=0, column=0, sticky="NEW")
    robotAbilitesText = tkinter.Text(teamAbilityWindow, wrap=tkinter.NONE)
    robotAbilitesText.grid(row=1, column=0, sticky="NESW")
    robotAbilitesText.insert(tkinter.END, abilityPrecentagesDataFrame.to_string(index=False))
    robotAbilitesText.configure(state=tkinter.DISABLED)

pyplot.switch_backend("TkAgg")
initalizeMergeWindow()