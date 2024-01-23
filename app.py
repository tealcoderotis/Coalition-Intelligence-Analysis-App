import pandas
import tkinter
import tkinter.filedialog

def addCsvFile():
    global filesToMerge
    files = tkinter.filedialog.askopenfilenames(filetypes=[("CSV File", "*.csv")])
    for file in files:
        filesToMerge.append(file)
    csvFileListbox.configure(listvariable=tkinter.StringVar(value=filesToMerge))

def mergeCsvFiles():
    global dataFrame
    global filesToMerge
    dataFrame = pandas.DataFrame()
    for file in filesToMerge:
        data = pandas.read_csv(file)
        fileDataFrame = pandas.DataFrame(data)
        pandas.concat([dataFrame, fileDataFrame], axis=1)
    initalizeDataWindow()

def initalizeDataWindow():
    mergeWindow.destroy()
    dataWindow = tkinter.Tk()
    dataWindow.title("Coalition Intelligence Graphing App")
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
    csvFileListbox = tkinter.Listbox()
    csvFileListbox.grid(row=0, column=0, sticky="NESW", columnspan=3)
    addCsvFileButton = tkinter.Button(text="Add CSV file", command=addCsvFile)
    addCsvFileButton.grid(row=1, column=1)
    #TODO Display an error message when there is no data or CSV files selected
    displayDataButton = tkinter.Button(text="Done", command=mergeCsvFiles)
    displayDataButton.grid(row=1, column=2)
    mergeWindow.mainloop()

initalizeMergeWindow()