import os
import xml
import datetime
import sys
import re
import win32api
import xml.etree.ElementTree as ET
import ffmpeg
from shutil import copy2

def prepare_workpaths_structure():
	structure = []
	possible_workpaths = ['!MP', '!MIHEEV_PAVLOV', '!WORKS', '!MIHEEV_PAVLOV_PROD']
	workpaths = [os.path.join(root_letter, x) for x in possible_workpaths if os.path.exists(os.path.join(root_letter, x))]
	for path in workpaths:
		structlocal = os.walk(path)
		for entry in structlocal:
			structure.append(entry)
	return structure

def check_drives():
	avaliable_letters = {'f', 'g', 'h', 'i', 'j','k','l'}
	drives = []
	for letter in avaliable_letters:
		if os.path.exists(letter + '://'):
			drives.append(letter + '://')
	return drives

def check_in_workpaths(filename):
	for line in workpathfiles:
		if filename in line[2]:
			print('File', filename, 'is already in ', line[0])
			return True
	return False

#def correct_date_2001(file):

def try_get_metadata_camera_name(infile):
	vid = ffmpeg.probe(infile)
	name = None
	if 'comment' in vid['format']['tags'].keys():
		name = vid['format']['tags']['comment']
	if 'encoder' in vid['format']['tags'].keys():
		name = vid['format']['tags']['encoder']
	return name

def check_metadata(infile):
	# print('checking', infile)
	camera = try_get_metadata_camera_name(infile)
	if camera:
		if camera == 'FUJIFILM DIGITAL CAMERA X-T4':
			return 'XT4'
		if camera == 'FUJIFILM DIGITAL CAMERA X-T3':
			return 'XT3'
	else:
		return None


def take_flash(path):
	print('Work drive:', path)
	structure = os.walk(path)
	for line in structure:
		if line[2]:
			for fil in line[2]:
				extension = fil.split('.')[-1].lower()

				if extension not in extlist:
					continue

				name = fil.split('.')[0]
				xmlp = line[0]+ '\\' + name + 'M01.XML'
#				correct_date_2001(line[0] + '\\' + fil)
				fildateraw = os.path.getctime(line[0] + '\\' + fil)

				if fildateraw == 315507600:
					# Почему-то зум не пишет дату создания
					# Вместо этого пишет дату модификации
					fildateraw = os.path.getmtime(line[0] + '\\' + fil)
				if extension == 'wav' and name.lower().startswith('rec'):
					tempnowyear = datetime.datetime.now().year
					tempfildaterawyear = datetime.datetime.fromtimestamp(fildateraw).year
					if tempfildaterawyear + 20 == tempnowyear:
						z = datetime.datetime.fromtimestamp(fildateraw)
						fildateraw = datetime.datetime.timestamp(datetime.datetime(z.year + 20, z.month, z.day, z.hour, z.minute, z.second))

				days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(fildateraw)).days
				fildate = datetime.datetime.fromtimestamp(fildateraw).strftime('%Y-%m-%d_%H-%M-%S')
				postfix = 'UnknownCam'

				if days > daysold:
					print(fil, 'too old to copy')
					continue

				# Проверяем на mp4
				if extension == 'mp4':
					# print(fil, fildate)
					if name.lower().startswith('dji'):
						postfix = 'AIR'
					if name.lower().startswith('dji') and (name.lower().endswith('_d') or name.lower().endswith('_os4')):
						cameraname = try_get_metadata_camera_name(os.path.join(line[0],fil))
						if cameraname == 'DJI OsmoAction3':
							postfix = 'OSMO3'
						if cameraname == 'DJI OsmoAction4':
							postfix = 'OSMO4'
						if cameraname == 'DJI Mini4 Pro':
							postfix = 'AIR'
						if cameraname == 'DJI OsmoPocket3':
							postfix = 'POCKET'
						if cameraname == 'DJI OsmoAction5 Pro':
							postfix = 'OSMO5'
					if os.path.exists(xmlp):
						tree = ET.parse(xmlp)
						root = tree.getroot()
						for child in root:
							if 'Device' in child.tag:
								attr = child.attrib
								if 'modelName' in attr:
									if attr['modelName'] == 'ILCE-6500':
										postfix = 'SONY'
									if attr['modelName'] == 'FDR-X3000':
										postfix = 'ACTION'
					if re.match('[0-9]+_[0-9]+a', name.lower()):
						postfix = 'REG'
					if check_metadata(line[0] + '\\' + fil):
						postfix = check_metadata(line[0] + '\\' + fil)
				
				if extension == 'mov':
					if name.lower().startswith('dsc'):
						postfix = 'FUJI'
					if check_metadata(line[0] + '\\' + fil):
						postfix = check_metadata(line[0] + '\\' + fil)
					if name.lower().startswith('cam5'):
						postfix = 'CAM5'
					if name.lower().startswith('xh2s'):
						postfix = 'XH2S'
				if extension == 'insv':
					postfix = 'nochange'

				if extension == 'lrv':
					postfix = 'nochange'
					extension = 'change_to:mp4'

				if extension == 'mp3':
					postfix = 'SOUND'

				if extension == 'wav':
					if name.lower().startswith('zoom'):
						postfix = 'SOUND'
						if '_' in name:
							splittedname = name.split('_')
							if len(splittedname) > 0:
								postfix = 'SOUND_' + splittedname[1]
					if name.lower().startswith('rec'):
						postfix = 'SOUND_GUN'
					if name.lower().startswith('dji_'):
						# print(line)
						# print(line[0].split('//')[0])
						# print(type(line[0].split('//')[0]))
						volumeName = win32api.GetVolumeInformation(line[0].split('//')[0])[0]
						postfix = 'SOUND_' + volumeName
				
				newname = fildate + '_' + postfix

				if postfix == 'nochange':
					newname = name

				if extension.startswith('change_to'):
					extension = extension.split(':')[1]

				dstname = newname + '.' + extension

				# print('Candidate file:', dstname)					
				path_left = line[0] + '\\' + fil
				path_right = os.path.join(input_path, dstname)

				if not(os.path.exists(dstname)):
					if NEED_TO_CHECK_IN_WORKS_AND_MP:
						if check_in_workpaths(dstname):
							continue
					print('copy from', fil, ' to ', dstname)
					copy2(path_left, path_right)
				else:
					if os.stat(path_left).st_size != os.stat(path_right).st_size:
						print('copy from', fil, ' to ', dstname, 'with overwrite. Size differs')
						copy2(path_left, path_right)


if __name__ == '__main__':


	daysold = int(sys.argv[1])

	root_letter = os.getcwd().split('\\')[0] + '\\'
	input_path = os.path.join(root_letter, '!!INPUT')
	extlist = ['mp4', 'mov', 'mp3', 'wav', 'insv', 'lrv']

	NEED_TO_CHECK_IN_WORKS_AND_MP = True

	drives = check_drives()
	workpathfiles = prepare_workpaths_structure()

	for drive in drives:
		take_flash(drive)
