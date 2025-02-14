import xmltodict
from PIL import Image

img_width = 224
img_height = 224

flag = "Normal"

def zoom_at(img, x, y, zoom):
    w, h = img.size
    zoom2 = zoom * 2
    img = img.crop((x - w / zoom2, y - h / zoom2, 
                    x + w / zoom2, y + h / zoom2))
    return img.resize((w, h), Image.LANCZOS)

def get_arrays_from_past_and_seq(past, seq):
    x_array = []
    y_array = []
    dir_imgs = past + str(seq) + "/imgs/"

    with open(past + str(seq) + "/annotations.xml", "rb") as org_file:
        dict_file = xmltodict.parse(org_file)

    arr_plants = dict_file["annotations"]["image"]

    file = arr_plants[43]

    # for file in arr_plants:
    try:
        name_img = file["@name"]
        x_min = file["box"]
        img = Image.open(dir_imgs + name_img)
        img = img.resize((img_width, img_height)) # 0.3 = 576x324 --- 0.2 = 384x216 --- 0.15 = 288x162
        x_array.append(img)
        y_array.append(1)

    except:
        print("QUAL = ", len(y_array))
        name_img = file["@name"]
        img = Image.open(dir_imgs + name_img)
        img = img.resize((img_width, img_height))
        rotated_image1 = img.rotate(90) 
        img.show()
        rotated_image1.show()
        rotated_image1 = img.rotate(180)
        rotated_image1.show()
        rotated_image1 = img.rotate(270)
        rotated_image1.show()
        # rotated_image1 = zoom_at(rotated_image1, 120, 120, 1.5)
        # rotated_image1 = rotated_image1.resize((img_width, img_height))
        # rotated_image1.show()
        if flag == "Duplicated":
            print("Just to be sure")
            x_array.append(rotated_image1)
            y_array.append(0)
        x_array.append(img)
        y_array.append(0)

    return x_array, y_array

past_and_last_seq_0 = ("RumexWeeds/20210806_hegnstrup/seq", 17)
past_and_last_seq_1 = ("RumexWeeds/20210806_stengard/seq", 20)
past_and_last_seq_2 = ("RumexWeeds/20210807_lundholm/seq", 28)
past_and_last_seq_3 = ("RumexWeeds/20210908_lundholm/seq", 13)
past_and_last_seq_4 = ("RumexWeeds/20211006_stengard/seq", 15)

x_train = []
y_train = []

x_test = []
y_test = []

train = past_and_last_seq_2
test = past_and_last_seq_0
# for i in range(train[1]+1):
x_aux, y_aux = get_arrays_from_past_and_seq(train[0], 0)
x_train.extend(x_aux)
y_train.extend(y_aux)

# for i in range(test[1]+1):
# 	x_aux, y_aux = get_arrays_from_past_and_seq(test[0], i)
# 	x_test.extend(x_aux)
# 	y_test.extend(y_aux)