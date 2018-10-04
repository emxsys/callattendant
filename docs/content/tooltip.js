var tooltip = {
		hideTooltipTimeOut : 1000,
		showTooltipTimeOut : 500,
		xOffset : 20,
		yOffset : 0,
		area : Object,
		shadowArea : Object,
		tipLayer : Object, 
		tipConnectorLayer : Object, 
		tipPinLayer : Object, 
		hideTimeoutId : '', 
		showTimeoutId : '', 
		opacityId : '', 
		tooltipVisible : false, 
		
		init : function(){
			tipLayer = document.createElement('div');
			tipLayer.id = 'toolTip';
			document.getElementsByTagName('body')[0].appendChild(tipLayer);
			tipLayer.className="TableContent Documentation";
			tipLayer.style.top = '0';
			tipLayer.style.visibility = 'hidden';
			tipLayer.style.zIndex=5;
			tipLayer.onmouseover= function onmouseover(event) {
				if (window.showTimeoutId) {
					clearTimeout(showTimeoutId);
				}
				if (window.hideTimeoutId) {
					clearTimeout(hideTimeoutId);
				}
			};
			tipLayer.onmouseout= function onmouseout(event) {
				tooltip.hide();
			};
			
			{
				// tip connector
				tipConnectorLayer = document.createElement('div');
				tipConnectorLayer.id = 'toolTipConnector';
				document.getElementsByTagName('body')[0].appendChild(tipConnectorLayer);
				tipConnectorLayer.className="Documentation";
				tipConnectorLayer.style.top = '0';
				tipConnectorLayer.style.visibility = 'hidden';
				tipConnectorLayer.style.zIndex=2; // index = 2, below indicator's index = 3
				tipConnectorLayer.onmouseover = tipLayer.onmouseover;
				tipConnectorLayer.onmouseout = tipLayer.onmouseout;
			}
			{
				// tip pin
				tipPinLayer = document.createElement('div');
				tipPinLayer.id = 'toolTipPin';
				document.getElementsByTagName('body')[0].appendChild(tipPinLayer);
				tipPinLayer.className="Documentation";
				tipPinLayer.style.top = '0';
				tipPinLayer.style.visibility = 'hidden';
				tipPinLayer.style.zIndex=2; // index = 2, below indicator's index = 3
				tipPinLayer.onmouseover = tipLayer.onmouseover;
				tipPinLayer.onmouseout = tipLayer.onmouseout;
			}
			
			
			shadowArea = document.createElement('div');
			shadowArea.id = 'shadowArea';
			shadowArea.onmouseover= tipLayer.onmouseover;
			shadowArea.onmouseout = tipLayer.onmouseout;
			
			document.getElementsByTagName('body')[0].appendChild(shadowArea);
		},
		
		show : function(area){
			this.tooltipVisible = true;
			
			if (window.hideTimeoutId) {
				clearTimeout(hideTimeoutId);
			}
			if (window.opacityId) {
				clearTimeout(opacityId);
			}
			
			this.area = area;
			area.removeAttribute('title');
			this.updateShadowArea(area);
			
			tipLayer.style.visibility = 'visible';
			tipLayer.style.opacity = '.1';
			tipLayer.style.zIndex=5;
			tipLayer.innerHTML = area.getAttribute('docContent')
				.replace(/&gt;/g, '>').replace(/&lt;/g, '<')
				.replace(/&\u200blt;/g, '&lt;').replace(/&\u200bgt;/g, '&gt;') // replace the &{zero-length-space}lt; to &lt;
				.replace(/&quot;/g, '"');
			
			tipConnectorLayer.style.visibility = 'visible';
			tipConnectorLayer.style.opacity = '.1';
			tipConnectorLayer.style.zIndex=5;
			
			tipPinLayer.style.visibility = 'visible';
			tipPinLayer.style.opacity = '.1';
			tipPinLayer.style.zIndex=5;
			
			this.moveTo(area);
			this.fade(10);
		},
		
		updateShadowArea : function(area){
			
			var imageId = area.getAttribute("imageId");
			
			var areaCoordinate;
			if (area.getAttribute("relativeBounds") == 1) {
				var lRelativeX = findPosX(area);
				var lRelativeY = findPosY(area);
				areaCoordinate = (lRelativeX+","+lRelativeY+","+(lRelativeX+area.offsetWidth)+","+(lRelativeY+area.offsetHeight)).split(",")
			}
			else {
				areaCoordinate = area.coords.split(",")
			}
			var topRightX = areaCoordinate[2]*1
			var topRightY = areaCoordinate[1]*1
			var width = this.xOffset;
			var height = areaCoordinate[3]*1 - topRightY;
			
			N = (document.all) ? 0 : 1;
			var diagram = document.getElementById(imageId);
			if (N) {
				shadowArea.style.left = findPosX(diagram) + topRightX;
				shadowArea.style.top = findPosY(diagram) + topRightY;
			} else {
				shadowArea.style.posLeft = findPosX(diagram) + topRightX;
				shadowArea.style.posTop = findPosY(diagram) + topRightY;
			}		
			shadowArea.style.width = width;
			shadowArea.style.height = height;
			
		},
		
		fade : function(opac) {
			var passed = parseInt(opac);
			var newOpac = parseInt(passed+5);
			if ( newOpac < 90 ) {
				tipLayer.style.opacity = '.'+newOpac;
				tipLayer.style.filter = "alpha(opacity:"+newOpac+")";
				tipConnectorLayer.style.opacity = '.'+newOpac;
				tipConnectorLayer.style.filter = "alpha(opacity:"+newOpac+")";
				tipPinLayer.style.opacity = '.'+newOpac;
				tipPinLayer.style.filter = "alpha(opacity:"+newOpac+")";
				opacityId = window.setTimeout("tooltip.fade('"+newOpac+"')", 40);
			}
			else { 
				tipLayer.style.opacity = '.90';
				tipLayer.style.filter = "alpha(opacity:90)";
				tipConnectorLayer.style.opacity = '.90';
				tipConnectorLayer.style.filter = "alpha(opacity:90)";
				tipPinLayer.style.opacity = '.90';
				tipPinLayer.style.filter = "alpha(opacity:90)";
			}
		},
		
		moveTo : function(area) {
			var imageId = area.getAttribute("imageId");
			
			var diagram = document.getElementById(imageId);
			
			var lDiagramX = findPosX(diagram)
			var lDiagramY = findPosY(diagram)
			
			var lTipLayerX = lDiagramX;
			var lTipLayerY = lDiagramY;
			// for showing Tooltip in Table/Cell, diagram is a Table, need get height by .offsetHeight
			if (diagram.height > 0) {
				lTipLayerY += diagram.height;
			}
			else if (diagram.offsetHeight > 0) {
				lTipLayerY += diagram.offsetHeight;
			}
			
			lTipLayerX += getScrollLeft();
			
			var lAreaCoordinate;
			if (area.getAttribute("relativeBounds") == 1) {
				// the x/y need - Diagram.x/y
				var lRelativeX = findPosX(area)-lDiagramX;
				var lRelativeY = findPosY(area)-lDiagramY;
				lRelativeX -= 2; // -2 for 4 width/height of the tipPinLayer
				lRelativeY -= 2; // -2 for 4 width/height of the tipPinLayer
				lAreaCoordinate = (lRelativeX+","+lRelativeY+","+(lRelativeX+area.offsetWidth)+","+(lRelativeY+area.offsetHeight)).split(",")
			}
			else {
				lAreaCoordinate = area.coords.split(",");
			}

//			var lAreaTop = lAreaCoordinate[1]*1 + lDiagramY;
			var lAreaBottom = lAreaCoordinate[3]*1 + lDiagramY;
			var lAreaX1 = lAreaCoordinate[0]*1 + lDiagramX;
			var lAreaX2 = lAreaCoordinate[2]*1 + lDiagramX;
			
			var lScreenBottom = getScrollTop()+getClientHeight() - tipLayer.offsetHeight; // no height is set in layer. Just try to - 300
			if (lTipLayerY > lScreenBottom) {
				
				if (lScreenBottom < lAreaBottom) {
					// don't overlap with the area
					lScreenBottom = lAreaBottom;
				}
				lTipLayerY = lScreenBottom;
			}
			
			N = (document.all) ? 0 : 1;
			if (N) {
				tipLayer.style.left = lTipLayerX;
				tipLayer.style.top = lTipLayerY;
				
				tipPinLayer.style.left = lAreaX1;
				tipPinLayer.style.top = lAreaBottom;
				
				tipConnectorLayer.style.left = lAreaX1+((lAreaX2-lAreaX1)/2); // -2 for connector's width/2
				tipConnectorLayer.style.top = lAreaBottom+6; // +6 for pin's height+borderHeight
			}
			else {
				tipLayer.style.posLeft = lTipLayerX;
				tipLayer.style.posTop = lTipLayerY;

				tipPinLayer.style.posLeft = lAreaX1;
				tipPinLayer.style.posTop = lAreaBottom;
				
				tipConnectorLayer.style.posLeft = lAreaX1+((lAreaX2-lAreaX1)/2); // -2 for connector's width/2
				tipConnectorLayer.style.posTop = lAreaBottom+6; // +6 for pin's height+borderHeight
			}
			
			var lScreenWidth = getWidth(lTipLayerX);
			tipLayer.style.width = lScreenWidth;
			
			tipPinLayer.style.width = lAreaX2-lAreaX1;
			
			if (lTipLayerY > lAreaBottom+6) {
				tipConnectorLayer.style.height = lTipLayerY-lAreaBottom-6;
			}
			else {
				tipPinLayer.style.visibility = 'hidden';
				tipConnectorLayer.style.visibility = 'hidden';
			}
			
			
			
		},
		
		hide : function() {
			hideTimeoutId = window.setTimeout(function() {
				this.tooltipVisible = false;
				
				if (window.showTimeoutId) {
					clearTimeout(showTimeoutId);
				}
				if (window.hideTimeoutId) {
					clearTimeout(hideTimeoutId);
				}
				if (window.opacityId) {
					clearTimeout(opacityId);
				}
				tipLayer.style.visibility = 'hidden';
				tipConnectorLayer.style.visibility = 'hidden';
				tipPinLayer.style.visibility = 'hidden';
			}, this.hideTooltipTimeOut);
		}
};

function initPage(){
	tooltip.init();
}

function showTooltip(area) {
	if (tooltip.tooltipVisible) {
		if (window.showTimeoutId) {
			clearTimeout(showTimeoutId);
		}
		if (window.hideTimeoutId) {
			clearTimeout(hideTimeoutId);
		}
		
		showTimeoutId = window.setTimeout(function() {
			if (window.showTimeoutId) {
				clearTimeout(showTimeoutId);
			}
			tooltip.show(area);
		}, tooltip.showTooltipTimeOut);
	}
	else {
		tooltip.show(area);
	}
}

function hideTooltip(){
	tooltip.hide();
}

function getWidth(aLeft) {
	var lWidth = getClientWidth() + getScrollLeft() - aLeft - 20;
	
	return lWidth;
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
function filterResults(aWin, aDoc, aBody) {
	var aResult = aWin ? aWin : 0;
	if (aDoc && (!aResult || (aResult > aDoc)))
		aResult = aDoc;
	return aBody && (!aResult || (aResult > aBody)) ? aBody : aResult;
}