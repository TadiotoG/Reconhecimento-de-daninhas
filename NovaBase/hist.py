import xmltodict
from PIL import Image
import pandas as pd
import numpy as np
import os
from random import randint
import cv2
import matplotlib.pyplot as plt

cutted_past_name = "RumexWeedsCutted"
#def plot_img_resized():

def soma_vet(vet_A, vet_B):
    vet_result = []
    for i in range(vet_A):
        vet_result.append((vet_A[i] + vet_B[i]))

    return vet_result

def dividir_vet(vet_A, x):
    vet_result = []
    for i in range(vet_A):
        vet_result.append((vet_A[i] / x))

    return vet_result

def get_hist(past, sequencia, flag_HSV = False):
    # Inicializa os histogramas como arrays do NumPy
    weed_hist_r = np.zeros((256, 1), dtype=np.float32)
    weed_hist_g = np.zeros((256, 1), dtype=np.float32)
    weed_hist_b = np.zeros((256, 1), dtype=np.float32)
    weed_counter = 0

    past_hist_r = np.zeros((256, 1), dtype=np.float32)
    past_hist_g = np.zeros((256, 1), dtype=np.float32)
    past_hist_b = np.zeros((256, 1), dtype=np.float32)
    past_counter = 0

    # mem = 0

    for seq in range(sequencia+1):
        dir_imgs = past + str(seq) + "/imgs/"

        with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
            dict_file = xmltodict.parse(org_file)

        arr_plants = dict_file["annotations"]["image"]

        for file in arr_plants:
            try:
                name_img = file["@name"]
                x_min = file["box"]
                img = cv2.imread(dir_imgs + name_img)
                if(flag_HSV):
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                canal_b, canal_g, canal_r = cv2.split(img)
                weed_hist_r += cv2.calcHist([canal_r], [0], None, [256], [0, 256])
                weed_hist_g += cv2.calcHist([canal_g], [0], None, [256], [0, 256])
                weed_hist_b += cv2.calcHist([canal_b], [0], None, [256], [0, 256])
                weed_counter+=1
        
            except:
                img = cv2.imread(dir_imgs + name_img)
                if(flag_HSV):
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                past_hist_r += cv2.calcHist([canal_r], [0], None, [256], [0, 256])
                past_hist_g += cv2.calcHist([canal_g], [0], None, [256], [0, 256])
                past_hist_b += cv2.calcHist([canal_b], [0], None, [256], [0, 256])
                past_counter += 1

        # print("Na sequencia ", str(seq), " tem ", str((weed_counter+past_counter-mem)), " imagens")
        # mem = weed_counter+past_counter

    weed_hist_mean_b = weed_hist_b / weed_counter
    weed_hist_mean_g = weed_hist_g / weed_counter
    weed_hist_mean_r = weed_hist_r / weed_counter
    past = past.split("/")
    plt.figure(figsize=(8, 6))
    plt.xlabel('Valores de Pixel')
    plt.ylabel('Frequência')

    if(flag_HSV):
        plt.title('Histograma Daninha ' + past[1] + ' dos Canais HSV ' + str(weed_counter))
        plt.plot(weed_hist_mean_b, color='blue', label='Canal H')
        plt.plot(weed_hist_mean_g, color='green', label='Canal S')
        plt.plot(weed_hist_mean_r, color='red', label='Canal V')
    else:
        plt.title('Histograma Daninha ' + past[1] + ' dos Canais RGB ' + str(weed_counter))
        plt.plot(weed_hist_mean_b, color='blue', label='Canal B')
        plt.plot(weed_hist_mean_g, color='green', label='Canal G')
        plt.plot(weed_hist_mean_r, color='red', label='Canal R')

    plt.legend()
    plt.xlim([-2, 256])

    past_hist_mean_r = past_hist_r / past_counter
    past_hist_mean_g = past_hist_g / past_counter
    past_hist_mean_b = past_hist_b / past_counter
    plt.figure(figsize=(8, 6))
    plt.xlabel('Valores de Pixel')
    plt.ylabel('Frequência')

    if(flag_HSV):
        plt.title('Histograma Pastagem ' + past[1] + ' dos Canais HSV ' + str(past_counter))
        plt.plot(past_hist_mean_b, color='blue', label='Canal H')
        plt.plot(past_hist_mean_g, color='green', label='Canal S')
        plt.plot(past_hist_mean_r, color='red', label='Canal V')
    else:
        plt.title('Histograma Pastagem ' + past[1] + ' dos Canais RGB ' + str(past_counter))
        plt.plot(past_hist_mean_b, color='blue', label='Canal B')
        plt.plot(past_hist_mean_g, color='green', label='Canal G')
        plt.plot(past_hist_mean_r, color='red', label='Canal R')

    plt.legend()
    plt.xlim([-2, 256])
    plt.ylim([-500, 45000])
    plt.show()
        

past_and_last_seq = []
past_and_last_seq.append(("RumexWeeds/20210806_hegnstrup/seq", 17))
past_and_last_seq.append(("RumexWeeds/20210806_stengard/seq", 20))
past_and_last_seq.append(("RumexWeeds/20210807_lundholm/seq", 28))
past_and_last_seq.append(("RumexWeeds/20210908_lundholm/seq", 13))
past_and_last_seq.append(("RumexWeeds/20211006_stengard/seq", 15))

past_n = 0

get_hist(past_and_last_seq[past_n][0], past_and_last_seq[past_n][1], True)