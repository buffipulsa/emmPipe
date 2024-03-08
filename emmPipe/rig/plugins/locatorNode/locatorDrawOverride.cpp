#include "locatorDrawOverride.h"
#include "locatorData.h"
#include "locatorNode.h"

#include <maya/MBoundingBox.h>
#include <maya/MPoint.h>
#include <maya/MUserData.h>
#include <maya/MMatrix.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MFnMatrixData.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MMatrix.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MEulerRotation.h>
#include <maya/MGlobal.h>
#include <maya/MPointArray.h>


const double LocatorDrawOverride::radian = 3.14159265358979323846 / 180;

LocatorDrawOverride::LocatorDrawOverride(const MObject& obj) : MHWRender::MPxDrawOverride(obj, nullptr, false){}

MHWRender::MPxDrawOverride* LocatorDrawOverride::creator(const MObject& obj)
{
	return new LocatorDrawOverride(obj);
}

MHWRender::DrawAPI LocatorDrawOverride::supportedDrawAPIs() const
{
	return MHWRender::kAllDevices;
}

bool LocatorDrawOverride::isBounded(const MDagPath& objPath, const MDagPath& cameraPath) const
{
	return true;
}

MBoundingBox LocatorDrawOverride::boundingBox(const MDagPath& objPath, const MDagPath& cameraPath) const
{
	return MBoundingBox(MPoint(1.0, 1.0, 1.0), MPoint(-1.0, -1.0, -1.0));
}

MUserData* LocatorDrawOverride::prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath, const MHWRender::MFrameContext& frameContext, MUserData* oldData)
{
	LocatorData* data = dynamic_cast<LocatorData*>(oldData);
	
	if (!data) {
		data = new LocatorData();
	}

	const MObject nodeObj = objPath.node();

	data->color          = MPlug(nodeObj, LocatorNode::colorsEnum).asShort();
    data->displayStatus  = MGeometryUtilities::displayStatus(objPath);
	data->wireFrameColor = MGeometryUtilities::wireframeColor(objPath);
	data->shape          = MPlug(nodeObj, LocatorNode::shapesEnum).asShort();
	data->filled         = MPlug(nodeObj, LocatorNode::filled).asBool();
	data->lineThickness  = MPlug(nodeObj, LocatorNode::lineThickness).asFloat();

	return data;
}

bool LocatorDrawOverride::hasUIDrawables() const
{
	return true;
}

void LocatorDrawOverride::addUIDrawables(const MDagPath& objPath, MUIDrawManager& drawManager, const MFrameContext& frameContext, const MUserData* data)
{
	const LocatorData* userData = dynamic_cast<const LocatorData*>(data);
	if (!data) {
		return;
	}

	drawManager.beginDrawable();;

	drawManager.setColor(userData->wireFrameColor);
	if (userData->displayStatus == MHWRender::kDormant) {
		drawManager.setColorIndex(userData->color);
	}

	drawManager.setLineWidth(userData->lineThickness);

	switch (userData->shape) {
	case 0:
	{
		drawManager.circle(MPoint(0, 0, 0), MVector(0, 1, 0), 1, userData->filled);
		break;
	}
	case 1:
	{
		drawManager.rect(MPoint(0, 0, 0), MVector(0, 0, 1), MVector(0, 1, 0), 1.0, 1.0, userData->filled);
		break;
	}
	case 2:
	{
		const double trianglePoints[4][4] = { { -1.0, 0.0, -1.0}, {0.0, 0.0, 1.0}, {1.0, 0.0, -1.0}, {-1.0, 0.0, -1.0} };
		MPointArray pointArray = MPointArray(trianglePoints, 4);
		drawManager.lineStrip(pointArray, false);
		break;
	}
	case 3:
	{
		drawManager.box(MPoint(0, 0, 0), MVector(0, 1, 0), MVector(1, 0, 0), 1.0, 1.0, 1.0, userData->filled);
		break;
	}
	case 4:
	{
		drawManager.sphere(MPoint(0,0,0), 1.0, 8, 6, userData->filled);
		break;
	}
	}

	drawManager.endDrawable();
}

MMatrix LocatorDrawOverride::transform(const MDagPath& objPath, const MDagPath& cameraPath) const
{
	/* Create a new matrix for the shape by getting the transforms matrix
		and adding a local matrix for position, orientation and scale */

	MStatus status;

	const MObject nodeObj = objPath.node(); 
	const MObject transformObj = objPath.transform();

	// Find all plugs needed
	float localTx = MPlug(nodeObj, LocatorNode::localPositionX).asFloat();
	float localTy = MPlug(nodeObj, LocatorNode::localPositionY).asFloat();
	float localTz = MPlug(nodeObj, LocatorNode::localPositionZ).asFloat();
	float localSx = MPlug(nodeObj, LocatorNode::localScaleX).asFloat();
	float localSy = MPlug(nodeObj, LocatorNode::localScaleY).asFloat();
	float localSz = MPlug(nodeObj, LocatorNode::localScaleZ).asFloat();
	float scale   = MPlug(nodeObj, LocatorNode::scale).asFloat();
	float localRx = MPlug(nodeObj, LocatorNode::localRotationX).asFloat();
	float localRy = MPlug(nodeObj, LocatorNode::localRotationY).asFloat();
	float localRz = MPlug(nodeObj, LocatorNode::localRotationZ).asFloat();

	// Get the transform matrix
	MPlug transformMatrixPlugArray = MPlug(transformObj, LocatorNode::worldMatrix);
	transformMatrixPlugArray.evaluateNumElements();
	MPlug transformMatrixPlug = transformMatrixPlugArray.elementByPhysicalIndex(0);
	MObject transformMatrixPlugObj = transformMatrixPlug.asMObject();
	MMatrix transformMatrix = MFnMatrixData(transformMatrixPlugObj).matrix();

	// Set the local translates
	MTransformationMatrix localMatrix = MTransformationMatrix(MMatrix());
	localMatrix.setTranslation(MVector(localTx, localTy, localTz), MSpace::kObject);
	
	// Set the local scale
	double scaleArray[3] = {localSx * scale, localSy * scale, localSz * scale};
	localMatrix.setScale(scaleArray, MSpace::kObject);

	// Calculate radians for rotation
	double radiansX = localRx * radian;
	double radiansY = localRy * radian;
	double radiansZ = localRz * radian;
	MEulerRotation orientation = MEulerRotation(radiansX, radiansY, radiansZ);
	localMatrix.rotateBy(orientation, MSpace::kObject);

	MMatrix resultMatrix = localMatrix.asMatrix() * transformMatrix;

	return resultMatrix;
}