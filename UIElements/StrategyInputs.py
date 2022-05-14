# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QComboBox, QFileDialog, QWidget
from Managers.StrategyManager import StrategyManager
from UIElements.ExtendedComboBox import ExtendedComboBox


class StrategyInputBox(QWidget):

    def setupUi(self, Dialog, strategy_to_execute):
        self.strategyInputTracker = {}
        Dialog.setObjectName("Dialog")
        Dialog.resize(578, 441)
        self.Dialog=Dialog
        self.strategy = strategy_to_execute
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.formLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.mandatoryInputs = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.mandatoryInputs.setContentsMargins(0, 0, 0, 0)
        self.mandatoryInputs.setObjectName("mandatoryInputs")
        self.startTimeLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.startTimeLabel.setObjectName("startTimeLabel")
        self.brokerSelectorLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.brokerSelectorLabel.setObjectName("brokerSelectorLabel")
        self.mandatoryInputs.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.startTimeLabel)
        # self.startTimeSelect = QtWidgets.QTimeEdit(self.formLayoutWidget)
        # self.startTimeSelect.setObjectName("startTimeSelect")
        # self.mandatoryInputs.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.startTimeSelect)
        # self.endTimeLabel = QtWidgets.QLabel(self.formLayoutWidget)
        # self.endTimeLabel.setObjectName("endTimeLabel")
        # self.mandatoryInputs.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.endTimeLabel)
        # self.endTimeSelect = QtWidgets.QTimeEdit(self.formLayoutWidget)
        # self.endTimeSelect.setObjectName("endTimeSelect")
        # self.mandatoryInputs.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.endTimeSelect)
        # self.maxProfitLabel = QtWidgets.QLabel(self.formLayoutWidget)
        # self.maxProfitLabel.setObjectName("maxProfitLabel")
        # self.mandatoryInputs.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.maxProfitLabel)
        # self.maxProfitSpinner = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.brokerSelector = QComboBox(self.formLayoutWidget)
        from Managers.BrokerManager import BrokerManager
        brokers = list(BrokerManager.get_instance().alias_brokers.keys())
        self.brokerSelector.addItems(brokers)
        # self.brokerSelector.setEditable(True)
        self.brokerSelector.setInsertPolicy(QComboBox.NoInsert)
        self.mandatoryInputs.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.brokerSelectorLabel)
        self.mandatoryInputs.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.brokerSelector)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.splitter)
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.strategyInputs = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.strategyInputs.setContentsMargins(0, 0, 0, 0)
        self.strategyInputs.setObjectName("strategyInputs")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 234, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 0, 1, 1)
        self.strategyStartButton = QtWidgets.QPushButton(Dialog)
        self.strategyStartButton.setObjectName("strategyStartButton")
        self.bulkStart = QtWidgets.QPushButton(Dialog)
        self.bulkStart.setObjectName("bulkStart")
        self.gridLayout_2.addWidget(self.strategyStartButton, 0, 2, 1, 1)
        self.gridLayout_2.addWidget(self.bulkStart, 0, 1, 1, 1)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout_2.addWidget(self.cancelButton, 0, 3, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 0, 1, 1)
        self.retranslateUi(Dialog)
        self.strategyStartButton.clicked.connect(self.startStrategyClicked)
        self.bulkStart.clicked.connect(self.bulkStartClicked)
        self.cancelButton.clicked.connect(self.Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def bulkStartClicked(self, Dialog):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            import pandas as pd
            df = pd.read_csv(fileName, dtype=str)
            records = df.to_dict('records')
            for record in records:
                self.startStrategyForInputs(inputs=record)
            self.Dialog.close()

    def startStrategyForInputs(self, inputs):
        strategy_to_start = self.strategy()
        StrategyManager.get_instance().add_strategy(strategy=strategy_to_start)
        StrategyManager.get_instance().start_strategy(strategy=strategy_to_start, inputs=inputs)

    def startStrategyClicked(self,Dialog):
        broker_for_strategy = self.brokerSelector.currentText()
        inputs = {}
        for input, value in self.strategyInputTracker.items():
            if  isinstance(value, QComboBox):
                inputs[input] = value.currentText()
            else:
                inputs[input] = value.text()
        inputs['broker_alias'] = broker_for_strategy
        self.startStrategyForInputs(inputs)
        self.Dialog.close()

    def addAttr(self, label, input):
        inputextend = QtWidgets.QLineEdit()
        inputextend.setText(str(input))
        self.strategyInputTracker[label]=inputextend
        self.strategyInputs.addRow(label,inputextend)

    def addAttrList(self, label, input):
        inputExtend = ExtendedComboBox(self.formLayoutWidget)
        inputExtend.addItems(input)
        self.strategyInputTracker[label] = inputExtend
        self.strategyInputs.addRow(label, inputExtend)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.strategyStartButton.setText(_translate("Dialog", "Start"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))
        self.brokerSelectorLabel.setText(_translate("Dialog", "Broker "))
        self.bulkStart.setText(_translate("Dialog", "Bulk Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = StrategyInputBox()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
