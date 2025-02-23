# from flask import Flask, request, jsonify
import os

import LCD_1in44
from PIL import Image, ImageDraw, ImageFont

# app = Flask(__name__)

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

def val_deter(x, LCD):
    if x >= 70:
        sad(LCD)
    elif x>=40:
        medium(LCD)
    else:
        happy(LCD)


# @app.route('/api/', methods=['POST'])
# def receive_value():
#     data = request.get_json()
#     if not data or 'value' not in data:
#         return jsonify({"error": "Missing required field: 'value'"}), 400

#     value = data["value"]
#     if not value or not isinstance(value, int):
#         return jsonify({'error': 'Value must be an integer'}), 400
#     # Optionally, print the value to the server's console
#     print(f"Received value: {value}")
#     val_deter(value, LCD)


#     # Respond with a success message
#     return jsonify({'message': f"Value {value} received successfully"}), 200

# if __name__ == '__main__':
#     global LCD
#     LCD = init()  # Correctly assign the global LCD
#     port = int(os.environ.get('PORT', 8080))
#     app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)


if __name__ == '__main__':
    global LCD
    LCD = init()  # Correctly assign the global LCD
    val_deter(5, LCD)
