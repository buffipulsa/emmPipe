
import os
import json
import shutil

import maya.cmds as cmds

from emmPipe.rig.deformers import skincluster, ngSkinToolsData 


class Component:
    """
    The Component class provides methods for browsing, importing, and exporting various components in a project.

    Args:
        projectPath (str): The path to the project.
    """

    def __init__(self, project_path):
        self.project_path = project_path

    def update_project_path(self, new_path):
        """
        Updates the project path.

        Args:
            new_path (str): The new path to the project.

        Returns:
            None
        """
        self.project_path = new_path
    
        return

    def browse_component(self, component):
        """
        Opens the specified component in the file browser.

        Args:
            component (str): The name of the component.

        Returns:
            None
        """
        component_path = os.path.join(self.project_path, component)

        if os.path.exists(component_path):
            os.system('start {}'.format(component_path))
        else:
            cmds.warning('{} component does not exist on disk.'.format(component))

        return

    def import_model_component(self):
        """
        Imports the model component.

        Returns:
            None
        """
        cmds.file(self.get_file_path('model'), i=True)

        print('#' * 50)
        print('Imported model component from: {}'.format(self.get_file_path('model')))
        print('#' * 50)

        return

    def import_blueprint_component(self):
        """
        Imports the blueprint component.

        Returns:
            None
        """
        component_path = self.get_component_path('blueprint')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        cmds.file('{}/blueprint.ma'.format(full_path), i=True)

        print('#' * 50)
        print('Imported blueprint component from: {}'.format(full_path))
        print('#' * 50)

        return

    def export_blueprint_component(self):
        """
        Exports the blueprint component.

        Returns:
            None
        """
        component_path = self.get_component_path('blueprint')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        cmds.select('grp_blueprint')
        cmds.file('{}/blueprint'.format(full_path), force=True, type='mayaAscii', exportSelected=True)

        print('#' * 50)
        print('Exported blueprint component to: {}'.format(full_path))
        print('#' * 50)

        return

    def save_hold_file(self):
        """
        Saves the hold file.

        Returns:
            None
        """
        component_path = self.get_component_path('hold')
        hold_file_path = '{}/hold_001.ma'.format(component_path)

        cmds.file(rename=hold_file_path)
        cmds.file(save=True, type='mayaAscii')

        print('#'*50)
        print('Exported hold component to: {}'.format(hold_file_path))
        print('#' * 50)

        return

    def open_hold_file(self):
        """
        Opens the hold file.

        Returns:
            None
        """
        cmds.file(self.get_file_path('hold'), o=True, force=True)

        print('#' * 50)
        print('Imported model component from: {}'.format(self.get_file_path('model')))
        print('#' * 50)

        return

    def export_controls_component(self):
        """
        Exports the control shapes.

        Returns:
            None
        """
        component_path = self.get_component_path('controls')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        controls = cmds.ls(sl=True, type='transform', shapes=False)
        if not controls:
            controls = cmds.ls('ctrl_*', type='transform', shapes=False)

            if not controls:
                cmds.warning('No controls in scene, none will be exported')
                return

        for control in controls:
            control_data = self.cTools.get_curve_data(control)

            file_out = open('{}/{}.json'.format(full_path, control), 'w')
            json.dump(control_data, file_out, indent=2)
            file_out.close()

            print('Exported {} to: {}'.format(control, full_path))

        return

    def import_controls_component(self):
        """
        Imports the control shapes.

        Returns:
            None
        """
        component_path = self.get_component_path('controls')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        imported_controls = []

        controls = cmds.ls('ctrl_*', type='transform', shapes=False)
        for control in controls:
            if cmds.listRelatives(control, shapes=True):
                ctrl_shapes = cmds.listRelatives(control, shapes=True)

                for ctrl_shape in ctrl_shapes:
                    component_file = '{}.json'.format(control)
                    if component_file in os.listdir(full_path):
                        if cmds.objExists(ctrl_shape):
                            file_in = open(os.path.join(full_path, component_file))
                            control_data = json.load(file_in)
                            file_in.close()

                            control_cvs = cmds.ls('{}.cv[*]'.format(ctrl_shape), flatten=True)
                            for i, cv in enumerate(control_cvs):
                                cv_shape = '{}.cv[{}]'.format(ctrl_shape, i)
                                cmds.move(control_data[cv_shape][0], control_data[cv_shape][1], control_data[cv_shape][2],
                                          cv, localSpace=True)

            imported_controls.append(control)

        if imported_controls:
            print('#' * 50)
            print('Imported the following control shapes from: {}'.format(full_path))
            for control in imported_controls:
                print(control)
            print('#' * 50)

        return


    def export_deformers_component(self):
        """
        Exports the skinCluster weights and ngSkinTools data.

        Returns:
            None
        """
        component_path = self.get_component_path('deformers')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        skinweights_exported = []

        c_ngskintools_data = ngSkinToolsData.NgSkinData()

        selection = cmds.ls(sl=True)
        for obj in selection:
            try:
                skincluster.saveSkinclusterData(obj, full_path)
                skinweights_exported.append(obj)
            except:
                print('{} does not have a skincluster node'.format(obj))

            self.c_ngskintools_data.exportNgSkinData(obj, full_path)

        if skinweights_exported:
            print('#' * 50)
            print('Exported skinCluster weights for following objects to: {}/skincluster'.format(full_path))
            for exported_weights_obj in skinweights_exported:
                print(exported_weights_obj)
            print('#' * 50)

        return

    def import_deformers_component(self, ng_skin=True):
        """
        Imports the skinCluster weights and ngSkinTools data.

        Args:
            ng_skin (bool, optional): Whether to import ngSkinTools data. Defaults to True.

        Returns:
            None
        """
        component_path = self.get_component_path('deformers')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        skinweights_imported = []

        skincluster_path = os.path.join(full_path, 'skincluster')
        if os.path.exists(skincluster_path):
            for obj in os.listdir(skincluster_path):
                obj = obj.split('.')[0]
                if cmds.objExists(obj):
                    skincluster.load_skincluster_data(obj, skincluster_path)
                    skinweights_imported.append(obj)

        if ng_skin:
            c_ngskintools_data = ngSkinToolsData.NgSkinData()

            ng_skin_data_path = os.path.join(full_path, 'ngSkinData')
            if os.path.exists(ng_skin_data_path):
                for obj in os.listdir(ng_skin_data_path):
                    obj = obj.split('.')[0]
                    if cmds.objExists(obj):
                        c_ngskintools_data.import_ng_skin_data(obj, ng_skin_data_path)

        if skinweights_imported:
            print('#' * 50)
            print('Imported skinCluster weights for following objects to: {}/skincluster'.format(full_path))
            for imported_weights_obj in skinweights_imported:
                print(imported_weights_obj)
            print('#' * 50)

        return

    def export_misc_component(self):
        """
        Exports the misc component.

        Returns:
            None
        """
        component_path = self.get_component_path('misc')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        cmds.select('grp_misc')
        cmds.file('{}/misc.ma'.format(full_path), force=True, type='mayaAscii', exportSelected=True)

        print('#' * 50)
        print('Exported misc component to: {}'.format(full_path))
        print('#' * 50)

        return

    def import_misc_component(self):
        """
        Imports the misc component.

        Returns:
            None
        """
        component_path = self.get_component_path('misc')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        cmds.file('{}/misc.ma'.format(full_path), i=True)

        print('#' * 50)
        print('Imported misc component from: {}'.format(full_path))
        print('#' * 50)

        return

    def export_psd_data(self):
        """
        Exports the PSD data.

        Returns:
            None
        """
        component_path = self.get_component_path('psdData')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        psd_grp = cmds.ls(sl=True, type='transform', shapes=False)
        if not psd_grp:
            psd_grp = cmds.ls('*_PSD_Data_Grp', type='transform', shapes=False)

            if not psd_grp:
                cmds.warning('No PSD Data group in scene, none will be exported')
                return

        for grp in psd_grp:
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

            file_out = open('{}/{}.json'.format(full_path, grp), 'w')
            json.dump(data, file_out, indent=2)
            file_out.close()

        return

    def import_psd_data(self):
        """
        Imports the PSD data.

        Returns:
            None
        """
        component_path = self.get_component_path('psdData')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        psd_grp = cmds.ls(sl=True, type='transform', shapes=False)
        if not '_PSD_Data_Grp' in psd_grp:
            psd_grp = None
        if not psd_grp:
            psd_grp = cmds.ls('*_PSD_Data_Grp', type='transform', shapes=False)

            if not psd_grp:
                cmds.warning('No PSD Data group in scene, none will be imported')
                return

        for grp in psd_grp:
            component_file = '{}.json'.format(grp)
            if component_file in os.listdir(full_path):
                if cmds.objExists(grp):
                    file_in = open(os.path.join(full_path, component_file))
                    psd_data = json.load(file_in)
                    file_in.close()
                    for attr in psd_data[grp].keys():
                        if cmds.objExists(grp + '.' + attr):
                            cmds.setAttr(grp + '.' + attr, psd_data[grp][attr])

        return

    def import_targets_component(self):
        """
        Imports the targets component from the latest version.

        Returns:
            None
        """
        component_path = self.get_component_path('targets')
        component_version = self.get_component_version(component_path, latest=True)
        full_path = os.path.join(component_path, component_version)

        cmds.file('{}/targets.ma'.format(full_path), i=True)

        print('#' * 50)
        print('Imported targets component from: {}'.format(full_path))
        print('#' * 50)

        return


    def get_file_path(self, component):
        """
        Retrieves the file path of the latest version of a component.

        Args:
            component: (str) The name of the component.

        Returns:
            str: The file path of the latest version of the component.
        """
        component_path = self.get_component_path(component)
        print (component_path)
        full_directory = os.listdir(component_path)
        print(full_directory)
        for file in full_directory:
            if not file.startswith('{}_'.format(component)) and not file.endswith('.ma'):
                full_directory.remove(file)

        file_path = os.path.join(component_path, full_directory[-1])

        return file_path


    def get_component_path(self, component):
        """
        Retrieves the path of a component.

        Args:
            component: (str) The name of the component.

        Returns:
            str: The path of the component.
        """
        component_path = os.path.join(self.project_path, component)
        if not os.path.exists(component_path):
            os.makedirs(component_path)

        return component_path


    def get_component_version(self, component_path, version=1, latest=True):
        """
        Retrieves the version of a component.

        Args:
            component_path: (str) The path of the component.
            version: (int) The specific version to retrieve. Default is 1.
            latest: (bool) Whether to retrieve the latest version. Default is True.

        Returns:
            str: The version of the component.
        """
        versions = os.listdir(component_path)
        if not versions:
            first_version = '{}_001'.format(component_path.split('/')[-1])
            os.makedirs(os.path.join(component_path, first_version))
            versions.append(first_version)

        if latest:
            return versions[-1]
        else:
            return versions[version]


    def version_up_component(self, component):
        """
        Creates a new version of a component.

        Args:
            component: (str) The name of the component.

        Returns:
            None
        """
        component_path = self.get_component_path(component)
        current_version = self.get_component_version(component_path, latest=True)

        new_version_number = format(int(current_version.split('_')[-1]) + 1, '03d')

        new_version = '{}_{}'.format(current_version.split('_')[0], str(new_version_number))

        source = os.path.join(component_path, current_version)
        destination = os.path.join(component_path, new_version)

        shutil.copytree(source, destination)

        print('Created a new component version: {} in {}'.format(new_version, component_path))

        return


    def increment_file(self, file_path):
        """
        Increments the file name in a given file path.

        Args:
            file_path: (str) The file path.

        Returns:
            str: The new file path with the incremented file name.
        """
        full_directory = os.listdir(file_path)

        latest_version_str = ((full_directory[-1].split('_')[-1])).split('.')[0]
        new_version_str = '{:03d}'.format(int(latest_version_str)+1)

        new_file_name = '{}_{}'.format(full_directory[-1].split('_')[0], new_version_str)
        new_file_path = '{}/{}.ma'.format(file_path, new_file_name)

        return new_file_path



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

