#pragma once

#include <maya/MPxDrawOverride.h>

class LocatorDrawOverride : public MHWRender::MPxDrawOverride
{
private:
	static const double radian;
	
	static MString shapes[];
	static MStringArray shapesArray;

	LocatorDrawOverride(const MObject& obj);

public:

	static MHWRender::MPxDrawOverride* creator(const MObject& obj);

	MHWRender::DrawAPI supportedDrawAPIs()	const override;

	bool isBounded(const MDagPath& objPath, const MDagPath& cameraPath) const override;

	MBoundingBox boundingBox(const MDagPath& objPath, const MDagPath& cameraPath) const override;

	MUserData* prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath, const MHWRender::MFrameContext& frameContext, MUserData* oldData) override;

	bool hasUIDrawables() const override;

	void addUIDrawables(const MDagPath& objPath, MUIDrawManager& drawManager, const MFrameContext& frameContext, const MUserData* data) override;

	MMatrix transform(const MDagPath& objPath, const MDagPath& cameraPath) const override;

};

