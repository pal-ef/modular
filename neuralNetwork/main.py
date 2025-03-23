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
        
    print(len(userData))
    userData = np.array(userData)
    userLevel = np.array(userLevel)
    userLevel = userLevel.astype(int)

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

    newUsers=[
        [0.9291, 5.5150, 43, 649, 205, 4.7674, 98, 0.0930], #2
        [0.7156, 9.5786, 28, 401, 159, 5.6786, 73, 0.0364], #2
        [0.6809, 7.3096, 26, 303, 136, 5.2308, 48, -0.0357],  #2       
        [0.9428, 9.6019, 76, 391, 315, 4.1447, 54, -0.0213], #2
        [0.4667, 6.8251, 7, 147, 39, 5.5714, 34, 0.0833], #1
        [0.8143, 7.9129, 58, 297, 241, 4.1552, 33, 0.1515], #1
        [0.6825, 11.5290, 12, 65, 60, 5.0000, 20, -0.1250], #0
        [0.8085, 12.3136, 41, 656, 215, 5.2439, 12, 0.2000] #0
]

    normalized_newUsers = [normalizeData(user) for user in newUsers]
    normalized_newUsers = np.array(normalized_newUsers)

    predictions = model.predict(normalized_newUsers)
    
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


neural_network()