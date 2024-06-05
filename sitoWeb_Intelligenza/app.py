#importo le librerie necessarie
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit

import random

import json

import argparse
import sys
import time

import cv2
import mediapipe as mp

import threading

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


#variabili globali
result_text="inizializzazione"
daStampare = ""
ultimo_valore = ""

app = Flask(__name__)

COUNTER, FPS = 0, 0
START_TIME = time.time()

#funzione che ritorna la route principale del sito
@app.route('/')
def index():
    return render_template('index.html')

#route che abbiamo utilizzato per la visione dei primi risultati, non più necessaria
"""
@app.route('/jcp')
def jcp():
    global result_text
    return render_template('index.html', result=result_text)
"""
#Grazie a questa funzione, il sito riesce ad adattarsi a qualunque stringa sia inserita come route dopo l'ip del nostro sito
@app.route("/<path:p>")
def serve_static(p):
    return app.send_static_file(p)

#funzione per l'invio dei risultati alla route principale
@app.route("/dht")
def api_dht():
    global result_text
    global daStampare
    print("DHT: "+result_text)
    return Response(daStampare,
                        mimetype="text/plain; charset=utf-8",
                        headers={"Cache-Control":"no-cache"})


#funzione per la corretta stampa della stringa completa e logica per evitare ripetizione di lettere e garantire il corretto delete
def appendi(result_text):
    global daStampare
    global ultimo_valore

    if not result_text:
        return
    
    # Controllo per i comandi speciali
    if result_text == ultimo_valore:
        pass  # Se lo stesso carattere viene inserito due volte di fila, non fa nulla
    elif result_text == "del":
        daStampare = daStampare[:-1]  # Cancella l'ultimo carattere
        print(daStampare)
        ultimo_valore = "del"
    elif result_text == "not" or result_text == "None":
        ultimo_valore = ""  # Resetta il conteggio
    elif result_text == "space":
        daStampare += " "
        print(daStampare)
        ultimo_valore = "space"  # Resetta il conteggio
    else:
        daStampare += result_text
        ultimo_valore = result_text
        print(daStampare)

#definizione del metodo di run dell'intelligenza
def run(model: str, num_hands: int,
        min_hand_detection_confidence: float,
        min_hand_presence_confidence: float, min_tracking_confidence: float,
        camera_id: int, width: int, height: int) -> None:
            

    #catturo gli input dalla camera
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    #set dei parametri delle immagini
    row_size = 50  #pixel
    left_margin = 24  #pixel
    text_color = (0, 0, 0)  #balck
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 2

    label_text_color = (255, 255, 255)  #white
    label_font_size = 1
    label_thickness = 2

    recognition_frame = None
    recognition_result_list = []

    #salvo i rislutati
    def save_result(result: vision.GestureRecognizerResult,
                    unused_output_image: mp.Image, timestamp_ms: int):
        global FPS, COUNTER, START_TIME

        #calcolo degli FPS
        if COUNTER % fps_avg_frame_count == 0:
            FPS = fps_avg_frame_count / (time.time() - START_TIME)
            START_TIME = time.time()

        recognition_result_list.append(result)
        COUNTER += 1

    #Inizializzazione del modello (.task)
    base_options = python.BaseOptions(model_asset_path=model)
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=num_hands,
        min_hand_detection_confidence=min_hand_detection_confidence,
        min_hand_presence_confidence=min_hand_presence_confidence,
        min_tracking_confidence=min_tracking_confidence,
        result_callback=save_result
    )
    recognizer = vision.GestureRecognizer.create_from_options(options)

    #Continuo a cattuare immagini se la telecamera viene rilevata
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        image = cv2.flip(image, 1)

        #Converto l'immagine da un modello BGR ad un modello RGB, come richiesto nei modelli TFLite usati dall'intelligenza
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        #Utilizzo del modello
        recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)

        #Mostro a video gli FPS
        fps_text = 'FPS = {:.1f}'.format(FPS)
        global result_text
        text_location = (left_margin, row_size)
        current_frame = image
        cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_DUPLEX,
                    font_size, text_color, font_thickness, cv2.LINE_AA)

        if recognition_result_list:
            #Disegno a video i punti di riferimento trovati
            for hand_index, hand_landmarks in enumerate(
                    recognition_result_list[0].hand_landmarks):
                x_min = min([landmark.x for landmark in hand_landmarks])
                y_min = min([landmark.y for landmark in hand_landmarks])
                y_max = max([landmark.y for landmark in hand_landmarks])

                #Converto le coordinate in pixel
                frame_height, frame_width = current_frame.shape[:2]
                x_min_px = int(x_min * frame_width)
                y_min_px = int(y_min * frame_height)
                y_max_px = int(y_max * frame_height)

                #Classificazione del gesto in base al modello
                if recognition_result_list[0].gestures:
                    gesture = recognition_result_list[0].gestures[hand_index]
                    category_name = gesture[0].category_name
                    score = round(gesture[0].score, 2)
                    result_text = f'{category_name}'
                    #scommentare questa stampa per guardare la stampa di ogni singolo gesto riconosciuto sul terminale (più di un gesto al secondo)
                    #print(f'Recognized gesture: {result_text}')
                    appendi(result_text)
					
                    #sistemo la grandezza testo da stampare 
                    text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_DUPLEX,
                                                label_font_size, label_thickness)[0]
                    text_width, text_height = text_size

                    #calcolo la posizione della mano
                    text_x = x_min_px
                    text_y = y_min_px - 10

                    if text_y < 0:
                        text_y = y_max_px + text_height

                    #Disegno a video il testo
                    cv2.putText(current_frame, result_text, (text_x, text_y),
                                cv2.FONT_HERSHEY_DUPLEX, label_font_size,
                                label_text_color, label_thickness, cv2.LINE_AA)

                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y,
                                                    z=landmark.z) for landmark in
                    hand_landmarks
                ])
                mp_drawing.draw_landmarks(
                    current_frame,
                    hand_landmarks_proto,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

            recognition_frame = current_frame
            recognition_result_list.clear()

        if recognition_frame is not None:
            cv2.imshow('gesture_recognition', recognition_frame)

        #Il programma viene interrotto se premo ESC
        if cv2.waitKey(1) == 27:
            break

    recognizer.close()
    cap.release()
    cv2.destroyAllWindows()

#avvio il thread dell'AI
def ai_thread():
    run('gesture_recognizer.task', 1, 0.5,0.5, 0.5,0, 640, 480)

x = threading.Thread(target=ai_thread, args=())
x.start()
