var xForRefIcon = 0;
var yForRefIcon = 0;

var xForSubDiagramIcon = 0;
var yForSubDiagramIcon = 0;

var xForTransIcon = 0;
var yForTransIcon = 0;

var fileLinks = [];
var folderLinks = [];
var urlLinks = [];
var diagramLinks = [];
var shapeLinks = [];
var subdiagramLinks = [];
var fromTransitorLinks = [];
var toTransitorLinks = [];

// vplink
var vpLinkProjectLink;
var vpLinkPageUrl;
var vpLinkProjectLinkWithName;
var vpLinkPageUrlWithName;

function showDefaultReferenceIcon(imageId, modelValues, objectId) {
	if (modelValues != ''){
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeX = xyValueArray[0]*1;
			var shapeY = xyValueArray[1]*1;
			var x = shapeX + xOffset*1;
			var y = shapeY + yOffset*1 - 13;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var referenceIconLayer = document.getElementById(objectId);
		
			N = (document.all) ? 0 : 1;
			if (N) {
				referenceIconLayer.style.left = x - 3;
				referenceIconLayer.style.top = y + h;
			} else {
				referenceIconLayer.style.posLeft = x - 3;
				referenceIconLayer.style.posTop = y + h;
			}
			referenceIconLayer.style.visibility="visible"
//		}
	}
}
function showReferenceIcon(imageId, modelValues) {
	if (modelValues != '') {
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeX = xyValueArray[0]*1;
			var shapeY = xyValueArray[1]*1;
			var x = shapeX + xOffset*1;
			var y = shapeY + yOffset*1 - 13;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var referenceIconLayer = document.getElementById("referenceIconLayer");
		
			N = (document.all) ? 0 : 1;
			if (N) {
				referenceIconLayer.style.left = x - 3;
				referenceIconLayer.style.top = y + h;
			} else {
				referenceIconLayer.style.posLeft = x - 3;
				referenceIconLayer.style.posTop = y + h;
			}
			referenceIconLayer.style.visibility="visible"
//		}
	}
}
function hideReferenceIcon() {
	var referenceIconLayer = document.getElementById("referenceIconLayer");
	if (referenceIconLayer != null) {
		referenceIconLayer.style.visibility="hidden"
	}
}

function showDefaultSubdiagramIcon(imageId, modelValues, objectId) {
	if (modelValues != ''){
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeRightX = xyValueArray[2]*1;
			var shapeRightY = xyValueArray[1]*1;
			var x = shapeRightX + xOffset*1 - 10;
			var y = shapeRightY + yOffset*1 - 13;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var subdiagramIconLayer = document.getElementById(objectId);
		
			N = (document.all) ? 0 : 1;
			if (N) {
				subdiagramIconLayer.style.left = x - 3;
				subdiagramIconLayer.style.top = y + h;
			} else {
				subdiagramIconLayer.style.posLeft = x - 3;
				subdiagramIconLayer.style.posTop = y + h;
			}
			subdiagramIconLayer.style.visibility="visible"
//		}
	}
}
function showSubdiagramIcon(imageId, modelValues) {
	if (modelValues != ''){
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeRightX = xyValueArray[2]*1;
			var shapeRightY = xyValueArray[1]*1;
			var x = shapeRightX + xOffset*1 - 10;
			var y = shapeRightY + yOffset*1 - 13;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var subdiagramIconLayer = document.getElementById("subdiagramIconLayer");
		
			N = (document.all) ? 0 : 1;
			if (N) {
				subdiagramIconLayer.style.left = x - 3;
				subdiagramIconLayer.style.top = y + h;
			} else {
				subdiagramIconLayer.style.posLeft = x - 3;
				subdiagramIconLayer.style.posTop = y + h;
			}
			subdiagramIconLayer.style.visibility="visible"
//		}
	}
}
function hideSubdiagramIcon() {
	var subdiagramIconLayer = document.getElementById("subdiagramIconLayer");
	if (subdiagramIconLayer != null) {
		subdiagramIconLayer.style.visibility="hidden"
	}
}

function showDefaultTransitorIcon(imageId, modelValues, objectId) {
	if (modelValues != ''){
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeRightX = xyValueArray[2]*1;
			var shapeRightY = xyValueArray[1]*1;
			var x = shapeRightX + xOffset*1 - 10;
			var y = shapeRightY + yOffset*1;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var transitorIconLayer = document.getElementById(objectId);
		
			N = (document.all) ? 0 : 1;
			if (N) {
				transitorIconLayer.style.left = x - 3;
				transitorIconLayer.style.top = y + h;
			} else {
				transitorIconLayer.style.posLeft = x - 3;
				transitorIconLayer.style.posTop = y + h;
			}
			transitorIconLayer.style.visibility="visible"
//		}
	}
}
function showTransitorIcon(imageId, modelValues) {
	if (modelValues != ''){
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeRightX = xyValueArray[2]*1;
			var shapeRightY = xyValueArray[1]*1;
			var x = shapeRightX + xOffset*1 - 10;
			var y = shapeRightY + yOffset*1;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var transitorIconLayer = document.getElementById("transitorIconLayer");
		
			N = (document.all) ? 0 : 1;
			if (N) {
				transitorIconLayer.style.left = x - 3;
				transitorIconLayer.style.top = y + h;
			} else {
				transitorIconLayer.style.posLeft = x - 3;
				transitorIconLayer.style.posTop = y + h;
			}
			transitorIconLayer.style.visibility="visible"
//		}
	}
}
function hideTransitorIcon() {
	var transitorIconLayer = document.getElementById("transitorIconLayer");
	if (transitorIconLayer != null) {
		transitorIconLayer.style.visibility="hidden"
	}
}

function showDefaultDocumentationIcon(imageId, modelValues, objectId) {
	if (modelValues != ''){
		var xyValueArray = modelValues.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			var diagram = document.getElementById(imageId);
			var xOffset = findPosX(diagram);
			var yOffset = findPosY(diagram);
			
			var shapeX = xyValueArray[0]*1;
			var shapeY = xyValueArray[1]*1;
			var x = shapeX + xOffset*1;
			var y = shapeY + yOffset*1;
			var h = xyValueArray[3]*1 - xyValueArray[1]*1;
			var url = xyValueArray[4];
	
			var documentationIconLayer = document.getElementById(objectId);
		
			N = (document.all) ? 0 : 1;
			if (N) {
				documentationIconLayer.style.left = x - 3;
				documentationIconLayer.style.top = y + h;
			} else {
				documentationIconLayer.style.posLeft = x - 3;
				documentationIconLayer.style.posTop = y + h;
			}
			documentationIconLayer.style.visibility="visible"
//		}
	}
}

function storeReferenceAndSubdiagramInfos(imageId, coords, fileRefs, folderRefs, urlRefs, diagramRefs, shapeRefs, subdiagrams, modelElementRefs, fromTransitors, toTransitors) {
	
	if (coords != ''){
		var xyValueArray = coords.split(",");
		var shapeWidth = xyValueArray[2]*1 - xyValueArray[0]*1;
//		if (shapeWidth > 24){
			fileLinks = [];
			folderLinks = [];
			urlLinks = [];
			diagramLinks = [];
			shapeLinks = [];
			subdiagramLinks = [];
			modelElementLinks = [];
			fromTransitorLinks = [];
			toTransitorLinks = [];
			
				var popup = document.getElementById("linkPopupMenuTable");
				popup.width = 250; // reset to 250 first (forZachman may changed it to 500)
				
				for (i = 0 ; i < fileRefs.length ; i++) {
					fileLinks[i] = fileRefs[i];
				}
				for (i = 0 ; i < folderRefs.length ; i++) {
					folderLinks[i] = folderRefs[i];
				}
				for (i = 0 ; i < urlRefs.length ; i++) {
					urlLinks[i] = urlRefs[i];
				}
				for (j = 0 ; j < diagramRefs.length ; j++) {
					diagramLinks[j] = diagramRefs[j]
				}
				for (j = 0 ; j < shapeRefs.length ; j++) {
					shapeLinks[j] = shapeRefs[j]
				}
				for (j = 0 ; j < subdiagrams.length ; j++) {
					subdiagramLinks[j] = subdiagrams[j]
				}
				for (j = 0 ; j < modelElementRefs.length ; j++) {
					modelElementLinks[j] = modelElementRefs[j]
				}
				for (j = 0 ; j < fromTransitors.length ; j++) {
					fromTransitorLinks[j] = fromTransitors[j]
				}
				for (j = 0 ; j < toTransitors.length ; j++) {
					toTransitorLinks[j] = toTransitors[j]
				}
				
				var diagram = document.getElementById(imageId);
				var xOffset = findPosX(diagram);
				var yOffset = findPosY(diagram);
				
				var shapeX = xyValueArray[0]*1;
				var shapeY = xyValueArray[1]*1;
				var x = shapeX + xOffset*1;
				var y = shapeY + yOffset*1 + 2;
				var w = xyValueArray[2]*1 - xyValueArray[0]*1;
				var h = xyValueArray[3]*1 - xyValueArray[1]*1;
				var url = xyValueArray[4];
			
				xForRefIcon = x;
				yForRefIcon = y + h;

				shapeX = xyValueArray[2]*1;
				shapeY = xyValueArray[1]*1;
				x = shapeX + xOffset*1 - 12;
				y = shapeY + yOffset*1 + 2;
				w = xyValueArray[2]*1 - xyValueArray[0]*1;
				h = xyValueArray[3]*1 - xyValueArray[1]*1;
				url = xyValueArray[4];

				xForSubDiagramIcon = x;
				yForSubDiagramIcon = y + h;
				
				xForTransIcon = x;
				yForTransIcon = y + h + 12;
//		}
	}
}

function resetPopupForReference() {
	clearLinkPopupContent();

	var popup = document.getElementById("linkPopupMenuTable");
	
	// file references
	for (i = 0 ; i < fileLinks.length ; i++) {
		var fileNameUrl = fileLinks[i].split("*");
		var name = fileNameUrl[0];
		var url = fileNameUrl[1]; // may be null

		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(../images/icons/FileReference.png) !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='../images/icons/FileReference.png'); background-repeat: no-repeat;\"></div>&nbsp;"+name;
		imgPopupCell.valign="middle";
		if (url == null) {
			imgPopupCell.className="PopupMenuRowNonSelectable";
		}
		else {
			imgPopupCell.destination=url;
			imgPopupCell.className="PopupMenuRowDeselected";
	 		imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
			imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
			imgPopupCell.onclick= function onclick(event) { window.open(this.destination);hideLinkPopup(); };
		}
		
	}
	
	// folder reference
	for (i = 0 ; i < folderLinks.length ; i++) {
		var folderNameUrl = folderLinks[i].split("*");
		var name = folderNameUrl[0];
		var url = folderNameUrl[1]; // may be null

		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(../images/icons/FolderReference.png) !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='../images/icons/FolderReference.png'); background-repeat: no-repeat;\"></div>&nbsp;"+name;
		imgPopupCell.valign="middle";
		if (url == null) {
			imgPopupCell.className="PopupMenuRowNonSelectable";
		}
		else if (url != null) {
			imgPopupCell.destination=url;
			imgPopupCell.className="PopupMenuRowDeselected";
			imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
			imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
			imgPopupCell.onclick= function onclick(event) { window.open(this.destination);hideLinkPopup(); };
		}
	}
	
	// url reference
	for (i = 0 ; i < urlLinks.length ; i++) {
		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		var destination = urlLinks[i][0];
		var name = urlLinks[i][1];
		if (name == null || name == '') {
			name = destination;
		}
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(../images/icons/UrlReference.png) !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='../images/icons/UrlReference.png'); background-repeat: no-repeat;\"></div>&nbsp;"+name
		imgPopupCell.valign="middle"
		imgPopupCell.destination=destination;
		imgPopupCell.className="PopupMenuRowDeselected";
		imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
		imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
		imgPopupCell.onclick= function onclick(event) { window.open(this.destination);hideLinkPopup(); };
	}
	
	// diagram reference
	for (j = 0 ; j < diagramLinks.length ; j++) {
		var diagramUrlNameType = diagramLinks[j].split("/");
		var url = diagramUrlNameType[0];
		var name = diagramUrlNameType[1];
		var type = diagramUrlNameType[2];
		var imgSrc = '../images/icons/'+type+'.png';
							
		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
		imgPopupCell.valign="middle"
		imgPopupCell.className="PopupMenuRowDeselected";
		imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
		imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
		if (url == 'vplink') {
			imgPopupCell.destination= diagramUrlNameType[3].replace('@','/');
			imgPopupCell.vpLinkWithName= diagramUrlNameType[4].replace('@','/');
			imgPopupCell.onclick= function onclick(event) { showVpLink(this.destination, this.vpLinkWithName, null, this) };
		} else {
			imgPopupCell.destination=url
			if (url != null && url != '') {
				imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
			}
		}
	}
	
	// shape reference
	for (j = 0 ; j < shapeLinks.length ; j++) {
		var shapeUrlNameType = shapeLinks[j].split("/");
		var url = shapeUrlNameType[0];
		var name = shapeUrlNameType[1];
		var iconFileName = shapeUrlNameType[2];
		var imgSrc = '../images/icons/'+iconFileName+'.png';
		
		var row = popup.insertRow(popup.rows.length)
		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
		imgPopupCell.valign="middle"
		imgPopupCell.destination=url
		imgPopupCell.className="PopupMenuRowDeselected";
		imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
		imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
		if (iconFileName.length > 0){
			imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
		}
	}
	
	// model element reference
	for (j = 0 ; j < modelElementLinks.length ; j++) {
		var modelElementUrlNameType = modelElementLinks[j].split("/");
		var url = modelElementUrlNameType[0];
		var name = modelElementUrlNameType[1];
		var iconFileName = modelElementUrlNameType[2];
		var imgSrc = '../images/icons/'+iconFileName+'.png';
		
		var row = popup.insertRow(popup.rows.length)
		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
		imgPopupCell.valign="middle"
		imgPopupCell.destination=url
		imgPopupCell.className="PopupMenuRowDeselected";
		imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
		imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
		if (iconFileName.length > 0) {
			imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
		}
	}
	
}

function resetPopupForSubdiagram() {
	clearLinkPopupContent();

	var popup = document.getElementById("linkPopupMenuTable");
	
	// subdiagram
	for (j = 0 ; j < subdiagramLinks.length ; j++) {
		var diagramUrlNameType = subdiagramLinks[j].split("/");
		var url = diagramUrlNameType[0];
		var name = diagramUrlNameType[1];
		var type = diagramUrlNameType[2];
		var imgSrc = '../images/icons/'+type+'.png';
		
		var row = popup.insertRow(popup.rows.length)
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
		imgPopupCell.valign="middle"
		imgPopupCell.destination=url
		imgPopupCell.className="PopupMenuRowDeselected";
		imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
		imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
		if (url != null && url != '') {
			imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
		}
	}
}

function movePopupPositionToReferenceIconPosition() {
	movePopupPositionToSpecificPosition(xForRefIcon, yForRefIcon);
}

function movePopupPositionToSubdiagramIconPosition() {
	movePopupPositionToSpecificPosition(xForSubDiagramIcon, yForSubDiagramIcon);
}

function movePopupPositionToCursorPosition(imageId, event) {
	var diagram = document.getElementById(imageId);
	var xOffset = 0;
	var yOffset = 0;
	
	var e = (window.event) ? window.event : event;
	xOffset = e.clientX;
	yOffset = e.clientY;
	
	if (document.all) {
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
	
	var nX = xOffset*1;
	var nY = yOffset*1;
	
	movePopupPositionToSpecificPosition(nX, nY);
}

function movePopupPositionToSpecificPosition(x, y) {
	var popupLayer = document.getElementById("linkPopupMenuLayer");
	N = (document.all) ? 0 : 1;
	if (N) {
		popupLayer.style.left = x;
		popupLayer.style.top = y;
	} else {
		popupLayer.style.posLeft = x;
		popupLayer.style.posTop = y;
	}
}

function switchPopupShowHideStatus(){
	var popup = document.getElementById("linkPopupMenuTable");
	if (popup.style.visibility=="visible") {
		hideLinkPopup();
	}else{
		showLinkPopup();
	}
}
function switchPopupShowHideStatusForZachman(aForZachmanKind) {
	var popup = document.getElementById("linkPopupMenuTable");
	if (popup.style.visibility=="visible") {
		
		if (aForZachmanKind == popup.forZachmanKind) {
			popup.forZachmanKind = null;
			hideLinkPopup();
		}
		else {
			// keep popup shown, just need change its forZachmanKind
			popup.forZachmanKind = aForZachmanKind;
		}
			
	}else{
		popup.forZachmanKind = aForZachmanKind;
		showLinkPopup();
	}
}

function adjustPopupPositionForSpotLightTable() {
	movePopupPositionToSpecificPosition(cursorX,cursorY);
}

function showLinkPopup(){
	
	hideVpLink();
	hideReferencedBys();
	
	var popup = document.getElementById("linkPopupMenuTable");
	popup.style.visibility="visible"
	document.getElementById("linkPopupMenuLayer").style.visibility="visible";
}

function hideLinkPopup(){
	var popup = document.getElementById("linkPopupMenuTable");
	if (popup != null) {
		
		popup.style.visibility="hidden"
		document.getElementById("linkPopupMenuLayer").style.visibility="hidden";
	}
}

function clearLinkPopupContent(){
	var popup = document.getElementById("linkPopupMenuTable");
	for (i = popup.rows.length ; i >0 ; i--) {
		popup.deleteRow(0);
	}
}

function movePopupPositionToTransitorIconPosition() {
	movePopupPositionToSpecificPosition(xForTransIcon, yForTransIcon);
}

function resetPopupForTransitor() {
	clearLinkPopupContent();

	var popup = document.getElementById("linkPopupMenuTable");
	
	// transitor
	var row = popup.insertRow(popup.rows.length);
	var popupCell = row.insertCell(0);
	popupCell.innerHTML="<div style=\"font-size:11px\">From:</div>";
	for (j = 0 ; j < fromTransitorLinks.length ; j++) {
		var shapeUrlNameType = fromTransitorLinks[j].split("/");
		addPopupItem(popup, shapeUrlNameType);
	}
	row = popup.insertRow(popup.rows.length);
	popupCell = row.insertCell(0);
	popupCell.innerHTML="<div style=\"font-size:11px\">To:</div>";
	for (j = 0 ; j < toTransitorLinks.length ; j++) {
		var shapeUrlNameType = toTransitorLinks[j].split("/");
		addPopupItem(popup, shapeUrlNameType);
	}
}

// for From/To Transitor
function addPopupItem(popup, shapeUrlNameType) {
	var url = shapeUrlNameType[0];
	var name = shapeUrlNameType[1];
	var iconFileName = shapeUrlNameType[2];
	var imgSrc = '../images/icons/'+iconFileName+'.png';
						
	var row = popup.insertRow(popup.rows.length)
	var imgPopupCell = row.insertCell(0);
	imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
	imgPopupCell.valign="middle";
	imgPopupCell.destination=url;
	imgPopupCell.className="PopupMenuRowDeselected";
	imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
	imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
	imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
}

// for Zachman
// @param format: url/name/type, url/name/type, ...
function resetPopupForZachmanCellDiagrams(lCellId, lValues) {
	clearLinkPopupContent();
	
	var popup = document.getElementById("linkPopupMenuTable");
	popup.style.width = 250;
	
	var lZachmanCell = document.getElementById(lCellId);
	var lZachmanCellX = findPosX(lZachmanCell);
	var lZachmanCellY = findPosY(lZachmanCell);
	
	if (lZachmanCellX > 250) {
		// show on left
		movePopupPositionToSpecificPosition(lZachmanCellX+lZachmanCell.offsetWidth-popup.offsetWidth-5, lZachmanCellY+lZachmanCell.offsetHeight-5);
	}
	else {
		// show on right
		// x+5 & y-5 to let the popup overlap with current cell
		movePopupPositionToSpecificPosition(lZachmanCellX+5, lZachmanCellY+lZachmanCell.offsetHeight-5);	
	}
	
	// ZachmanCell.diagrams
	for (j = 0 ; j < lValues.length ; j++) {
		var diagramUrlNameType = lValues[j].split("/");
		var url = diagramUrlNameType[0];
		var name = diagramUrlNameType[1];
		var type = diagramUrlNameType[2];
		var imgSrc = '../images/icons/'+type+'.png';
		
		var row = popup.insertRow(popup.rows.length);
		var imgPopupCell = row.insertCell(0);
		imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name;
		imgPopupCell.valign="middle";
		imgPopupCell.destination=url;
		imgPopupCell.className="PopupMenuRowDeselected";
		imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
		if (url != null && url != '') {
			imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
			imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
		}
		else {
			imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowNonSelectable"; };
		}
		
	}
}
// @param format: url/name/aliases/labels/documentation, url/name/aliases/labels/documentation, ...
function resetPopupForZachmanCellTerms(lCellId, lValues) {
	clearLinkPopupContent();
	
	var popup = document.getElementById("linkPopupMenuTable");
	popup.style.width = 500;
	
	var lZachmanCell = document.getElementById(lCellId);
	var lZachmanCellX = findPosX(lZachmanCell);
	var lZachmanCellY = findPosY(lZachmanCell);
	
	if (lZachmanCellX > 500) {
		// show on left
		movePopupPositionToSpecificPosition(lZachmanCellX+lZachmanCell.offsetWidth-popup.offsetWidth-5, lZachmanCellY+lZachmanCell.offsetHeight-5);
	}
	else {
		// show on right
		// x+5 & y-5 to let the popup overlap with current cell
		movePopupPositionToSpecificPosition(lZachmanCellX+5, lZachmanCellY+lZachmanCell.offsetHeight-5);	
	}
	
	// ZachmanCell.terms
	{
		var row = popup.insertRow(popup.rows.length);
		row.className="PopupMenuHeaderRow";
		{
			var lPopupCell = row.insertCell(0);
			lPopupCell.innerHTML="Name";
			lPopupCell.valign="middle";
		}
		{
			var lPopupCell = row.insertCell(1);
			lPopupCell.innerHTML="Aliases";
			lPopupCell.valign="middle";
		}
		{
			var lPopupCell = row.insertCell(2);
			lPopupCell.innerHTML="Labels";
			lPopupCell.valign="middle";
		}
		{
			var lPopupCell = row.insertCell(3);
			lPopupCell.innerHTML="Documentation";
			lPopupCell.valign="middle";
		}
	}
	
	for (j = 0 ; j < lValues.length ; j++) {
		var lValue = lValues[j].split("/");
		var url = lValue[0];
		var name = lValue[1];
		var aliases = lValue[2];
		var labels = lValue[3];
		var documentation = lValue[4];
		
		var row = popup.insertRow(popup.rows.length);
		for (lCellIndex = 1; lCellIndex < lValue.length; lCellIndex++) {
			var lPopupCell = row.insertCell(lCellIndex-1);
			lPopupCell.id="cell"+j+","+lCellIndex-1;
			lPopupCell.innerHTML=lValue[lCellIndex];
			lPopupCell.valign="middle";
		}
		if (url != null && url != '') {
			row.destination=url;
			row.className="PopupMenuRowDeselected";
			row.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
			row.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
			row.onclick= function onclick(event) { window.open(this.destination,'_self') };
		}
		else {
			row.className="PopupMenuRowNonSelectable";
		}
		
	}
}
// @param format: url/id/name/ruleText, url/id/name/ruleText, ...
function resetPopupForZachmanCellRules(lCellId, lValues) {
	clearLinkPopupContent();
	
	var popup = document.getElementById("linkPopupMenuTable");
	popup.style.width = 500;
	
	var lZachmanCell = document.getElementById(lCellId);
	var lZachmanCellX = findPosX(lZachmanCell);
	var lZachmanCellY = findPosY(lZachmanCell);
	
	if (lZachmanCellX > 500) {
		// show on left
		movePopupPositionToSpecificPosition(lZachmanCellX+lZachmanCell.offsetWidth-popup.offsetWidth-5, lZachmanCellY+lZachmanCell.offsetHeight-5);
	}
	else {
		// show on right
		// x+5 & y-5 to let the popup overlap with current cell
		movePopupPositionToSpecificPosition(lZachmanCellX+5, lZachmanCellY+lZachmanCell.offsetHeight-5);	
	}
	
	// ZachmanCell.rules
	{
		var row = popup.insertRow(popup.rows.length);
		row.className="PopupMenuHeaderRow";
		{
			var lPopupCell = row.insertCell(0);
			lPopupCell.innerHTML="ID";
			lPopupCell.valign="middle";
		}
		{
			var lPopupCell = row.insertCell(1);
			lPopupCell.innerHTML="Name";
			lPopupCell.valign="middle";
		}
		{
			var lPopupCell = row.insertCell(2);
			lPopupCell.innerHTML="Rule";
			lPopupCell.valign="middle";
		}
	}
	
	for (j = 0 ; j < lValues.length ; j++) {
		var lValue = lValues[j].split("/");
		var url = lValue[0];
		var id = lValue[1];
		var name = lValue[2];
		var ruleText = lValue[3];
		
		var row = popup.insertRow(popup.rows.length);
		for (lCellIndex = 1; lCellIndex < lValue.length; lCellIndex++) {
			var lPopupCell = row.insertCell(lCellIndex-1);
			lPopupCell.id="cell"+j+","+lCellIndex-1;
			lPopupCell.innerHTML=lValue[lCellIndex];
			lPopupCell.valign="middle";
		}
		if (url != null && url != '') {
			row.destination=url;
			row.className="PopupMenuRowDeselected";
			row.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
			row.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
			row.onclick= function onclick(event) { window.open(this.destination,'_self') };
		}
		else {
			row.className="PopupMenuRowNonSelectable";
		}
	}
}

function showVpLink(link, linkWithName, pageUrlElementName, linkElem) {
	// getting absolute location in page
	var lLeft = 0;
	var lTop = 0;
	var lParent = linkElem;
	while (lParent != null) {
		lLeft += lParent.offsetLeft;
		lTop += lParent.offsetTop;
		lParent = lParent.offsetParent;
	}
	showVpLinkAt(link, linkWithName, pageUrlElementName, lLeft, lTop + linkElem.offsetHeight);
}
function showVpLinkAtDiagram(link, linkWithName, pageUrlElementName, aLeft, aTop) {
	var lLeft = 0;
	var lTop = 0;
	var diagramElem = document.getElementById('diagram');
	var lParent = diagramElem;
	while (lParent != null) {
		lLeft += lParent.offsetLeft;
		lTop += lParent.offsetTop;
		lParent = lParent.offsetParent;
	}
	
	showVpLinkAt(link, linkWithName, pageUrlElementName, lLeft + aLeft, lTop + aTop);
}
function showVpLinkAt(link, linkWithName, pageUrlElementName, aLeft, aTop) {
	var popup = document.getElementById("vplink");
	if (popup.style.visibility == "visible") {
		popup.style.visibility="hidden";
	} else {
		var linktext = document.getElementById("vplink-text");
		var withName = document.getElementById("vplink-checkbox");
		var lLinkType = document.getElementById("vplink-linkType")
		
		// read from cookies (https://earth.space/#issueId=81262)
		var lWithNameValue = getCookie("vpProjectPublisher_vpLink_withName");
		if (lWithNameValue != null) {
			if (lWithNameValue == "true") {
				withName.checked = true;
			}
			else {
				withName.checked = false;
			}
		}
		
		var lLinkTypeValue = getCookie("vpProjectPublisher_vpLink_type");
		if (lLinkTypeValue != null) {
			if (lLinkTypeValue == "Page URL") {
				lLinkType.selectedIndex = 1; // 1 should be "Page URL"
			}
			else {
				lLinkType.selectedIndex = 0; // 0 should be "Project Link"
			}
		}
		
		
		vpLinkProjectLink = link;
		vpLinkProjectLinkWithName = linkWithName;
		if (pageUrlElementName != null) {
			vpLinkPageUrl = document.location.href;
			vpLinkPageUrlWithName = pageUrlElementName+"\n"+vpLinkPageUrl;
			
			lLinkType.disabled = false;
		}
		else {
			vpLinkPageUrl = null;
			vpLinkPageUrlWithName = null;
			
			lLinkType.selectedIndex = 0; // 0 should be "Project Link"
			lLinkType.disabled = true;
		}
		
		if (withName.checked) {
			if (lLinkType.disabled == false && lLinkType.options[lLinkType.selectedIndex].value == "Page URL") {
				// Page URL
				linktext.value = vpLinkPageUrlWithName;
			}
			else {
				// Project Link
				linktext.value = vpLinkProjectLinkWithName;
			}
		} else {
			if (lLinkType.disabled == false && lLinkType.options[lLinkType.selectedIndex].value == "Page URL") {
				// Page URL
				linktext.value = vpLinkPageUrl;
			}
			else {
				// Project Link
				linktext.value = vpLinkProjectLink;
			}
		}
		
		N = (document.all) ? 0 : 1;
		
		if (N) {
			popup.style.left = aLeft;
			popup.style.top = aTop;
		} else {
			popup.style.posLeft = aLeft;
			popup.style.posTop = aTop;
		}
		
		hideLinkPopup();
		hideReferencedBys();

		popup.style.visibility="visible"
		linktext.focus();
		linktext.select();
	}
}
function hideVpLink() {
	var popupLayer = document.getElementById("vplink");
	if (popupLayer != null && popupLayer.style.visibility == "visible") {
		
		popupLayer.style.visibility="hidden";
	}
}

function vpLinkToggleName() {
	var linktext = document.getElementById("vplink-text");
	var withName = document.getElementById("vplink-checkbox");
	var lLinkType = document.getElementById("vplink-linkType")
	
	// write to cookies (https://earth.space/#issueId=81262)
	setCookie("vpProjectPublisher_vpLink_withName", withName.checked);
	setCookie("vpProjectPublisher_vpLink_type", lLinkType.options[lLinkType.selectedIndex].value);
	
	if (withName.checked) {
		if (lLinkType.disabled == false && lLinkType.options[lLinkType.selectedIndex].value == "Page URL") {
			// Page URL
			linktext.value = vpLinkPageUrlWithName;
		}
		else {
			// Project Link
			linktext.value = vpLinkProjectLinkWithName;
		}
	} else {
		if (lLinkType.disabled == false && lLinkType.options[lLinkType.selectedIndex].value == "Page URL") {
			// Page URL
			linktext.value = vpLinkPageUrl;
		}
		else {
			// Project Link
			linktext.value = vpLinkProjectLink;
		}
	}
	
	linktext.focus();
	linktext.select();
}

function showReferencedBys(invokerId, refByDiagrams, refByModels) {
	
	var popupLayer = document.getElementById("referencedBys");
	if (popupLayer.style.visibility == "visible") {
		popupLayer.style.visibility="hidden";
	} else {
		
		var popup = document.getElementById("referencedBysTable");

		for (i = popup.rows.length ; i >0 ; i--) {
			popup.deleteRow(0);
		}
		

		var refByDiagramLinks = [];
		var refByModelLinks = [];
		
		{
			popup.width = 250; // reset to 250 first (forZachman may changed it to 500)
			
			for (i = 0 ; i < refByDiagrams.length ; i++) {
				refByDiagramLinks[i] = refByDiagrams[i];
			}
			for (i = 0 ; i < refByModels.length ; i++) {
				refByModelLinks[i] = refByModels[i];
			}
		}
		
		{
			// ref by diagrams
			for (j = 0 ; j < refByDiagramLinks.length ; j++) {
				var diagramUrlNameType = refByDiagramLinks[j].split("/");
				var url = diagramUrlNameType[0];
				var name = diagramUrlNameType[1];
				var type = diagramUrlNameType[2];
				var imgSrc = '../images/icons/'+type+'.png';
									
				var row = popup.insertRow(popup.rows.length)
				var imgPopupCell = row.insertCell(0);
				imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
				imgPopupCell.valign="middle"
				imgPopupCell.className="PopupMenuRowDeselected";
				imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
				imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
				if (url == 'vplink') {
					imgPopupCell.destination= diagramUrlNameType[3].replace('@','/');
					imgPopupCell.vpLinkWithName= diagramUrlNameType[4].replace('@','/');
					imgPopupCell.onclick= function onclick(event) { showVpLink(this.destination, this.vpLinkWithName, null, this) };
				} else {
					imgPopupCell.destination=url
					if (url != null && url != '') {
						imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
					}
				}
			}
			
			// ref by models
			for (j = 0 ; j < refByModelLinks.length ; j++) {
				var modelElementUrlNameType = refByModelLinks[j].split("/");
				var url = modelElementUrlNameType[0];
				var name = modelElementUrlNameType[1];
				var iconFileName = modelElementUrlNameType[2];
				var imgSrc = '../images/icons/'+iconFileName+'.png';
				
				var row = popup.insertRow(popup.rows.length)
				var row = popup.insertRow(popup.rows.length)
				var imgPopupCell = row.insertCell(0);
				imgPopupCell.innerHTML="<div style=\"float: left; width: 18px !important;height: 18px !important;background-image:url(" + imgSrc + ") !important; background-image:url(''); filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imgSrc + "'); background-repeat: no-repeat;\"></div>&nbsp;"+name
				imgPopupCell.valign="middle"
				imgPopupCell.destination=url
				imgPopupCell.className="PopupMenuRowDeselected";
				imgPopupCell.onmouseover= function onmouseover(event) { this.className="PopupMenuRowSelected"; };
				imgPopupCell.onmouseout= function onmouseover(event) { this.className="PopupMenuRowDeselected"; };
				if (iconFileName.length > 0) {
					imgPopupCell.onclick= function onclick(event) { window.open(this.destination,'_self') };
				}
			}
		}
		
		var invoker = document.getElementById(invokerId);
		var xOffset = findPosX(invoker);
		var yOffset = findPosY(invoker);
		yOffset = yOffset+18;
		
		N = (document.all) ? 0 : 1;
		if (N) {
			popupLayer.style.left = xOffset;
			popupLayer.style.top = yOffset;
		} else {
			popupLayer.style.posLeft = xOffset;
			popupLayer.style.posTop = yOffset;
		}
		
		hideLinkPopup();
		hideVpLink();
		popupLayer.style.visibility = "visible";
	}
	
}
function hideReferencedBys() {
	var popupLayer = document.getElementById("referencedBys");
	if (popupLayer != null && popupLayer.style.visibility == "visible") {
		
		popupLayer.style.visibility="hidden";
	}
}

function setCookie(c_name, value) {
	var c_value = escape(value);
	document.cookie = c_name + "=" + c_value;
}
function getCookie(c_name) {
	var c_value = document.cookie;
	var c_start = c_value.indexOf(" " + c_name + "=");
	if (c_start == -1) {
		c_start = c_value.indexOf(c_name + "=");
	}
	
	if (c_start == -1) {
		c_value = null;
	}
	else {
		c_start = c_value.indexOf("=", c_start)+1;
		var c_end = c_value.indexOf(";", c_start);
		if (c_end == -1) {
			c_end = c_value.length;
		}
		
		c_value = unescape(c_value.substring(c_start, c_end));
	}
	return c_value;
}