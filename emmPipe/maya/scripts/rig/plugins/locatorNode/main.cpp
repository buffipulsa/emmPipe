#include "locatorNode.h"
#include "locatorDrawOverride.h"

#include <maya\MFnPlugin.h>
#include <maya\MGlobal.h>
#include <maya\MStatus.h>
#include <maya\MDrawRegistry.h>

MStatus initializePlugin(MObject obj)
{

	const char* vendor = "Einar Mar Magnusson";
	const char* version = "1.0.0 DEBUG";
	const char* requiredAPIVersion = "Any";

	MStatus status;

	MFnPlugin fnPlugin(obj, vendor, version, requiredAPIVersion, &status); CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.registerNode("locatorNode", LocatorNode::typeId, LocatorNode::creator, LocatorNode::initialize, MPxNode::kLocatorNode, &LocatorNode::drawDbClassification); CHECK_MSTATUS_AND_RETURN_IT(status);

	if (status != MS::kSuccess)
	{
		MGlobal::displayError("Could not register the node: " + status.errorString());
	}

	status = MHWRender::MDrawRegistry::registerDrawOverrideCreator(LocatorNode::drawDbClassification, LocatorNode::drawRegistrantId, LocatorDrawOverride::creator);
	if (status != MS::kSuccess)
	{
		MGlobal::displayError("Could not register the node: " + status.errorString());
	}

	return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus status;

	MFnPlugin fnPlugin(obj);
	status = fnPlugin.deregisterNode(LocatorNode::typeId); CHECK_MSTATUS_AND_RETURN_IT(status);

	if (status != MS::kSuccess)
	{
		MGlobal::displayError("Could not unregister the node: " + status.errorString());
	}

	status = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(LocatorNode::drawDbClassification, LocatorNode::drawRegistrantId);

	if (status != MS::kSuccess)
	{
		MGlobal::displayError("Could not unregister the node: " + status.errorString());
	}

	return status;
}