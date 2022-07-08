from enum import Enum
import numpy as np
import math

class Rotation2DType(Enum):
	OBJECT_CENTER = 1
	WORLD_CENTER = 2
	GIVEN_POINT = 3

class Transformation2DType(Enum):
	TRANSLATION = 1
	SCALING = 2
	ROTATION = 3

class Transformation2D:
	def __init__(self, transformation_type):
		self.transformation_type = transformation_type

	def get_matrix(self):
		pass

	"""
	Funções que criam e retornam matrizes de transformação
	daos parametros
	"""
	def translation_matrix(x, y):
		return np.array(([1.0,  0.,  0.],[ 0,  1.0,  0.],[ x, y, 1.0]))

	def scaling_matrix(x, y, center = None):
		if(center == None):
			(cx,cy) = (0.,0.)
		else:
			(cx,cy) = center

		return np.array([[x,  0.,  0.],[0.,  y,  0.],[(cx-(x*cx)), (cy-(y*cy)), 1.0]])

	def rotation_matrix(rad, center = None):
		if(center == None):
			(x,y) = (0.,0.)
		else:
			(x,y) = center

		_sin = (math.sin(rad))
		_cos = (math.cos(rad))

		return np.array(([ _cos,  -_sin,  0.],[ _sin,  _cos,  0.],[ (x-(_cos*x)-(_sin*y)),  (y-(_cos*y)+(_sin*x)),  1.]))


	def unit_vector(vector):
		norm = np.linalg.norm(vector[:2])
		if (norm == 0):
			return None
		return [vector[0]/norm, vector[1]/norm,1]

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
	def transform_point(point, transformation_matrix):
		return point.dot(transformation_matrix)


class Rotation2D(Transformation2D):
	def __init__(self, rotation_type, degrees, x, y):
		super().__init__(Transformation2DType.ROTATION)
		self.rotation_type = rotation_type
		self.rad = math.radians(degrees)
		self.center = (x,y)
		self.x = x
		self.y = y

	def get_matrix(self, x = None, y = None):
		
		if(self.rotation_type == Rotation2DType.GIVEN_POINT):
			center = self.center
		elif(self.rotation_type == Rotation2DType.OBJECT_CENTER):
			center = (x,y)
		else:
			center = (0.,0.)

		return Transformation2D.rotation_matrix(self.rad, center)

	def __str__(self):
		return str((self.transformation_type, self.rad, self.center))


class Translation2D(Transformation2D):
	def __init__(self, x, y):
		super().__init__(Transformation2DType.TRANSLATION)
		self.x = x
		self.y = y

	def get_matrix(self, x = None, y = None):
		if(x == None or y == None):
			x = self.x
			y = self.y

		return Transformation2D.translation_matrix(x, y)

	def __str__(self):
		return str((self.transformation_type, self.x, self.y))

class Scaling2D(Transformation2D):
	def __init__(self, factor):
		super().__init__(Transformation2DType.SCALING)
		self.factor = factor

	def get_matrix(self, x = 0., y = 0.):
		center = (0., 0.)
		if(x != 0. or y!= 0.):
			center = (x,y)

		return Transformation2D.scaling_matrix(self.factor,self.factor,center)


	def __str__(self):
		return str((self.transformation_type, self.factor))

