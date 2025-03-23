import sys  
import tensorflow as tf  
import pymongo 
import numpy as np
import json

def getUserLevel():

    model = tf.keras.models.load_model('user_level.h5')

    with open('newUsers.json', 'r') as file:
        data = json.load(file)

    newUsers = []
        
    for i in data:
        correct_answers_percentage=(i["respuestas_correctas"] / i["total_respuestas"])
        average_time =(i["tiempo_respuestas"]/i["total_respuestas"])
        sessions=i["sesiones_totales"]
        flashcards_generated =i["flashcards_generadas"]
        words_learned =i["palabras_aprendidas"]
        learning_rate =i["palabras_aprendidas"]/i["sesiones_totales"]
        activity_days =i["dias_actividad"]
        accuracy_variation =((i["aciertos_semana_actual"]-i["aciertos_semana_pasada"])/i["aciertos_semana_pasada"])

        user = (
            correct_answers_percentage,
            average_time,
            sessions,
            flashcards_generated,
            words_learned,
            learning_rate,
            activity_days,
            accuracy_variation
        )

        normalized_user = normalizeData(user)
        newUsers.append(normalized_user)
        print(user)
        print(normalized_user)

    print(f'cantidad: {len(newUsers)}')
    newUsers=np.array(newUsers)
    predictions = model.predict(newUsers)
    
    for i, prediction in enumerate(predictions):
        predicted_class = np.argmax(prediction)  # El índice de la clase con la probabilidad más alta
        print(f"Predicción para el usuario {i+1}:")
        print("Predicción:", prediction)
        print("Clase predicha:", predicted_class)

def normalizeData(user):
    min_vals = [0, 0, 1, 10, 1, 1, 1, -1]
    max_vals = [1, 10, 100, 5000, 3000, 50, 1000, 1]

    normalized_user = []
    for i in range(len(user)):
        val = user[i]         
        min_v = min_vals[i]   
        max_v = max_vals[i]   
        if max_v - min_v != 0:
            normalized_value = (val - min_v) / (max_v - min_v)
        else:
            normalized_value = 0 

        normalized_user.append(normalized_value)
    return normalized_user


getUserLevel()