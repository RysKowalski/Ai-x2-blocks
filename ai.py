import numpy as np
import keras
import cv2
import pyautogui
import time


# Załaduj zbiór danych obrazów z cyframi (np. MNIST)
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

# Normalizacja danych
x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255


# Reshape your training and testing data
x_train = x_train.reshape(-1, 28 * 28)
x_test = x_test.reshape(-1, 28 * 28)


# Konwersja etykiet na wektory one-hot
y_train = keras.utils.to_categorical(y_train)
y_test = keras.utils.to_categorical(y_test)

# Definicja modelu sieci neuronowej

model = keras.Sequential()
model.add(keras.layers.Dense(64, activation='relu', input_shape=(28 * 28,)))
model.add(keras.layers.Dense(10, activation='softmax'))

# Kompilacja modelu

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# Trening modelu

model.fit(x_train, y_train, epochs=5)

# Ewaluacja modelu

test_loss, test_acc = model.evaluate(x_test, y_test)
print('Dokładność:', test_acc)

# Predykcja liczb z nowych obrazów


print("KHAGSDGHAJGSDGHGASDGUAYTISVFDYADFGASDFVSAFJGDVCFASDFCASJDFASTJDFASTDFGASTDFGASTDFASGTDGFASDASGFDIGASUDYASGUDYGASDUYASGDUYADGAUIYD")
time.sleep(5)
screenshot = pyautogui.screenshot(region=(1213, 135, 90, 90))

# Konwertuj zrzut ekranu na obraz OpenCV
new_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

new_image = cv2.resize(new_image, (28, 28))  # Resize to 28x28 pixels
new_image = new_image.reshape(1, 28 * 28)
new_image = new_image.astype('float32') / 255

# Przedprocesowanie obrazu
new_image = new_image.reshape(1, 28 * 28)
new_image = new_image.astype('float32') / 255

# Predykcja za pomocą modelu
prediction = model.predict(new_image)
predicted_digit = np.argmax(prediction)

print('Rozpoznana cyfra:', predicted_digit)
