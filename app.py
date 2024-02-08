import pandas
from math import isnan
import tkinter
import tkinter.filedialog
import tkinter.simpledialog

POINT_VALUES = {
    "auto_leave": 2,
    "ampNotes": 1,
    "auto_ampNotes": 2,
    "speakerNotes": 2,
    "auto_speakerNotes": 5,
    "ampSpeakerNotes": 5,
    "trapNotes": 5
}

def addCsvFile():
    global filesToMerge
    files = tkinter.filedialog.askopenfilenames(parent=mergeWindow, filetypes=[("CSV File", "*.csv")])
    for file in files:
        filesToMerge.append(file)
    csvFileListbox.configure(listvariable=tkinter.StringVar(value=filesToMerge))

def mergeCsvFiles():
    global dataFrame
    global filesToMerge
    dataFrame = pandas.read_csv(filesToMerge[0])
    for i in range(1, len(filesToMerge)):
        data = pandas.read_csv(filesToMerge[i])
        dataFrame = pandas.concat([dataFrame, data], ignore_index=True)
    initalizeDataWindow()

def exportMergedCsv():
    global dataFrame
    fileName = tkinter.filedialog.asksaveasfilename(parent=dataWindow, filetypes=[("CSV File", "*.csv")], initialfile="data.csv")
    if len(fileName) > 0:
        if teamToFilter != None:
            filteredDataFrame.to_csv(fileName, index=False)
        else:
            dataFrame.to_csv(fileName, index=False)

def selectTeam():
    global dataFrame
    global filteredDataFrame
    global teamToFilter
    teamToFilter = tkinter.simpledialog.askinteger(parent=dataWindow, title="Select Team", prompt="Enter the team number. Select cancel to show all teams.", minvalue=1)
    if teamToFilter != None:
        filteredDataFrame = dataFrame[dataFrame["teamNum"].values == teamToFilter]
    else:
        filteredDataFrame = None
    selectValue()

def selectValue(*args):
    global dataFrame
    global rawValueDataText
    global variableDropdown
    global variableDropdownVariable
    global noShowCountLabel
    global standardDeviationLabel
    global teamToFilter
    global filteredDataFrame
    if teamToFilter != None:
        dataFrameToUse = filteredDataFrame
    else:
        dataFrameToUse = dataFrame
    noShowCount = dataFrameToUse.loc[dataFrameToUse["noShow"] == True].shape[0]
    showCount = dataFrameToUse.loc[dataFrameToUse["noShow"] == False].shape[0]
    totalShowCount = noShowCount + showCount
    noShowCountLabel.configure(text=f"{noShowCount} instances without robot\n{showCount} instances with robot\n{totalShowCount} instances in total")
    dataFrameToDisplay = dataFrameToUse[dataFrameToUse["noShow"].values == False]
    columnToDisplay = dataFrameToDisplay[variableDropdownVariable.get()]
    if columnToDisplay.dtypes == "int64":
        if isnan(columnToDisplay.std()):
            standardDeviationLabel.grid_remove()
        else:
            standardDeviationLabel.configure(text=f"Standard deviation: {columnToDisplay.std()}")
            standardDeviationLabel.grid()
        print(columnToDisplay.std())
    else:
        standardDeviationLabel.grid_remove()
    rawValueDataText.configure(state=tkinter.NORMAL)
    rawValueDataText.delete("1.0", tkinter.END)
    rawValueDataText.insert(tkinter.END, dataFrameToDisplay[["roundNum", "teamNum", variableDropdownVariable.get()]].to_string(index=False))
    rawValueDataText.configure(state=tkinter.DISABLED)

def initalizeDataWindow():
    global dataWindow
    global dataFrame
    global rawValueDataText
    global variableDropdown
    global variableDropdownVariable
    global noShowCountLabel
    global standardDeviationLabel
    global teamToFilter
    global filteredDataFrame
    teamToFilter = None
    filteredDataFrame = None
    mergeWindow.destroy()
    dataWindow = tkinter.Tk()
    dataWindow.title("Coalition Intelligence Analysis App")
    dataWindow.geometry("800x480")
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
    exportTeamButton = tkinter.Button(upperFrame, text="Select team", command=selectTeam)
    exportTeamButton.grid(row=0, column=1)
    exportMergedButton = tkinter.Button(upperFrame, text="Export as CSV", command=exportMergedCsv)
    exportMergedButton.grid(row=0, column=2)
    upperFrame.grid(row=0, column=0, sticky="NEW")
    mainContainer = tkinter.PanedWindow(dataWindow, orient=tkinter.HORIZONTAL)
    valueContainer = tkinter.Frame()
    valueContainer.rowconfigure(1, weight=1)
    valueContainer.columnconfigure(0, weight=1)
    noShowCountLabel = tkinter.Label(valueContainer, anchor=tkinter.NW, justify=tkinter.LEFT)
    noShowCountLabel.grid(row=0, column=0, sticky="NEW")
    rawValueDataText = tkinter.Text(valueContainer, wrap=tkinter.NONE)
    rawValueDataText.grid(row=1, column=0, sticky="NESW")
    standardDeviationLabel = tkinter.Label(valueContainer, anchor=tkinter.NW, justify=tkinter.LEFT)
    standardDeviationLabel.grid(row=2, column=0, sticky="NESW")
    mainContainer.add(valueContainer, sticky="NESW")
    pointContainer = tkinter.Frame()
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

initalizeMergeWindow()