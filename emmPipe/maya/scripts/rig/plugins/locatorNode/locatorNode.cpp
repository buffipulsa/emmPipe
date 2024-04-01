#include "locatorNode.h"

#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MFnDependencyNode.h>


const std::vector<std::string>  LocatorNode::colors = { "Dark Grey", "Grey", "Black", "Light Grey", "Medium Grey", "Light Red",
										 "Dark Blue", "Blue", "Dark Green", "Dark Purple", "Pink", "Orange",
										 "Dark Brown", "Dark Red", "Red", "Green", "Light Blue", "White", "Yellow",
										 "Baby Blue", "Light Green", "Light Pink", "Light Orange", "Light Yellow",
										 "Dark Green", "Dark Orange", "Dark Yellow", "Toxic Green", "Green",
										 "Dark Baby Blue", "Silk Blue", "Purple", "Dark Pink" };

const std::vector<std::string>  LocatorNode::shapes = { "Circle", "Square", "Triangle", "Box", "Sphere" };


MObject LocatorNode::scale;
MObject LocatorNode::localRotationX;
MObject LocatorNode::localRotationY;
MObject LocatorNode::localRotationZ;
MObject LocatorNode::localRotation;

MObject LocatorNode::shapesEnum;
MObject LocatorNode::colorsEnum;
MObject LocatorNode::filled;
MObject LocatorNode::lineThickness;

const MTypeId LocatorNode::typeId = 0x8007;
const MString LocatorNode::drawDbClassification = "drawdb/geometry/locatorNode";
const MString LocatorNode::drawRegistrantId = "LocatorNode";

void* LocatorNode::creator()
{
	return new LocatorNode;
}

MStatus LocatorNode::initialize()
{
	MFnNumericAttribute fnNum;
	MFnCompoundAttribute fnComp;
	MFnEnumAttribute fnEnum;
	

	scale = fnNum.create("scale", "scale", MFnNumericData::kFloat, 1.0);
	fnNum.setMin(0.0);
	fnNum.setKeyable(false);
	fnNum.setWritable(true);
	fnNum.setChannelBox(true);
	addAttribute(scale);

	localRotationX = fnNum.create("localRotationX", "localRotationX", MFnNumericData::kFloat);
	fnNum.setMin(-360);
	fnNum.setMax(360);
	fnNum.setKeyable(false);
	fnNum.setWritable(true);
	fnNum.setChannelBox(true);
	addAttribute(localRotationX);

	localRotationY = fnNum.create("localRotationY", "localRotationY", MFnNumericData::kFloat);
	fnNum.setMin(-360);
	fnNum.setMax(360);
	fnNum.setKeyable(false);
	fnNum.setWritable(true);
	fnNum.setChannelBox(true);
	addAttribute(localRotationY);

	localRotationZ = fnNum.create("localRotationZ", "localRotationZ", MFnNumericData::kFloat);
	fnNum.setMin(-360);
	fnNum.setMax(360);
	fnNum.setKeyable(false);
	fnNum.setWritable(true);
	fnNum.setChannelBox(true);
	addAttribute(localRotationZ);

	localRotation = fnComp.create("localRotation", "localRotation");
	fnComp.addChild(localRotationX);
	fnComp.addChild(localRotationY);
	fnComp.addChild(localRotationZ);
	addAttribute(localRotation);

	shapesEnum = fnEnum.create("shapes", "shapes", 0);
	for (unsigned int i = 0; i < shapes.size(); i++) {
		fnEnum.addField(MString(shapes[i].c_str()), i);
	}
	fnEnum.setKeyable(false);
	fnEnum.setWritable(true);
	fnEnum.setChannelBox(true);
	addAttribute(shapesEnum);

	colorsEnum = fnEnum.create("colors", "colors", 6);
	for (unsigned int i = 0; i < colors.size(); i++) {
		fnEnum.addField(MString(colors[i].c_str()), i);
	}
	fnEnum.setKeyable(false);
	fnEnum.setWritable(true);
	fnEnum.setChannelBox(true);
	addAttribute(colorsEnum);

	filled = fnNum.create("filled", "filled", MFnNumericData::kBoolean, 0); fnNum.setKeyable(false);
	fnNum.setWritable(true);
	fnNum.setChannelBox(true);
	addAttribute(filled);

	lineThickness = fnNum.create("lineThickness", "lineThickness", MFnNumericData::kFloat, 1.0);
	fnNum.setMin(1.0);
	fnNum.setWritable(true);
	fnNum.setChannelBox(true);
	addAttribute(lineThickness);


	attributeAffects(scale, localScale);
	attributeAffects(localRotation, localScale);

	return MS::kSuccess;
}

void LocatorNode::postConstructor()
{
	MFnDependencyNode fnNode(thisMObject());
	fnNode.setName("locatorShape#");
}
