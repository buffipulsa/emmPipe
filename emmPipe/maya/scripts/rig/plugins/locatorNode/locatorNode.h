#pragma once

#include <maya\MPxLocatorNode.h>

#include <iostream>
#include <vector>

class LocatorNode : public MPxLocatorNode
{
public:

	static const std::vector<std::string> colors;
	static const std::vector<std::string> shapes;

	static MObject scale;
	static MObject localRotationX;
	static MObject localRotationY;
	static MObject localRotationZ;
	static MObject localRotation;

	static MObject shapesEnum;
	static MObject colorsEnum;
	static MObject filled;
	static MObject lineThickness;

	// Foundation
	static const MTypeId typeId;
	static const MString drawDbClassification;
	static const MString drawRegistrantId;

	static void *creator();
	static MStatus initialize();

	void postConstructor() override;

};

