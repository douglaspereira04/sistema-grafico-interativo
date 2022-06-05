from enum import Enum
import numpy as np
import math

class RotationType(Enum):
	OBJECT_CENTER = 1
	WORLD_CENTER = 2
	GIVEN_POINT = 3

class TransformationType(Enum):
	TRANSLATION = 1
	SCALING = 2
	ROTATION = 3

class Transformation:
	def __init__(self, transformation_type):
		self.transformation_type = transformation_type

	def get_matrix(self):
		pass

	"""
	Funções que criam e retornam matrizes de transformação
	daos parametros
	"""
	def translation_matrix(x, y):
		return [[1.0,  0.,  0.],[ 0,  1.0,  0.],[ x,  y,  1.]]

	def scaling_matrix(x, y):
	    return [[x,  0.,  0.],[ 0,  y,  0.],[ 0., 0., 1.]]

	def rotation_matrix(degrees):
		_sin = (math.sin(math.radians(degrees)))
		_cos = (math.cos(math.radians(degrees)))

		return [[ _cos,  -_sin,  0.],[ _sin,  _cos,  0.],[ 0.,  0.,  1.]]

	"""
	Transforma todos os pontos dado uma matriz de transformação
	Recalcula o centroid
	"""
	def transform(coords, transformation_matrix):
		if(len(transformation_matrix)>0):
			for i in range(len(coords)):
				coords[i] = Transformation.transform_point(coords[i], transformation_matrix)


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
		(x,y) = point
		[x1,y1,z1] = np.matmul([x,y,1],transformation_matrix)
		return (x1,y1)


class Rotation(Transformation):
	def __init__(self, rotation_type, degrees, x, y):
		super().__init__(TransformationType.ROTATION)
		self.rotation_type = rotation_type
		self.degrees = degrees
		self.x = x
		self.y = y

	def get_matrix(self, x = None, y = None):
		if(x == None or y == None):
			x = self.x
			y = self.y

		if(self.rotation_type == RotationType.WORLD_CENTER):
			return Transformation.rotation_matrix(self.degrees)
		else:
			parcial = np.matmul(Transformation.translation_matrix(-x, -y),Transformation.rotation_matrix(self.degrees))
			return np.matmul(parcial,Transformation.translation_matrix(x, y))

	def __str__(self):
		return str((self.transformation_type, self.rotation_type.name, self.degrees, self.x, self.y))


class Translation(Transformation):
	def __init__(self, x, y):
		super().__init__(TransformationType.TRANSLATION)
		self.x = x
		self.y = y

	def get_matrix(self, x = None, y = None):
		if(x == None or y == None):
			x = self.x
			y = self.y

		return Transformation.translation_matrix(x, y)

	def __str__(self):
		return str((self.transformation_type, self.x, self.y))

class Scaling(Transformation):
	def __init__(self, factor):
		super().__init__(TransformationType.SCALING)
		self.factor = factor

	def get_matrix(self, x = 0, y = 0):
		parcial = np.matmul(Transformation.translation_matrix(-x, -y),Transformation.scaling_matrix(self.factor,self.factor))
		return np.matmul(parcial,Transformation.translation_matrix(x, y))


	def __str__(self):
		return str((self.transformation_type, self.factor))

