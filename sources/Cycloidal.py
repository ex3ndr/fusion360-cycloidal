import adsk.core, adsk.fusion, traceback, math

#
# Generation of cycloidal drive
#

def createCycloidalDisk(root, pinD, numOuterPins, pinCircleD, diskHeight, eccentricity):

    # Load the necessary api
    extrudes = root.features.extrudeFeatures
    sketches = root.sketches
    xyPlane = root.xYConstructionPlane

    # We are calciulating by offsetting so disk base radius is half the pin circle diameter
    diskRadius =  pinCircleD / 2
    approximation_points_per_pin = 32
    approximation_points = numOuterPins * approximation_points_per_pin

    # Create the sketch for the pin circle
    pinCircleSketch = sketches.add(xyPlane)
    pinCircleSketch.name = 'Pin Circle'
    for i in range(numOuterPins):
        angle = i * math.pi * 2 / numOuterPins
        px = (pinCircleD / 2) * math.cos(angle)
        py = (pinCircleD / 2) * math.sin(angle)
        pinCircleSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(px, py, 0), pinD/2)
    pinCircleSketch.sketchPoints.add(adsk.core.Point3D.create(0, 0, 0)) # Center point
    pinCircleSketch.sketchPoints.add(adsk.core.Point3D.create(-eccentricity, 0, 0)) # Eccentricity point

    # Create the sketch for the cycloidal disk
    diskSketch = sketches.add(xyPlane)
    diskSketch.name = 'Cycloidal Disk'

    # Draw the cycloidal disk points
    points = adsk.core.ObjectCollection.create()
    for i in range(approximation_points + 1):

        # Calculate the current angle
        angle = (i / approximation_points) * 2 * math.pi

        # Add a point
        px = -eccentricity + (diskRadius * math.cos(angle)) + (eccentricity * math.cos(numOuterPins * angle))
        py = (diskRadius * math.sin(angle)) + (eccentricity * math.sin(numOuterPins * angle))
        points.add(adsk.core.Point3D.create(px, py, 0))
    spline = diskSketch.sketchCurves.sketchFittedSplines.add(points)
    curves = diskSketch.findConnectedCurves(spline)
    dirPoint = adsk.core.Point3D.create(0, 0, 0)
    diskSketch.offset(curves, dirPoint, pinD/2)
    spline.deleteMe() # Delete the base spline

    # Extrude the disk
    prof = diskSketch.profiles.item(1)
    distance = adsk.core.ValueInput.createByReal(diskHeight)
    diskExtrude = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)        
    disk = diskExtrude.bodies.item(0)
    disk.name = "Cycloidal Disk"

#
# UI Wrapper
#

_app = None
_ui  = None
pinDiameter = adsk.core.ValueCommandInput.cast(None)
pinNumber = adsk.core.ValueCommandInput.cast(None)
pinCircleDiameter = adsk.core.ValueCommandInput.cast(None)
diskHeight = adsk.core.ValueCommandInput.cast(None)
eccentricity = adsk.core.ValueCommandInput.cast(None)
_handlers = []

class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            onDestroy = CommandDestroyHandler()
            _handlers.append(onDestroy) 
            cmd.destroy.add(onDestroy)
            inputs = cmd.commandInputs
            global pinDiameter, pinNumber, diskHeight, eccentricity, pinCircleDiameter

            # add inputs
            diskHeight = inputs.addValueInput('diskHeight', 'Disk Height', 'mm', adsk.core.ValueInput.createByReal(0.5))
            pinDiameter = inputs.addValueInput('pinDiameter', 'Pin Diameter', 'mm', adsk.core.ValueInput.createByReal(0.5))
            pinCircleDiameter = inputs.addValueInput('pinCircleDiameter', 'Pin Circle Diameter', 'mm', adsk.core.ValueInput.createByReal(5))
            pinNumber = inputs.addValueInput('pinNumber', 'Number of Pins', '', adsk.core.ValueInput.createByReal(10))
            eccentricity = inputs.addValueInput('eccentricity', 'Eccentricity', 'mm', adsk.core.ValueInput.createByReal(0.2))
            

            onExecute = CycloidalGearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CycloidalGearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global pinDiameter, pinNumber, diskHeight, eccentricity, pinCircleDiameter
            
            pinDiameter = pinDiameter.value
            pinNumber = int(pinNumber.value)
            diskHeight = diskHeight.value
            eccentricity = eccentricity.value
            pinCircleDiameter = pinCircleDiameter.value

            app = adsk.core.Application.get()
            design = app.activeProduct
            rootComp = design.rootComponent
            createCycloidalDisk(rootComp, pinDiameter, pinNumber, pinCircleDiameter, diskHeight, eccentricity)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        cmdDef = _ui.commandDefinitions.itemById('cmdInputsCyclGear')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdInputsCyclGear', 'Cycloidal Gear', 'Creates a cycloidal gear based on input parameters.')
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        cmdDef.execute()
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))