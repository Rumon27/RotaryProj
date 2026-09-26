import cv2 as cv 
import numpy as np
import matplotlib.pyplot as plt 
import os 

def gaussianKernel(size, sigma):
     kernel = cv.getGaussianKernel(size, sigma)
     kernel = np.outer(kernel, kernel)
     return kernel

def gaussianFiltering():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/kessa-cat-1647775_1920.jpg')
     img = cv.imread(imgpath)

     n = 51
     fig = plt.figure()
     plt.subplot(121)
     kernel = gaussianKernel(n, 8)
     plt.imshow(kernel)

     ax = fig.add_subplot(122, projection='3d')
     x = np.arange(0,n,1)
     y = np.arange(0,n,1)
     X,Y = np.meshgrid(x, y)
     ax.plot_surface(X, Y, kernel, cmap='viridis')
     plt.show()


if __name__=="__main__":
     gaussianFiltering()

