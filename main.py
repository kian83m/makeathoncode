# import LCD_1in44
# import time

# from PIL import Image,ImageDraw,ImageFont,ImageColor

# #try:
# def main():
#     LCD = LCD_1in44.LCD()

#     print ("**********Init LCD**********")
#     Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
#     LCD.LCD_Init(Lcd_ScanDir)
#     LCD.LCD_Clear()

#     image = Image.new("RGB", (LCD.width, LCD.height), "WHITE")
#     draw = ImageDraw.Draw(image)
#     #font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 16)
#     print ("***draw line")
#     draw.line([(0,0),(127,0)], fill = "BLUE",width = 5)
#     draw.line([(127,0),(127,127)], fill = "BLUE",width = 5)
#     draw.line([(127,127),(0,127)], fill = "BLUE",width = 5)
#     draw.line([(0,127),(0,0)], fill = "BLUE",width = 5)
#     print ("***draw rectangle")
#     draw.rectangle([(18,10),(110,20)],fill = "RED")

#     print ("***draw text")
#     draw.text((33, 22), 'WaveShare ', fill = "BLUE")
#     draw.text((32, 36), 'Electronic ', fill = "BLUE")
#     draw.text((28, 48), '1.44inch LCD ', fill = "BLUE")

#     LCD.LCD_ShowImage(image,0,0)
#     time.sleep(3)

#     image = Image.open('time.bmp')
#     LCD.LCD_ShowImage(image,0,0)
#     time.sleep(3)
# 	#while (True):
	
# if __name__ == '__main__':
#     main()


import LCD_1in44
import time
from PIL import Image, ImageDraw, ImageFont



def sad(LCD):
    LCD.LCD_Clear()

    # Create a new image with a red background
    image = Image.new("RGB", (LCD.width, LCD.height), "RED")
    draw = ImageDraw.Draw(image)

    # Draw two eyes for the sad face
    # Left eye
    draw.ellipse((40, 40, 50, 50), fill="WHITE", outline="BLACK")
    # Right eye
    draw.ellipse((78, 40, 88, 50), fill="WHITE", outline="BLACK")

    # Draw a frowning mouth using an arc
    # The arc is drawn from 200 to 340 degrees to form a downward curve (frown)
    draw.arc((40, 70, 90, 110), start=200, end=340, fill="WHITE", width=2)

    # Draw text "sad" below the face
    
    # Display the image on the LCD
    LCD.LCD_ShowImage(image, 0, 0)


def happy(LCD):
    LCD.LCD_Clear()

    # Create a new image with a red background
    image = Image.new("RGB", (LCD.width, LCD.height), "LawnGreen")
    draw = ImageDraw.Draw(image)

    # Draw two eyes for the sad face
    # Left eye
    draw.ellipse((40, 40, 50, 50), fill="WHITE", outline="BLACK")
    # Right eye
    draw.ellipse((78, 40, 88, 50), fill="WHITE", outline="BLACK")

    # Draw a frowning mouth using an arc
    # The arc is drawn from 200 to 340 degrees to form a downward curve (frown)
    draw.arc((40, 60, 90, 100), start=20, end=160, fill="WHITE", width=2)

    # Draw text "sad" below the face
    # draw.text((50, 115), "sad", fill="WHITE")
    
    # Display the image on the LCD
    LCD.LCD_ShowImage(image, 0, 0)

def medium(LCD):
    LCD.LCD_Clear()

    # Create a new image with a red background
    image = Image.new("RGB", (LCD.width, LCD.height), "ORANGE")
    draw = ImageDraw.Draw(image)

    # Draw two eyes for the sad face
    # Left eye
    draw.ellipse((40, 40, 50, 50), fill="WHITE", outline="BLACK")
    # Right eye
    draw.ellipse((78, 40, 88, 50), fill="WHITE", outline="BLACK")

    # Draw a frowning mouth using an arc
    # The arc is drawn from 200 to 340 degrees to form a downward curve (frown)
    draw.line((40, 90, 90, 90), fill="WHITE", width=2)

    # Draw text "sad" below the face
    # draw.text((50, 115), "sad", fill="WHITE")
    
    # Display the image on the LCD
    LCD.LCD_ShowImage(image, 0, 0)

def init():
    LCD = LCD_1in44.LCD()
    print("********** Init LCD **********")
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # Default scan direction
    LCD.LCD_Init(Lcd_ScanDir)
    return LCD

def val_deter(x):
    if x > 80:
        happy()
    elif x>40:
        medium()
    else:
        sad()


def main():
    # Initialize the LCD display
    LCD = init()

    while (True):
        x = int(input())
        val_deter(x)
if __name__ == '__main__':
    main()
