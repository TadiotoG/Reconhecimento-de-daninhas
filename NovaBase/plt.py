import xmltodict
from PIL import Image
import pandas as pd
import numpy as np
import os
from random import randint
import cv2

cutted_past_name = "RumexWeedsCutted"

def cut_img_and_save(x_min, y_min, x_max, y_max, source_dir, destination_dir):
	img = Image.open(source_dir)
	image_arr = np.array(img)
	image_arr = image_arr[y_min:y_max, x_min:x_max]
	new_image = Image.fromarray(image_arr)
	new_image.save(destination_dir)

def generate_random_positions(width, height, vet_limits, size_w, size_h):
	size_w = randint(size_w-20, size_w+20)
	size_h = randint(size_h-20, size_h+20)
	print("Size Width = ", size_w)
	print("Size Height = ", size_h)
	generated_img = 0

	while(generated_img == 0):
		new_x_min = randint(0, width-size_w)
		new_y_min = randint(0, height-size_h)
		new_x_max = new_x_min + size_w
		new_y_max = new_y_min + size_h

		generated_img = 1
		for pixel_i in range(new_x_min, new_x_max):
			for pixel_j in range(new_y_min, new_y_max):
				for limit in vet_limits:
					x_min = limit[0]
					y_min = limit[1]
					x_max = limit[2]
					y_max = limit[3]
					if pixel_i > x_min and pixel_i < x_max and pixel_j > y_min and pixel_j < y_max:
						generated_img = 0

	return new_x_min, new_y_min, new_x_max, new_y_max

def get_avg_from_weeds(past, seq):
	weed_counter = 0
	sum_size_x = 0
	sum_size_y = 0

	with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
		dict_file = xmltodict.parse(org_file)

	arr_plants = dict_file["annotations"]["image"]

	for file in arr_plants:
		arr_of_limits_weeds = []
		try:
			if type(file["box"]) == list:
				for box in file["box"]:
					x_min = int(box["@xtl"])
					y_min = int(box["@ytl"])
					x_max = int(box["@xbr"])
					y_max = int(box["@ybr"])

					if(x_min > x_max):
						aux = x_min
						x_min = x_max
						x_max = aux

					if(y_min > y_max):
						aux = y_min
						y_min = y_max
						y_max = aux

					sum_size_x += x_max - x_min
					sum_size_y += y_max - y_min
					weed_counter +=1
					
			else:
				x_min = int(file["box"]["@xtl"])
				y_min = int(file["box"]["@ytl"])
				x_max = int(file["box"]["@xbr"])
				y_max = int(file["box"]["@ybr"])
				arr_of_limits_weeds.append((x_min, y_min, x_max, y_max))

				if(x_min > x_max):
					aux = x_min
					x_min = x_max
					x_max = aux

				if(y_min > y_max):
					aux = y_min
					y_min = y_max
					y_max = aux

				sum_size_x += x_max - x_min
				sum_size_y += y_max - y_min
				weed_counter+=1
	
		except:
			pass

	return int(sum_size_x/weed_counter), int(sum_size_y/weed_counter)

#def plot_img_resized():


def plot_imgs(past, seq, destination_folder, width_avg, height_avg):
	weed_counter = 0
	counter = 0
	dir_imgs = past + str(seq) + "/imgs/"

	with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
		dict_file = xmltodict.parse(org_file)

	# print("NOME : ", past[11:-4])
	second_dir = past[11:-4] # Pega só o nome do segundo diretorio
	try:
		os.makedirs(destination_folder + "/" + second_dir)

	except:
		pass
	
	dir_complete = destination_folder + "/" + second_dir + "/" + "seq" + str(seq)
	try:
		os.makedirs(dir_complete)
	except:
		pass

	arr_plants = dict_file["annotations"]["image"]

	for file in arr_plants:
		arr_of_limits_weeds = []
		try:
			name_img = file["@name"]
			img = cv2.imread(dir_imgs + name_img)

			if type(file["box"]) == list:
				# print(dir_complete, "   img: ", file["@name"])
				for box in file["box"]:
					x_min = int(box["@xtl"])
					y_min = int(box["@ytl"])
					x_max = int(box["@xbr"])
					y_max = int(box["@ybr"])
					arr_of_limits_weeds.append((x_min, y_min, x_max, y_max))
					cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)
					weed_counter+=1
					
			else:
				x_min = int(file["box"]["@xtl"])
				y_min = int(file["box"]["@ytl"])
				x_max = int(file["box"]["@xbr"])
				y_max = int(file["box"]["@ybr"])
				arr_of_limits_weeds.append((x_min, y_min, x_max, y_max))
				cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)		
				weed_counter+=1
	
		except:
			# name_img = file["@name"]
			# img = cv2.imread(dir_imgs + name_img)]
			pass

		x_min_past, y_min_past, x_max_past, y_max_past = generate_random_positions(1920, 1080, arr_of_limits_weeds, width_avg, height_avg)
		cv2.rectangle(img, (x_min_past, y_min_past), (x_max_past, y_max_past), (255, 0, 0), 3)
		img_s = cv2.resize(img, (960, 540))
		cv2.imshow(("Seq "+ str(i) + "  -  Imagem " + str(counter)), img_s) # Plota a imagem
		cv2.waitKey(0)
		counter+=1

past_and_last_seq = []
# past_and_last_seq.append(("RumexWeeds/20210806_hegnstrup/seq", 17))
# past_and_last_seq.append(("RumexWeeds/20210806_stengard/seq", 20))
# past_and_last_seq.append(("RumexWeeds/20210807_lundholm/seq", 28))
past_and_last_seq.append(("RumexWeeds/20210908_lundholm/seq", 13))
# past_and_last_seq.append(("RumexWeeds/20211006_stengard/seq", 15))

for past in past_and_last_seq: # Para todas as pastas
	for i in range(past[1]+1): # Para todas as sequencias
		avg_x, avg_y = get_avg_from_weeds(past[0], i)

		print("X = ", avg_x, "  Y = ", avg_y)
		plot_imgs(past[0], i, cutted_past_name, avg_x, avg_y)