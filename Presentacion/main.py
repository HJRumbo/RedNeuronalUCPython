import sys
import time

from PyQt5.QtCore import QDir, QAbstractTableModel
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QTableWidgetItem, QTableWidget, \
    QHeaderView, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from Entidad.Patron import Patron
from Logica.MensajeService import MensajeService
from Presentacion.gui_ejemplo import Ui_MainWindow

"""class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.figure = Figure(figsize=(20,12), dpi=80)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        self.layoutvertical = QVBoxLayout(self)
        self.layoutvertical.addWidget(self.canvas)"""

class ejemplo_Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.init_widget()
        self.ui.btnSubirPatrones.clicked.connect(self.subirPatrones)
        self.ui.btnSubirPesos.clicked.connect(self.subirPesos)
        self.ui.btnSubirUmbral.clicked.connect(self.subirUmbral)
        self.ui.btnEntrenar.clicked.connect(self.entrenar)
        self.mensajeService = MensajeService()
        self.arrayMensajes = []
        self.cabeceras = []
        self.fila = 0
        self.entradas = []
        self.yd = 0
        self.pesos = []
        self.contadorIteracion = 0
        self.seguir = 0
        self.patrones = list()
        self.sumatoriaXw = 0
        self.funcion = ""
        self.yr = 0
        self.erroresPatrones = []
        self.errsIt = []
        self.numsIt = []

    def init_widget(self):
        self.figure = Figure(dpi=80, constrained_layout=True)
        self.axis = self.figure.add_subplot(111)
        self.axis.set_title('Iteración Vs Error de iteración')
        self.axis.set_xlabel('Iteración')
        self.axis.set_ylabel('Error de iteración')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layoutvertical = QVBoxLayout(self.ui.widgetEntrenamiento)
        self.layoutvertical.setContentsMargins(0, 0, 0, 0)
        self.layoutvertical.addWidget(self.canvas)

    def subirPesos(self):
        self.deleteAllRows(self.ui.tblWidgetPesos)
        file = self.buscarArchivo()
        if file:
            f = self.mensajeService.consultar(file)
            self.fila = 0
            for line in f.readlines():
                separador = ";"
                datos = line.split(separador)
                self.llenarTablaPesos(datos)
                self.fila += 1
            f.close()

    def llenarTablaPesos(self, datos):
        self.fila = 0
        columna = 0
        self.ui.tblWidgetPesos.setColumnCount(len(datos))
        self.ui.tblWidgetPesos.insertRow(self.fila)
        for i in range(len(datos)):
            self.cabeceras.append("w" + str(i+1) + "1")
            self.ui.tblWidgetPesos.setHorizontalHeaderLabels(self.cabeceras)
            self.ui.tblWidgetPesos.horizontalHeader().setStretchLastSection(True)
            self.ui.tblWidgetPesos.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            celda = QTableWidgetItem(str(datos[i]))
            self.ui.tblWidgetPesos.setItem(self.fila, columna, celda)
            columna += 1
            self.pesos.append(float(datos[i]))

    def subirUmbral(self):
        file = self.buscarArchivo()
        if file:
            f = self.mensajeService.consultar(file)
            for line in f.readlines():
                separador = ";"
                datos = line.split(separador)
                self.ui.txtUmbral.setText(datos[0])
            f.close()

    def entrenar(self):
        self.contadorIteracion = 0
        self.seguir = 'S'
        self.funcion = self.ui.comboFuncionActivacion.currentText()
        while self.contadorIteracion < int(self.ui.txtNumIteracion.text()) and self.seguir == 'S':
            for item in self.patrones:
                self.calcularSoma(item)
                """QMessageBox.question(self, "Mensaje", "Ver", QMessageBox.Ok, QMessageBox.Ok)"""
            self.calcularErrorIteracion()
            self.erroresPatrones.clear()

        if self.seguir == 'S':
            QMessageBox.question(self, "Mensaje", "La red no aprendó, porque no alcanzó el error máximo permitido.", QMessageBox.Ok, QMessageBox.Ok)

    def calcularSoma(self, patron):
        multiXW = 0
        self.sumatoriaXw = 0
        for i in range(len(patron.entradas)):
            multiXW = patron.entradas[i] * self.pesos[i]
            self.sumatoriaXw = self.sumatoriaXw + float(multiXW)
        soma = self.sumatoriaXw - float(self.ui.txtUmbral.text())
        self.ui.txtSoma.setText(str(soma))
        self.funcionActivacion(soma, patron)

    def funcionActivacion(self, soma, patron):

        if self.funcion == "Lineal":
            self.salidaLineal(soma, patron)
        elif self.funcion == "Escalon":
            self.salidaEscalon(soma, patron)
        elif self.funcion == "Sigmoide":
            self.salidaSigmoide(soma, patron)

    def salidaLineal(self, soma, patron):
        print("")

    def salidaEscalon(self, soma, patron):
        if soma >= 0:
            self.yr = 1
        else:
            self.yr = 0

        self.ui.txtYR.setText(str(self.yr))
        self.calcularErrorPatron(self.yr, patron)

    def salidaSigmoide(self, soma, patron):
        print("")

    def calcularErrorPatron(self, yr, patron):
        errorLineal = 0
        errorPatron = 0

        errorLineal = float(patron.yd) - float(yr)

        self.ui.txtErrorLineal.setText(str(errorLineal))

        errorPatron = abs(errorLineal) / 1
        self.ui.txtErrorPatron.setText(str(errorPatron))
        self.erroresPatrones.append(errorPatron)

        self.algoritmoEntrenamiento(errorLineal, patron)

    def algoritmoEntrenamiento(self, errorLineal, patron):
        rataAprendizaje = float(self.ui.txtRataAprendizaje.text())
        nuevosPesos = []
        nuevosPesos.clear()
        c = 0
        i = 0
        j = 0
        while i < len(self.pesos):
            nuevosPesos.append(self.pesos[i]+rataAprendizaje*errorLineal*patron.entradas[i])
            i += 1
        self.pesos.clear()
        self.pesos = []

        self.deleteAllRows(self.ui.tblWidgetPesos)

        self.llenarTablaPesos(nuevosPesos)

        nuevoUmbral = float(self.ui.txtUmbral.text())+rataAprendizaje*errorLineal*1
        self.ui.txtUmbral.setText(str(nuevoUmbral))

    def calcularErrorIteracion(self):
        sumatoriaErroresPatrones = 0
        errorIteracion = 0
        numeroPatrones = len(self.erroresPatrones)

        for i in self.erroresPatrones:
            sumatoriaErroresPatrones = sumatoriaErroresPatrones +i

        errorIteracion = sumatoriaErroresPatrones / numeroPatrones

        self.contadorIteracion += 1
        self.ui.txtIteracionesCumplidas.setText(str(self.contadorIteracion))

        self.ui.lbIteracion.setText(str(self.contadorIteracion))
        self.ui.lbErrorIt.setText(str(errorIteracion))

        self.errsIt.append(errorIteracion)
        self.numsIt.append(self.contadorIteracion)

        self.axis.clear()

        self.axis.plot(self.numsIt, self.errsIt)
        self.axis.set_title('Iteración Vs Error de iteración')
        self.axis.set_xlabel('Número de iteración', fontsize=12)
        self.axis.set_ylabel('Error de iteración', fontsize=12)

        "self.matplotlibWidget.axis.plot(self.contadorIteracion, errorIteracion, color='green', linewidth=2)"
        self.canvas.draw()

        self.canvas.flush_events()
        time.sleep(0.9)

        if errorIteracion <= float(self.ui.txtErrorMaxPermitido.text()):
            QMessageBox.question(self, 'Mensaje', "El error de iteracion: " + str(errorIteracion) + ", es menor o igual al error maximo permitido. " + self.ui.txtErrorMaxPermitido.text(), QMessageBox.Ok, QMessageBox.Ok)
            self.seguir = 'N'


    def guardar(self):
        texto = self.txtMensaje.text()
        QMessageBox.question(self, 'Mensaje', "Escribiste: " + texto, QMessageBox.Ok, QMessageBox.Ok)
        self.etiqueta.setText(texto)
        mensaje = self.mensajeService.guardar(texto)
        QMessageBox.question(self, 'Mensaje', "Escribiste: " + mensaje, QMessageBox.Ok, QMessageBox.Ok)

    def buscarArchivo(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Buscar Archivo', QDir.homePath(),
                                              "Text Files (*.txt)")
        return file

    def subirPatrones(self):

        file = self.buscarArchivo()

        self.deleteAllRows(self.ui.tblWidgetEntSal)

        if file:
            f = self.mensajeService.consultar(file)
            fila = 0
            cabeceras = []
            for line in f.readlines():
                separador = ";"
                datos = line.split(separador)
                columna = 0
                self.ui.tblWidgetEntSal.setColumnCount(len(datos))
                self.ui.tblWidgetEntSal.insertRow(fila)
                self.entradas = []
                for i in range(len(datos)):
                    if i == (len(datos)-1):
                        cabeceras.append("YD")
                        self.yd = float(datos[i])
                    else:
                        cabeceras.append("x" + str(i + 1))
                        self.entradas.append(float(datos[i]))
                    self.ui.tblWidgetEntSal.setHorizontalHeaderLabels(cabeceras)
                    celda = QTableWidgetItem(datos[i])
                    self.ui.tblWidgetEntSal.setItem(fila, columna, celda)
                    columna += 1

                patron = Patron(self.yd, self.entradas)
                self.patrones.append(patron)
                fila += 1
            self.ui.txtNEntradas.setText(str(len(self.entradas)))
            self.ui.txtNSalidas.setText("1")
            self.ui.txtPatrones.setText(str(len(self.patrones)))
            f.close()

    def deleteAllRows(self, table: QTableWidget) -> None:
        # Obtener el modelo de la tabla
        model: QAbstractTableModel = table.model()
        # Remover todos las filas
        model.removeRows(0, model.rowCount())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui_ejemplo = ejemplo_Gui()
    gui_ejemplo.show()
    sys.exit(app.exec_())
