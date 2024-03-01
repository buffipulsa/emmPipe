
import os
import json
import shutil

import maya.cmds as cmds

from emmPipe.rig.deformers import skincluster, ngSkinToolsData 

class FileIO():

    def __init__(self, projectPath):
        self.projectPath = projectPath

        self.cTools = tools.Tools()
        self.cNgSkinToolsData = ngSkinToolsData.NgSkinData()

    def browseComponent(self, component):
        componentPath = os.path.join(self.projectPath, component)

        if os.path.exists(componentPath):
            os.system('start {}'.format(componentPath))
        else:
            cmds.warning('{} component does not exist on disk.'.format(component))

        return

    def importModelComponent(self):
        cmds.file(self.getFilePath('model'), i=True)

        print('#' * 50)
        print('Imported model component from: {}'.format(self.getFilePath('model')))
        print('#' * 50)

        return

    def importBlueprintComponent(self):
        componentPath = self.getComponentPath('blueprint')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        cmds.file('{}/blueprint.ma'.format(fullPath), i=True)

        print('#' * 50)
        print('Imported blueprint component from: {}'.format(fullPath))
        print('#' * 50)

        return

    def exportBlueprintComponent(self):
        componentPath = self.getComponentPath('blueprint')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        cmds.select('grp_blueprint')
        cmds.file('{}/blueprint'.format(fullPath), force=True, type='mayaAscii', exportSelected=True)

        print('#' * 50)
        print('Exported blueprint component to: {}'.format(fullPath))
        print('#' * 50)

        return

    def saveHoldFile(self):
        componentPath = self.getComponentPath('hold')
        holdFilePath = '{}/hold_001.ma'.format(componentPath)

        cmds.file(rename=holdFilePath)
        cmds.file(save=True, type='mayaAscii')

        print('#'*50)
        print('Exported hold component to: {}'.format(holdFilePath))
        print('#' * 50)

        return

    def openHoldFile(self):
        cmds.file(self.getFilePath('hold'), o=True, force=True)

        print('#' * 50)
        print('Imported model component from: {}'.format(self.getFilePath('model')))
        print('#' * 50)

        return

    def exportControlsComponent(self):
        componentPath = self.getComponentPath('controls')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        # ctrlShapes = cmds.listRelatives(cmds.ls(sl=True), shapes=True)
        controls = cmds.ls(sl=True, type='transform', shapes=False)
        if not controls:
            controls = cmds.ls('ctrl_*', type='transform', shapes=False)

            if not controls:
                cmds.warning('No controls in scene, none will be exported')
                return

        for control in controls:
            controlData = self.cTools.getCurveData(control)

            fileOut = open('{}/{}.json'.format(fullPath, control), 'w')
            json.dump(controlData, fileOut, indent=2)
            fileOut.close()

            print('Exported {} to: {}'.format(control, fullPath))

        return

    def importControlsComponent(self):
        componentPath = self.getComponentPath('controls')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        importedControls = []

        controls = cmds.ls('ctrl_*', type='transform', shapes=False)
        for control in controls:
            if cmds.listRelatives(control, shapes=True):
                ctrlShapes = cmds.listRelatives(control, shapes=True)

                for ctrlShape in ctrlShapes:
                    componentFile = '{}.json'.format(control)
                    if componentFile in os.listdir(fullPath):
                        if cmds.objExists(ctrlShape):
                            fileIn = open(os.path.join(fullPath, componentFile))
                            controlData = json.load(fileIn)
                            fileIn.close()

                            controlCvs = cmds.ls('{}.cv[*]'.format(ctrlShape), flatten=True)
                            for i, cv in enumerate(controlCvs):
                                cvShape = '{}.cv[{}]'.format(ctrlShape, i)
                                cmds.move(controlData[cvShape][0], controlData[cvShape][1], controlData[cvShape][2],
                                          cv, localSpace=True)

            importedControls.append(control)

        if importedControls:
            print('#' * 50)
            print('Imported the following control shapes from: {}'.format(fullPath))
            for control in importedControls:
                print(control)
            print('#' * 50)

        return


    def exportDeformersComponent(self):
        componentPath = self.getComponentPath('deformers')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        skinweightsExported = []

        selection = cmds.ls(sl=True)
        for obj in selection:
            try:
                skincluster.saveSkinclusterData(obj, fullPath)
                skinweightsExported.append(obj)
            except:
                print('{} does not have a skincluster node'.format(obj))

            self.cNgSkinToolsData.exportNgSkinData(obj, fullPath)

        if skinweightsExported:
            print('#' * 50)
            print('Exported skinCluster weights for following objects to: {}/skincluster'.format(fullPath))
            for exportedWeightsObj in skinweightsExported:
                print(exportedWeightsObj)
            print('#' * 50)

        return

    def importDeformersComponent(self, ngSkin=True):
        componentPath = self.getComponentPath('deformers')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        skinweightsImported = []

        skinclusterPath = os.path.join(fullPath, 'skincluster')
        if os.path.exists(skinclusterPath):
            for obj in os.listdir(skinclusterPath):
                obj = obj.split('.')[0]
                if cmds.objExists(obj):
                    skincluster.loadSkinclusterData(obj, skinclusterPath)
                    skinweightsImported.append(obj)

        if ngSkin:
            ngSkinDataPath = os.path.join(fullPath, 'ngSkinData')
            if os.path.exists(ngSkinDataPath):
                for obj in os.listdir(ngSkinDataPath):
                    obj = obj.split('.')[0]
                    if cmds.objExists(obj):
                        self.cNgSkinToolsData.importNgSkinData(obj, ngSkinDataPath)

        if skinweightsImported:
            print('#' * 50)
            print('Imported skinCluster weights for following objects to: {}/skincluster'.format(fullPath))
            for importedWeightsObj in skinweightsImported:
                print(importedWeightsObj)
            print('#' * 50)

        return

    def exportMiscComponent(self):
        componentPath = self.getComponentPath('misc')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        cmds.select('grp_misc')
        cmds.file('{}/misc.ma'.format(fullPath), force=True, type='mayaAscii', exportSelected=True)

        print('#' * 50)
        print('Exported misc component to: {}'.format(fullPath))
        print('#' * 50)

        return

    def importMiscComponent(self):
        componentPath = self.getComponentPath('misc')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        cmds.file('{}/misc.ma'.format(fullPath), i=True)

        print('#' * 50)
        print('Imported misc component from: {}'.format(fullPath))
        print('#' * 50)

        return

    def exportPSDData(self):
        componentPath = self.getComponentPath('psdData')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        psdGrp = cmds.ls(sl=True, type='transform', shapes=False)
        if not psdGrp:
            psdGrp = cmds.ls('*_PSD_Data_Grp', type='transform', shapes=False)

            if not psdGrp:
                cmds.warning('No PSD Data group in scene, none will be exported')
                return

        for grp in psdGrp:
            attrs = cmds.listAttr(grp)

            values_dict = {}

            for attr in attrs:
                if 'Up' in attr or 'Down' in attr or 'Front' in attr or 'Back' in attr or 'Source' in attr:
                    if 'Corrective' in attr or 'Settings' in attr:
                        continue
                    else:
                        attr_value = cmds.getAttr(grp + '.' + attr)
                        values_dict[attr] = attr_value
            data = {grp: values_dict}
            # data[grp] = values_dict

            fileOut = open('{}/{}.json'.format(fullPath, grp), 'w')
            json.dump(data, fileOut, indent=2)
            fileOut.close()

        return

    def importPSDData(self):
        componentPath = self.getComponentPath('psdData')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        psdGrp = cmds.ls(sl=True, type='transform', shapes=False)
        if not '_PSD_Data_Grp' in psdGrp:
            psdGrp = None
        if not psdGrp:
            psdGrp = cmds.ls('*_PSD_Data_Grp', type='transform', shapes=False)

            if not psdGrp:
                cmds.warning('No PSD Data group in scene, none will be imported')
                return

        for grp in psdGrp:
            componentFile = '{}.json'.format(grp)
            if componentFile in os.listdir(fullPath):
                if cmds.objExists(grp):
                    fileIn = open(os.path.join(fullPath, componentFile))
                    psdData = json.load(fileIn)
                    fileIn.close()
                    for attr in psdData[grp].keys():
                        if cmds.objExists(grp + '.' + attr):
                            cmds.setAttr(grp + '.' + attr, psdData[grp][attr])

        return

    def importTargetsComponent(self):
        componentPath = self.getComponentPath('targets')
        componentVersion = self.getComponentVersion(componentPath, latest=True)
        fullPath = os.path.join(componentPath, componentVersion)

        cmds.file('{}/targets.ma'.format(fullPath), i=True)

        print('#' * 50)
        print('Imported targets component from: {}'.format(fullPath))
        print('#' * 50)

        return

    def getFilePath(self, component):
        componentPath = self.getComponentPath(component)
        fullDirectory = os.listdir(componentPath)

        for file in fullDirectory:
            if not file.startswith('{}_'.format(component)) and not file.endswith('.ma'):
                fullDirectory.remove(file)

        filePath = os.path.join(componentPath, fullDirectory[-1])

        return filePath

    def getComponentPath(self, component):
        componentPath = os.path.join(self.projectPath, component)
        if not os.path.exists(componentPath):
            os.makedirs(componentPath)

        return componentPath

    def getComponentVersion(self, componentPath, version=1, latest=True):
        versions = os.listdir(componentPath)
        if not versions:
            firstVersion = '{}_001'.format(componentPath.split('/')[-1])
            os.makedirs(os.path.join(componentPath, firstVersion))
            versions.append(firstVersion)

        if latest:
            return versions[-1]
        else:
            return versions[version]

    def versionUpComponent(self, component):
        componentPath = self.getComponentPath(component)
        currentVersion = self.getComponentVersion(componentPath, latest=True)

        newVersionNumber = format(int(currentVersion.split('_')[-1]) + 1, '03d')

        newVersion = '{}_{}'.format(currentVersion.split('_')[0], str(newVersionNumber))

        source = os.path.join(componentPath, currentVersion)
        destination = os.path.join(componentPath, newVersion)

        shutil.copytree(source, destination)

        print('Created a new component version: {} in {}'.format(newVersion, componentPath))

        return

    def incrimentFile(self, filePath):
        fullDirectory = os.listdir(filePath)

        latestVersionStr = ((fullDirectory[-1].split('_')[-1])).split('.')[0]
        newVersionStr = '{:03d}'.format(int(latestVersionStr)+1)

        newFileName = '{}_{}'.format(fullDirectory[-1].split('_')[0], newVersionStr)
        newFilePath = '{}/{}.ma'.format(filePath, newFileName)

        return newFilePath



def file_incriment(path, file_name):
    """
    Args:
        path: (str) path to files
        file_name: name of file to increment

    Returns: Name of new file
    """

    files = os.listdir(path)

    if files:

        files.sort()

        greatest = 0
        for old_file in files:

            num = old_file.split('_v')[1]
            num = int(num.split('.json')[0])

            if num > greatest:
                greatest = num

        increment = greatest+1

        new_file = '{}_v{}.json'.format(file_name, increment)

    else:

        new_file = '{}_v1.json'.format(file_name)

    return new_file

def save_json(data, path, file_name):
    """
    This function saves out the data given to a json file at a given path.
    Args:
        data:
        path:
        file_name:

    Returns: None
    """

    with open('{}/{}'.format(path, file_name)) as f_out:

        json.dump(data, f_out, indent=2)

    #print "# Exported data to '%s' #" % file_name

def load_json(path):
    """
    This function loads in the json file from a given path.
    Args:
        path:

    Returns:
    """

    files = os.listdir(path)

    if files:
        numbers = []
        for f in files:
            name = f.split('_v',)
            num = name[1].split('.')[0]
            numbers.append(int(num))
        
        max_num = max(numbers)

        name = path + name[0]+'_v'+str(max_num)+'.json'

        f_in = open(name, 'r')
        data_in = json.load(f_in) #read the json file and convert it into python data
        f_in.close()

        data = data_in.get('Controls', None) #get the points value or None
                                                #if it doesn't exist

        return {'Data':data_in}


def clean_anim_ctrls(suffix='Ctrl'):
    """
    This function cleans the channelBox for every anim control on the rig.
    Args:
        suffix: (str) The suffix for the anim controls

    Returns: None
    """

    for ctrl in cmds.ls('*{0}'.format(suffix)):

        outputs = cmds.listConnections(ctrl, connections=True, destination=True)
        if outputs:
            for output in outputs:
                if '.' not in output:
                    try:
                        cmds.setAttr(output+'.isHistoricallyInteresting', 0)
                    except:
                        cmds.warning('Could not hide output {0} on {1}'.format(output, ctrl))

        shapes = cmds.listRelatives(ctrl, shapes=True)

        if shapes:
            for shape in shapes:
                try:
                    cmds.setAttr(shape+'.isHistoricallyInteresting', 0)
                except:
                    cmds.warning('Could not hide shape {0} on {1}'.format(shape, ctrl))

