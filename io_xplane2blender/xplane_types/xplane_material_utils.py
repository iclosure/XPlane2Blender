import bpy
from ..xplane_constants import *

def _validateNormalMetalness(refMat, mat):
    errors = []
    if mat.getEffectiveNormalMetalness() != refMat.getEffectiveNormalMetalness():
        errors.append('NORMAL_METALNESS must be set for all materials with the same albedo texture')

    return errors

def compare(refMat, mat, exportType, autodetectTextures):
    if exportType == EXPORT_TYPE_SCENERY:
        return compareScenery(refMat, mat, autodetectTextures)
    elif exportType == EXPORT_TYPE_INSTANCED_SCENERY:
        return compareInstanced(refMat, mat, autodetectTextures)
    elif exportType == EXPORT_TYPE_COCKPIT or exportType == EXPORT_TYPE_AIRCRAFT:
        return compareAircraft(refMat, mat, autodetectTextures)

def compareScenery(refMat, mat, autodetectTextures):
    errors = []

    if mat.options.draw:
        if mat.options.draped and refMat.options.draped:
            if mat.blenderMaterial.specular_intensity != refMat.blenderMaterial.specular_intensity and \
               mat.getEffectiveNormalMetalness() == False:
                errors.append('Specularity must be %f, is %f' % (refMat.blenderMaterial.specular_intensity,mat.blenderMaterial.specular_intensity))

    if mat.options.draw and autodetectTextures:
        if mat.texture != refMat.texture:
            errors.append('Texture must be "%s".' % refMat.texture)
            errors.extend(_validateNormalMetalness(refMat, mat))

        if mat.textureLit != refMat.textureLit:
            errors.append('Lit/Emissive texture must be "%s".' % refMat.textureLit)

        if mat.textureNormal != refMat.textureNormal:
            errors.append('Normal/Alpha/Specular texture must be "%s".' % refMat.textureNormal)

    return errors

def compareInstanced(refMat, mat, autodetectTextures):
    errors = []

    if mat.options.draw:
        if mat.blenderMaterial.specular_intensity != refMat.blenderMaterial.specular_intensity and \
           mat.getEffectiveNormalMetalness() == False:
            errors.append('Specularity must be %f, is %f' % (refMat.blenderMaterial.specular_intensity,mat.blenderMaterial.specular_intensity))

        if mat.options.blend != refMat.options.blend:
            if refMat.options.blend:
                errors.append('Alpha cutoff must be enabled.')
            else:
                errors.append('Alpha cutoff must be disabled.')
        elif mat.options.blendRatio != refMat.options.blendRatio:
            errors.append('Alpha cutoff ratio must be %f' % refMat.options.blendRatio)
        errors.extend(_validateNormalMetalness(refMat, mat))
            
    if mat.options.draw and autodetectTextures:
        if mat.texture != refMat.texture:
            errors.append('Texture must be "%s".' % refMat.texture)
            
        if mat.textureLit != refMat.textureLit:
            errors.append('Lit/Emissive texture must be "%s".' % refMat.textureLit)

        if mat.textureNormal != refMat.textureNormal:
            errors.append('Normal/Alpha/Specular texture must be "%s".' % refMat.textureNormal)

    return errors

def compareAircraft(refMat, mat, autodetectTextures):
    errors = []
    if mat.options.draw:
        # panel parts can have anything
        if not mat.options.panel and not refMat.options.panel and autodetectTextures:
            if mat.texture != refMat.texture:
                errors.append('Texture must be "%s".' % refMat.texture)

            if mat.textureLit != refMat.textureLit:
                errors.append('Lit/Emissive texture must be "%s".' % refMat.textureLit)

            if mat.textureNormal != refMat.textureNormal:
                errors.append('Normal/Alpha/Specular texture must be "%s".' % refMat.textureNormal)

        if mat.getEffectiveBlendGlass() != refMat.getEffectiveBlendGlass():
            errors.append('BLEND_GLASS must be set for all materials with the same albedo texture')

    return errors


def validate(mat, exportType):
    errors = []

    if mat.options == None:
        errors.append('Is invalid.')
        return errors
    
    if (exportType == EXPORT_TYPE_SCENERY or exportType == EXPORT_TYPE_INSTANCED_SCENERY) and mat.options.draped:
        return validateDraped(mat)
    elif exportType == EXPORT_TYPE_SCENERY:
        return validateScenery(mat)
    elif exportType == EXPORT_TYPE_INSTANCED_SCENERY:
        return validateInstanced(mat)
    elif exportType == EXPORT_TYPE_COCKPIT and mat.options.panel:
        return validatePanel(mat)
    elif exportType == EXPORT_TYPE_COCKPIT and not mat.options.panel:
        return validateCockpit(mat)
    elif exportType == EXPORT_TYPE_AIRCRAFT:
        if bpy.context.scene.xplane.version >= VERSION_1040 and mat.options.panel:
            return validatePanel(mat)
        else:
            return validateAircraft(mat)

    return errors

def validateScenery(mat):
    errors = []

    if mat.options.panel:
        errors.append('Must not be part of the cockpit panel.')

    if mat.options.draped:
        errors.append('Must not be draped.')

    if mat.options.solid_camera:
        errors.append('Must have camera collision disabled.')

    if mat.blenderObject.xplane.manip.enabled:
        errors.append('Must not be a manipulator.')
    
    if mat.getEffectiveBlendGlass():
        errors.append('Blend glass only legal on aircraft and cockpit objects')

    return errors


def validateInstanced(mat):
    errors = []

    if mat.options.lightLevel:
        errors.append('Must not override light level.')

    if mat.options.panel:
        errors.append('Must not be part of the cockpit panel.')

    if mat.options.draped:
        errors.append('Must not be draped.')

    if mat.options.solid_camera:
        errors.append('Must have camera collision disabled.')

    if mat.options.poly_os > 0:
        errors.append('Must not have polygon offset.')

    if mat.blenderObject.xplane.manip.enabled:
        errors.append('Must not be a manipulator.')

    if mat.getEffectiveBlendGlass():
        errors.append('Blend glass only legal on aircraft and cockpit objects')

    return errors


def validatePanel(mat):
    errors = []

    if mat.options.lightLevel:
        errors.append('Must not override light level.')

    if mat.options.draw:
        if mat.textureLit:
            errors.append('Must not have a lit/emissive texture.')

        if mat.textureNormal:
            errors.append('Must not have a normal/alpha/specularity texture.')

    if not mat.options.panel:
        errors.append('Must be part of the cockpit panel.')

    if mat.options.draped:
        errors.append('Must not be draped.')

    if mat.options.surfaceType != 'none':
        errors.append('Must have the surface type "none".')

    return errors


def validateCockpit(mat):
    errors = []

    if mat.options.panel:
        errors.append('Must not be part of the cockpit panel.')

    if mat.options.draped:
        errors.append('Must not be draped.')

    return errors


def validateAircraft(mat):
    errors = []

    if mat.options.panel:
        errors.append('Must not be part of the cockpit panel.')

    if mat.options.draped:
        errors.append('Must not be draped.')

    if mat.blenderObject.xplane.manip.enabled:
        errors.append('Must not be a manipulator.')

    return errors


def validateDraped(mat):
    errors = []

    if not mat.options.draped:
        errors.append('Must be draped')

    if mat.options.lightLevel:
        errors.append('Must not override light level.')

    if mat.options.panel:
        errors.append('Must not be part of the cockpit panel.')

    if mat.options.surfaceType != 'none':
        errors.append('Must have the surface type "none".')

    if not mat.options.draw:
        errors.append('Must have draw enabled.')

    if mat.options.solid_camera:
        errors.append('Must have camera collision disabled.')

    if mat.options.poly_os > 0:
        errors.append('Must not have polygon offset.')

    if mat.blenderObject.xplane.manip.enabled:
        errors.append('Must not be a manipulator.')

    if mat.getEffectiveBlendGlass():
       errors.append('Blend glass only legal on aircraft and cockpit objects')

    return errors

def getFirstMatchingMaterial(materials, validation):
    for mat in materials:
        errors = validation(mat)

        if len(errors) == 0 and mat.options.draw:
            return mat

    return None

# Method: getReferenceMaterials
# Returns a list of one or materials, the first valid ones it finds. The content of the slots has meaning based on
# What the current export type is
#
# Aircraft:  [0] is the aircraft material, [1] is the (optional) panel material
# Cockpit:   [0] is the cockpit material,  [1] is the (optional) panel material
# Instanced: [0] is the instanced scenery, [1] is the (optional) draped material
# Scenery:   [0] is the scenery material,  [1] is the (optional) draped material
#
# Parameters:
#    List<XPlaneMaterial> - A list of materials found in an object
#    string exportType - The export type given by xplane_file.options.export_type
#
#    Returns list of 1 or more reference materials
def getReferenceMaterials(materials, exportType):
    refMats = []

    if exportType == EXPORT_TYPE_COCKPIT:
        refMats.append(getFirstMatchingMaterial(materials, validateCockpit))
        refMats.append(getFirstMatchingMaterial(materials, validatePanel))
    elif exportType == EXPORT_TYPE_AIRCRAFT:
        refMats.append(getFirstMatchingMaterial(materials, validateAircraft))
        refMats.append(getFirstMatchingMaterial(materials, validatePanel))
    elif exportType == EXPORT_TYPE_SCENERY:
        refMats.append(getFirstMatchingMaterial(materials, validateScenery))
        refMats.append(getFirstMatchingMaterial(materials, validateDraped))
    elif exportType == EXPORT_TYPE_INSTANCED_SCENERY:
        refMats.append(getFirstMatchingMaterial(materials, validateInstanced))
        refMats.append(getFirstMatchingMaterial(materials, validateDraped))

    return refMats
