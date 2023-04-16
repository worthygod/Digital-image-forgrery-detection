# -*- coding: utf-8 -*-
"""
Created on Thu feb  9 13:18:31 2023

@author: aniket shinde
         kavita rathod
         nishchal tayade
"""


import streamlit as st
import matplotlib.pyplot as plt
from tensorflow.keras.utils import normalize
from tensorflow.keras.models import *
import numpy as np
import pickle as pkl
from PIL import *
import cv2


#Function for ela 
def convert_to_ela_image(image, quality):
    temp_filename = 'temp_file.jpg'
    ela_filename = 'temp_ela_file.png'
    
    image.save(temp_filename, 'JPEG', quality = quality)
    temp_image = Image.open(temp_filename)
    
    ela_image = ImageChops.difference(image, temp_image)
    
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    
    return ela_image

#Function for filters 
import numpy as np
q = [4.0, 12.0, 2.0]
filter1 = [[0, 0, 0, 0, 0],
           [0, -1, 2, -1, 0],
           [0, 2, -4, 2, 0],
           [0, -1, 2, -1, 0],
           [0, 0, 0, 0, 0]]
filter2 = [[-1, 2, -2, 2, -1],
           [2, -6, 8, -6, 2],
           [-2, 8, -12, 8, -2],
           [2, -6, 8, -6, 2],
           [-1, 2, -2, 2, -1]]
filter3 = [[0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 1, -2, 1, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0]]


filter1 = np.asarray(filter1, dtype=float) / q[0]
filter2 = np.asarray(filter2, dtype=float) / q[1]
filter3 = np.asarray(filter3, dtype=float) / q[2]
    
filters = filter1+filter2+filter3



image_size = (128, 128)

def prepare_image(image_path):
    return np.array(convert_to_ela_image(image_path, 85).resize(image_size)).flatten() / 255.0


    
#Load model 
json_file = open('v1model.json', 'r')
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
# load weights into new model
model.load_weights("v1model.h5")


#Load model for phase 2 
# load json and create model
json_file2 = open('dunetm.json', 'r')
loaded_model_json = json_file2.read()
json_file2.close()
#load weights 
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("dunet.h5")

def predict(image,model) :
    im = Image.open(image)
    ela_img=prepare_image(im)
    ela_img=ela_img.reshape(1,128,128,3)
    prediction=model.predict(ela_img)
    
    return ela_img,prediction


def predict_region(img,model) :
    img=np.array(Image.open(img))
    temp_img_arr=cv2.resize(img,(512,512))
    temp_preprocess_img=cv2.filter2D(temp_img_arr,-1,filters)
    temp_preprocess_img=cv2.resize(temp_preprocess_img,(512,512))
    temp_img_arr=temp_img_arr.reshape(1,512,512,3)
    temp_preprocess_img=temp_preprocess_img.reshape(1,512,512,3)
    model_temp=model.predict([temp_img_arr,temp_preprocess_img])
    model_temp=model_temp[0].reshape(512,512)
    for i in range(model_temp.shape[0]) :
        for j in range(model_temp.shape[1]) :
            if model_temp[i][j]>0.75 :
                model_temp[i][j]=1.0
            else :
                model_temp[i][j]=0.0
                
    
    return model_temp



      

st.title("Image Forgery Detection (Copy-Move Forgery Detection)")
st.header("Upload a image to get whether image is forged or pristine")
# To View Uploaded Image
image_file = st.file_uploader("Upload Images", type=["png","jpg"])
# You don't have handy image 
if bool(image_file)==True :
    st.image(image_file)
    ela_img,pred=predict(image_file,model)
    st.text("ELA image for this image")
    st.image(ela_img)
    pred=pred[0]
    st.markdown("Probability of input image to be real is " + str(pred[0]))
    st.markdown("Probability of input image to be fake is " + str(1-pred[0]))
    
    if pred >= 0.5 :
        st.title("This is a pristine image")
    else :
        st.title("This is a fake image")
        predi=predict_region(image_file,loaded_model)
        st.image(predi)
        st.write("##### NOTE : Black region is part of image where original image may be tempered Please have a close look on these regions . Thankyou ❤️") 
        
        
else :
    ran_imageid=['Au_ani_00043','Au_sec_00040','Au_sec_30730','Tp_D_CRN_M_N_nat10129_cha00086_11522','Tp_D_CRN_S_N_cha10130_art00092_12187']
    st.text("")
    st.text("")
    st.text("You can download some sample images by clicking on the below links :")
    st.write("[link](https://drive.google.com/file/d/187K3FpyiTTcxDq8gFeE_U2E370BRbmNp/view?usp=share)")
    st.write("[link](https://drive.google.com/file/d/1K1UD0YWfp1-dUmIrbOayAQIhKX7HKvqw/view?usp=share)")
    st.write("[link](https://drive.google.com/file/d/14EafkfByi9XZ4tLJZ4O3JfQv1bWJmnYE/view?usp=share)")
    st.text("")
    st.text("")
      
    
