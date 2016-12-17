from PySide.QtGui import *
from PySide.QtCore import *
from twilio.rest import TwilioRestClient
import sys

MY_NUMBER = ""
class TriviaWidget(QWidget):
    def __init__(self):
        global MY_NUMBER
        super(TriviaWidget, self).__init__()

        self.initUI()
        self.registrationActive = False
        self.questionActive = False
        self.connectedUsers = 0
        self.userData = {}

        f = open('./account.txt', 'r')
        ACCOUNT_SID = f.readline().strip()
        AUTH_TOKEN = f.readline().strip()
        MY_NUMBER = f.readline().strip()

        self.client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


    def initUI(self):
        layout = QHBoxLayout()
        
        controlBox = QGroupBox("Controls")
        controlLayout = QVBoxLayout()

        regBox = QGroupBox("Registration")
        regLayout = QVBoxLayout()
        self.regButton = QPushButton("Start Registration")
        
        regLayout.addWidget(self.regButton)

        regBox.setLayout(regLayout)

        controlLayout.addWidget(regBox)

        questionBox = QGroupBox("Question")
        questionLayout = QFormLayout()

        self.answers = QComboBox()
        self.answers.addItems(["A","B","C","D","E","Other"])
        self.otherAnswer = QLineEdit()
        self.otherAnswer.setEnabled(False)
        self.questionButton = QPushButton("Start Question")

        questionLayout.addRow("Answer:", self.answers)
        questionLayout.addRow("Other Answer:", self.otherAnswer)
        questionLayout.addRow("", self.questionButton)

        questionBox.setLayout(questionLayout)
        controlLayout.addWidget(questionBox)
        
        winnerBox = QGroupBox("Choose Winners")
        winnerLayout = QFormLayout()

        self.numWinnersBox = QSpinBox()
        self.notifyWinnersButton = QPushButton("Notify Winners")
        winnerLayout.addRow("Number of Winners:", self.numWinnersBox)
        winnerLayout.addRow("", self.notifyWinnersButton)

        winnerBox.setLayout(winnerLayout)

        controlLayout.addWidget(winnerBox)

        exitBox = QGroupBox("Exit")
        exitLayout = QVBoxLayout()
        self.exitButton = QPushButton("Exit Application")
        
        exitLayout.addWidget(self.exitButton)

        exitBox.setLayout(exitLayout)

        controlLayout.addWidget(exitBox)

        controlBox.setLayout(controlLayout)
        layout.addWidget(controlBox)

        tableLayout = QVBoxLayout()
        tableBox = QGroupBox("Participants")

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Phone Number","Score","Current Answer"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        tableLayout.addWidget(self.table)
        tableBox.setLayout(tableLayout)
        layout.addWidget(tableBox)

        self.setLayout(layout)

        self.regButton.setCheckable(True)
        self.questionButton.setCheckable(True)

        self.regButton.toggled.connect(self.toggleRegistration)
        self.questionButton.toggled.connect(self.toggleQuestion)
        self.exitButton.clicked.connect(self.quit)

        self.notifyWinnersButton.clicked.connect(self.sendResults)

        self.answers.currentIndexChanged.connect(self.answerChanged)


    @Slot(bool)
    def toggleRegistration(self,start):
        if(start):
            self.regButton.setText("Stop Registration")
            self.questionButton.setEnabled(False)
            self.notifyWinnersButton.setEnabled(False)
            self.registrationActive = True
        else:
            self.regButton.setText("Start Registration")
            self.notifyWinnersButton.setEnabled(True)
            self.questionButton.setEnabled(True)
            self.registrationActive = False

    @Slot(bool)
    def toggleQuestion(self,start):
        if(start):
            self.questionButton.setText("End Question")
            self.regButton.setEnabled(False)
            self.notifyWinnersButton.setEnabled(False)
            self.answers.setEnabled(False)
            self.otherAnswer.setEnabled(False)
            self.questionActive = True
        else:
            self.scoreQuestion()
            self.questionButton.setText("Start Question")
            self.regButton.setEnabled(True)
            self.notifyWinnersButton.setEnabled(True)
            self.answers.setEnabled(True)
            self.otherAnswer.setEnabled(self.answers.currentText() == "Other")
            self.questionActive = False

    def registerUser(self, user):
        if(self.registrationActive):
            self.connectedUsers += 1
            self.userData[user] = dict()
            self.userData[user]["id"] = self.connectedUsers
            self.userData[user]["answer"] = ""
            self.userData[user]["score"] = 0

            self.table.setRowCount(self.connectedUsers)

            phoneNumber = QTableWidgetItem(user)
            score = QTableWidgetItem(str(self.userData[user]["score"]))
            self.table.setItem(self.connectedUsers-1, 0, phoneNumber)
            self.table.setItem(self.connectedUsers-1, 1, score) 

    def putAnswer(self, user, answer):
        if(self.questionActive):
            self.userData[user]["answer"] = answer
            answerItem = QTableWidgetItem(answer)
            self.table.setItem(self.userData[user]["id"]-1, 2, answerItem)

    def scoreQuestion(self):
        correctAnswer = self.answers.currentText()
        if correctAnswer == "Other":
            correctAnswer = self.otherAnswer.text()
        for user in self.userData:
           userAnswer = self.userData[user]["answer"]
           if(userAnswer.lower().strip() == correctAnswer.lower().strip()):
               self.userData[user]["score"] += 1
               score = QTableWidgetItem(str(self.userData[user]["score"]))
               self.table.setItem(self.userData[user]["id"] - 1, 1, score)
               self.sendCorrectAnswerMessage(user)
           else:
               self.sendIncorrectAnswerMessage(user, userAnswer, correctAnswer)
           self.table.item(self.userData[user]["id"] - 1, 2).setText("")
           userAnswer = self.userData[user]["answer"] = ""

    def sendCorrectAnswerMessage(self, user):
        contents = "Congratulations, you had the correct answer!\n"\
        +"You have answered " + str(self.userData[user]["score"])\
        +" questions correctly."
        self.client.messages.create(to=user, from_=MY_NUMBER, body=contents)

    def sendIncorrectAnswerMessage(self, destination, userAnswer, correctAnswer):
        contents = "Sorry, that was not the correct answer.\n"\
        +"Your answer was: " + userAnswer + ".\n"\
        +"The correct answer was: " + correctAnswer + ".\n"\
        +"You have answered " + str(self.userData[destination]["score"])\
        +" questions correctly."
        self.client.messages.create(to=destination, from_=MY_NUMBER, body=contents)

    def sendResults(self):
        numWinners = int(self.numWinnersBox.cleanText())
        leaderboard = sorted(self.userData, key = lambda k: self.userData[k]["score"], reverse=True)
        for i in range(0,min(numWinners, self.connectedUsers)):
            destination = leaderboard[i]
            contents = "Congratulations, you won Lake Orion Swim and Dive Trivia!\n\n"\
            + "Come to the Swim and Dive Office and present this text "\
            + "to claim your prize.\n\nThanks for playing, and join us again next time!"
            self.client.messages.create(to=destination, from_=MY_NUMBER, body=contents)
        for i in range(numWinners, self.connectedUsers):
            destination = leaderboard[i]
            contents = "Sorry, you did not win Lake Orion Swim and Dive Trivia.\n\n"\
            + "Thanks for playing, and join us again next time!"
            self.client.messages.create(to=destination, from_=MY_NUMBER, body=contents)


    def answerChanged(self):
        self.otherAnswer.setEnabled(self.answers.currentText() == "Other")
        if self.answers.currentText != "Other":
            self.otherAnswer.clear()

    def quit(self):
        QApplication.quit()

