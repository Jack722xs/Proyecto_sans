import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk, ImageSequence
import os
import sys
import pygame
import cv2
import threading
import time

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Carpeta temporal de PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def obtener_ruta_recurso(ruta_relativa):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

def cargar_fuente_undertale():
    """Carga la fuente con el estilo exacto de Undertale"""
    try:
        # Buscar la fuente PixelOperator-Bold.ttf
        rutas_posibles = [
            obtener_ruta_recurso("determination.ttf"),
            obtener_ruta_recurso("fonts/determination.ttf")
        ]
        
        for ruta_fuente in rutas_posibles:
            if os.path.exists(ruta_fuente):
                print(f"Fuente encontrada en: {ruta_fuente}")
                # Crear la fuente más grande para el efecto Undertale
                try:
                    fuente_personalizada = font.Font(file=ruta_fuente, size=24)
                    return fuente_personalizada
                except Exception as e:
                    print(f"Error creando fuente desde archivo: {e}")
                    continue
        
        print("Fuente PixelOperator-Bold.ttf no encontrada")
        
        # Fuente Fixedsys es la que más se parece a Undertale
        try:
            fuente_fixedsys = font.Font(family="Fixedsys", size=20, weight="bold")
            print("Usando fuente Fixedsys (estilo Undertale)")
            return fuente_fixedsys
        except:
            pass
            
        # Alternativas si Fixedsys no está disponible
        fuentes_alternativas = [
            ("Terminal", 18, "bold"),
            ("MS Sans Serif", 16, "bold"), 
            ("Courier New", 16, "bold"),
            ("Consolas", 16, "bold")
        ]
        
        for fuente_info in fuentes_alternativas:
            try:
                fuente_respaldo = font.Font(family=fuente_info[0], size=fuente_info[1], weight=fuente_info[2])
                print(f"Usando fuente alternativa: {fuente_info[0]}")
                return fuente_respaldo
            except:
                continue
                
        # Última opción
        return font.Font(family="Courier", size=16, weight="bold")
        
    except Exception as e:
        print(f"Error general cargando fuente: {e}")
        return font.Font(family="Courier", size=16, weight="bold")

# Variables globales para el video
video_cap = None
video_label = None
reproduciendo_video = False
label_texto_gif = None
hilo_video = None
frames_gif_cache = []  # Cache para los frames del GIF
eliminando_texto = False  # Bandera para controlar la eliminación del texto

def reproducir_video_hilo():
    """Reproduce el video en un hilo separado para mejor rendimiento"""
    global video_cap, reproduciendo_video
    
    try:
        video_path = obtener_ruta_recurso("video/deltarune Battle Meme Layout - Ordayne (720p, h264).mp4")
        video_cap = cv2.VideoCapture(video_path)
        
        if not video_cap.isOpened():
            print("No se pudo abrir el video")
            return
            
        # Configurar buffer del video para mejor rendimiento
        video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        while reproduciendo_video:
            ret, frame = video_cap.read()
            if ret:
                # Redimensionar el frame al tamaño de la ventana
                frame = cv2.resize(frame, (800, 400))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convertir a formato que tkinter puede usar
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(img)
                
                # Actualizar en el hilo principal
                if video_label and reproduciendo_video:
                    try:
                        video_label.config(image=img_tk)
                        video_label.image = img_tk
                    except:
                        break
                
                # Control de FPS más eficiente
                time.sleep(1/60)  # ~30 FPS
            else:
                # Video terminado, programar eliminación del texto
                if not eliminando_texto:
                    ventana.after(0, iniciar_eliminacion_texto)
                # Reiniciar video
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
    except Exception as e:
        print(f"Error en hilo de video: {e}")

def reproducir_video_fondo():
    """Inicia la reproducción del video de fondo"""
    global video_label, reproduciendo_video, hilo_video
    
    try:
        reproduciendo_video = True
        
        # Reproducir el audio del video (la música de Deltarune)
        try:
            audio_video_path = obtener_ruta_recurso("video/deltarune Battle Meme Layout - Ordayne.mp3")
            pygame.mixer.music.load(audio_video_path)
            pygame.mixer.music.play()
            print("Reproduciendo audio del video")
        except Exception as e:
            print(f"Error cargando audio del video: {e}")
        
        # Crear label para el video de fondo
        video_label = tk.Label(ventana, bg="#000000")
        video_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Iniciar hilo del video
        hilo_video = threading.Thread(target=reproducir_video_hilo, daemon=True)
        hilo_video.start()
        
    except Exception as e:
        print(f"Error reproduciendo video: {e}")

def iniciar_eliminacion_texto():
    """Inicia el proceso de eliminación del texto"""
    global eliminando_texto
    if not eliminando_texto:
        eliminando_texto = True
        ventana.after(2000, eliminar_texto_final)

def eliminar_texto_final():
    """Elimina el texto 'LO LOGRASTE' gradualmente"""
    global label_texto_gif, eliminando_texto
    if label_texto_gif and eliminando_texto:
        texto_actual = label_texto_gif.cget("text")
        if len(texto_actual) > 0:
            # Eliminar letra por letra con efecto
            nuevo_texto = texto_actual[:-1]
            label_texto_gif.config(text=nuevo_texto)
            # Programar siguiente eliminación
            ventana.after(100, eliminar_texto_final)
        else:
            eliminando_texto = False
            print("Texto 'LO LOGRASTE' eliminado completamente")

def detener_video():
    """Detiene la reproducción del video"""
    global video_cap, video_label, reproduciendo_video, hilo_video
    reproduciendo_video = False
    
    if hilo_video and hilo_video.is_alive():
        hilo_video.join(timeout=1)
    
    if video_cap:
        video_cap.release()
    if video_label:
        video_label.destroy()

def precargar_gif():
    """Precarga los frames del GIF para mejor rendimiento"""
    global frames_gif_cache
    try:
        gif_path = obtener_ruta_recurso("images/chicos-estoy.gif")
        pil_image = Image.open(gif_path)
        
        frames_gif_cache = []
        for frame in ImageSequence.Iterator(pil_image):
            frame = frame.convert("RGBA")
            # Redimensionar el frame del GIF
            width, height = frame.size
            new_width = int(width * 0.7)
            new_height = int(height * 0.7)
            frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
            frames_gif_cache.append(ImageTk.PhotoImage(frame))
        
        print(f"GIF precargado: {len(frames_gif_cache)} frames")
        
    except Exception as e:
        print(f"Error precargando GIF: {e}")

ventana = tk.Tk()
ventana.title("Sans")
ventana.geometry("800x600")
ventana.configure(bg="#000000")
ventana.resizable(False, False)

# Cargar icono si existe
try:
    ventana.iconbitmap(obtener_ruta_recurso("images/sans.ico"))
except:
    pass

# Inicializar pygame para audio
try:
    pygame.mixer.init()
    sonido_letra = pygame.mixer.Sound(obtener_ruta_recurso("just-sans-talking (mp3cut.net).wav"))
    
    # Cargar música de fondo
    ruta_musica = obtener_ruta_recurso("gasters-theme_PgFVfMX.mp3")
    pygame.mixer.music.load(ruta_musica)
    pygame.mixer.music.play(loops=-1)
except Exception as e:
    print(f"Error cargando audio: {e}")
    sonido_letra = None

# Precargar GIF al inicio
precargar_gif()

# Cargar la fuente de Undertale
fuente_personalizada = cargar_fuente_undertale()

dialogos = [
    "* Hola, humano. ¿Quieres ver algo interesante?",
    "* Este mundo está lleno de cosas interesantes.",
    "* Mereces ver algo tan interesante...",
    "(Presiona ENTER para presenciar)"
]

indice_dialogo = 0
mostrando_texto = False

frame_central = tk.Frame(ventana, bg="#000000")
frame_central.pack(expand=True)

# Crear el cuadro de diálogo estilo Undertale con tamaño fijo
dialogo_frame = tk.Frame(frame_central, bg="white", bd=4, relief="solid", 
                        width=700, height=250)
dialogo_frame.pack(pady=60, padx=60)
dialogo_frame.pack_propagate(False)

# Frame interno negro para el texto
dialogo_interno = tk.Frame(dialogo_frame, bg="#000000")
dialogo_interno.pack(fill="both", expand=True, padx=4, pady=4)

# Crear el label con texto blanco que se ajuste al cuadro
label = tk.Label(dialogo_interno, text="", font=fuente_personalizada, 
                fg="white", bg="#000000", justify="left", 
                wraplength=650, padx=15, pady=10, anchor="nw")
label.pack(fill="both", expand=True)

def formatear_texto(texto, ancho=40):
    import textwrap
    return '\n'.join(textwrap.wrap(texto, width=ancho))

def mostrar_texto(texto, indice_letra=0):
    global mostrando_texto
    mostrando_texto = True
    if indice_letra <= len(texto):
        texto_formateado = formatear_texto(texto[:indice_letra])
        label.config(text=texto_formateado)

        # Reproducir sonido de letra si está disponible
        if sonido_letra and indice_letra > 0 and texto[indice_letra - 1] not in [' ', '\n']:
            sonido_letra.stop()
            sonido_letra.play()

        ventana.after(100, mostrar_texto, texto, indice_letra + 1)
    else:
        mostrando_texto = False

def mostrar_texto_gif(label_texto, texto, indice_letra=0):
    """Muestra texto en el GIF con control de eliminación"""
    global mostrando_texto, eliminando_texto
    
    if eliminando_texto:  # Si ya se está eliminando, no continuar
        return
        
    mostrando_texto = True
    if indice_letra <= len(texto):
        texto_mostrado = texto[:indice_letra]
        label_texto.config(text=texto_mostrado)

        # Reproducir sonido de letra si está disponible
        if sonido_letra and indice_letra > 0 and texto[indice_letra - 1] not in [' ', '\n']:
            sonido_letra.stop()
            sonido_letra.play()

        ventana.after(100, mostrar_texto_gif, label_texto, texto, indice_letra + 1)
    else:
        mostrando_texto = False

def mostrar_siguiente_dialogo(event=None):
    global indice_dialogo
    if mostrando_texto:
        return
    if indice_dialogo < len(dialogos):
        mostrar_texto(dialogos[indice_dialogo])
        indice_dialogo += 1
    else:
        mostrar_pantalla_negra_y_gif()

def mostrar_pantalla_negra_y_gif():
    try:
        pygame.mixer.music.fadeout(1000)
    except:
        pass

    label.pack_forget()
    frame_central.pack_forget()
    ventana.configure(bg="#000000")
    
    # Iniciar video 1 segundo antes que el GIF
    ventana.after(1000, reproducir_video_fondo)
    ventana.after(2000, aparecer_gif_final)

def aparecer_gif_final():
    global label_texto_gif, eliminando_texto
    eliminando_texto = False  # Reiniciar bandera
    
    try:
        if not frames_gif_cache:
            print("No hay frames de GIF cargados")
            return

        # Crear un frame contenedor para el GIF y el texto
        container_frame = tk.Frame(ventana, bg="#000000")
        container_frame.place(relx=0.5, rely=0.3, anchor="center")

        # Label para el GIF
        label_gif = tk.Label(container_frame, bg="#000000")
        label_gif.pack()

        # Label para el texto debajo del GIF
        label_texto_gif = tk.Label(container_frame, text="", font=fuente_personalizada, 
                                  fg="white", bg="#000000", justify="center")
        label_texto_gif.pack(pady=(20, 0))

        def animar_gif(indice=0):
            if indice < len(frames_gif_cache):
                frame = frames_gif_cache[indice]
                label_gif.config(image=frame)
                label_gif.image = frame
                # Usar after_idle para mejor rendimiento
                ventana.after(120, animar_gif, (indice + 1) % len(frames_gif_cache))

        # Iniciar animación del GIF
        animar_gif()
        
        # Mensaje que aparecerá debajo del GIF
        mensaje_gif = "LO LOGRASTE"
        
        # Esperar antes de mostrar el texto
        ventana.after(1500, lambda: mostrar_texto_gif(label_texto_gif, mensaje_gif))
        
    except Exception as e:
        print(f"Error mostrando GIF: {e}")
        # Mostrar texto alternativo si no se puede cargar el GIF
        label_error = tk.Label(ventana, text="¡Algo interesante debería aparecer aquí!", 
                              font=fuente_personalizada, fg="white", bg="#000000")
        label_error.place(relx=0.5, rely=0.5, anchor="center")

# Eventos
ventana.bind("<Return>", mostrar_siguiente_dialogo)
ventana.bind("<Escape>", lambda e: ventana.destroy())

# Hacer la ventana enfocable para recibir eventos de teclado
ventana.focus_set()

# Asegurar que el video se detenga al cerrar la ventana
def on_closing():
    detener_video()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", on_closing)

mostrar_siguiente_dialogo()
ventana.mainloop()

## hola prueba commit 1