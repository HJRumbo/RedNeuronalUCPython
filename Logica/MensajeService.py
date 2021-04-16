from Datos.MensajeRepository import MensajeRepository


class MensajeService:
    mensajeRepository = MensajeRepository()
    arrayMensajes = []

    def guardar(self, mensaje):
        try:
            self.mensajeRepository.guardar(mensaje)
            return "Mensaje guardado correctamente. "
        except:
            return "Error al guardar el mensaje. "

    def consultar(self, file):
        f = self.mensajeRepository.consultar(file)
        return f