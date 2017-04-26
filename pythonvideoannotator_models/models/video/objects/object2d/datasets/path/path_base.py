import cv2, math, os, numpy as np
from pythonvideoannotator_models.models.video.objects.object2d.utils.interpolation import interpolate_positions
from pythonvideoannotator_models.models.video.objects.object2d.datasets.dataset import Dataset



class PathBase(Dataset):

	def __init__(self, object2d):
		super(PathBase, self).__init__(object2d)

		self.name 		= 'path({0})'.format(len(object2d))  if len(object2d)>0 else 'path'
		self._points 	= [] #path of the object

		self._tmp_points= [] #store a temporary path to pre-visualize de interpolation
		self._sel_pts 	= [] #store the selected points

		
	######################################################################
	### CLASS FUNCTIONS ##################################################
	######################################################################

	def __len__(self): 					 return len(self._points)
	def __getitem__(self, index): 		 return self._points[index] if index<len(self) else None
	def __setitem__(self, index, value): 
		if index<len(self): self._points[index] = None
	def __str__(self):					 return self.name

	######################################################################
	### DATA MODIFICATION AND ACCESS #####################################
	######################################################################

	def calculate_tmp_interpolation(self): 
		#store a temporary path to visualize the interpolation 
		begin 		= self._sel_pts[0]
		end 		= self._sel_pts[1]
		positions 	= [[i, self.get_position(i)] for i in range(begin, end+1) if self.get_position(i) is not None]

		if len(positions)>=2:
			positions   = interpolate_positions(positions, begin, end, interpolation_mode=self.interpolation_mode)
			self._tmp_points= [pos for frame, pos in positions]
			return True
		else:
			return False

	def delete_range(self, begin, end):
		for index in range(begin+1, end):
			if index <= len(self) and self[index] != None: self[index] = None
			self._tmp_points= []

	def interpolate_range(self, begin, end, interpolation_mode=None):
		positions = [[i, self.get_position(i)] for i in range(begin, end+1) if self.get_position(i) is not None]
		if len(positions)>2:
			positions = interpolate_positions(positions, begin, end, interpolation_mode)
			for frame, pos in positions: self.set_position(frame, pos[0], pos[1])
			self._tmp_points= []

	def get_velocity(self, index):
		p1 = self.get_position(index)
		p2 = self.get_position(index-1)
		if p1 is None or p2 is None: return None
		return p2[0]-p1[0], p2[1]-p1[1]
		

	def get_acceleration(self, index):
		v1 = self.get_velocity(index)
		v2 = self.get_velocity(index-1)
		if v1 is None or v2 is None: return None
		return v2[0]-v1[0], v2[1]-v1[1]

	def get_position(self, index):
		if index<0 or index>=len(self): return None
		return self[index] if self[index] is not None else None

	def set_position(self, index, x, y):
		# add positions in case they do not exists
		if index >= len(self):
			for i in range(len(self), index + 1): self._points.append(None)

		if x is None or y is None: 
			self._points[index] = None
		else:
			# create a new moment in case it does not exists
			self._points[index] = int(round(x)),int(round(y))

	def set_data_from_blob(self,index, blob):
		if blob is None: 
			self.set_position(index, None, None)
		else:
			x, y = blob._centroid
			self.set_position(index, x, y)
			

	def collide_with_position(self, index, x, y, radius=20):
		p1 = self.get_position(index)
		if p1 is None: return False
		return math.sqrt((p1[0] - x)**2 + (p1[1] - y)**2) < radius
	
	######################################################################
	### VIDEO EVENTS #####################################################
	######################################################################

	def draw_circle(self, frame, frame_index):
		position = self.get_position(frame_index)
		if position != None:
			cv2.circle(frame, position[:2], 20, (255, 255, 255), 4, lineType=cv2.LINE_AA)  # pylint: disable=no-member
			cv2.circle(frame, position[:2], 20, (50, 50, 255), 1, lineType=cv2.LINE_AA)  # pylint: disable=no-member

			cv2.putText(frame, str(frame_index), position[:2], cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)  # pylint: disable=no-member
			cv2.putText(frame, str(frame_index), position[:2], cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)  # pylint: disable=no-member

	def draw_position(self, frame, frame_index):
		pos = self.get_position(frame_index)
		if pos is None: return
		
		cv2.circle(frame, pos, 8, (255,255,255), -1, lineType=cv2.LINE_AA)
		cv2.circle(frame, pos, 6, (100,0,100), 	 -1, lineType=cv2.LINE_AA)


	def draw(self, frame, frame_index):
		self.draw_position(frame, frame_index)

		# Draw the selected blobs
		for item in self._sel_pts: #store a temporary path for interpolation visualization
			self.draw_circle(frame, item)

		# Draw the selected path #store a temporary path for interpolation visualization
		if 1 <= len(self._sel_pts) == 2: #store a temporary path for interpolation visualization
			start = self._sel_pts[0] #store a temporary path for interpolation visualization
			end = frame_index if len(self._sel_pts)==1 else self._sel_pts[1]
			cnt = np.int32([p for p in self._points[start:end] if p is not None])
			cv2.polylines(frame, [cnt], False, (0,0,255), 1, lineType=cv2.LINE_AA)
		
		# Draw a temporary path
		if len(self._tmp_points)>=2:
			cnt = np.int32(self._tmp_points)
			cv2.polylines(frame, [cnt], False, (255, 0, 0), 1, lineType=cv2.LINE_AA)


	######################################################################
	### PROPERTIES #######################################################
	######################################################################

	@property
	def interpolation_mode(self): return None