# **Finding Lane Lines on the Road** 

Overview
---

When we drive, we use our eyes to decide where to go.  The lines on the road that show us where the lanes are act as our constant reference for where to steer the vehicle.  Naturally, one of the first things we would like to do in developing a self-driving car is to automatically detect lane lines using an algorithm.

This repo contains my solution to Udacity's self-drving course project, [Finding Lane Lines on the Road](https://github.com/udacity/CarND-LaneLines-P1)

---

### Pipeline Description

#### 1. Color Filtering

In the assignment, highway lanes are in either yellow or white. To remove noice, the first step is to only select yellow and white color in the RGB space.

Original images vs. Color filtered images

