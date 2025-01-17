import xmltodict
from PIL import Image
import pandas as pd
import numpy as np
import os
from random import randint

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
	#print("Size Width = ", size_w)
	#print("Size Height = ", size_h)
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

def get_min_wh_weeds(past, seq):

	with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
		dict_file = xmltodict.parse(org_file)

	arr_plants = dict_file["annotations"]["image"]
	res_min = 100000
	width_min = 0
	height_min = 0
	smallest = "None"

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

					width = x_max - x_min
					height = y_max - y_min

					if(res_min > (width * height)):
						res_min = width * height
						width_min = width
						height_min = height
						smallest = file["@name"]

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

				width = x_max - x_min
				height = y_max - y_min

				if(res_min > (width * height)):
					res_min = width * height
					width_min = width
					height_min = height
					smallest = file["@name"]

		except:
			pass

	return int(res_min), int(width_min), int(height_min), str(smallest)

def cut_and_save_img_from_past(past, seq, destination_folder, width_avg, height_avg):
	weed_counter = 0
	pasture_counter = 0
	dir_imgs = past + str(seq) + "/imgs/"

	with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
		dict_file = xmltodict.parse(org_file)

	# print("NOME : ", past[11:-4])
	second_dir = past[11:-4] # Pega só o nome do segundo diretorio
	try:
		os.makedirs(destination_folder + "/" + second_dir)

	except:
		pass
		# print("Diretorio ja criado")
	
	dir_complete = destination_folder + "/" + second_dir + "/" + "seq" + str(seq)
	try:
		os.makedirs(dir_complete)
	except:
		pass
		# print("Diretorio ja criado")

	arr_plants = dict_file["annotations"]["image"]


	for file in arr_plants:
		arr_of_limits_weeds = []
		try:
			name_img = file["@name"]

			if type(file["box"]) == list:
				# print(dir_complete, "   img: ", file["@name"])
				for box in file["box"]:
					x_min = int(box["@xtl"])
					y_min = int(box["@ytl"])
					x_max = int(box["@xbr"])
					y_max = int(box["@ybr"])
					arr_of_limits_weeds.append((x_min, y_min, x_max, y_max))
					cut_img_and_save(x_min, y_min, x_max, y_max, (dir_imgs+name_img), (dir_complete + "/Weed_" + str(weed_counter) + ".jpg"))
					weed_counter+=1
					
			else:
				x_min = int(file["box"]["@xtl"])
				y_min = int(file["box"]["@ytl"])
				x_max = int(file["box"]["@xbr"])
				y_max = int(file["box"]["@ybr"])
				arr_of_limits_weeds.append((x_min, y_min, x_max, y_max))
				cut_img_and_save(x_min, y_min, x_max, y_max, (dir_imgs+name_img), (dir_complete + "/Weed_" + str(weed_counter) + ".jpg"))
				
				weed_counter+=1
	
		except:
			# name_img = file["@name"]
			# img = Image.open(dir_imgs + name_img)
			# x_array.append(img)
			# y_array.append([0])
			# print("Imagem sem daninha!")
			pass

		# Corta pastagem
		x_min_past, y_min_past, x_max_past, y_max_past = generate_random_positions(1920, 1080, arr_of_limits_weeds, width_avg, height_avg)
		cut_img_and_save(x_min_past, y_min_past, x_max_past, y_max_past, (dir_imgs+name_img), (dir_complete + "/Pasture_" + str(pasture_counter) + ".jpg"))
		pasture_counter+=1

past_and_last_seq = []
past_and_last_seq.append(("RumexWeeds/20210806_hegnstrup/seq", 17))
past_and_last_seq.append(("RumexWeeds/20210806_stengard/seq", 20))
past_and_last_seq.append(("RumexWeeds/20210807_lundholm/seq", 28))
past_and_last_seq.append(("RumexWeeds/20210908_lundholm/seq", 13))
past_and_last_seq.append(("RumexWeeds/20211006_stengard/seq", 15))

smallest_res = 1000000
smallest_width = 10000
smallest_height = 10000
smallest_name = "None"

# Corta todas as imagens e da um crop
for past in past_and_last_seq: # Para todas as pastas
	for i in range(past[1]+1): # Para todas as sequencias
		avg_x, avg_y = get_avg_from_weeds(past[0], i)

		print(past[0], "-", i, "-X = ", avg_x, "  Y = ", avg_y)
		cut_and_save_img_from_past(past[0], i, cutted_past_name, avg_x, avg_y)