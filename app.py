import pandas
import tkinter
import tkinter.filedialog

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
    files = tkinter.filedialog.askopenfilenames(filetypes=[("CSV File", "*.csv")])
    for file in files:
        filesToMerge.append(file)
    csvFileListbox.configure(listvariable=tkinter.StringVar(value=filesToMerge))

def mergeCsvFiles():
    global dataFrame
    global filesToMerge
    dataFrame = pandas.read_csv(filesToMerge[0])
    for i in range(1, len(filesToMerge)):
        data = pandas.read_csv(filesToMerge[i])
        pandas.concat([dataFrame, data], ignore_index=True)
    initalizeDataWindow()

def initalizeDataWindow():
    global dataWindow
    global variableDropdown
    global currentVariableDropdown
    global dataFrame
    mergeWindow.destroy()
    dataWindow = tkinter.Tk()
    dataWindow.title("Coalition Intelligence Graphing App")
    dataFrameColumns = list(dataFrame.columns)
    print(dataFrame.to_string())
    currentVariableDropdown = tkinter.StringVar(value=dataFrameColumns[0])
    variableDropdown = tkinter.OptionMenu(dataWindow, currentVariableDropdown, *dataFrameColumns)
    variableDropdown.grid(row=0, column=0)
    dataWindow.mainloop()

def initalizeMergeWindow():
    global filesToMerge
    global mergeWindow
    global csvFileListbox
    global addCsvFileButton
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