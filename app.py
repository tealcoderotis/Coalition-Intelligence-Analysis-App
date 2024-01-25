import pandas
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
    if (len(fileName) > 0):
        dataFrame.to_csv(fileName, index=False)

def exportTeamData():
    tkinter.simpledialog.askinteger(parent=dataWindow, title="Export team data as CSV", prompt="Enter team number", minvalue=0)

def initalizeDataWindow():
    global dataWindow
    global dataFrame
    mergeWindow.destroy()
    dataWindow = tkinter.Tk()
    dataWindow.title("Coalition Intelligence Graphing App")
    dataWindow.geometry("800x480")
    dataWindow.columnconfigure(0, weight=1)
    upperFrame = tkinter.Frame()
    upperFrame.columnconfigure(0, weight=1)
    dataFrameColumns = list(dataFrame.columns)
    variableDropdown = tkinter.OptionMenu(upperFrame, tkinter.StringVar(value=dataFrameColumns[0]), *dataFrameColumns)
    variableDropdown.grid(row=0, column=0, sticky="NEW")
    exportTeamButton = tkinter.Button(upperFrame, text="Export team data as CSV", command=exportTeamData)
    exportTeamButton.grid(row=0, column=1)
    exportMergedButton = tkinter.Button(upperFrame, text="Export merged CSV", command=exportMergedCsv)
    exportMergedButton.grid(row=0, column=2)
    upperFrame.grid(row=0, column=0, sticky="NEW")
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