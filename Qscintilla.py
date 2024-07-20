from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QMenuBar, QMenu, QFileDialog, QTextEdit, QDockWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QStatusBar, QDialog, QVBoxLayout
from PyQt6.QtGui import QIcon, QPixmap, QKeySequence, QAction, QIntValidator,QColor
from PyQt6.QtCore import Qt, QMetaObject, QCoreApplication, QRect
from PyQt6.Qsci import QsciScintilla, QsciLexerPython

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.textEdit = QsciScintilla(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        
        self.menuSearch = QMenu(self.menubar)
        self.menuSearch.setObjectName("menuSearch")
        
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setShortcut("Ctrl+O")
        
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setShortcut("Ctrl+S")
        
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setShortcut("Ctrl+Q")
        
        self.actionFind = QAction(MainWindow)
        self.actionFind.setObjectName("actionFind")
        self.actionFind.setShortcut("Ctrl+F")
        
        self.actionWord_Count = QAction(MainWindow)
        self.actionWord_Count.setObjectName("actionWord_Count")
        self.actionWord_Count.setShortcut("Ctrl+G")
        
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionNew.setShortcut("Ctrl+N")
        
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExit)
        
        self.menuSearch.addAction(self.actionFind)
        self.menuSearch.addAction(self.actionWord_Count)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSearch.menuAction())

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuSearch.setTitle(_translate("MainWindow", "Search"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionFind.setText(_translate("MainWindow", "Find"))
        self.actionWord_Count.setText(_translate("MainWindow", "Go to Line"))
        self.actionNew.setText(_translate("MainWindow", "New"))

class Ui_Dock_Find(object):
    def setupUi(self, Dock_Find):
        Dock_Find.setObjectName("Dock_Find")
        Dock_Find.resize(320, 65)
        Dock_Find.setMinimumSize(320, 65)
        font = Dock_Find.font()
        font.setPointSize(10)
        Dock_Find.setFont(font)
        
        icon = QIcon()
        icon.addPixmap(QPixmap("Ok.png"), QIcon.Mode.Normal, QIcon.State.Off)
        Dock_Find.setWindowIcon(icon)
        
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        
        self.serachLabel = QLabel(self.dockWidgetContents)
        self.serachLabel.setGeometry(10, 10, 71, 16)
        self.serachLabel.setObjectName("serachLabel")
        self.serachLabel.setText("Search For:")
        
        self.findLine = QLineEdit(self.dockWidgetContents)
        self.findLine.setGeometry(80, 10, 151, 20)
        self.findLine.setObjectName("findLine")
        self.findLine.setPlaceholderText("Type Here")
        
        self.findButton = QPushButton(self.dockWidgetContents)
        self.findButton.setGeometry(240, 10, 75, 23)
        self.findButton.setObjectName("findButton")
        self.findButton.setText("Find")
        
        Dock_Find.setWidget(self.dockWidgetContents)

        self.retranslateUi(Dock_Find)

    def retranslateUi(self, Dock_Find):
        Dock_Find.setWindowTitle("Find")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Defining Menu Actions
        self.actionNew.triggered.connect(self.newFile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionExit.triggered.connect(self.exitFile)
        self.actionFind.triggered.connect(self.findWord)
        self.actionWord_Count.triggered.connect(self.gotoLine)

        self.showMaximized()

    def newFile(self):
        self.textEdit.clear()

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', ".", "(*.txt *.py *.log *.csv)")
        if filename:
            with open(filename, 'rt') as fp:
                data = fp.read()
                self.textEdit.setText(data)

    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', ".", "(*.txt)")
        if filename:
            with open(filename, 'wt') as f:
                text = self.textEdit.toPlainText()
                f.write(text)
                QMessageBox.about(self, "Save File", "File Saved Successfully")

    def exitFile(self):
        choice = QMessageBox.question(self, 'Close', "Do you want to close?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            self.saveFile()
            self.close()

    def findWord(self):
        try:
            dock = Dock_Find()
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
            dock.show()

            def handleFind():
                try:
                    word = dock.findLine.text()
                    if not word:
                        QMessageBox.about(self, "Find", "Please enter a search term.")
                        return

                    if not hasattr(self, 'textEdit'):
                        raise AttributeError("self.textEdit is not defined.")

                    self.textEdit.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, 0)
                    self.textEdit.SendScintilla(QsciScintilla.SCI_SETTARGETEND, self.textEdit.length())
                    pos = self.textEdit.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, len(word), word.encode())

                    if pos != -1:
                        try:
                            self.textEdit.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.textEdit.length())
                            indicator = self.textEdit.indicatorDefine(QsciScintilla.INDIC_ROUNDBOX)  # Define a custom indicator style
                            self.textEdit.setIndicatorForegroundColor(QColor(Qt.yellow))  # Set the indicator color
                            self.textEdit.setIndicatorBackgroundColor(QColor(Qt.yellow))  # Set the background color
                            self.textEdit.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, pos, len(word))  # Fill indicator range
                            self.textEdit.SendScintilla(QsciScintilla.SCI_INDICATORSETSTYLE, indicator, QsciScintilla.INDIC_ROUNDBOX)  # Apply indicator style
                        except Exception as e:
                            print(f"Error highlighting: {e}")
                    else:
                        QMessageBox.about(self, "Find", f"Text '{word}' not found.")
                except AttributeError as ae:
                    print(f"AttributeError in handleFind: {ae}")
                except Exception as e:
                    print(f"Error in handleFind: {e}")

            dock.findButton.clicked.connect(handleFind)

        except Exception as e:
            print(f'Error in findWord: {e}')


    def gotoLine(self):
        window = GoTo()
        window.exec()

        def handleGoTo():
            ln = int(window.findText.text()) - 1  # convert to zero-based index
            linecursor = self.textEdit.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, ln)
            self.textEdit.SendScintilla(QsciScintilla.SCI_ENSUREVISIBLE, ln)
            self.textEdit.SendScintilla(QsciScintilla.SCI_GOTOPOS, linecursor)
            window.close()

        window.findButton.clicked.connect(handleGoTo)

class Dock_Find(QDockWidget, Ui_Dock_Find):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.findLine.setPlaceholderText("Type Here")

class GoTo(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Go To")

    def initUI(self):
        self.lb1 = QLabel("Go To Line:", self)
        self.lb1.setStyleSheet("font-size: 15px")
        self.lb1.move(10, 10)
        
        self.findText = QLineEdit(self)
        self.findText.move(10, 40)
        self.findText.resize(200, 20)
        self.findText.setPlaceholderText('Type the line number')
        self.findText.setClearButtonEnabled(True)
        self.findText.setValidator(QIntValidator())
        
        self.findButton = QPushButton('GO', self)
        self.findButton.move(220, 40)

        layout = QVBoxLayout(self)
        layout.addWidget(self.lb1)
        layout.addWidget(self.findText)
        layout.addWidget(self.findButton)
        self.setLayout(layout)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    QApplication.setStyle("Fusion")
    myGUI = MainWindow()
    myGUI.show()
    sys.exit(app.exec())
