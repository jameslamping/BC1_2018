Steps within the JSON pipeline are as follows:

1) Data is reprojected into UTM Zone 11N so that all units are uniform in X, Y, and Z.

2) Classifications are wiped clean and a value of 0 is applied to the Classification dimension for every point. 

3) The Extended Local Minimum algorithm (Chen 2012) is run to identify low noise points that will impact ground segmentation areas. This classified noise points with a value of 7.

4) Outliers are filtered into class 7.

5) The Simple Morphological Filter (Pingel 2013) performs ground segmentation. Here we specify that noise is ignored in class 7 and the last option considers only last returns for ground segmentation where information is available.

5) Ground returns are extracted to create a digital terrain model (DTM) using a range filter for class 2.