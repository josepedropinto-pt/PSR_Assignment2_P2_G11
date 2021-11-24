# PSR_2021_Ar_Paint
This project is based on a powerful library called OpenCV that has tools to help with image processing. It is a mix of two different programs that together will allow the creation of an Augmented Reality Paint! Following, we will give some insight on how they work.

## Color segmenter
The color segmenter is the first requirement to do the setup of the AR Paint. Basically, we have 6 trackbars that we will use to define the max and min of the **BGR**  (blue, green and red) or **HSV** (hue, saturation and value) values in order to segmentate the pixels of the color of the object that we will use as a brush. As soon as we are set with the values, we save this data in a library called *limits* as a *.json* file and then we move on to the next program, AR Paint.

### How to use 

```text
optional arguments:
  -h, --help            show this help message and exit
  -hsv, --segmentate_in_hsv
```

***

## AR Paint

Use a colored object to paint the world around you!

This program allows you to use an object of your choice as a brush and paint on a white canvas by moving the object in the air as it is being recorded by a webcam. You may choose to use the augmented reality mode, which lets you paint on the live video of your camera, as opposed to a white canvas. Your world becomes your canvas.

**NOTE**: *To use this program, you need to create a limits.json file using the previous program, Color Segmenter.*

### How to use 

To run the code, you need to pass in the required argument -j, of json file path. You may also pass in some additional arguments, as follows.

```text
optional arguments:
  -h, --help            show this help message
                        and exit
  -j JSON_JSON, --json_JSON JSON_JSON
                        Full path to json file.
  -usp, --use_shake_prevention
                        To use shake prevention.
  -ar, --augmented_reality
                        To draw on displayed
                        frame
  -m, --mirror_image    Mirror the image
                        captured by camera
  -pn COLOR_BY_NUMBERS, --color_by_numbers COLOR_BY_NUMBERS
                        Path to file to paint by
                        numbers
  -hp, --hand_painting  Using finger as pencil

```

***
Trabalho 2 da unidade curricular de Programação de Sistemas Robóticos, Mestrado Integrado em Engenharia Mecânica, Universidade de Aveiro.
Trabalho realizado por:

- Jose Pedro Pinto
- Pedro Carvalho
- Vinicius Campos