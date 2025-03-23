import sys  
import tensorflow as tf  
import pymongo 
import numpy as np
import json

def neural_network():

    with open('userMetrics.json', 'r') as file:
        data = json.load(file)

    userData = []
    userLevel = []
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
        userData.append(normalized_user)
        userLevel.append(i["nivel"])
        
    userData = np.array(userData)
    userLevel = np.array(userLevel)
    userLevel = userLevel.astype(int)

    print(len(userData))
    print(type(userData))  
    print(type(userLevel))  

    inputLayer = tf.keras.layers.Dense(units=16, activation='relu', input_shape=[8])
    hiddenLayer = tf.keras.layers.Dense(units=8,activation='relu')
    outputLayer = tf.keras.layers.Dense(units=3,activation='softmax')

    model = tf.keras.Sequential([inputLayer,hiddenLayer,outputLayer])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(userData,userLevel,epochs=600,verbose=1,batch_size=2)
    model.save('user_level.h5')

    test_loss, test_acc = model.evaluate(userData, userLevel)
    print("Precisión en test:", test_acc)

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


neural_network()