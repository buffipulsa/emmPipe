#pragma once
#include <maya/MUserData.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MColor.h>


class LocatorData : public MUserData
{
public:
	
	MColor wireFrameColor;
	int color;
	short shape;
	bool filled;
	float lineThickness;
	MHWRender::DisplayStatus displayStatus;
	
	LocatorData();
	virtual ~LocatorData() override;

};

