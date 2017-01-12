#! /usr/bin/python2
# -*- coding: utf-8 -*-
#from pythonvideoannotator_models.video.objects import Objects

import cv2, os
from pythonvideoannotator_models.models.video.objects.object2d import Object2D
from pythonvideoannotator_models.models.video.image import Image
from pythonvideoannotator_models.models.imodel import IModel


class VideoBase(IModel):

	def __init__(self, project):
		super(IModel, self).__init__()

		self._project  = project
		self._project  += self

		self.name 	   = ''
		self._filename = None
		self._videocap = None
		
		self._childrens = []
			

	######################################################################################
	#### FUNCTIONS #######################################################################
	######################################################################################

	def __len__(self): return len(self._childrens)
	def __str__(self): return self.name

	def __add__(self, obj):
		if isinstance(obj, Object2D) or isinstance(obj, Image): self._childrens.append(obj)
		return self

	def __sub__(self, obj):
		if isinstance(obj, Object2D) or isinstance(obj, Image):  self._childrens.remove(obj)
		return self

	def create_object(self): return Object2D(self)
	def create_image(self):  return Image(self)

	######################################################################################
	#### PROPERTIES ######################################################################
	######################################################################################

	@property
	def objects(self):
		for child in self._childrens:
			if isinstance(child, Object2D): yield child

	@property
	def images(self): 
		for child in self._childrens:
			if isinstance(child, Image): yield child

	@property
	def filepath(self): return self._filename
	@filepath.setter
	def filepath(self, value): 
		self._filename = value
		self._videocap = cv2.VideoCapture(value)
		filename 	   = os.path.basename(value)
		self.name, _   = os.path.splitext(filename)


	@property
	def filename(self): return os.path.basename(self.filepath)
	
	
	@property
	def video_capture(self): return self._videocap

	@property
	def total_frames(self): return self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

	@property
	def project(self): 	return self._project

	@property
	def directory(self): return os.path.join( self.project.directory, 'videos', self.name )
	
