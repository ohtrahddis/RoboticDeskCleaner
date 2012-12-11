from numpy import *
from numpy.linalg import *

L1 = 11 #link lengths in cm
L2 = 14
L3 = 9
L4 = 17 #this will be our z height

def inversekinematics(x,y):
	z = L4 #this positions the end effector so our grippor is at 0 height
	A0=arctan(y/x)
	zT=z #height 
	wT=sqrt(x**2+y**2)#Distance 
	AG=radians(0)
	w2 = wT - L3*cos(AG);
	z2 = zT - L3*sin(AG);
	L12 = sqrt(( w2 )**2 + ( z2 )**2);
	A12 = arctan (z2 / w2);
	A1 = arccos ( ( ( L1 )**2 + ( L12 )**2 - ( L2)**2) / (2 * L1 * L12 )) + A12
	w1 = L1*cos(A1);
	z1 = L1*sin(A1);
	A2 = arctan ( ( z2 - z1 ) / ( w2 - w1 ) ) - A1
	A3 = AG - A1 - A2
	A0=degrees(A0)
	A1=degrees(A1)
	A2=degrees(A2)
	A3=degrees(A3)
	return [A0,A1,A2,A3]

