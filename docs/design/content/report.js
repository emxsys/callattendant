var incX = 0;
var incY = 0;
var intervalID = -1;
var goToURL = "#";
var shapeSpecURL = "#";
var cursorX = 0;
var cursorY = 0;

function loadUrl() {
    var lArgString = location.search.substring(1, location.search.length);
    var lArgs = lArgString.split("&");
    for (i = 0; i < lArgs.length; i++) {
        var lIndex = lArgs[i].indexOf('=');
        if (lIndex>0) {
            var lArgName = lArgs[i].substring(0, lIndex);
            if (lArgName == 'url') {
                var lUrl = lArgs[i].substring(lIndex+1);
                parent._content_pane.location.href = lUrl;
            }
        }
    }
}

var baseX = 0;
function initDiagram() {

	var diagram = document.getElementById("diagram");
	var spotLight_top = document.getElementById("spotlight_top");
	if (diagram != null && spotLight_top != null) {
		baseX = findPosX(diagram)-findPosX(spotLight_top);
	}
	
	url = window.location.href;
	shapeIndex = url.indexOf('?shapeid=');
	if (shapeIndex != -1) {
		shapeid = url.substring(shapeIndex + '?shapeid='.length);
		lSelect = document.getElementById("SelectShape");
		if (lSelect != null) {
			for (i = 0; i < lSelect.options.length; i++) {
				if (lSelect.options[i].id == "option" + shapeid) {
					lSelect.selectedIndex = i;
					scrollWin("diagram", lSelect.value);
					showSpotLight("diagram", lSelect.value);
					break;
				}
			}
		}
	}
}
function initGridDiagram() {
	url = window.location.href;
	modelIndex = url.indexOf('.html#');
	if (modelIndex != -1) {
		modelid = url.substring(modelIndex + '.html#'.length);
		
		highlightGridModelSelection(modelid);
	}
}
var lastGridModelSelection;
var lastGridModelSelectionBackground;
function highlightGridModelSelection(modelid) {
	if (lastGridModelSelection != null) {
		lastGridModelSelection.style.background = lastGridModelSelectionBackground;
		lastGridModelSelection = null;
	}
	
	lSelect = document.getElementById('modelSelection' + modelid);
	if (lSelect != null) {
		
		lastGridModelSelection = lSelect;
		lastGridModelSelectionBackground = lSelect.style.background;
		
		lSelect.style.background='#FFE0E0';
	}
}
var currentStateSelectShapeId;
var currentStateImageId;
var currentStateDescriptionId;
var currentStateElementsId;
function initWireframeDiagram() {
	url = window.location.href;
	var stateIndex = url.indexOf('.html#');
	
	var lDefaultStateId = document.getElementById("defaultState").getAttribute("data-value");
	
	var lDefaultStateSelectShapeId = "selectShape" + lDefaultStateId;
	var lDefaultStateImageId = "diagram" + lDefaultStateId;
	var lDefaultStateDescriptionId = "description" + lDefaultStateId;
	var lDefaultStateElementsId = "elements" + lDefaultStateId;
	
	var lPageTitleId = "PageTitleText";
	
	currentStateSelectShapeId = lDefaultStateSelectShapeId;
	currentStateImageId = lDefaultStateImageId;
	currentStateDescriptionId = lDefaultStateDescriptionId;
	currentStateElementsId = lDefaultStateElementsId;
	
	if (stateIndex != -1) {
		// url can be #{state.id};{element.id}, refer to WireframeDiagramTemplate's element url
		var lArgString = url.substring(stateIndex + '.html#'.length);
		var lArgs = lArgString.split(";");
		var stateId = lArgs[0];
		
		var lStateSelectShapeId = "selectShape" + stateId;
		var lStateImageId = "diagram" + stateId;
		var lStateDescriptionId = "description" + stateId;
		var lStateElementsId = "elements" + stateId;
		
		var lStateTitleTextId = "pageTitleText"+stateId;
		
		okWireframeStatesDialog(lStateSelectShapeId, lStateImageId, lStateDescriptionId, lStateElementsId, lPageTitleId, lStateTitleTextId);
	}
	else {
		
		var lDefaultStateTitleTextId = "defaultPageTitleText";
		
		okWireframeStatesDialog(lDefaultStateSelectShapeId, lDefaultStateImageId, lDefaultStateDescriptionId, lDefaultStateElementsId, lPageTitleId, lDefaultStateTitleTextId);
	}
	
}



function scrollWin(diagramId, modelValues) {

	if (modelValues != '') {
		var diagram = document.getElementById(diagramId);
		var xOffset = findPosX(diagram);
		var yOffset = findPosY(diagram);
	
		var viewportWidth = 0, viewportHeight = 0;
		if( typeof( window.innerWidth ) == 'number' ) {
			viewportWidth = window.innerWidth;
			viewportHeight = window.innerHeight;
		} else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
			viewportWidth = document.documentElement.clientWidth;
			viewportHeight = document.documentElement.clientHeight;
		} else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
			viewportWidth = document.body.clientWidth;
			viewportHeight = document.body.clientHeight;
		}
		
		var lValues = modelValues.split("|");
		var lValueIndex = 0;
		var shapeOrConnector = lValues[lValueIndex++];
		
		var shapeX = lValues[lValueIndex++]*1;
		var shapeY = lValues[lValueIndex++]*1;
		var w = lValues[lValueIndex++]*1 + 20;
		var h = lValues[lValueIndex++]*1 + 20;
		var x = shapeX + xOffset*1 - viewportWidth/2 + w/2;
		var y = shapeY + yOffset*1 - viewportHeight/2 + h/2;
	
		incX = incY = 2;
		
		if (document.all) {
			if (!document.documentElement.scrollLeft)
				incX *= (document.body.scrollLeft > x?-15:15);
			else
				incX *= (document.documentElement.scrollLeft > x?-15:15);
								 
			if (!document.documentElement.scrollTop)
				incY *= (document.body.scrollTop > y?-15:15);
			else
				incY *= (document.documentElement.scrollTop > y?-15:15);
	
		}
		else {
			incX *= (window.pageXOffset > x?-15:15);
			incY *= (window.pageYOffset > y?-15:15);
		}
		
		intervalID = setInterval("doScroll(" + x + ", " + y +")", 1);
	}	
}

function doScroll(x, y) {
	var beforeX;
	var beforeY;
	var afterX;
	var afterY;

	if (document.all){
		if (!document.documentElement.scrollLeft)
			beforeX = document.body.scrollLeft;
		else
			beforeX = document.documentElement.scrollLeft;
							 
		if (!document.documentElement.scrollTop)
			beforeY = document.body.scrollTop;
		else
			beforeY = document.documentElement.scrollTop;
			
	}else{
		beforeX = window.pageXOffset;
		beforeY = window.pageYOffset;
	}

	window.scrollTo(beforeX+incX, beforeY+incY);
	
		if (document.all){
		if (!document.documentElement.scrollLeft)
			afterX = document.body.scrollLeft;
		else
			afterX = document.documentElement.scrollLeft;
							 
		if (!document.documentElement.scrollTop)
			afterY = document.body.scrollTop;
		else
			afterY = document.documentElement.scrollTop;
			
	}else{
		afterX = window.pageXOffset;
		afterY = window.pageYOffset;
	}
	
	if (incX!=0 && beforeX==afterX)
		incX = 0;
	if (incY!=0 && beforeY==afterY)
		incY = 0;
	
	if ((incX < 0 && (afterX < x || afterX+incX < x)) || (incX > 0 && (afterX > x || afterX+incX > x))) {
		incX = 0;
	} if ((incY < 0 && (afterY < y || afterY+incY < y)) || (incY > 0 && (afterY > y || afterY+incY > y))) {
		incY = 0;
	}

	if (incX==0 && incY==0) {
				window.clearInterval(intervalID);
	}
}

function findPosX(obj)
{
	var curleft = 0;
	if (obj.offsetParent)
	{
		while (obj.offsetParent)
		{
			curleft += obj.offsetLeft
			obj = obj.offsetParent;
		}
	}
	else if (obj.x)
		curleft += obj.x;
	return curleft;
}

function findPosY(obj)
{
	var curtop = 0;
	if (obj.offsetParent)
	{
		while (obj.offsetParent)
		{
			curtop += obj.offsetTop
			obj = obj.offsetParent;
		}
	}
	else if (obj.y)
		curtop += obj.y;
	return curtop;
}

function showSpotLight(diagramId, modelValues) {
	hideWireframeStatesDialog();
	
	if (modelValues != '') {
		var diagram = document.getElementById(diagramId);
		var xOffset = findPosX(diagram);
		var yOffset = findPosY(diagram);
		
		xOffset -= baseX;
		
		var lValues = modelValues.split("|");
		var lValueIndex = 0;
		var shapeOrConnector = lValues[lValueIndex++];
		
		var shapeX = lValues[lValueIndex++]*1;
		var shapeY = lValues[lValueIndex++]*1;
		var x = shapeX + xOffset*1 - 10;
		var y = shapeY + yOffset*1 - 10;
		var w = lValues[lValueIndex++]*1 + 20;
		var h = lValues[lValueIndex++]*1 + 20;
		var url_for_image_map = lValues[lValueIndex++];
		var url_for_spec = lValues[lValueIndex++];
		
		var spotLight = document.getElementById("spotlight");
		var spotLight_top = document.getElementById("spotlight_top");
		var spotLight_bottom = document.getElementById("spotlight_bottom");
		var spotLight_left = document.getElementById("spotlight_left");
		var spotLight_right = document.getElementById("spotlight_right");
		
		var spotlight_c = document.getElementById("spotlight_c");
		var spotLightResourcesTop = document.getElementById("spotLightResourcesTop");
		var spotLightResourcesRight = document.getElementById("spotLightResourcesRight");
		var spotLightTable = document.getElementById("spotLightTable");
		var spotLightCell = document.getElementById("spotLightCell");
		
		if (spotLight == null) {
			spotLight_top.style.width = w+2;
			spotLight_bottom.style.width = w+2;
			spotLight_left.style.height = h+2;
			spotLight_right.style.height = h+2;
			
			spotLight_top.style.height = 2;
			spotLight_bottom.style.height = 2;
			spotLight_left.style.width = 2;
			spotLight_right.style.width = 2;
		}
		else {
			spotLight.style.width = w;
			spotLight.style.height = h;
		}
		
		spotlight_c.width = w;
		spotlight_c.height = h;
		
		goToURL = url_for_image_map;
		shapeSpecURL = url_for_spec;
		
		var areaId = lValues[lValueIndex++];
		var areaObj = document.getElementById(areaId);
		if (areaId != null && spotLightCell != null) {
			spotLightCell.onmouseover= function onmouseover(event) {
				if (areaObj != null) {
					areaObj.onmouseover();
				}
			};
			spotLightCell.onmouseout= function onmouseout(event) {
				if (areaObj != null) {
					areaObj.onmouseout();
				}
			};
		}
		
		N = (document.all) ? 0 : 1;
		if (N) {
			if (spotLight == null) {
				spotLight_top.style.left = x;
				spotLight_top.style.top = y;
				spotLight_bottom.style.left = x;
				spotLight_bottom.style.top = y+h+2;
				spotLight_left.style.left = x;
				spotLight_left.style.top = y;
				spotLight_right.style.left = x+w;
				spotLight_right.style.top = y;
			}
			else {
				spotLight.style.left = x;
				spotLight.style.top = y;
				
				spotLightTable.style.width = w;
				spotLightCell.style.width = w
				spotLightCell.style.height = h;
			}
			
			spotlight_c.style.left = x;
			spotlight_c.style.top = y;
			
			spotLightResourcesTop.style.left = x + w - 50;
			spotLightResourcesTop.style.top = y - 25;
			spotLightResourcesRight.style.left = x + w;
			spotLightResourcesRight.style.top = y + 10;
		}
		else {
			if (spotLight == null) {
				spotLight_top.style.posLeft = x;
				spotLight_top.style.posTop = y;
				spotLight_bottom.style.posLeft = x;
				spotLight_bottom.style.posTop = y+h;
				spotLight_left.style.posLeft = x;
				spotLight_left.style.posTop = y;
				spotLight_right.style.posLeft = x+w;
				spotLight_right.style.posTop = y;
			}
			else {
				spotLight.style.posLeft = x;
				spotLight.style.posTop = y;
				
				spotLightTable.style.width = w;
				spotLightCell.style.width = w;
				spotLightCell.style.height = h;
			}
			spotlight_c.style.posLeft = x;
			spotlight_c.style.posTop = y;
			
			spotLightResourcesTop.style.posLeft = x + w - 50;
			spotLightResourcesTop.style.posTop = y - 25;
			spotLightResourcesRight.style.posLeft = x + w;
			spotLightResourcesRight.style.posTop = y + 10;
		}			
		
		
		if (shapeOrConnector == 'connector') {
			// drawing connector
			if (spotLight == null) {
				spotLight_top.style.visibility = "hidden";
				spotLight_bottom.style.visibility = "hidden";
				spotLight_left.style.visibility = "hidden";
				spotLight_right.style.visibility = "hidden";
			}
			else {
				spotLight.style.visibility = "hidden";
			}
			
			var lPointCount = lValues[lValueIndex++];
			if (lPointCount > 0) {
				spotlight_c.style.visibility = "visible"
				
				var context = spotlight_c.getContext('2d');
				
				{
					context.beginPath();
					for (var lPointIndex = 0; lPointIndex < lPointCount; lPointIndex++) {
						var lPointX = lValues[lValueIndex++]*1 + 10; // +10, because <canvas 's x/y is -10, w/h is + 20.
						var lPointY = lValues[lValueIndex++]*1 + 10;
						
						if (lPointIndex == 0) {
							context.moveTo(lPointX+0.5, lPointY+0.5);
						}
						else {
							context.lineTo(lPointX+0.5, lPointY+0.5);
						}
					}
					context.lineWidth = 7;
					context.lineJoin = "round";
					context.strokeStyle="#0000FF";
					context.stroke();
				}
			}
			else {
				spotlight_c.style.visibility = "hidden"
			}
		}
		else {
			if (spotLight == null) {
				spotLight_top.style.visibility = "visible";
				spotLight_bottom.style.visibility = "visible";
				spotLight_left.style.visibility = "visible";
				spotLight_right.style.visibility = "visible";
			}
			else {
				spotLight.style.visibility = "visible";
			}
			
			spotlight_c.style.visibility = "hidden"
		}
		
		if (shapeY < 40){
			spotLightResourcesRight.style.visibility = "visible"
			spotLightResourcesTop.style.visibility = "hidden"
		}
		else {
			spotLightResourcesRight.style.visibility = "hidden"
			spotLightResourcesTop.style.visibility = "visible"
		}
		
	}
	else {
		var spotLight = document.getElementById("spotlight");
		var spotLight_top = document.getElementById("spotlight_top");
		var spotLight_bottom = document.getElementById("spotlight_bottom");
		var spotLight_left = document.getElementById("spotlight_left");
		var spotLight_right = document.getElementById("spotlight_right");
		var spotlight_c = document.getElementById("spotlight_c");
		var spotLightResourcesTop = document.getElementById("spotLightResourcesTop");
		var spotLightResourcesRight = document.getElementById("spotLightResourcesRight");
		
		if (spotLight == null) {
			spotLight_top.style.visibility = "hidden";
			spotLight_bottom.style.visibility = "hidden";
			spotLight_left.style.visibility = "hidden";
			spotLight_right.style.visibility = "hidden";
		}
		else {
			spotLight.style.visibility = "hidden";
		}
		
		spotlight_c.style.visibility = "hidden"
		spotLightResourcesTop.style.visibility = "hidden"
		spotLightResourcesRight.style.visibility = "hidden"
	}
}

function clearSpotLight() {
	var spotLight = document.getElementById("spotlight");
	var spotLight_top = document.getElementById("spotlight_top");
	var spotLight_bottom = document.getElementById("spotlight_bottom");
	var spotLight_left = document.getElementById("spotlight_left");
	var spotLight_right = document.getElementById("spotlight_right");
	var spotlight_c = document.getElementById("spotlight_c");
	var spotLightResourcesTop = document.getElementById("spotLightResourcesTop");
	var spotLightResourcesRight = document.getElementById("spotLightResourcesRight");
	
	if (spotLight == null) {
		spotLight_top.style.visibility = "hidden";
		spotLight_bottom.style.visibility = "hidden";
		spotLight_left.style.visibility = "hidden";
		spotLight_right.style.visibility = "hidden";
	}
	else {
		spotLight.style.visibility = "hidden";
	}
	
	spotlight_c.style.visibility = "hidden"
	spotLightResourcesTop.style.visibility = "hidden"
	spotLightResourcesRight.style.visibility = "hidden"
	// document.location.href = goToURL;
}

function clearSpotLightFromOpenSpecButton() {
	var spotLight = document.getElementById("spotlight");
	var spotLight_top = document.getElementById("spotlight_top");
	var spotLight_bottom = document.getElementById("spotlight_bottom");
	var spotLight_left = document.getElementById("spotlight_left");
	var spotLight_right = document.getElementById("spotlight_right");
	var spotlight_c = document.getElementById("spotlight_c");
	var spotLightResourcesTop = document.getElementById("spotLightResourcesTop");
	var spotLightResourcesRight = document.getElementById("spotLightResourcesRight");
	
	if (spotLight == null) {
		spotLight_top.style.visibility = "hidden";
		spotLight_bottom.style.visibility = "hidden";
		spotLight_left.style.visibility = "hidden";
		spotLight_right.style.visibility = "hidden";
	}
	else {
		spotLight.style.visibility = "hidden"
	}
		
	spotlight_c.style.visibility = "hidden"
	spotLightResourcesTop.style.visibility = "hidden"
	spotLightResourcesRight.style.visibility = "hidden"
	document.location.href = shapeSpecURL;
}

function showLayersDialog(layersDialogId) {
	var layersDialog = document.getElementById(layersDialogId);
	
	var base = document.getElementById("diagram");
	
	var xOffset = findPosX(base) + 10;
	var yOffset = findPosY(base);
	
	layersDialog.style.left = xOffset;
	layersDialog.style.top = yOffset;
	layersDialog.style.display = "block";
	layersDialog.style.zIndex = 5;
}
function okLayersDialog(layersDialogId, checkBoxIds) {
	var layersDialog = document.getElementById(layersDialogId);
	layersDialog.style.display = "none";
	
	var count = checkBoxIds.length;
	var lHidedCount = 0;
	for (var i = 0; i < count; i++) {
		var checkbox = document.getElementById(checkBoxIds[i]);
		if (checkbox.checked) {
		}
		else {
			lHidedCount++;
		}
	}
	
	if (lHidedCount == 0) {
		showComponent("fullDiagram");
		hideComponent("layersBackground");
	}
	else {
		hideComponent("fullDiagram");
		showComponent("layersBackground");
	}
	
	for (var i = 0; i < count; i++) {
		var checkbox = document.getElementById(checkBoxIds[i]);
		var rowIds = checkbox.value.split(";");
		if (checkbox.checked) {
			var rowCount = rowIds.length;
			for (var rowIndex = 0; rowIndex < rowCount; rowIndex++) {
				var lRowId = rowIds[rowIndex]
				if (lHidedCount == 0 && lRowId.length > 12 && lRowId.substring(12, 0) == "diagramLayer") {
					hideComponent(lRowId); // hide Diagram, because all layers shown, just show the full diagram
				}
				else {
					showComponent(lRowId);
				}
			}
		}
		else {
			var rowCount = rowIds.length;
			for (var rowIndex = 0; rowIndex < rowCount; rowIndex++) {
				hideComponent(rowIds[rowIndex]);
			}
		}
	}
	layersDialog.style.zIndex = 1;
}

function showWireframeStatesDialog() {
	clearSpotLight();
	
	var lDialogId = "wireframeStatesDialog"; // hardcoded in #showWireframeStatesDialog(...), #okWireframeStatesDialog(...), #hideWireframeStatesDialog(...)
	var wireframeStatesDialog = document.getElementById(lDialogId);
	
	if (wireframeStatesDialog.style.display != "none") {
		wireframeStatesDialog.style.display = "none";
	}
	else {
		
		var base = document.getElementById(currentStateImageId);
		
		var xOffset = findPosX(base) + 10;
		var yOffset = findPosY(base);
		
		wireframeStatesDialog.style.left = xOffset;
		wireframeStatesDialog.style.top = yOffset;
		wireframeStatesDialog.style.display = "block";
		wireframeStatesDialog.style.zIndex = 5;
		
		var lMaxWidth = getClientWidth()-xOffset-50;
		var lMaxHeight = getClientHeight()-yOffset-100;
		wireframeStatesDialog.style.width = lMaxWidth;
		wireframeStatesDialog.style.height = lMaxHeight;
		
	}
}
// called from #showSpotLight() to make it can hide the wireframe dialog if wireframe dialog exists and showing.
function hideWireframeStatesDialog() {
	var lDialogId = "wireframeStatesDialog"; // hardcoded in #showWireframeStatesDialog(...), #okWireframeStatesDialog(...), #hideWireframeStatesDialog(...)
	var wireframeStatesDialog = document.getElementById(lDialogId);
	
	if (wireframeStatesDialog != null && wireframeStatesDialog.style.display != "none") {
		wireframeStatesDialog.style.display = "none";
	}
}
function okWireframeStatesDialog(stateSelectShapeId, stateImageId, stateDescriptionId, stateElementsId, pageTitleId, stateTitleTextId) {
	
	var lDialogId = "wireframeStatesDialog"; // hardcoded in #showWireframeStatesDialog(...), #okWireframeStatesDialog(...), #hideWireframeStatesDialog(...)
	var wireframeStatesDialog = document.getElementById(lDialogId);
	wireframeStatesDialog.style.display = "none";
	
	var stateTitleText = document.getElementById(stateTitleTextId).getAttribute("data-value");
	
	hideComponent(currentStateSelectShapeId);
	hideComponent(currentStateImageId);
	if ("none" != currentStateDescriptionId) {
		hideComponent(currentStateDescriptionId);
	}
	hideComponent(currentStateElementsId);
	
	showComponent(stateSelectShapeId);
	showComponent(stateImageId);
	if ("none" != stateDescriptionId) {
		showComponent(stateDescriptionId);
	}
	showComponent(stateElementsId);
	
	currentStateSelectShapeId = stateSelectShapeId;
	currentStateImageId = stateImageId;
	currentStateDescriptionId = stateDescriptionId;
	currentStateElementsId = stateElementsId;
	
	wireframeStatesDialog.style.zIndex = 1;
	
	var lPageTitle = document.getElementById(pageTitleId);
	lPageTitle.innerHTML = stateTitleText;
}

var currentSelectStateDialog;
var currentSelectStateButton;
function showFoeWireframeStatesDialog(stateDialogId, selectStateDialogButtonId) {
	var stateDialog = document.getElementById(stateDialogId);
	
	if (stateDialog.style.display != "none") {
		stateDialog.style.display = "none";
		
		if (currentSelectStateButton != null) {
			currentSelectStateButton.style.marginRight = 5;
		}
		
		currentSelectStateDialog = null;
		currentSelectStateButton = null;
	}
	else {
		
		if (currentSelectStateDialog != null) {
			currentSelectStateDialog.style.display = "none";
		}
		currentSelectStateDialog = stateDialog;
		
		var base = document.getElementById(selectStateDialogButtonId);
		currentSelectStateButton = base;
		
		var xOffset = findPosX(base);
		var yOffset = findPosY(base);
		
		var lButtonWidth = 15;
		var lDialogWidth = 300;
		var lDialogHeight = 400;
		
		xOffset = xOffset + lButtonWidth - lDialogWidth;
		yOffset = yOffset-getScrollTop();
		if (yOffset + lDialogHeight > getClientHeight()) {
			yOffset = getClientHeight()-lDialogHeight;
			
			if (yOffset < getScrollTop()) {
				yOffset = getScrollTop();
			}
		}
		
		base.style.marginRight = lDialogWidth;
		
		currentSelectStateDialog.style.left = xOffset;
		currentSelectStateDialog.style.top = yOffset;
		currentSelectStateDialog.style.display = "block";
		currentSelectStateDialog.style.zIndex = 5;
	}
}

function showComponent(componentId) {
	var component = document.getElementById(componentId);
	if (component != null) {
		if (component.tagName.toLowerCase() == "option") {
			component.disabled = false;
		}
		else if (component.tagName.toLowerCase() == "area") {
			component.coords = component.getAttribute("coords2");
		}
		else if (component.style.display == "none") {
			component.style.display = "";
		}
	}
}
function hideComponent(componentId) {
	var component = document.getElementById(componentId);
	if (component != null) {
		if (component.tagName.toLowerCase() == "option") {
			component.disabled = true;
			
			lSelect = document.getElementById("SelectShape");
			if (lSelect != null) {
				for (i = 0; i < lSelect.options.length; i++) {
					if (lSelect.options[i].id == componentId && lSelect.selectedIndex == i) {
						lSelect.selectedIndex = 0;
						showSpotLight("diagram", lSelect.value);
						break;
					}
				}
			}
			
		}
		else if (component.tagName.toLowerCase() == "area") {
			component.coords = "0,0,0,0";
		}
		else if (component.style.display != "none") {
			component.style.display = "none";
		}
	}
}

function collapseLogicalViewElement(aLogicalViewElementIds, aExpandAnchorId, aCollapseAnchorId, aOpenFolderImageId, aCloseFolderImageId) {
	
	var count = aLogicalViewElementIds.length;
	for (var i = 0; i < count; i++) {
		var lLogicalViewElementId = aLogicalViewElementIds[i];
		var lComponentIds = lLogicalViewElementId.split(";"); // [rowId, level] or [rowId, level, expandAnchorId, collapseAnchorId]
		hideComponent(lComponentIds[0]);
	}
	
	showComponent(aExpandAnchorId);
	showComponent(aCloseFolderImageId);
	hideComponent(aCollapseAnchorId);
	hideComponent(aOpenFolderImageId);
}
function expandLogicalViewElement(aLogicalViewElementIds, aExpandAnchorId, aCollapseAnchorId, aOpenFolderImageId, aCloseFolderImageId) {
	var lCollapsedLevel = -1;
	var count = aLogicalViewElementIds.length;
	for (var i = 0; i < count; i++) {
		var lLogicalViewElementId = aLogicalViewElementIds[i];
		var lComponentIds = lLogicalViewElementId.split(";"); // [rowId, level] or [rowId, level, expandAnchorId, collapseAnchorId]
		var lComponentLevel = lComponentIds[1];
		if (lCollapsedLevel == -1 || lComponentLevel <= lCollapsedLevel) {
			showComponent(lComponentIds[0]);
			lCollapsedLevel = -1;
			
			if (lComponentIds.length == 4) {
				var lCollapseAnchor = document.getElementById(lComponentIds[2]);
				if (lCollapseAnchor.style.display != "none") {
					// its children is collapsed, don't expand them
					lCollapsedLevel = lComponentLevel;
				}
				
			}
		}
	}
	
	showComponent(aCollapseAnchorId);
	showComponent(aOpenFolderImageId);
	hideComponent(aExpandAnchorId);
	hideComponent(aCloseFolderImageId);
}

function updateCursorPos(event){
		var e = (window.event) ? window.event : event;
		var xOffset = e.clientX;
		var yOffset = e.clientY;

	if (document.all){
		if (!document.documentElement.scrollLeft)
			xOffset += document.body.scrollLeft;
		else
			xOffset += document.documentElement.scrollLeft;
		
		if (!document.documentElement.scrollTop)
			yOffset += document.body.scrollTop;
		else
			yOffset += document.documentElement.scrollTop;
		
	}else{
		xOffset += window.pageXOffset;
		yOffset += window.pageYOffset;
	}
	cursorX = xOffset;
	cursorY = yOffset;
}

function selectProject(aUrl) {
	document.location.href = aUrl;
}

function getClientWidth() {
	return filterResults (
			window.innerWidth ? window.innerWidth : 0,
					document.documentElement ? document.documentElement.clientWidth : 0,
							document.body ? document.body.clientWidth : 0
	);
}
function getClientHeight() {
	return filterResults (
			window.innerHeight ? window.innerHeight : 0,
					document.documentElement ? document.documentElement.clientHeight : 0,
							document.body ? document.body.clientHeight : 0
	);
}
function getScrollLeft() {
	return filterResults (
			window.pageXOffset ? window.pageXOffset : 0,
					document.documentElement ? document.documentElement.scrollLeft : 0,
							document.body ? document.body.scrollLeft : 0
	);
}
function getScrollTop() {
	return filterResults (
			window.pageYOffset ? window.pageYOffset : 0,
					document.documentElement ? document.documentElement.scrollTop : 0,
							document.body ? document.body.scrollTop : 0
	);
}