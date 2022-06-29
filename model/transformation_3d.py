from enum import Enum
import numpy as np
import math

class Rotation3DType(Enum):
	OBJECT_CENTER = 1
	WORLD_CENTER = 2
	GIVEN_POINT = 3

class RotationAxis(Enum):
	X = 1
	Y = 2
	Z = 3
	U = 4

class Transformation3DType(Enum):
	TRANSLATION = 1
	SCALING = 2
	ROTATION = 3

class Transformation3D:
	def __init__(self, transformation_type):
		self.transformation_type = transformation_type

	def get_matrix(self):
		pass

	"""
	Funções que criam e retornam matrizes de transformação
	daos parametros
	"""
	def translation_matrix(x, y, z):
		return np.array(([1.0,  0.,  0., 0.],[ 0,  1.0,  0., 0.],[ 0.,  0.,  1., 0.], [x, y, z, 1.0]))

	def scaling_matrix(x, y, z):
	    return np.array(([x,  0.,  0., 0.],[ 0,  y,  0., 0.],[ 0., 0., z, 0.],[ 0., 0., 0., 1.0]))


	def rotation_x_matrix(rad, center = None):
		if(center == None):
			(x,y,z) = (0,0,0)
		else:
			(x,y,z) = center

		_sin = (math.sin(rad))
		_cos = (math.cos(rad))

		return np.array(([1.0, 0., 0., 0.], [ 0., _cos,  _sin,  0.],[0., - _sin,  _cos,  0.],[0, (y-(_cos*y)+(_sin*z)), (z-(_cos*z)-(_sin*y)),  1.]))

	def rotation_y_matrix(rad, center = None):
		if(center == None):
			(x,y,z) = (0,0,0)
		else:
			(x,y,z) = center

		_sin = (math.sin(rad))
		_cos = (math.cos(rad))

		return np.array(([_cos, 0., -_sin, 0.],[0., 1.0,  0.,  0.], [ _sin, 0.,  _cos,  0.],[ (x-(_cos*x)-(_sin*z)), 0., (z-(_cos*z)+(_sin*x)),  1.]))


	def rotation_z_matrix(rad, center = None):
		if(center == None):
			(x,y,z) = (0,0,0)
		else:
			(x,y,z) = center

		_sin = (math.sin(rad))
		_cos = (math.cos(rad))

		return np.array(([ _cos,  _sin,  0., 0.],[ -_sin,  _cos,  0., 0.],[ 0.,  0.,  1., 0.],[(x-(_cos*x)+(_sin*y)), (y-(_cos*y)-(_sin*x)), 0.,  1.]))


	def unit_vector(vector):
		norm = np.linalg.norm(vector)
		if (norm == 0):
			return None
		return (vector[0]/norm, vector[1]/norm, vector[2]/norm)


	def rotation_given_axis_matrix(rad, a, center=None):
		_sin = math.sin(rad)
		_cos = math.cos(rad)

		a = Transformation3D.unit_vector(a)
		if(a == None):
			print("erro")
			return None


		aa = np.array((
		[a[0]*a[0], a[0]*a[1], a[0]*a[2]],
		[a[1]*a[0], a[1]*a[1], a[1]*a[2]],
		[a[2]*a[0], a[2]*a[1], a[2]*a[2]]
		))

		A =  np.array((
		[0,     -a[2], a[1] ],
		[a[2],  0,     -a[0]],
		[-a[1], a[0],  0    ]
		))

		identity = np.array(([1,0,0],[0,1,0],[0,0,1]))

		m1 = identity * _cos
		m2 = aa * (1-_cos)
		m3 = A * (_sin)

		R = m1 + m2 + m3
		R = np.hstack((R, [[0],[0],[0]]))
		R = np.vstack((R, [0,0,0,1]))

		rotation_matrix = None

		if(center != None):
			(x,y,z) = center
			translation_center= Transformation3D.translation_matrix(-x, -y, -z)
			translation_back = Transformation3D.translation_matrix(x, y, z)
			rotation_matrix = translation_center @ R @ translation_back
		else:
			rotation_matrix = R



		return rotation_matrix


	"""
	Transforma todos os pontos dado uma matriz de transformação
	"""
	def transform(coords, transformation_matrix):
		if(len(transformation_matrix)>0):
			for i in range(len(coords)):
				coords[i] = Transformation3D.transform_3d_point(coords[i], transformation_matrix)


	"""
	Dada uma lista de matrizes de transformação
	retorna a matriz resultante
	"""
	def compose_matrix(transformation_matrix_list):
		transformation_matrix_composition = []
		if(len(transformation_matrix_list) > 0):
			transformation_matrix_composition = transformation_matrix_list[0]

			for i in range(len(transformation_matrix_list)-1):
				transformation_matrix_composition = transformation_matrix_composition @ transformation_matrix_list[i+1]

		return transformation_matrix_composition


	"""
	Retorna o ponto transformado dado um ponto e uma matriz de transformação
	"""
	def transform_3d_point(point, transformation_matrix):
		p = np.array(([point[0],point[1],point[2], 1]))
		[x1,y1,z1,_] = p @ transformation_matrix
		return (x1,y1,z1)

	"""
	Retorna o ponto transformado dado um ponto e uma matriz de transformação
	"""
	def transform_point(point, transformation_matrix):
		p = np.array(([point[0],point[1],point[2], 1]))
		return p @ transformation_matrix


class Rotation3D(Transformation3D):
	def __init__(self, rotation_type, rotation_axis, axis_vector, degrees, x, y, z):
		super().__init__(Transformation3DType.ROTATION)
		self.rotation_type = rotation_type
		self.rotation_axis = rotation_axis
		self.rad = math.radians(degrees)
		self.center = (x,y,z)
		self.x = x
		self.y = y
		self.z = z
		self.axis_vector = axis_vector

	def get_matrix(self, x = None, y = None, z = None):
		rotation_matrix = None

		if(self.rotation_type == Rotation3DType.GIVEN_POINT):
			center = self.center
		elif(self.rotation_type == Rotation3DType.OBJECT_CENTER):
			center = (x,y,z)
		else:
			center = (0,0,0)

		if(self.rotation_axis == RotationAxis.X):
			rotation_matrix = Transformation3D.rotation_x_matrix(self.rad, center)
		elif(self.rotation_axis == RotationAxis.Y):
			rotation_matrix = Transformation3D.rotation_y_matrix(self.rad, center)
		elif(self.rotation_axis == RotationAxis.Z):
			rotation_matrix = Transformation3D.rotation_z_matrix(self.rad, center)
		elif(self.rotation_axis == RotationAxis.U):
			rotation_matrix = Transformation3D.rotation_given_axis_matrix(self.rad, self.axis_vector, center)

		return rotation_matrix

	def __str__(self):
		return str((self.transformation_type, self.rotation_type.name, self.rotation_axis ,self.rad, self.center))


class Translation3D(Transformation3D):
	def __init__(self, x, y, z):
		super().__init__(Transformation3DType.TRANSLATION)
		self.x = x
		self.y = y
		self.z = z

	def get_matrix(self, x = None, y = None, z = None):
		if(x == None or y == None or z == None):
			x = self.x
			y = self.y
			z = self.z

		return Transformation3D.translation_matrix(x, y, z)

	def __str__(self):
		return str((self.transformation_type, self.x, self.y))

class Scaling3D(Transformation3D):
	def __init__(self, factor):
		super().__init__(Transformation3DType.SCALING)
		self.factor = factor

	def get_matrix(self, x = 0, y = 0, z = 0):
		if(x != 0 or y!= 0 or z!= 0):
			return Transformation3D.translation_matrix(-x, -y, -z) @ Transformation3D.scaling_matrix(self.factor,self.factor,self.factor) @ Transformation3D.translation_matrix(x, y, z)
		else:
			return Transformation3D.scaling_matrix(self.factor,self.factor,self.factor)


	def __str__(self):
		return str((self.transformation_type, self.factor))

