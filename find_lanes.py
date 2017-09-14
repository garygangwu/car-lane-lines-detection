#importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import sys
import os
import math
from moviepy.editor import VideoFileClip

def keep_only_line_color(img):
  converted_img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
  lower = np.array([ 10,  0,100])
  upper = np.array([ 40,255,255])
  yellow_mask = cv2.inRange(converted_img, lower, upper)

  lower = np.array([  0, 200, 0])
  upper = np.array([255,255,255])
  white_mask = cv2.inRange(converted_img, lower, upper)

  mask = cv2.bitwise_or(yellow_mask, white_mask)

  return cv2.bitwise_and(converted_img, converted_img, mask = mask)


def grayscale(img):
  """Applies the Grayscale transform
  This will return an image with only one color channel
  but NOTE: to see the returned image as grayscale
  (assuming your grayscaled image is called 'gray')
  you should call plt.imshow(gray, cmap='gray')"""
  return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  # Or use BGR2GRAY if you read an image with cv2.imread()
  # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def canny(img, low_threshold, high_threshold):
  """Applies the Canny transform"""
  return cv2.Canny(img, low_threshold, high_threshold)

def gaussian_blur(img, kernel_size):
  """Applies a Gaussian Noise kernel"""
  return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def region_of_interest(img, vertices):
  """
  Applies an image mask.

  Only keeps the region of the image defined by the polygon
  formed from `vertices`. The rest of the image is set to black.
  """
  #defining a blank mask to start with
  mask = np.zeros_like(img)

  #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
  if len(img.shape) > 2:
    channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
    ignore_mask_color = (255,) * channel_count
  else:
    ignore_mask_color = 255

  #filling pixels inside the polygon defined by "vertices" with the fill color
  cv2.fillPoly(mask, vertices, ignore_mask_color)

  #returning the image only where mask pixels are nonzero
  masked_image = cv2.bitwise_and(img, mask)
  return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
  """
  NOTE: this is the function you might want to use as a starting point once you want to
  average/extrapolate the line segments you detect to map out the full
  extent of the lane (going from the result shown in raw-lines-example.mp4
  to that shown in P1_example.mp4).

  Think about things like separating line segments by their
  slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
  line vs. the right line.  Then, you can average the position of each of
  the lines and extrapolate to the top and bottom of the lane.

  This function draws `lines` with `color` and `thickness`.
  Lines are drawn on the image inplace (mutates the image).
  If you want to make the lines semi-transparent, think about combining
  this function with the weighted_img() function below
  """
  for line in lines:
    for x1,y1,x2,y2 in line:
      cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
  """
  `img` should be the output of a Canny transform.

  Returns an image with hough lines drawn.
  """
  return cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)

# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, a=0.8, b=1., l=0.):
  """
  `img` is the output of the hough_lines(), An image with lines drawn on it.
  Should be a blank image (all black) with lines drawn on it.

  `initial_img` should be the image before any processing.

  The result image is computed as follows:
  NOTE: initial_img and img must be the same shape!
  """
  return cv2.addWeighted(initial_img, a, img, b, l)


def filter_incorrect_lines(lines, x_max_len, y_max_len):
  ret = []
  for line in lines:
    l = line[0]
    x1 = l[0]
    y1 = l[1]
    x2 = l[2]
    y2 = l[3]
    if x1 == x2:
      continue
    m = (y2-y1) * 1.0 / (x2 - x1)
    if (x1 > x_max_len / 2 or x2 > x_max_len / 2) and m <= 0.5:
      continue
    if (x1 <= x_max_len / 2 or x2 <= x_max_len / 2) and m >= -0.5:
      continue

    b = y1 * 1.0 - m * x1
    x0 = -b / m
    if (x1 > x_max_len / 2 or x2 > x_max_len / 2) and x0 >= x_max_len * 0.3:
      continue
    if (x1 <= x_max_len / 2 or x2 <= x_max_len / 2) and x0 <= x_max_len * 0.7:
      continue

    ret.append(line)
  return np.array(ret)


def process_image(image, file_name=''):
  # NOTE: The output you return should be a color image (3 channel) for processing video below
  # TODO: put your pipeline here,
  # you should return the final output (image where lines are drawn on lanes)

  filtered_color_image = keep_only_line_color(image)
  #filtered_color_image = image
  if len(file_name) > 0:
    mpimg.imsave('test_images_output/filtered_' + file_name, filtered_color_image)

  gray = grayscale(filtered_color_image)
  blur_gray = gaussian_blur(gray, 5)
  if len(file_name) > 0:
    mpimg.imsave('test_images_output/gray_' + file_name, blur_gray)

  edges = canny(blur_gray, 50 , 150)
  if len(file_name) > 0:
    mpimg.imsave('test_images_output/edges_' + file_name, edges)

  imshape = image.shape
  vertices = np.array(
    [[(50,imshape[0]),(imshape[1]/2-50, imshape[0] * 0.6), (imshape[1]/2+50, imshape[0] * 0.6), (imshape[1]-50,imshape[0])]],
    dtype=np.int32)
  masked_edges = region_of_interest(edges, vertices)
  if len(file_name) > 0:
    mpimg.imsave('test_images_output/masked_edges_' + file_name, masked_edges)

  rho = 1 # distance resolution in pixels of the Hough grid
  theta = np.pi/180 # angular resolution in radians of the Hough grid
  threshold = 5     # minimum number of votes (intersections in Hough grid cell)
  min_line_len = 5 #minimum number of pixels making up a line
  max_line_gap = 150    # maximum gap in pixels between connectable line segments
  lines = hough_lines(masked_edges, rho, theta, threshold, min_line_len, max_line_gap)
  lines = filter_incorrect_lines(lines, imshape[1], imshape[0])

  line_image = np.copy(image)*0
  draw_lines(line_image, lines, color=[255, 0, 0], thickness=5)
  weighted_image = weighted_img(line_image, image)

  return weighted_image


def images():
  for file_name in os.listdir("test_images/"):
    image = mpimg.imread('test_images/' + file_name)
    weighted_image = process_image(image, file_name=file_name)
    print('This image is:', type(weighted_image), 'with dimensions:', weighted_image.shape)
    #print(lines)
    mpimg.imsave('test_images_output/' + file_name, weighted_image)


def videos():
  for file_name in os.listdir("test_videos/"):
    clip = VideoFileClip('test_videos/' + file_name)
    new_clip = clip.fl_image(process_image)
    output_file = 'test_videos_output/' + file_name
    new_clip.write_videofile(output_file, audio=False)


def main(argv):
  if len(argv) == 2 and argv[1].lower() == 'video':
    videos()
  else:
    images()

if __name__ == "__main__":
  main(sys.argv)
