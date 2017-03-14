import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy

#
# SurgeryToolkit
#

class SurgeryToolkit(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SurgeryToolkit" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"

#
# SurgeryToolkitWidget
#

class SurgeryToolkitWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # threshold value
    #
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 0.1
    self.imageThresholdSliderWidget.minimum = -100
    self.imageThresholdSliderWidget.maximum = 100
    self.imageThresholdSliderWidget.value = 0.5
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = SurgeryToolkitLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

#
# SurgeryToolkitLogic
#

class SurgeryToolkitLogic(ScriptedLoadableModuleLogic):
    """
        @Tamas
        I would start by creating a python list with the indices of the longer fiducial list: [1,2,3,...].
        If there are N number of fiducials in the smaller fiducial list, I would compute the permutations of all
        N-element combinations of the longer fiducial list indices. Then I would run the landmark registration on all
        these permutations, and record the FRE. The combination/permutation of the lowest FRE value is probably the right one.
        To generate permutations and combinations, google python permutation and python combination.
    """
    def fiduciaryRegistration(self):
        """
        @John Martin
        Input: two fiducial lists
        Output: Minimum RMSE after fiducial registration
        Description:
        Take the smaller of the two lists, try every possible combination of fiducial registration,
        checking the average distance (root mean square distance), each time and find the minimum RMS Distance.
        This is a greedy algorithm, and will be implmented as such.
        """
        x = 0
        return x

    def averageTransformedDistance(self, alphaPoints, betaPoints, alphaToBetaMatrix):
        average = 0
        num = 0

        numberOfPoints = alphaPoints.GetNumberOfPoints()
        bNum = betaPoints.GetNumberOfPoints()

        if numberOfPoints != bNum:
            logging.error('number of points in two lists do not match')
            return -1

        for i in range(numberOfPoints):
            num = num + 1
            a = alphaPoints.GetPoint(i)
            pointA_Alpha = numpy.array(a)
            pointA_Alpha = numpy.append(pointA_Alpha, 1)
            pointA_Beta = alphaToBetaMatrix.MultiplyFloatPoint(pointA_Alpha)
            b = betaPoints.GetPoint(i)
            pointB_Beta = numpy.array(b)
            pointB_Beta = numpy.append(pointB_Beta, 1)
            distance = numpy.linalg.norm(pointA_Beta - pointB_Beta)
            average = average+ (distance-average) / num

        return average

    def rigidRegistration(self, alphaPoints, betaPoints, alphaToBetaMatrix):
        landmarkTransform = vtk.vtkLandmarkTransform()
        landmarkTransform.SetSourceLandmarks(alphaPoints)
        landmarkTransform.SetTargetLandmarks(betaPoints)
        landmarkTransform.SetModeToRigidBody()
        landmarkTransform.Update()
        landmarkTransform.GetMatrix(alphaToBetaMatrix)





class SurgeryToolkitTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  """
  @Raniem Alsaadi
  This function is used to create the first test case which generates two fiducial lists one
  with 8 points and the second one is created by adding noise to the first list and reorder the points
  the second list just have 6 elements to test the registration with missing points and missed up order
  """

  def generatePoints(self, numPoints, Scale, Sigma):
      rasFids = slicer.util.getNode('fromFiducials')
      if rasFids == None:
          rasFids = slicer.vtkMRMLMarkupsFiducialNode()
          rasFids.SetName('fromFiducials')
          slicer.mrmlScene.AddNode(rasFids)
      rasFids.RemoveAllMarkups()

      refFids = slicer.util.getNode('toFiducials')
      if refFids == None:
          refFids = slicer.vtkMRMLMarkupsFiducialNode()
          refFids.SetName('toFiducials')
          slicer.mrmlScene.AddNode(refFids)
      refFids.RemoveAllMarkups()
      refFids.GetDisplayNode().SetSelectedColor(1,1,0)

      fromNormCoordinates = numpy.random.rand(numPoints, 3)

      noise = numpy.random.normal(0.0, Sigma, numPoints*3)

      #@John: It is not clear what the purpose of tempPoints is

      # create temporary points
      tempPoints = vtk.vtkPoints()

      # create the reference points
      for i in range(numPoints):
          x = (fromNormCoordinates[i, 0] - 0.5) * Scale
          y = (fromNormCoordinates[i, 1] - 0.5) * Scale
          z = (fromNormCoordinates[i, 2] - 0.5) * Scale
          rasFids.AddFiducial(x, y, z)

          #@John: Only 6 fiducals created for 'toFiducials'
          if not i > numPoints-3:
              xx = x+noise[i*3]
              yy = y+noise[i*3+1]
              zz = z+noise[i*3+2]
              refFids.AddFiducial(xx, yy, zz)



  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SurgeryToolkit1()

  def test_SurgeryToolkit1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    self.generatePoints(8, 100, 3)
