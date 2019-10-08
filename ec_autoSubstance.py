import maya.cmds as cmds
from functools import partial
import os
import maya.mel as mel


class AutoSubstance():
    def __init__(self):
        self.win_name = 'autoSubstanceWin'
        if cmds.window(self.win_name, ex=1):
            cmds.deleteUI(self.win_name)

        self.createWin()

    def createWin(self):
        field_height = 17
        border_space = 10
        line_space = 5

        self.win = cmds.window(self.win_name,
                               w=100,
                               h=400,
                               rtf=1,
                               s=0,
                               t='EC Auto Substance')

        self.main_form = cmds.formLayout(nd=100)

        self.channel_text = cmds.text(fn='boldLabelFont', l='Channel Mapping')

        self.diff_txt = cmds.text(l='baseColor:')
        self.spec_txt = cmds.text(l='specular:')
        self.rough_txt = cmds.text(l='roughness:')
        self.height_txt = cmds.text(l='height:')
        self.metal_txt = cmds.text(l='metalness:')
        self.normal_txt = cmds.text(l='normal:')
        self.emission_txt = cmds.text(l='emission:')

        self.diff_field = cmds.textField(h=field_height, tx='BaseColor')
        self.spec_field = cmds.textField(h=field_height, tx='Specular')
        self.rough_field = cmds.textField(h=field_height, tx='Roughness')
        self.height_field = cmds.textField(h=field_height, tx='Height')
        self.metal_field = cmds.textField(h=field_height, tx='Metalness')
        self.normal_field = cmds.textField(h=field_height, tx='Normal')
        self.emission_field = cmds.textField(h=field_height, tx='Emission')

        self.options_text = cmds.text(fn='boldLabelFont', l='Options')
        self.UDIM_box = cmds.checkBox(l='UDIM')
        self.disp_box = cmds.checkBox(l='height as displacement')
        self.cloth_box = cmds.checkBox(l='facing ratio for clothing')
        self.sss_box = cmds.checkBox(l='baseColor as SSS')
        self.create_btn = cmds.button(h=60, l='create network', c=self.build)

        cmds.formLayout(
            self.main_form,
            e=True,
            attachForm=(
                (self.channel_text, 'top', border_space),
                (self.channel_text, 'left', border_space),
                (self.diff_field, 'right', border_space),
                (self.spec_field, 'right', border_space),
                (self.rough_field, 'right', border_space),
                (self.height_field, 'right', border_space),
                (self.metal_field, 'right', border_space),
                (self.normal_field, 'right', border_space),
                (self.emission_field, 'right', border_space),
                (self.options_text, 'left', border_space),
                (self.UDIM_box, 'left', border_space * 2),
                (self.disp_box, 'left', border_space * 2),
                (self.cloth_box, 'left', border_space * 2),
                (self.sss_box, 'left', border_space * 2),
                (self.create_btn, 'left', border_space),
                (self.create_btn, 'bottom', border_space),
                (self.create_btn, 'right', border_space),
            ),
            attachPosition=(
                (self.diff_txt, 'right', border_space, 50),
                (self.diff_field, 'left', 0, 50),
                (self.spec_txt, 'right', border_space, 50),
                (self.spec_field, 'left', 0, 50),
                (self.rough_txt, 'right', border_space, 50),
                (self.rough_field, 'left', 0, 50),
                (self.height_txt, 'right', border_space, 50),
                (self.height_field, 'left', 0, 50),
                (self.metal_txt, 'right', border_space, 50),
                (self.metal_field, 'left', 0, 50),
                (self.normal_txt, 'right', border_space, 50),
                (self.normal_field, 'left', 0, 50),
                (self.emission_txt, 'right', border_space, 50),
                (self.emission_field, 'left', 0, 50),
            ),
            attachControl=(
                (self.diff_txt, 'top', border_space, self.channel_text),
                (self.diff_field, 'top', border_space, self.channel_text),
                (self.spec_txt, 'top', line_space, self.diff_txt),
                (self.spec_field, 'top', line_space, self.diff_txt),
                (self.rough_txt, 'top', line_space, self.spec_txt),
                (self.rough_field, 'top', line_space, self.spec_txt),
                (self.height_txt, 'top', line_space, self.rough_txt),
                (self.height_field, 'top', line_space, self.rough_txt),
                (self.metal_txt, 'top', line_space, self.height_txt),
                (self.metal_field, 'top', line_space, self.height_txt),
                (self.normal_txt, 'top', line_space, self.metal_txt),
                (self.normal_field, 'top', line_space, self.metal_txt),
                (self.emission_txt, 'top', line_space, self.normal_txt),
                (self.emission_field, 'top', line_space, self.normal_txt),
                (self.options_text, 'top', border_space, self.emission_field),
                (self.UDIM_box, 'top', line_space, self.options_text),
                (self.disp_box, 'top', line_space, self.UDIM_box),
                (self.cloth_box, 'top', line_space, self.disp_box),
                (self.sss_box, 'top', line_space, self.cloth_box),
                (self.create_btn, 'top', border_space, self.sss_box),
            ))

        cmds.showWindow(self.win)
        cmds.window(self.win, e=1, w=300, h=350)

    def build(self, *args):
        # store selection
        sel = cmds.ls(sl=1)

        texture_set = ''
        proj_name = ''

        # get map names
        diff_name = cmds.textField(self.diff_field, q=1, tx=1)
        spec_name = cmds.textField(self.spec_field, q=1, tx=1)
        rough_name = cmds.textField(self.rough_field, q=1, tx=1)
        height_name = cmds.textField(self.height_field, q=1, tx=1)
        metal_name = cmds.textField(self.metal_field, q=1, tx=1)
        normal_name = cmds.textField(self.normal_field, q=1, tx=1)
        emission_name = cmds.textField(self.emission_field, q=1, tx=1)

        # destination attrs
        diff_attr = 'baseColor'
        spec_attr = 'specular'
        rough_attr = 'specularRoughness'
        height_attr = 'bumpMap'
        metal_attr = 'metalness'
        normal_attr = 'normalCamera'
        emission_attr = 'emissionColor'
        sss_attr = 'subsurfaceColor'

        # maps
        diff_map = ''
        spec_map = ''
        rough_map = ''
        height_map = ''
        metal_map = ''
        normal_map = ''
        emission_map = ''

        extension = ''

        for item in sel:
            if cmds.objectType(item) == 'file':
                file_name_long = cmds.getAttr(item + '.fileTextureName')
                if file_name_long:
                    file_name = file_name_long.replace(
                        '\\', '/').split('/')[-1].split('.')[0]
                    curr_texture_set = file_name.split('_')[-2]

                    if not texture_set:
                        texture_set = curr_texture_set
                    if texture_set != curr_texture_set:
                        cmds.error('Multiple texture sets detected!')

                    # store the map
                    map = file_name.split('_')[-1]

                    # UDIM
                    if cmds.checkBox(self.UDIM_box, q=1, v=1):
                        cmds.setAttr(item + '.uvTilingMode', 3)
                        proj_name = file_name.split('_')[0]

                    if map == diff_name:
                        diff_map = item
                    if map == spec_name:
                        spec_map = item
                    if map == rough_name:
                        rough_map = item
                    if map == height_name:
                        height_map = item
                    if map == metal_name:
                        metal_map = item
                    if map == normal_name:
                        normal_map = item
                    if map == emission_name:
                        emission_map = item

        # change name if UDIM
        if cmds.checkBox(self.UDIM_box, q=1, v=1):
            texture_set = proj_name

        # check if a shader is selected
        mat = [x for x in sel if cmds.objectType(x) == 'aiStandardSurface']
        if len(mat) > 1:
            raise Exception('More than one shader selected!')
        if len(mat) == 1: mat = mat[0]

        # check if we have a sg already
        sg = ''
        if mat:
            sg_conns = cmds.listConnections(mat, type='shadingEngine')
            if sg_conns:
                sg = sg_conns[0]

        # build the shader
        if not mat:
            mat = cmds.shadingNode('aiStandardSurface',
                                   asShader=1,
                                   n=texture_set + '_MAT')
        # build the sg
        if not sg:
            sg = cmds.sets(renderable=1,
                        noSurfaceShader=1,
                        empty=1,
                        n=texture_set + '_SG')
            cmds.connectAttr(mat + '.outColor', sg + '.surfaceShader')

        if diff_map:
            if cmds.checkBox(self.cloth_box, q=1, v=1):
                ramp = facingRatio(texture_set, diff_map)
                cmds.connectAttr(ramp + '.outColor', mat + '.' + diff_attr)
            else:
                cmds.connectAttr(diff_map + '.outColor', mat + '.' + diff_attr)

        if spec_map:
            cmds.connectAttr(spec_map + '.outAlpha', mat + '.' + spec_attr)

        if rough_map:
            cmds.connectAttr(rough_map + '.outAlpha', mat + '.' + rough_attr)

        if emission_map:
            cmds.connectAttr(emission_map + '.outColor',
                             mat + '.' + emission_attr)
            cmds.setAttr(mat + '.emissionStrength', 1)

        if height_map and cmds.checkBox(self.disp_box, q=1, v=1):
            disp = setRangeDisp(texture_set, height_map)
            cmds.connectAttr(disp + '.displacement',
                             sg + '.displacementShader')

        if normal_map:
            bump = aiNormal(texture_set, normal_map)
            cmds.connectAttr(bump + '.outValue', mat + '.' + normal_attr)

        if metal_map:
            cmds.connectAttr(metal_map + '.outAlpha', mat + '.' + metal_attr)

        if cmds.checkBox(self.sss_box, q=1, v=1):
            if diff_map:
                remap_hsv = sssCC(texture_set, diff_map)
                cmds.connectAttr(diff_map + '.outColor', mat + '.' + sss_attr)
                cmds.connectAttr(remap_hsv + '.outColor',
                                 mat + '.subsurfaceRadius')
                cmds.setAttr(mat + '.subsurface', 1)
                cmds.setAttr(mat + '.subsurfaceType', 1)

        # alpha is luminance and color space settings
        raw_files = [rough_map, height_map, normal_map, metal_map, spec_map]
        for file in raw_files:
            if file:
                cmds.setAttr(file + '.colorSpace', 'Raw', type='string')
                cmds.setAttr(file + '.ignoreColorSpaceFileRules', 1)
                cmds.setAttr(file + '.alphaIsLuminance', 1)


def verifyTexture(name, texture):
    if not texture:
        sel = cmds.ls(sl=1, type='file')
        if len(sel) == 1:
            texture = sel[0]
        else:
            cmds.error('Select only one file texture!')
    if not name:
        name = texture

    return name, texture


def facingRatio(name, texture):
    name, texture = verifyTexture(name, texture)

    facing_ratio = cmds.shadingNode('aiFacingRatio', au=1, n=name + '_AFR')
    ramp = cmds.shadingNode('ramp', au=1, n=name + '_RMP')
    color_correct = cmds.shadingNode('aiColorCorrect', au=1, n=name + '_COC')

    cmds.connectAttr(texture + '.outColor', color_correct + '.input')
    cmds.connectAttr(facing_ratio + '.outValue', ramp + '.uvCoord.uCoord')
    cmds.setAttr(ramp + '.type', 1)
    cmds.connectAttr(color_correct + '.outColor',
                     ramp + '.colorEntryList[0].color')
    cmds.connectAttr(texture + '.outColor', ramp + '.colorEntryList[1].color')
    cmds.setAttr(ramp + '.colorEntryList[0].position', 0)
    cmds.setAttr(ramp + '.colorEntryList[1].position', 1)
    cmds.setAttr(color_correct + '.gamma', 2)

    return ramp


def setRangeDisp(name, texture):
    name, texture = verifyTexture(name, texture)

    disp = cmds.shadingNode('displacementShader', asShader=1, n=name + '_DSP')
    set_range = cmds.shadingNode('setRange', au=1, n=name + '_SRG')

    cmds.setAttr(set_range + '.oldMinX', 0)
    cmds.setAttr(set_range + '.oldMaxX', 1)

    cmds.connectAttr(texture + '.outAlpha', set_range + '.valueX')
    cmds.connectAttr(set_range + '.outValueX', disp + '.displacement')

    return disp


def aiNormal(name, texture):
    name, texture = verifyTexture(name, texture)

    bump = cmds.shadingNode('aiNormalMap', au=1, n=name + '_NML')
    cmds.connectAttr(texture + '.outColor', bump + '.input')

    return bump


def sssCC(name, texture):
    name, texture = verifyTexture(name, texture)

    remap_hsv = cmds.shadingNode('remapHsv', au=1, n=name + '_HSV')
    remap_col = cmds.shadingNode('remapColor', au=1, n=name + '_RGB')

    cmds.connectAttr(texture + '.outColor', remap_col + '.color')
    cmds.connectAttr(remap_col + '.outColor', remap_hsv + '.color')
    cmds.setAttr(remap_hsv + '.value[1].value_FloatValue', .1)

    return remap_hsv


def create_output_node(nodeName, channelName):
    formatAtt = "%s.bakeFormat" % nodeName
    sbs_AutomaticBakeCheck = cmds.getAttr(nodeName + ".autoBake")
    PBRWorkflow = cmds.getAttr("%s.workflow" % nodeName)

    SubstanceHelpers.createOrGetSubstanceOutputNode(
        nodeName,
        channelName)  # This function checks if the node already exists or not
    outputNodeName = SubstanceHelpers.getSubstanceOutputNodeConnected(
        nodeName, channelName)

    # if sbs_AutomaticBakeCheck == 1:
    #     outputNodeName = SubstanceHelpers.sbsBakeOutput(outputNodeName, channelName)
    print 'output node name is {}'.format(outputNodeName)
    return outputNodeName
