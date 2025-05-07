import tensorflow as tf
import pymongo 
import numpy as np

def getUserLevel(newUser):
    model = tf.keras.models.load_model('/home/jin/Code/modular/modular/neuralNetwork/user_level.h5')

    correct_answers_percentage=(newUser["respuestas_correctas"] / newUser["total_respuestas"])
    average_time =(newUser["tiempo_respuestas"]/newUser["total_respuestas"])
    sessions=newUser["sesiones_totales"]
    flashcards_generated =newUser["flashcards_generadas"]
    words_learned =newUser["palabras_aprendidas"]
    learning_rate =newUser["palabras_aprendidas"]/newUser["sesiones_totales"]
    activity_days =newUser["dias_actividad"]
    accuracy_variation =((newUser["aciertos_semana_actual"]-newUser["aciertos_semana_pasada"])/newUser["aciertos_semana_pasada"])
    user = [
        correct_answers_percentage,
        average_time,
        sessions,
        flashcards_generated,
        words_learned,
        learning_rate,
        activity_days,
        accuracy_variation
    ]
    
    normalized_user = normalizeData(user)
    user = np.array([normalized_user])
    prediction = model.predict(user)
    
    predicted_class = int(np.argmax(prediction))

    return predicted_class


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
#
# newUser={
#         "_id": "8",
#         "nombre": "Usuario 8",
#         "email": "user8@example.com",
#         "fecha_registro": "2025-02-23",
#         "nivel": "0",
#         "flashcards_generadas": 34,
#         "total_respuestas": 31,
#         "tiempo_respuestas": 380.23783718085997,
#         "respuestas_correctas": 14,
#         "sesiones_totales": 6,
#         "palabras_aprendidas": 12,
#         "dias_actividad": 62,
#         "aciertos_semana_pasada": 20,
#         "aciertos_semana_actual": 16
#     }
# print("Prediccion: ",getUserLevel(newUser))
#
# newUser={
#         "_id": "9",
#         "nombre": "Usuario 9",
#         "email": "user9@example.com",
#         "fecha_registro": "2025-02-18",
#         "nivel": "2",
#         "flashcards_generadas": 553,
#         "total_respuestas": 650,
#         "tiempo_respuestas": 4035.8489415449285,
#         "respuestas_correctas": 575,
#         "sesiones_totales": 100,
#         "palabras_aprendidas": 372,
#         "dias_actividad": 69,
#         "aciertos_semana_pasada": 71,
#         "aciertos_semana_actual": 73
#     }
# print("Prediccion: ",getUserLevel(newUser))
