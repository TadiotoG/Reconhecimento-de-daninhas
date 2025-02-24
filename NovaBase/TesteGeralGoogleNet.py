import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import tensorflow as tf
from tensorflow.keras import layers,models
from tensorflow import keras
from PIL import Image

import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F

import xmltodict
import cv2
from PIL import Image
from GoogleNetFunc import GoogLeNet

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
import numpy as np

img_width = 224
img_height = 224

flag = "Duplicated"

def zoom_at(img, x, y, zoom):
	w, h = img.size
	zoom2 = zoom * 2
	img = img.crop((x - w / zoom2, y - h / zoom2, 
					x + w / zoom2, y + h / zoom2))
	return img.resize((w, h), Image.LANCZOS)

def get_number_of_positives_and_negatives(past, seq):
	dir_imgs = past + str(seq) + "/imgs/"
	positives = 0
	negatives = 0

	with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
		dict_file = xmltodict.parse(org_file)

	arr_plants = dict_file["annotations"]["image"]

	for file in arr_plants:
		try:
			name_img = file["@name"]
			x_min = file["box"]
			positives += 1

		except Exception as e:
			negatives += 1
	return positives, negatives


def get_arrays_from_past_and_seq(past, seq):
	x_array = []
	y_array = []
	dir_imgs = past + str(seq) + "/imgs/"

	with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
		dict_file = xmltodict.parse(org_file)

	arr_plants = dict_file["annotations"]["image"]

	for file in arr_plants:
		try:
			name_img = file["@name"]
			x_min = file["box"]
			img = Image.open(dir_imgs + name_img)
			img = img.resize((img_width, img_height)) # 0.3 = 576x324 --- 0.2 = 384x216 --- 0.15 = 288x162
			x_array.append(img)
			y_array.append(1)

		except:
			name_img = file["@name"]
			img = Image.open(dir_imgs + name_img)
			img = img.resize((img_width, img_height))
			rotated_image1 = img.rotate(90)
			rotated_image2 = img.rotate(180)
			rotated_image3 = img.rotate(270)


			# rotated_image1 = zoom_at(rotated_image1, 960, 540, 1.5)
			# rotated_image1 = rotated_image1.resize((img_width, img_height))
			# img.show()
			# rotated_image1.show()
			if flag == "Duplicated":
				# print("Just to be sure")
				x_array.append(rotated_image1)
				y_array.append(0)
				x_array.append(rotated_image2)
				y_array.append(0)
				x_array.append(rotated_image3)
				y_array.append(0)
			x_array.append(img)
			y_array.append(0)

	return x_array, y_array

past_and_last_seq_0 = ("RumexWeeds/20210806_hegnstrup/seq", 17)
past_and_last_seq_1 = ("RumexWeeds/20210806_stengard/seq", 20)
past_and_last_seq_2 = ("RumexWeeds/20210807_lundholm/seq", 28)
past_and_last_seq_3 = ("RumexWeeds/20210908_lundholm/seq", 13)
past_and_last_seq_4 = ("RumexWeeds/20211006_stengard/seq", 15)

# list_of_pasts = [past_and_last_seq_0, past_and_last_seq_1, past_and_last_seq_2, past_and_last_seq_3, past_and_last_seq_4]
list_of_pasts = [past_and_last_seq_2, past_and_last_seq_3, past_and_last_seq_4]

# model = GoogLeNet(img_width=img_width, img_height=img_height) 
# model.summary()

# print("Modelo - número de saídas:", len(model.outputs))
# print("Formato da saída do modelo:", model.output)

for i in range(0, len(list_of_pasts)):
	for j in range(i+1, len(list_of_pasts)):
		print("I = ", i, "  J = ", j)

		x_train = []
		y_train = []

		x_test = []
		y_test = []

		train = list_of_pasts[i]
		test = list_of_pasts[j]

		for k in range(train[1]+1):
			x_aux, y_aux = get_arrays_from_past_and_seq(train[0], k)
			x_train.extend(x_aux)
			y_train.extend(y_aux)

		for l in range(test[1]+1):
			x_aux, y_aux = get_arrays_from_past_and_seq(test[0], l)
			x_test.extend(x_aux)
			y_test.extend(y_aux)

		for aux in range(2):
			if(aux == 1): # Inverte treino e teste, para que seja testado com I e J, ambos sendo treino e teste
				save = x_train
				x_train = x_test
				x_test = save

				save = y_train
				y_train = y_test
				y_test = save

				train = list_of_pasts[j]
				test = list_of_pasts[i]

			x_train = np.array(x_train)
			y_train = np.array(y_train)

			x_test = np.array(x_test)
			y_test = np.array(y_test)

			my_dict = {
				"Train":[],
				"Test":[],
				str(str(img_width) + "_" + flag + "_AC"): [],
				"F1":[],
				"EPOCH":[],
				"SENS": [],
				"ESP": []
			}

			for x in range(6):
				epochs_num = 5+x*2
				# print("Onde estou -> ", epochs_num)
				model = GoogLeNet(img_width=img_width, img_height=img_height) 
				model.compile(optimizer='adam', loss=['binary_crossentropy', 'binary_crossentropy', 'binary_crossentropy'], metrics=['accuracy', 'accuracy', 'accuracy'])
				model.fit(x_train, [y_train, y_train, y_train], epochs=epochs_num) 

				Y_test = []
				answer = model.predict(x_test)
				for elem in y_test:
					Y_test.append(elem)
				
				answer_2 = np.argmax(answer[0], axis=1)

				TN, FP, FN, TP = confusion_matrix(Y_test, answer_2).ravel()
				my_dict["Train"].append(train[0])
				my_dict["Test"].append(test[0])
				my_dict[str(str(img_width) + "_" + flag + "_AC")].append(accuracy_score(Y_test, answer_2))
				my_dict["F1"].append(f1_score(Y_test, answer_2))
				my_dict["EPOCH"].append(epochs_num)
				my_dict["SENS"].append((TP/(TP+FN)))
				my_dict["ESP"].append((TN/(FP+TN)))

			my_dict = pd.DataFrame(my_dict)

			train_name = ""
			test_name = ""

			for h in train[0]:
				if h.isalpha() or h.isnumeric() or h == "_":
					train_name += h

			for g in test[0]:
				if g.isalpha() or g.isnumeric() or g == "_":
					test_name += g

			my_dict.to_csv("Result_"+ str(img_width) + "_" + flag + train_name + "_" + test_name + ".csv", index=False)
