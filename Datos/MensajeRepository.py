import os.path as path


class MensajeRepository:

    file = "mensaje.txt"
    arrayMensajes = []

    def guardar(self, mensaje):
        f = open(self.file, 'a')
        f.write(
            mensaje)
        f.write("\n")
        f.close()

    def consultar(self, file):
        if path.exists(file):
            f = open(file, 'r')
            return f
        else:
            return None