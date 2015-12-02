import maya.cmds as mc
import os

def sceneInfo() : 
	currentPath = mc.file(q = True, sn = True)

	if currentPath : 
		drive = os.path.splitdrive(currentPath)[0]
		tail = os.path.splitdrive(currentPath)[-1]
		fileName = os.path.split(tail)[-1]
		path = os.path.split(tail)[0]
		split = path.split('/')

		project = split[1]
		assetType = split[4]
		assetSubType = split[5]
		assetName = split[6]
		department = split[7]
		refPath = ('/').join([drive, project, 'asset', '3D', assetType, assetSubType, assetName, 'ref'])
		renderAsset = '%s_Render.mb' % assetName
		renderAssetPath = '%s' % (refPath)

		dictInfo = {'project': project, 
					'assetType': assetType, 
					'assetSubType': assetSubType, 
					'assetName': assetName, 
					'department': department, 
					'fileName': fileName, 
					'drive': drive, 
					'renderAssetPath': renderAssetPath}


		return dictInfo