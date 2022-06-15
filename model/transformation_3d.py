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
		return [[1.0,  0.,  0., 0.],[ 0,  1.0,  0., 0.],[ 0.,  0.,  1., 0.], [x, y, z, 1.0]]

	def scaling_matrix(x, y, z):
	    return [[x,  0.,  0., 0.],[ 0,  y,  0., 0.],[ 0., 0., z, 0.],[ 0., 0., 0., 1.0]]


	def rotation_x_matrix(degrees):
		_sin = (math.sin(math.radians(degrees)))
		_cos = (math.cos(math.radians(degrees)))

		return [[1.0, 0., 0., 0.], [ 0., _cos,  _sin,  0.],[0., - _sin,  _cos,  0.],[0., 0.,  0.,  1.]]

	def rotation_y_matrix(degrees):
		_sin = (math.sin(math.radians(degrees)))
		_cos = (math.cos(math.radians(degrees)))

		return [[_cos, 0., -_sin, 0.],[0., 1.0,  0.,  0.], [ _sin, 0.,  _cos,  0.],[0., 0.,  0.,  1.]]


	def rotation_z_matrix(degrees):
		_sin = (math.sin(math.radians(degrees)))
		_cos = (math.cos(math.radians(degrees)))

		return [[ _cos,  _sin,  0., 0.],[ -_sin,  _cos,  0., 0.],[ 0.,  0.,  1., 0.], [0., 0., 0., 1.0]]

	def unit_vector(vector):
		return vector/np.linalg.norm(vector)

	def rotation_given_axis_matrix(degrees, a):
		_sin = (math.sin(math.radians(degrees)))
		_cos = (math.cos(math.radians(degrees)))

		a = Transformation3D.unit_vector(a)


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

		m1 = np.multiply(identity,_cos)
		m2 = np.multiply(aa,(1-_cos))
		m3 = np.multiply(A,(_sin))

		R = m1 + m2 + m3
		R = np.hstack((R, [[0],[0],[0]]))
		R = np.vstack((R, [0,0,0,1]))

		return R


	"""
	Transforma todos os pontos dado uma matriz de transformação
	"""
	def transform(coords, transformation_matrix):
		if(len(transformation_matrix)>0):
			for i in range(len(coords)):
				coords[i] = Transformation3D.transform_point(coords[i], transformation_matrix)


	"""
	Dada uma lista de matrizes de transformação
	retorna a matriz resultante
	"""
	def compose_matrix(transformation_matrix_list):
		transformation_matrix_composition = []
		if(len(transformation_matrix_list) > 0):
			transformation_matrix_composition = transformation_matrix_list[0]

			for i in range(len(transformation_matrix_list)-1):
				transformation_matrix_composition = np.matmul(transformation_matrix_composition,transformation_matrix_list[i+1])

		return transformation_matrix_composition


	"""
	Retorna o ponto transformado dado um ponto e uma matriz de transformação
	"""
	def transform_point(point, transformation_matrix):
		(x,y,z) = point
		[x1,y1,z1,_] = np.matmul([x,y,z,1],transformation_matrix)
		return (x1,y1,z1)


class Rotation3D(Transformation3D):
	def __init__(self, rotation_type, rotation_axis, degrees, x, y, z):
		super().__init__(TransformationType.ROTATION)
		self.rotation_type = rotation_type
		self.rotation_axis = rotation_axis
		self.degrees = degrees
		self.x = x
		self.y = y
		self.z = z

	def get_matrix(self, x = None, y = None, z = None, axis = None):
		rotation_matrix = None

		if(self.rotation_axis != RotationAxis.U):
			rotation_matrix = None

			if(self.rotation_axis == RotationAxis.X):
				rotation_matrix = Transformation3D.rotation_x_matrix(self.degrees)
			elif(self.rotation_axis == RotationAxis.Y):
				rotation_matrix = Transformation3D.rotation_y_matrix(self.degrees)
			elif(self.rotation_axis == RotationAxis.Z):
				rotation_matrix = Transformation3D.rotation_z_matrix(self.degrees)

			if(self.rotation_type == RotationType.GIVEN_POINT):
				rotation_matrix = np.matmul(Transformation3D.translation_matrix(-self.x, -self.y, -self.z), rotation_matrix)
				rotation_matrix = np.matmul(rotation_matrix,Transformation3D.translation_matrix(self.x, self.y, self.z))
			elif(self.rotation_type == RotationType.OBJECT_CENTER):
				rotation_matrix = np.matmul(Transformation3D.translation_matrix(-x, -y, -z), rotation_matrix)
				rotation_matrix = np.matmul(rotation_matrix,Transformation3D.translation_matrix(x, y, z))

		else:
			rotation_matrix = Transformation3D.rotation_given_axis_matrix(self.degrees, axis)

		return rotation_matrix

	def __str__(self):
		return str((self.transformation_type, self.rotation_type.name, self.rotation_axis ,self.degrees, self.x, self.y, self.z))


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
			parcial = np.matmul(Transformation3D.translation_matrix(-x, -y, -z),Transformation3D.scaling_matrix(self.factor,self.factor,self.factor))
			return np.matmul(parcial,Transformation3D.translation_matrix(x, y, z))
		else:
			return Transformation3D.scaling_matrix(self.factor,self.factor,self.factor)


	def __str__(self):
		return str((self.transformation_type, self.factor))

