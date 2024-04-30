# Importing required modules 
from PIL import Image 
import pywhatkit 

# Store path of image in input_path 
input_path = 'skull.png'

# Processing image 
input = Image.open(input_path) 

# Convert image to text form 
pywhatkit.image_to_ascii_art(input_path,'skull') 

# read word art text file 
read_file = open("skull.txt","r") 

# Print word art generated file 
print(read_file.read()) 
