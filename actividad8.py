import PySimpleGUI as sg
import json
import os
import re
import pandas as pd

# Crear archivo usuarios.txt
with open("usuarios.txt", "w") as archivo:
    archivo.write("admin,1234\n") 
    archivo.write("user1,password1\n") 
    archivo.write("user2,password2\n") 
    archivo.write("edgar,1234\n") 
    archivo.write("laura,9876\n")
print("Archivo 'usuarios.txt' creado con éxito.")

# Validar usuario
def validar_usuario(usuario, contraseña):
    try:
        with open("usuarios.txt", "r") as archivo:
            for linea in archivo:
                local_user, password_file = linea.strip().split(",")
                if usuario == local_user and contraseña == password_file:
                    return True
        return False
    except FileNotFoundError:
        sg.popup("Error: El archivo 'usuarios.txt' no existe.")
        return False

# Ventana de login
def ventana_login():
    layout = [
        [sg.Text("Usuario"), sg.Input(key="usuario")],
        [sg.Text("Contraseña"), sg.Input(password_char="*", key="contraseña")],
        [sg.Button("Login"), sg.Button("Salir")]
    ]
    return sg.Window("Login", layout)

# Diseño de la ventana principal con pestañas
def ventana_principal(eventos, participantes):
    layout = [
        [sg.TabGroup([  
            [sg.Tab('Eventos', [
                [sg.Text("Nombre del evento: "), sg.Input(key="nombre")],
                [sg.Text("Fecha (día/mes/año): "), sg.Input(key="fecha")],
                [sg.Text("Cupo: "), sg.Input(key="cupo")],
                [sg.Text("Lugar: "), sg.Input(key="lugar")],
                [sg.Text("Hora (23:59): "), sg.Input(key="hora")],
                [sg.Text("Imagen: "), sg.Input(key="imagen"), sg.FileBrowse("Seleccionar")],
                [sg.Button("Agregar Evento"), sg.Button("Modificar Evento"), sg.Button("Eliminar Evento")],
                [sg.Text("Eventos guardados: ")],
                [sg.Listbox(values=[e["nombre"] for e in eventos], size=(50, 10), key="lista_eventos")],
                [sg.Image(key="imagen_evento", size=(200, 200))]
            ])],
            [sg.Tab('Participantes', [
                [sg.Text("Evento"), sg.Combo([e["nombre"] for e in eventos], key="evento", readonly=True)],
                [sg.Text("Nombre"), sg.Input(key="nombre_participante")],
                [sg.Text("Tipo Documento"), sg.Combo(["CC", "TI", "Pasaporte"], key="tipo_documento")],
                [sg.Text("Número Documento"), sg.Input(key="numero_documento")],
                [sg.Text("Teléfono"), sg.Input(key="telefono")],
                [sg.Text("Dirección"), sg.Input(key="direccion")],
                [sg.Text("Tipo Participante"), sg.Combo(["Estudiante", "Profesor", "Colaborador"], key="tipo_participante")],
                [sg.Text("Imagen"), sg.Input(key="imagen_participante"), sg.FileBrowse("Seleccionar imagen")],
                [sg.Button("Agregar Participante"), sg.Button("Modificar Participante"), sg.Button("Eliminar Participante")],
                [sg.Listbox(values=[p["nombre"] for p in participantes], size=(50, 10), key="lista_participantes")]
            ])]
        ])]
    ]
    return sg.Window('Aplicación de Gestión de Eventos y Participantes', layout)

# Cargar eventos desde JSON
def cargar_eventos():
    if os.path.exists("eventos.json"):
        try:
            with open("eventos.json", "r") as archivo:
                eventos = json.load(archivo)
                return eventos
        except json.JSONDecodeError:
            sg.popup("Error al leer el archivo JSON. Archivo corrupto.")
            return []
    return []

# Guardar eventos en JSON
def guardar_eventos(eventos):
    try:
        with open("eventos.json", "w") as archivo:
            json.dump(eventos, archivo, indent=4)
    except Exception as e:
        sg.popup(f"Error al guardar los eventos: {e}")

# Guardar eventos en CSV
def guardar_csv(eventos):
    try:
        df = pd.DataFrame(eventos)
        df.to_csv("eventos.csv", index=False)
        sg.popup("Eventos exportados a eventos.csv exitosamente.")
    except Exception as e:
        sg.popup(f"Error al exportar los eventos a CSV: {e}")

# Validar hora en formato 24 horas
def validar_hora(hora):
    if not re.match(r"^\d{2}:\d{2}$", hora):
        raise ValueError("La hora debe estar en formato HH:MM (24 horas).")

# Agregar evento
def agregar_evento(eventos, nombre, fecha, cupo, lugar, hora, imagen):
    try: 
        if not all([nombre, fecha, lugar, cupo, hora, imagen]):
            raise ValueError("Todos los campos son obligatorios.")
        if nombre in [e['nombre'] for e in eventos]:
            raise ValueError("Este nombre de evento ya existe.")
        cupo = int(cupo)
        validar_hora(hora)
        if not os.path.isfile(imagen):
            raise ValueError("La imagen seleccionada no existe.")
        nuevo_evento = {
            "nombre": nombre,
            "fecha": fecha,
            "cupo": cupo,
            "lugar": lugar,
            "hora": hora,
            "imagen": imagen
        }
        eventos.append(nuevo_evento)
        guardar_eventos(eventos)
        guardar_csv(eventos)  # Guarda automáticamente en CSV
        return True, "Evento guardado con éxito."
    except ValueError as e:
        return False, str(e)
    except FileNotFoundError as e:
        return False, str(e)
    
# Modificar evento existente
def modificar_evento(eventos, nombre_seleccionado, nuevos_datos):
    try:
        if not nombre_seleccionado:
            raise ValueError("Debe seleccionar un evento para modificar.")
        
        # Validar datos obligatorios
        if not all(nuevos_datos.values()):
            raise ValueError("Todos los campos son obligatorios.")
        
        # Validar que el nombre sea único (excepto para el propio evento)
        for evento in eventos:
            if evento["nombre"] == nuevos_datos["nombre"] and evento["nombre"] != nombre_seleccionado:
                raise ValueError("Ya existe un evento con este nombre.")
        
        # Validar que el cupo sea numérico
        nuevos_datos["cupo"] = int(nuevos_datos["cupo"])

        # Validar formato de hora
        validar_hora(nuevos_datos["hora"])

        # Validar que la imagen exista
        if not os.path.isfile(nuevos_datos["imagen"]):
            raise FileNotFoundError("La imagen seleccionada no existe.")
        
        # Modificar el evento
        for evento in eventos:
            if evento["nombre"] == nombre_seleccionado:
                evento.update(nuevos_datos)
                guardar_eventos(eventos)
                guardar_csv(eventos)
                return True, "Evento modificado exitosamente."

        return False, "No se encontró el evento seleccionado."
    
    except ValueError as e:
        return False, str(e)
    except FileNotFoundError as e:
        return False, str(e)

# Función para eliminar un evento
def eliminar_evento(eventos, nombre_seleccionado):
    try:
        if not nombre_seleccionado:
            raise ValueError("Debe seleccionar un evento para eliminar.")
        
        # Buscar y eliminar el evento
        eventos[:] = [evento for evento in eventos if evento["nombre"] != nombre_seleccionado]
        guardar_eventos(eventos)
        guardar_csv(eventos)
        return True, "Evento eliminado exitosamente."
    
    except Exception as e:
        return False, f"Error al eliminar el evento: {e}"


# actualizar la lista de eventos
def actualizar_interfaz_eventos(eventos, window):

    nombres_eventos = [e["nombre"] for e in eventos]
    # Actualizar pestaña de eventos
    window["lista_eventos"].update(values=nombres_eventos)
    # Actualizar pestaña de participantes
    window["evento"].update(values=nombres_eventos)
    
    
def guardar_participantes(participantes):
    """
    Guarda la lista de participantes en un archivo JSON.
    """
    try:
        with open("participantes.json", "w") as archivo:
            json.dump(participantes, archivo, indent=4)
    except Exception as e:
        sg.popup(f"Error al guardar los participantes: {e}")
        

# Agregar participante
def agregar_participante(participantes, eventos, datos):
    try:
        # Validar campos obligatorios
        if not all(datos.values()):
            raise ValueError("Todos los campos son obligatorios.")
        
        # Validar que el número de documento sea numérico
        if not datos["numero_documento"].isdigit():
            raise ValueError("El número de documento debe ser numérico.")
        
        # Validar unicidad del número de documento
        for participante in participantes:
            if participante["numero_documento"] == datos["numero_documento"]:
                raise ValueError("Ya existe un participante con este número de documento.")
        
        # Validar que el evento exista
        evento_seleccionado = next((e for e in eventos if e["nombre"] == datos["evento"]), None)
        if not evento_seleccionado:
            raise ValueError("El evento seleccionado no existe.")
        
        # Validar que no se exceda el cupo del evento
        participantes_asociados = [p for p in participantes if p["evento"] == datos["evento"]]
        if len(participantes_asociados) >= evento_seleccionado["cupo"]:
            raise ValueError("El cupo del evento ha sido excedido.")
        
        # Validar que la imagen exista
        if not os.path.isfile(datos["imagen"]):
            raise FileNotFoundError("La imagen seleccionada no existe.")
        
        # Agregar participante
        participantes.append(datos)
        guardar_participantes(participantes)
        return True, "Participante agregado exitosamente."
    
    except ValueError as e:
        return False, str(e)
    except FileNotFoundError as e:
        return False, str(e)
    
# Modificar participante
def modificar_participante(participantes, numero_documento_seleccionado, nuevos_datos):
    try:
        if not numero_documento_seleccionado:
            raise ValueError("Debe seleccionar un participante para modificar.")
        
        # Validar campos obligatorios
        if not all(nuevos_datos.values()):
            raise ValueError("Todos los campos son obligatorios.")
        
        # Validar que el número de documento sea numérico
        if not nuevos_datos["numero_documento"].isdigit():
            raise ValueError("El número de documento debe ser numérico.")
        
        # Validar que la imagen exista
        if not os.path.isfile(nuevos_datos["imagen"]):
            raise FileNotFoundError("La imagen seleccionada no existe.")
        
        # Modificar el participante
        for participante in participantes:
            if participante["numero_documento"] == numero_documento_seleccionado:
                participante.update(nuevos_datos)
                guardar_participantes(participantes)
                return True, "Participante modificado exitosamente."
        
        return False, "No se encontró el participante seleccionado."
    
    except ValueError as e:
        return False, str(e)
    except FileNotFoundError as e:
        return False, str(e)

# Eliminar participante
def eliminar_participante(participantes, numero_documento_seleccionado):
    try:
        if not numero_documento_seleccionado:
            raise ValueError("Debe seleccionar un participante para eliminar.")
        
        # Eliminar el participante
        for participante in participantes:
            if participante["numero_documento"] == numero_documento_seleccionado:
                participantes.remove(participante)
                guardar_participantes(participantes)
                return True, "Participante eliminado exitosamente."
        
        return False, "No se encontró el participante seleccionado."
    
    except ValueError as e:
        return False, str(e)
    
def actualizar_interfaz_participantes(participantes, window):
    """
    Actualiza la lista de participantes en la interfaz de la pestaña de Participantes.
    """
    nombres_participantes = [p["nombre"] for p in participantes]
    window["lista_participantes"].update(values=nombres_participantes)
    
    
# Flujo principal para la pestaña de Participantes
def gestionar_participantes(participantes, eventos, window):
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Salir":
            break

        # Agregar participante
        if event == "Agregar Participante":
            datos = {
                "evento": values["evento"],
                "nombre": values["nombre_participante"],
                "tipo_documento": values["tipo_documento"],
                "numero_documento": values["numero_documento"],
                "telefono": values["telefono"],
                "direccion": values["direccion"],
                "tipo_participante": values["tipo_participante"],
                "imagen": values["imagen_participante"]
            }
            exito, mensaje = agregar_participante(participantes, eventos, datos)
            sg.popup(mensaje)
            if exito:
                # Actualizar la lista de participantes
                actualizar_interfaz_participantes(participantes, window)

        # Modificar participante
        elif event == "Modificar Participante":
            seleccionado = values["lista_participantes"]
            if seleccionado:
                numero_documento_seleccionado = seleccionado[0]
                nuevos_datos = {
                    "evento": values["evento"],
                    "nombre": values["nombre_participante"],
                    "tipo_documento": values["tipo_documento"],
                    "numero_documento": values["numero_documento"],
                    "telefono": values["telefono"],
                    "direccion": values["direccion"],
                    "tipo_participante": values["tipo_participante"],
                    "imagen": values["imagen_participante"]
                }
                exito, mensaje = modificar_participante(participantes, numero_documento_seleccionado, nuevos_datos)
                sg.popup(mensaje)
                if exito:
                    # Actualizar la lista de participantes
                    actualizar_interfaz_participantes(participantes, window)

        # Eliminar participante
        elif event == "Eliminar Participante":
            seleccionado = values["lista_participantes"]
            if seleccionado:
                numero_documento_seleccionado = seleccionado[0]
                exito, mensaje = eliminar_participante(participantes, numero_documento_seleccionado)
                sg.popup(mensaje)
                if exito:
                    # Actualizar la lista de participantes
                    actualizar_interfaz_participantes(participantes, window)

    window.close()


# Función principal 
def main():
    eventos = cargar_eventos()
    participantes = []  

    # Mostrar ventana de login
    window_login = ventana_login()
    while True:
        event, values = window_login.read()
        if event == sg.WINDOW_CLOSED or event == 'Salir':
            break
        if event == 'Login':
            usuario = values['usuario']
            contraseña = values['contraseña']
            if validar_usuario(usuario, contraseña):
                window_login.close()
                window_principal = ventana_principal(eventos, participantes)
                while True:
                    event, values = window_principal.read()
                    if event == sg.WINDOW_CLOSED:
                        break
                    # Lógica para manejar los botones y eventos
                    if event == "Agregar Evento":
                        # Obtener datos del evento
                        nombre = values["nombre"]
                        fecha = values["fecha"]
                        cupo = values["cupo"]
                        lugar = values["lugar"]
                        hora = values["hora"]
                        imagen = values["imagen"]
                        exito, mensaje = agregar_evento(eventos, nombre, fecha, cupo, lugar, hora, imagen)
                        sg.popup(mensaje)
                    elif event == "Modificar Evento":
                        # Obtener datos del evento seleccionado y modificar
                        seleccionado = values["lista_eventos"]
                        if seleccionado:
                            datos_nuevos = {
                                "nombre": values["nombre"],
                                "fecha": values["fecha"],
                                "cupo": values["cupo"],
                                "lugar": values["lugar"],
                                "hora": values["hora"],
                                "imagen": values["imagen"]
                            }
                            exito, mensaje = modificar_evento(eventos, seleccionado[0], datos_nuevos)
                            sg.popup(mensaje)
                            if exito:
                                window_principal["lista_eventos"].update([e["nombre"] for e in eventos])
                    elif event == "Eliminar Evento":
                        seleccionado = values["lista_eventos"]
                        if seleccionado:
                            exito, mensaje = eliminar_evento(eventos, seleccionado[0])
                            sg.popup(mensaje)
                            if exito:
                                window_principal["lista_eventos"].update([e["nombre"] for e in eventos])
                    
                    # Agregar participante
                    if event == "Agregar Participante":
                        evento = values["evento"]
                        nombre_participante = values["nombre_participante"]
                        tipo_documento = values["tipo_documento"]
                        numero_documento = values["numero_documento"]
                        telefono = values["telefono"]
                        direccion = values["direccion"]
                        tipo_participante = values["tipo_participante"]
                        imagen_participante = values["imagen_participante"]
                        
                        datos = {
                            "evento": values["evento"],
                            "nombre": values["nombre_participante"],
                            "tipo_documento": values["tipo_documento"],
                            "numero_documento": values["numero_documento"],
                            "telefono": values["telefono"],
                            "direccion": values["direccion"],
                            "tipo_participante": values["tipo_participante"],
                            "imagen": values["imagen_participante"]
                        }
                        exito, mensaje = agregar_participante(participantes, eventos, datos)
                        sg.popup(mensaje)
                        if exito:
                            window_principal["lista_participantes"].update([p["nombre"] for p in participantes])

                    # Modificar participante
                    elif event == "Modificar Participante":
                        seleccionado = values["lista_participantes"]
                        if seleccionado:
                            nombre_seleccionado = seleccionado[0]
                            nuevos_datos = {
                                "evento": values["evento"],
                                "nombre": values["nombre_participante"],
                                "tipo_documento": values["tipo_documento"],
                                "numero_documento": values["numero_documento"],
                                "telefono": values["telefono"],
                                "direccion": values["direccion"],
                                "tipo_participante": values["tipo_participante"],
                                "imagen": values["imagen_participante"]
                            }
                            for participante in participantes:
                                if participante["nombre"] == nombre_seleccionado:
                                    participante.update(nuevos_datos)
                                    sg.popup(f"Participante {nombre_seleccionado} modificado exitosamente.")
                                    window_principal["lista_participantes"].update([p["nombre"] for p in participantes])
                                    break

                    # Eliminar participante
                    elif event == "Eliminar Participante":
                        seleccionado = values["lista_participantes"]
                        if seleccionado:
                            nombre_seleccionado = seleccionado[0]
                            participantes = [p for p in participantes if p["nombre"] != nombre_seleccionado]
                            sg.popup(f"Participante {nombre_seleccionado} eliminado correctamente.")
                            window_principal["lista_participantes"].update([p["nombre"] for p in participantes])

                window_principal.close()
                break
            else:
                sg.popup("Usuario o contraseña incorrectos.")
    window_login.close()

if __name__ == "__main__":
    main()
    
    