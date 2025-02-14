import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import tensorflow as tf
from tensorflow.keras import layers,models
from tensorflow import keras
from PIL import Image
from collections import Counter

import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F

import xmltodict
import cv2
from PIL import Image
from GoogleNetFunc import GoogLeNet

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

list_of_pasts = [past_and_last_seq_0, past_and_last_seq_1, past_and_last_seq_2, past_and_last_seq_3, past_and_last_seq_4]

for i in range(len(list_of_pasts)):
	for j in range(i+1, len(list_of_pasts)):
		print("I = ", i, "  J = ", j)

		x_train = []
		y_train = []

		x_test = []
		y_test = []

		train = list_of_pasts[i]
		test = list_of_pasts[j]

		for i in range(train[1]+1):
			x_aux, y_aux = get_arrays_from_past_and_seq(train[0], i)
			x_train.extend(x_aux)
			y_train.extend(y_aux)

		for i in range(test[1]+1):
			x_aux, y_aux = get_arrays_from_past_and_seq(test[0], i)
			x_test.extend(x_aux)
			y_test.extend(y_aux)

		x_train = np.array(x_train)
		y_train = np.array(y_train)

		x_test = np.array(x_test)
		y_test = np.array(y_test)


		total_pos = 0
		total_neg = 0
		for i in range(train[1]+1):
			p, n = get_number_of_positives_and_negatives(train[0], i)
			total_pos += p
			total_neg += n
			#print(i, " = ", p, "  ", n)
		print(train[0])
		print("Total treino = ", len(y_train))
		print("Positives: ", total_pos)
		print("Negatives: ", total_neg, "\n")


		total_pos = 0
		total_neg = 0
		for i in range(test[1]+1):
			p, n = get_number_of_positives_and_negatives(test[0], i)
			total_pos += p
			total_neg += n
			#print(i, " = ", p, "  ", n)
		print(test[0])
		print("Total teste = ", len(y_test))
		print("Positives: ", total_pos)
		print("Negatives: ", total_neg, "\n")

		print(x_train.shape)
		print(x_test.shape)
		# (580, 1200, 1920, 3)

		model = GoogLeNet() 
		model.summary()

		from sklearn.metrics import classification_report
		from sklearn.metrics import confusion_matrix
		from sklearn.metrics import accuracy_score
		import numpy as np

		my_dict = {
			"Train":[],
			"Test":[],
			str(str(img_width) + "_" + flag + "_AC"): [],
			"EPOCH":[],
			"SENS": [],
			"ESP": []
		}

		for x in range(6):
			epochs_num = 5+x*2
			print("Onde estou -> ", epochs_num)
			model = GoogLeNet() 
			model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy', 'accuracy', 'accuracy'])
			model.fit(x_train, y_train, epochs=epochs_num)

			Y_test = []
			answer = model.predict(x_test)
			for elem in y_test:
				Y_test.append(elem)
				
			answer_2 = np.argmax(answer[0], axis=1)
			TN, FP, FN, TP = confusion_matrix(Y_test, answer_2).ravel()
			my_dict["Train"].append(train[0])
			my_dict["Test"].append(test[0])
			my_dict[str(str(img_width) + "_" + flag + "_AC")].append(accuracy_score(Y_test, answer_2))
			my_dict["EPOCH"].append(epochs_num)
			my_dict["SENS"].append((TP/(TP+FN)))
			my_dict["ESP"].append((TN/(FP+TN)))

		import pandas as pd

		my_dict = pd.DataFrame(my_dict)

		train_name = ""
		test_name = ""

		for i in train[0]:
			if i.isalpha() or i.isnumeric() or i == "_":
				train_name += i

		for i in test[0]:
			if i.isalpha() or i.isnumeric() or i == "_":
				test_name += i

		my_dict.to_csv("Result_"+ str(img_width) + "_" + flag + train_name + "_" + test_name + ".csv", index=False)