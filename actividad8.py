import json
import os
import re
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt


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
def ventana_principal(eventos, participantes, configuracion):
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
                [sg.Image(key="imagen_evento", size=(200, 200))],
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
            ])],
            [sg.Tab('Configuración', [
                [sg.Checkbox('Validar aforo al agregar participantes', key='-VALIDAR_AFORO-', default=configuracion.get('-VALIDAR_AFORO-', True))],
                [sg.Checkbox('Solicitar imagen', key='-SOLICITAR_IMAGEN-', default=configuracion.get('-SOLICITAR_IMAGEN-', True))],
                [sg.Checkbox('Solicitar registros', key='-SOLICITAR_REGISTROS-', default=configuracion.get('-SOLICITAR_REGISTROS-', True))],
                [sg.Checkbox('Eliminar registros', key='-ELIMINAR_REGISTROS-', default=configuracion.get('-ELIMINAR_REGISTROS-', True))],
                [sg.Button('Guardar')]
            ])],
            [sg.Tab('Análisis', [
                [sg.Text('Participantes que fueron a todos los eventos')],
                [sg.Text('', key='todos_eventos_resultados')],
                [sg.Text('Participantes que fueron al menos a un evento')],
                [sg.Text('', key='al_menos_un_evento_resultados')],
                [sg.Text('Participantes que fueron solo al primer evento')],
                [sg.Text('', key='solo_primer_evento_resultados')]
            ])],
            [sg.Tab('Gráficos', [
                [sg.Button('Mostrar Gráficos', key='mostrar_graficos')],
                [sg.Image(key="grafico1")],
                [sg.Image(key="grafico2")],
                [sg.Image(key="grafico3")],
                [sg.Button("Generar Gráficos", key="Generar_Graficos")]

            ])]
        ])]
    ]
    return sg.Window('Gestión de Evento', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == "Mostrar Gráficos":
            window_graficos = ventana_graficos()
            while True:
                event_graficos, values_graficos = window_graficos.read()
                if event_graficos == sg.WINDOW_CLOSED:
                    break
                if event_graficos == "Generar Gráficos":
                    mostrar_graficos(participantes, eventos)  # Llamar a la función para mostrar los gráficos

            window_graficos.close()

    window.close()


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
    
# Cargar participantes desde un archivo JSON
def cargar_participantes():
    if os.path.exists("participantes.json"):
        try:
            with open("participantes.json", "r") as archivo:
                participantes = json.load(archivo)
                return participantes
        except json.JSONDecodeError:
            sg.popup("Error al leer el archivo participantes.json. Archivo corrupto.")
            return []
    return []  # Si no existe el archivo, retorna una lista vacía


    
# Función para cargar la configuración desde un archivo JSON
def cargar_configuracion():
    if os.path.exists("configuracion.json"):
        try:
            with open("configuracion.json", "r") as archivo:
                configuracion = json.load(archivo)
                return configuracion
        except json.JSONDecodeError:
            sg.popup("Error al leer el archivo de configuración. Archivo corrupto.")
            return {}  # Si el archivo está corrupto, retorna un diccionario vacío
    return {
        '-VALIDAR_AFORO-': True,
        '-SOLICITAR_IMAGEN-': True,
        '-SOLICITAR_REGISTROS-': True,
        '-ELIMINAR_REGISTROS-': True
    }  


# Función para guardar la configuración en un archivo JSON
def guardar_configuracion(configuracion):
    try:
        with open("configuracion.json", "w") as archivo:
            json.dump(configuracion, archivo, indent=4)
        sg.popup("Configuración guardada correctamente.")  # Mensaje de éxito
    except Exception as e:
        sg.popup(f"Error al guardar la configuración: {e}")


def realizar_analisis(participantes, eventos, window, tipo_analisis):
    if not eventos:
        window["-RESULTADOS_ANALISIS-"].update("No hay eventos registrados para realizar el análisis.")
        return

    if not participantes:
        window["-RESULTADOS_ANALISIS-"].update("No hay participantes registrados para realizar el análisis.")
        return

    # Diccionario de asistencias de cada participante
    asistencias = {p["numero_documento"]: [] for p in participantes}

    # Relacionar participantes con eventos
    for participante in participantes:
        for evento in eventos:
            if participante["evento"] == evento["nombre"]:
                asistencias[participante["numero_documento"]].append(evento["nombre"])

    # Cálculos según el tipo de análisis
    todos_eventos = set([e["nombre"] for e in eventos])

    if tipo_analisis == "todos_eventos":
        resultados = [
            p["nombre"] for p in participantes
            if set(asistencias[p["numero_documento"]]) == todos_eventos
        ]
        mensaje = f"Participantes que fueron a todos los eventos:\n{', '.join(resultados) if resultados else 'Ninguno'}"
        window["-RESULTADOS_ANALISIS-"].update(mensaje)

    elif tipo_analisis == "al_menos_un_evento":
        resultados = [
            p["nombre"] for p in participantes
            if len(asistencias[p["numero_documento"]]) > 0
        ]
        mensaje = f"Participantes que fueron al menos a un evento:\n{', '.join(resultados) if resultados else 'Ninguno'}"
        window["-RESULTADOS_ANALISIS_2-"].update(mensaje)

    elif tipo_analisis == "solo_primer_evento":
        primer_evento = eventos[0]["nombre"]
        resultados = [
            p["nombre"] for p in participantes
            if set(asistencias[p["numero_documento"]]) == {primer_evento}
        ]
        mensaje = f"Participantes que fueron solo al primer evento:\n{', '.join(resultados) if resultados else 'Ninguno'}"
        window["-RESULTADOS_ANALISIS_3-"].update(mensaje)

import matplotlib.pyplot as plt

def mostrar_graficos(participantes, eventos):
    if not participantes or not eventos:
        sg.popup("No hay datos suficientes para generar gráficos.")
        return

    # Gráfico 1: Distribución de participantes por tipo de participante
    tipos = [p["tipo_participante"] for p in participantes]
    conteo_tipos = pd.Series(tipos).value_counts()

    plt.figure(figsize=(6, 6))
    conteo_tipos.plot(kind="pie", autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Distribución de participantes por tipo")
    plt.ylabel("")  # Quitar etiqueta del eje Y
    plt.savefig("grafico_tipo_participante.png")
    plt.close()

    # Gráfico 2: Participantes por evento
    eventos_nombres = [p["evento"] for p in participantes]
    conteo_eventos = pd.Series(eventos_nombres).value_counts()

    plt.figure(figsize=(8, 6))
    conteo_eventos.plot(kind="bar", color=plt.cm.tab20.colors)
    plt.title("Participantes por evento")
    plt.xlabel("Evento")
    plt.ylabel("Cantidad de Participantes")
    plt.savefig("grafico_participantes_evento.png")
    plt.close()

    # Gráfico 3: Eventos por fecha
    fechas = [e["fecha"] for e in eventos]
    conteo_fechas = pd.Series(fechas).value_counts()

    plt.figure(figsize=(8, 6))
    conteo_fechas.sort_index().plot(kind="bar", color=plt.cm.viridis.colors)
    plt.title("Eventos por fecha")
    plt.xlabel("Fecha")
    plt.ylabel("Cantidad de Eventos")
    plt.savefig("grafico_eventos_fecha.png")
    plt.close()

    sg.popup("Gráficos generados exitosamente.")



# Función principal
def main():
    eventos = cargar_eventos()  # Cargar eventos previamente guardados
    participantes = cargar_participantes()  # Cargar participantes previamente guardados
    configuracion = cargar_configuracion()  # Cargar configuración antes de mostrar la ventana

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
                window_principal = ventana_principal(eventos, participantes, configuracion)
                while True:
                    event, values = window_principal.read()
                    if event == sg.WINDOW_CLOSED:
                        break

                    # Manejo de eventos
                    if event == "Agregar Evento":
                        # Obtener datos del evento
                        nombre = values["nombre"]
                        fecha = values["fecha"]
                        cupo = values["cupo"]
                        lugar = values["lugar"]
                        hora = values["hora"]
                        imagen = values["imagen"]
                        agregar_evento(eventos, nombre, fecha, cupo, lugar, hora, imagen)
                        
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
                            
                        # Manejo de la pestaña de configuración y el botón "Guardar"
                if event == "Guardar":
                    # Recoger el estado de los checkboxes
                    configuracion = {
                        '-VALIDAR_AFORO-': values["-VALIDAR_AFORO-"],
                        '-SOLICITAR_IMAGEN-': values["-SOLICITAR_IMAGEN-"],
                        '-SOLICITAR_REGISTROS-': values["-SOLICITAR_REGISTROS-"],
                        '-ELIMINAR_REGISTROS-': values["-ELIMINAR_REGISTROS-"]
                    }
                    # Guardar la configuración
                    guardar_configuracion(configuracion)  # Guardar configuración

                            
                # Manejo de la pestaña Análisis
                if event in ['todos_eventos', 'al_menos_un_evento', 'solo_primer_evento']:
                        realizar_analisis(participantes, eventos, window_principal, event)
                        

            window_login.close()

            if event == 'Participantes que fueron a todos los eventos':
                        realizar_analisis(participantes, eventos, window_principal, "todos_eventos")
            elif event == 'Participantes que fueron al menos a un evento':
                        realizar_analisis(participantes, eventos, window_principal, "al_menos_un_evento")
            elif event == 'Participantes que fueron solo al primer evento':
                        realizar_analisis(participantes, eventos, window_principal, "solo_primer_evento")
                        
                        

            if event == "Generar_Graficos":
                    mostrar_graficos(participantes, eventos)
                    # Actualizar los gráficos en la ventana
                    window_principal["grafico1"].update(filename="grafico_tipo_participante.png")
                    window_principal["grafico2"].update(filename="grafico_participantes_evento.png")
                    window_principal["grafico3"].update(filename="grafico_eventos_fecha.png")
                    sg.popup("Gráficos generados correctamente.")
                    



            window_principal.close()
            break
        else:
            sg.popup("Usuario o contraseña incorrectos.")

if __name__ == "__main__":
    main()