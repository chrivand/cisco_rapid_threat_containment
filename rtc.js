function getStarted() {

    // global views
    gl_view = "";
    gl_details = "";
    gl_current_user = {};
    gl_current_host = {};
    
    // global xhr requests
    gl_xhr = new XMLHttpRequest();
    gl_users_xhr = new XMLHttpRequest();
    gl_hosts_xhr = new XMLHttpRequest();
    gl_rtcconfig_xhr = new XMLHttpRequest();        

    gl_view = "ABOUT";
    gl_sw_config = [
	{ "id" :"sw_server","value":"", "label": "SW SERVER" },
	{ "id" :"sw_username","value":"", "label": "SW USERNAME" },	
	{ "id" :"sw_password","value":"", "label": "SW PASSWORD" }
    ];
    gl_ise_config = [
	{ "id" :"ise_server","value":"", "label": "ISE SERVER" },
	{ "id" :"ise_username","value":"", "label": "ISE USERNAME" },	
	{ "id" :"ise_password","value":"", "label": "ISE PASSWORD" },
	{ "id" :"pxgrid_client_cert","value":"", "label": "PXGRID CLIENT CERT" },
	{ "id" :"pxgrid_client_key","value":"", "label": "PXGRID CLIENT KEY" },
	{ "id" :"pxgrid_client_key_pw","value":"", "label": "PXGRID CLIENT KEY PASSWORD" },
	{ "id" :"pxgrid_server_cert","value":"", "label": "PXGRID SERVER CERT" },
	{ "id" :"pxgrid_nodename","value":"", "label": "PXGRID NODE NAME" }
    ];
    gl_amp_config = [
	{ "id" :"amp_api_client_id","value":"", "label": "AMP CLIENT ID" },
	{ "id" :"amp_api_key","value":"", "label": "AMP CLIENT KEY" },
	{ "id" :"tg_api_key","value":"", "label": "ThreatGrid KEY" }	
    ];
    gl_umbrella_config = [
	{ "id" :"u_orgid","value":"", "label": "UMBRELLA ORG ID" },
	{ "id" :"u_investigate_token","value":"", "label": "UMBRELLA INVESTIGATE" },
	{ "id" :"u_enforce_token","value":"", "label": "UMBRELLA ENFORCEMENT" },
	{ "id" :"u_secret","value":"", "label": "UMBRELLA SECRET" },
	{ "id" :"u_key","value":"", "label": "UMBRELLA KEY" },
    ];
    
    gl_sw_events = [

    ];
    gl_amp_events = [

    ];
    gl_umbrella_events = [
	{ "id" : 0, "uname" : "Command and Control", "description" : "Client communicated to Command and Control Domain" },
	{ "id" : 1, "uname" : "Cryptomining", "description" : "Client communicated to Crypto miningDomain" },	
    ];

    gl_hosts = [];
    gl_users = [];    
    gl_timeglass = null;
    gl_host_timer = null;
    gl_host_timer = null;        
    gl_timeelapsed = 0;
    gl_retcode = "";
    gl_rtc_config = {};
    gl_initializing = true;
    gl_got_rtc = false;
    gl_got_hosts = false;
    gl_got_users = false;
    gl_got_event_types = false;
    
    mAbout();    
    mRefreshEventTypes()
    mRefreshHosts();
    mRefreshUsers();
    mEditRTC();        
    gl_retcode = "Initializing.."
    timeGlass();
    updateRetCode("Wait",gl_retcode)    


}

//
//  Helper Functions
//
function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

function shortString(s) {
    shorter = s
    if (s.length > 20) {
	shorter = s.substring(0,15) + "...";
//	endstr  = s.substring((s.length-5),4);
//	alert(s.length-5);
//	alert(endstr);
	shorter = shorter;
    }
    return shorter;
    
}
function catchEvent(eventObj, event, eventHandler) {
    if (eventObj.addEventListener) {
        eventObj.addEventListener(event, eventHandler, false);
    }
    else if (eventObj.attachEvent) {
        event = "on" + event;
        eventObj.attachEvent(event, eventHandler);
    }
}

function timeGlass() {
    gl_timeglass = window.setTimeout(cbTimeGlass,1000);
}
function cbTimeGlass() {
    gl_timeelapsed = gl_timeelapsed +1;
    var tmpstring = gl_retcode + " ... " + gl_timeelapsed + " seconds";
    updateRetCode("Wait",tmpstring);
    timeGlass();
}

function hostTimer() {
    gl_host_timer = window.setTimeout(cbHostTimer,20000);
}
function cbHostTimer() {
    mRefreshHosts(true);
    hostTimer();
}

function userTimer() {
    gl_user_timer = window.setTimeout(cbUserTimer,20000);
}
function cbUserTimer() {
    mRefreshUsers(true);
    userTimer();
}


function stopTimeGlass() {
    window.clearTimeout(gl_timeglass)
    gl_timeglass = null;
    gl_retcode = "";
    gl_timeelapsed = 0;
}

//
//   DOM creation Helpers
//
function buildTable() {

    var oldChild = document.getElementById("divChild");
    var divContent = document.getElementById("divContent");
    var divChild = document.createElement("div");
    divContent.replaceChild(divChild,oldChild);    
    divChild.setAttribute("id","divChild");
    divChild.setAttribute("class","container");

    var divTable = document.createElement("div");
    divTable.setAttribute("class","divTable");

    divChild.appendChild(divTable);
    return divTable

}

function buildTable2() {

    var tables = [];
    var oldChild = document.getElementById("divChild");
    var divContent = document.getElementById("divContent");

    var divChild = document.createElement("div");
    divContent.replaceChild(divChild,oldChild);    
    divChild.setAttribute("id","divChild");
    divChild.setAttribute("class","container");

    var divTable = document.createElement("div");
    divTable.setAttribute("class","divTable2");
    divTable.setAttribute("id","divTable");


    var divDetails = document.createElement("div");
    divDetails.setAttribute("class","divDetails");
    divDetails.setAttribute("id","divDetails");
    
    divChild.appendChild(divTable);
    divChild.appendChild(divDetails);
    
    tables = [];
    tables[0] = divTable;
    tables[1] = divDetails;
    return tables;

}

function buildDivDetails() {
    var divChild = document.getElementById("divChild");
    var divOld = document.getElementById("divDetails");
    var divDetails = document.createElement("div");
    divDetails.setAttribute("class","divDetails");
    divDetails.setAttribute("id","divDetails");
    divChild.replaceChild(divDetails,divOld);    
    return divDetails;
}

function startEdit() {
    var divContent = document.getElementById("divContent");
    var oldChild   = document.getElementById("divChild");
    var divChild = document.createElement("div");
    divChild.setAttribute("id","divChild");
    divChild.setAttribute("class","container");
    divContent.replaceChild(divChild,oldChild);
    return divChild
}

function tableHeader(divTable) {
    var divHeadRow = document.createElement("div");
    divHeadRow.setAttribute("class","divHeadRow");
    divTable.appendChild(divHeadRow);
    return divHeadRow;
}


function displayText(t) {

    var oldChild = document.getElementById("divChild");
    var divContent = document.getElementById("divContent");
    var divChild = document.createElement("div");
    divChild.setAttribute("id","divChild");

    divChild.innerHTML = t;

    divContent.replaceChild(divChild,oldChild);
    
}
function updateRetCode(result,result2) {

    if (result == "OK") {
	rsptext = result2;
	cssClass = "divOK";
    }
    else {
	rsptext = result2;
	cssClass = "divError";
    }
    var divContent = document.getElementById("divContent");
    var oldDivRetCode = document.getElementById("divRetCode");
    var divRetCode = document.createElement("div");
    divRetCode.setAttribute("id","divRetCode");
    divRetCode.setAttribute("class",cssClass);
    divRetCode.innerHTML = rsptext;
//    var p = document.createElement("p");
//    var txt = document.createTextNode(rsptext);
//    p.appendChild(txt);
//    divRetCode.appendChild(p);
    divContent.replaceChild(divRetCode,oldDivRetCode);

}

function addCell(divRow,text,color="") {

    var divHeader = document.createElement("div");
    if (color) {
	divHeader.style.backgroundColor = color;
    }
    divHeader.setAttribute("class","divCell");
    var txt = document.createTextNode(text);
    divHeader.appendChild(txt);
    divRow.appendChild(divHeader);

}
function addCellwCallback2(divRow,text,callback) {

    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divCell");
    divHeader.setAttribute("id",text);    
    var txt = document.createTextNode(text);
    catchEvent(divHeader,"click",callback);
    divHeader.appendChild(txt);
    divRow.appendChild(divHeader);

}

function addCellwCallback(divRow,iconClass,id,callback,tooltiptext) {


    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divCell");
    divHeader.setAttribute("id",id);
    catchEvent(divHeader,"click",callback);
    var tooltip = document.createElement("span");
    tooltip.setAttribute("class","tooltiptext");
    var t = document.createTextNode(tooltiptext);
    tooltip.appendChild(t);
    divHeader.appendChild(tooltip);
    var icon = document.createElement("i");
    icon.setAttribute("class",iconClass);
    divHeader.appendChild(icon);
    divRow.appendChild(divHeader);

}
function addCellImage(divRow,imgsrc) {


    var divImage = document.createElement("div");
    divImage.setAttribute("class","divCell");
    var image = document.createElement("img");
    image.setAttribute("src",imgsrc);
    image.setAttribute("class","imgTable");    
    divImage.appendChild(image);
    divRow.appendChild(divImage);

}



function addCellPassword(divRow,id,text,size) {

    var inputObj = document.createElement("input");
    inputObj.setAttribute("id",id);

    inputObj.setAttribute("type", "password");
    inputObj.setAttribute("value", text);
    inputObj.setAttribute("size", size);
    inputObj.setAttribute("class","inputText");


    var divHeader = document.createElement("div");
    divHeader.setAttribute("id","divRightCell");
    divHeader.setAttribute("class","divRightCell");

    divHeader.appendChild(inputObj);
    divRow.appendChild(divHeader);

}
function addCellSelection(divRow,id,options) {
    var divSel = document.createElement("div");
    divSel.setAttribute("class","col-75");
    var select = document.createElement("select");
    select.setAttribute("id",id);
    for (i=0;i<options.length;i++) {
        option =  document.createElement("option");
        option.value = options[i];
        option.textContent = options[i];
        select.appendChild(option);
    }
    divSel.appendChild(select);
    divRow.appendChild(divSel);
}

function addHeaderCell(divRow,text) {


    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divHeaderCell");
    var txt = document.createTextNode(text);
    divHeader.appendChild(txt);
    divRow.appendChild(divHeader);

}
function addCellRow(divChild) {
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divrow");
    divChild.appendChild(divRow);
    return divRow;
}
function addCellStatic(divRow,lbltxt,bgcolor=false) {
    var divStatic = document.createElement("div");
    divStatic.setAttribute("class","col-25-1");
    if (bgcolor) {
	divStatic.setAttribute("class","col-25-2");
    }
    var label = document.createElement("label");
    label.setAttribute("for",lbltxt);
    var t = document.createTextNode(lbltxt);
    label.appendChild(t);
    divStatic.appendChild(label);
    divRow.appendChild(divStatic);
}
function addCellStaticRight(divRow,lbltxt) {
    if (lbltxt) {
    }
    else {
	lbltxt = "-"
    }
    var divStatic = document.createElement("div");
    divStatic.setAttribute("class","col-75");
    var label = document.createElement("label");
    label.setAttribute("for",lbltxt);
    var t = document.createTextNode(lbltxt);
    label.appendChild(t);
    divStatic.appendChild(label);
    divRow.appendChild(divStatic);
}

function cbSectionClick(ev1) {
    divID = this.id;
    thisDiv = document.getElementById(divID+"Section");
    if (thisDiv.style.display === 'none') {
	thisDiv.style.display = 'block';
    }
    else {
	thisDiv.style.display = 'none';	
    }

    
}
function addCellSectionHead(divRow,lbltxt,divid) {

    var divStatic = document.createElement("div");
    if (divid) {
	lbltxt = "+- " + lbltxt;	
	divStatic.setAttribute("id",divid);

    }
    divStatic.setAttribute("class","col-100-1");
    var label = document.createElement("label");
    label.setAttribute("for",lbltxt);
    var t = document.createTextNode(lbltxt);
    label.appendChild(t);
    divStatic.appendChild(label);
    if (divid) {
	catchEvent(divStatic,"click",cbSectionClick);
    }
    divRow.appendChild(divStatic);
}


function addHiddenPassword(divParent) {
    var divInput = document.createElement("div");
    divInput.setAttribute("class","hideme");
    var input = document.createElement("input");
    input.setAttribute("type","password");
    input.setAttribute("id","hideme");
    input.setAttribute("name","");
    input.setAttribute("value","");
    divInput.appendChild(input);
    divParent.appendChild(divInput);
}

function addCellInput(divRow,type,id,name,value) {
    var divInput = document.createElement("div");
    divInput.setAttribute("class","col-75");
    var input = document.createElement("input");
    input.setAttribute("type",type);
    input.setAttribute("id",id);
    input.setAttribute("name",name);
    input.setAttribute("value",value);
    divInput.appendChild(input);
    divRow.appendChild(divInput);
}
function addCellNumber(divRow,id,name,value,min,max) {
    var divInput = document.createElement("div");
    divInput.setAttribute("class","col-75");
    var input = document.createElement("input");
    input.setAttribute("type","number");
    input.setAttribute("id",id);
    input.setAttribute("name",name);
    input.setAttribute("value",value);
    input.setAttribute("min",min);
    input.setAttribute("max",max);        
    divInput.appendChild(input);
    divRow.appendChild(divInput);
}
// needs a hidden password field before real one to avoid browser remembering password

function addCellInputRO(divRow,type,id,name,value) {
    var divInput = document.createElement("div");
    divInput.setAttribute("class","col-75");
    var input = document.createElement("input");
    input.setAttribute("type",type);
    input.setAttribute("id",id);
    input.setAttribute("name",name);
    input.setAttribute("value",value);
    input.readOnly = true;
    
    divInput.appendChild(input);
    divRow.appendChild(divInput);
}
function addCellTextArea(divRow,id,name,value) {
    var divInput = document.createElement("div");
    divInput.setAttribute("class","col-75");
    var ta = document.createElement("textarea");
    ta.setAttribute("id",id);
    ta.setAttribute("name",name);
    ta.setAttribute("style","height:200px");
    txt = document.createTextNode(value);
    ta.appendChild(txt);

    divInput.appendChild(ta);
    divRow.appendChild(divInput);

}


function addCellHTML(divRow,html) {
    var divHTML = document.createElement("div");
    divHTML.setAttribute("class","col-75");
    divHTML.innerHTML = html;
    divRow.appendChild(divHTML);

}

function addCellButton(divRow,id,label,type,callback) {


    var btnAdd = document.createElement("input");
    btnAdd.setAttribute("type", type);
    btnAdd.setAttribute("value", label);
    btnAdd.setAttribute("id", id);
    catchEvent(btnAdd, "click", callback);

    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divButton");
    divHeader.appendChild(btnAdd);
    divRow.appendChild(divHeader);

}

//
//  Menu Callbacks
//
function mAbout() {

    var t = "Mice Control - A revolutionary system for Rapid Threat Containment of Evil Rats. Powered by cats.py<br><br>";
    t = t+ '<img src="about.jpg"></img><br><br>';
    t = t+ "Copyright &copy 1997-2018";
    displayText(t);
    updateRetCode("OK","About RTC");
    gl_view = "ABOUT";
}
function mResetRTCevents() {

    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcResetEvents.py",post,resetEventsresponse);
    updateRetCode("Wait","Resetting Events");
    

}
function mStartRTC() {

    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcStart.py",post,rtcStartResponse);
    updateRetCode("Wait","Starting RTC");
}
function resetEventsresponse() {
    updateRetCode("OK","Reset Events");    
}
function rtcStartResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Started RTC");	
    }
    else {
	updateRetCode("Error","Could not start RTC");	
    }
}


function mRefreshHosts(timercallback=false) {
    gl_hosts_xhr = new XMLHttpRequest();
    post = {};
    if (timercallback) {
	post["recurring"] = true;
    }
    else  {
	post["recurring"] = false;
    }
//    alert("post is " + JSON.stringify(post))
    sendXpost(gl_hosts_xhr,"/cgi-bin/rtcGetHosts.py",post,hostsResponse);    
}

function mHostView() {

    gl_view = "HOSTS";
    if (gl_hosts.length > 0) {
	if (isEmpty(gl_current_host)) {
	    gl_current_host = gl_hosts[0];
	}
	showHosts(gl_hosts);
	showHostDetails(gl_current_host);
    }
    else {
	mRefreshHosts();
    }
}
function mUserView() {

    gl_view = "USERS";    
    if (gl_users.length > 0) {
	if (isEmpty(gl_current_user)) {
	    gl_current_user = gl_users[0];
	}
	showUsers(gl_users);
	showUserDetails(gl_current_user);
    }
    else {
	mRefreshUsers();
    }
}

function mRefreshUsers(timercallback = false) {
    gl_users_xhr = new XMLHttpRequest();
    post = {};
    if (timercallback) {
	post["recurring"] = true;
    }
    else  {
	post["recurring"] = false;
    }
    
    sendXpost(gl_users_xhr,"/cgi-bin/rtcGetUsers.py",post,usersResponse);
}

function mRefreshEventTypes() {
    var event_types_xhr = new XMLHttpRequest();    
    post = {}
    sendXpost(event_types_xhr,"/cgi-bin/rtcGetEventTypes.py",post,eventTypesResponse);
}

function mStealthwatchEvents() {
    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcSWevents.py",post,stealthwatchEventsResponse);
    gl_retcode = "Retrieving SW Events, please wait!"    
    updateRetCode("Wait",gl_retcode)
    timeGlass();
}
function mAMPevents() {
    gl_view = "";
    gl_details = "";
    
    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcAMPevents.py",post,AMPeventsResponse);
    gl_retcode = "Retrieving AMP events,please wait...";
    updateRetCode("Waint",gl_retcode);
    timeGlass();
}
function mUmbrellaEvents() {
    gl_view = "";
    gl_details = "";
    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcUMBRELLAevents.py",post,UmbrellaEventsResponse);
    gl_retcode = "Retrieving Umbrella events,please wait...";
    updateRetCode("Wait",gl_retcode);
    timeGlass();

}
function mISEsessions() {
    gl_view = "";
    gl_details = "";
    
    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcISEsessions.py",post,ISEsessionsResponse);
    gl_retcode = "Retrieving ISE sessions,please wait...";
    updateRetCode("Wait",gl_retcode);
    timeGlass();

}

function mEditRTC() {
    gl_view = "";
    gl_details = "";
    var rtcconfig_xhr =  new XMLHttpRequest();
    post = {}
    sendXpost(rtcconfig_xhr,"/cgi-bin/rtcGetConfig.py",post,updateRTCconfigResponse);
}
function mEditSW() {
    gl_view = "";
    gl_details = "";
    post = {}
    sendXpost(gl_xhr,"/cgi-bin/rtcGetSWconfig.py",post,updateSWconfigResponse);
}

function mEditISE() {
    gl_view = "";
    gl_details = "";
    post = {}
    sendXpost(gl_xhr,"/cgi-bin/rtcGetISEconfig.py",post,updateISEconfigResponse);
}
function mEditAMP() {
    gl_view = "";
    gl_details = "";
    post = {}
    sendXpost(gl_xhr,"/cgi-bin/rtcGetAMPconfig.py",post,updateAMPconfigResponse);
}
function mEditUmbrella() {
    gl_view = "";
    gl_details = "";
    post = {}
    sendXpost(gl_xhr,"/cgi-bin/rtcGetUMBRELLAconfig.py",post,updateUMBRELLAconfigResponse);
}




//
//  Responses XMLHTTP request
//
function eventTypesResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	gl_sw_events = [];
	gl_amp_events = [];
	var events = rsp["swEvents"]["data"];
	if (events) {
	    for (var i=0;i<events.length;i++) {
		event = events[i];
		var t_event = {};
		t_event["description"] = event["description"];
		t_event["name"] = event["name"];
    		t_event["id"] = event["id"];
		gl_sw_events.push(t_event);
	    }
	}
	events = rsp["ampEvents"]["data"];
	if (events) {
	    for (var i=0;i<events.length;i++) {
		event = events[i];
		var t_event = {};
		t_event["description"] = event["description"];
		t_event["name"] = event["name"];
    		t_event["id"] = event["id"];
		gl_amp_events.push(t_event);
	    }
	}
    }
    else {
	alert("Error refreshing AMP and SW event types" + rsp.rtcResult + rsp.info);
    }
    if (gl_initializing) {
	gl_got_event_types = true;
	if (gl_got_hosts && gl_got_users && gl_got_rtc) {
	    gl_initializing = false;
	    var retcode = "Initialized application.."
	    stopTimeGlass();
	    updateRetCode("OK",retcode)    
	    hostTimer();
	    userTimer();	    
	}
    }	
    else {
	mEditRTC();
    }

}

function openJSONresponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	data = xhr.responseText;
//	myWindow = window.open("data:text/html," + encodeURIComponent(data),"_blank", "width=200,height=100");	
	myWindow = window.open("data:text/html," + encodeURIComponent(data),"_blank");
//	myWindow.focus();
    }
    else {
	alert("Error in receiving json" + rsp.rtcResult + rsp.info);
    }
}
function domainResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {

	var divChild = startEdit();
	var divRow = addCellRow(divChild);
	addCellStatic(divRow,"Domain");
	addCellStaticRight(divRow,rsp["features"]["base_domain"])
	var divRow = addCellRow(divChild);	
	addCellStatic(divRow,"IP");
	addCellStaticRight(divRow,rsp["features"]["prefixes"][0])
	var divRow = addCellRow(divChild);	
	addCellStatic(divRow,"Countries");
	addCellStaticRight(divRow,rsp["features"]["country_codes"][0])
	var divRow = addCellRow(divChild);		
	addCellStatic(divRow,"ASN");
	addCellStaticRight(divRow,rsp["features"]["asns"][0])
	var divRow = addCellRow(divChild);		
	addCellStatic(divRow,"Geo Location");
	addCellStaticRight(divRow,JSON.stringify(rsp["features"]["locations"][0]));

	updateRetCode("OK","Retrieved Domain Info")

    }
    else {
	alert("Error in receiving json" + rsp.rtcResult + rsp.info);
    }
}


function FLOWresponse(xhr) {
    stopTimeGlass();
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
//	alert("ok flows received");
	showFlows(rsp);
	updateRetCode("OK","Retrieved flows");
    }
    else {
	alert("Error in receiving flows" + rsp.rtcResult + rsp.info);
    }





}

function uqResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Unquarantine Successful");		
    }
    else {
	alert("Error in Unqurantining" + rsp.rtcResult + rsp.info);
    }
}

function qResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Quarantine Successful");		
    }
    else {
	alert("Error in quarantining" + rsp.rtcResult + rsp.info);
    }
}

function updateSWconfigResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var config = JSON.parse(rsp.configstring);
	for (var i=0;i<gl_sw_config.length;i++) {
	    var id = gl_sw_config[i].id
	    gl_sw_config[i].value = config[id]
	}
    }
    else {
	alert("Error in updating SW config  parameters" + rsp.rtcResult + rsp.info);
    }
    editSWconfig()

}
function updateISEconfigResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {

	var config = JSON.parse(rsp.configstring);
	for (var i=0;i<gl_ise_config.length;i++) {
	    var id = gl_ise_config[i].id
	    gl_ise_config[i].value = config[id]
	}
    }
    else {
	alert("Error in updating ISE config  parameters" + rsp.rtcResult + rsp.info);
    }
    editISEconfig()

}

function updateAMPconfigResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var config = JSON.parse(rsp.configstring);
	for (var i=0;i<gl_amp_config.length;i++) {
	    var id = gl_amp_config[i].id
	    gl_amp_config[i].value = config[id]
	}
    }
    else {
	alert("Error in updating AMP config  parameters" + rsp.rtcResult + rsp.info);
    }
    editAMPconfig()

}
function updateUMBRELLAconfigResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var config = JSON.parse(rsp.configstring);
	for (var i=0;i<gl_umbrella_config.length;i++) {
	    var id = gl_umbrella_config[i].id
	    gl_umbrella_config[i].value = config[id]
	}
    }
    else {
	alert("Error in updating UMBRELLA config  parameters" + rsp.rtcResult + rsp.info);
    }
    editUMBRELLAconfig()

}
function updateRTCconfigResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	gl_rtc_config = JSON.parse(rsp.configstring)
	if (gl_initializing) {
	    gl_got_rtc = true;
	    if (gl_got_hosts && gl_got_users && gl_got_event_types) {
		gl_initializing = false;
		var retcode = "Initialized application.."
		stopTimeGlass();
		updateRetCode("OK",retcode)
		hostTimer();
		userTimer();	    
		
	    }
	}
	else {
	    editRTCconfig(gl_rtc_config)
	}
    }
    else {
	alert("Error in updating RTC config  parameters" + rsp.rtcResult + rsp.info);
    }


}

function hostsResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var hosts = rsp.hosts;
	gl_hosts = hosts;
	if (gl_hosts.length > 0) {
	    if (isEmpty(gl_current_host)) {
		gl_current_host = gl_hosts[0];
	    }
	}
	
	if (gl_initializing) {
	    gl_got_hosts = true;
	    if (gl_got_rtc && gl_got_users && gl_got_event_types) {
		gl_initializing = false;
		var retcode = "Initialized application.."
		stopTimeGlass();
		updateRetCode("OK",retcode)
		hostTimer();
		userTimer();	    
		
	    }
	}
// need to keep track of global_view, global_details_view, global_host, global_user	
	else {
	    if (rsp["recurring"]) {
		if (gl_view == "HOSTS") {
		    showHosts(gl_hosts);
		    host = gl_current_host;
		    if (gl_details == "") {
			showHostDetails(host)
		    }
		    if (gl_details == "AMP") {
			AMPhostDetails(host)
		    }
		    if (gl_details == "UMB") {
			UMBhostDetails(host)
		    }
		    if (gl_details == "SW") {
			SWhostDetails(host)
		    }
		}
	    }
	    else {
		showHosts(gl_hosts);
		gl_current_host = hosts[0];
		if (gl_current_host) {
		    showHostDetails(gl_current_host)
		}
		
	    }
		
	}

    }
    else {
	alert("Error in getting Hosts" + rsp.rtcResult + rsp.info);
    }

}

function usersResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var users = rsp.users;
	gl_users = users;
	if (gl_users.length > 0) {
	    if (isEmpty(gl_current_user)) {
		gl_current_user = gl_users[0];
	    }
	}
	
	if (gl_initializing) {
	    gl_got_users = true;
	    if (gl_got_hosts && gl_got_rtc && gl_got_event_types) {
		gl_initializing = false;
		var retcode = "Initialized application..";
		stopTimeGlass();
		updateRetCode("OK",retcode);
		hostTimer();
		userTimer();	    
	    }
	}
	else {
	    if (rsp["recurring"]) {
		if (gl_view == "USERS") {
		    showUsers(gl_users);
		    var user = gl_current_user;
		    if (gl_details == "") {
			showUserDetails(user)
		    }
		    if (gl_details == "AMP") {
			AMPuserDetails(user)
		    }
		    if (gl_details == "UMB") {
			UMBuserDetails(user)
		    }
		    if (gl_details == "SW") {
			SWuserDetails(user)
		    }
		    if (gl_details == "FLOWS") {

		    }
		    
		}
	    }
	    else {
		showUsers(gl_users);
		user = users[0];
		if (user) {
		    showUserDetails(user)
		}
	    }
	}

    }
    else {
	alert("Error in getting Users" + rsp.rtcResult + rsp.info);
    }

}


function showHostDetails(host) {

    gl_current_host = host;
    var divChild = document.getElementById("divChild");
    var divOld = document.getElementById("divDetails");
    var divDetails = document.createElement("div");
    divDetails.setAttribute("class","divDetails");
    divDetails.setAttribute("id","divDetails");

    
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"MAC",true);
    addCellStaticRight(divRow,host["mac"]);
    divDetails.appendChild(divRow);

    try {
	var username = host["ise"]["userName"];
    }
    catch (err) {
	var username = "";
    }
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"User",true);
    addCellStaticRight(divRow,username);
    divDetails.appendChild(divRow);

    try {
	var ipAddress = host["ise"]["ipAddresses"][0];
    }
    catch (err) {
	var ipAddress = "";
    }
    
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"IP",true);    
    addCellStaticRight(divRow,ipAddress);
    divDetails.appendChild(divRow);

    try {
	var endpointProfile = host["ise"]["endpointProfile"];
    }
    catch (err) {
	var endpointProfile = "";
    }
    
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"Profile",true);    
    addCellStaticRight(divRow,endpointProfile);
    divDetails.appendChild(divRow);

    try {
	var sgt = host["ise"]["ctsSecurityGroup"];
    }
    catch
	(err) {
	var sgt = "";
    }
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"SGT",true);    
    addCellStaticRight(divRow,sgt);
    divDetails.appendChild(divRow);

    // AMP
    try {
	var hostname = host["amp"]["data"][0]["hostname"];
    }
    catch (err) {
	var hostname = "";
    }
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"Hostname",true);    
    addCellStaticRight(divRow,hostname);
    divDetails.appendChild(divRow);    

    try {
	var os = host["amp"]["data"][0]["operating_system"];
    }
    catch (err) {
	var os = "";
    }
    divDetails.appendChild(divRow);
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"OS",true);    
    addCellStaticRight(divRow,os);

    try {
	var nas = host["ise"]["nasIpAddress"];
    }
    catch (err) {
	var nas = "";
    }
    divDetails.appendChild(divRow);
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"Network Device",true);    
    addCellStaticRight(divRow,nas);
    
    divDetails.appendChild(divRow);
    
    try {
	var nasport = host["ise"]["nasPortId"];
    }
    catch (err) {
	var nasport = "";
    }
    divDetails.appendChild(divRow);
    divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");
    addCellStatic(divRow,"Network Device Port",true);    
    addCellStaticRight(divRow,nasport);
    
    divDetails.appendChild(divRow);

    divChild.replaceChild(divDetails,divOld);
    updateRetCode("OK","Retrieved Host Details")

}
function getColor(penalty) {
    var color = "white";
    if (penalty > gl_rtc_config["rtcYELLOWThreshold"]) {
	   color = "yellow";
    }
    if (penalty > gl_rtc_config["rtcORANGEThreshold"]) {
	color = "orange";
    }
    if (penalty > gl_rtc_config["rtcREDThreshold"]) {
	color = "red";
    }
    return color;
}
function showHosts(hosts) {

    gl_view = "HOSTS";
//    alert(JSON.stringify(rsp));
    var ANCevents = [];
    
    var divs  = buildTable2();
    var divTable = divs[0];
    var divDetails = divs[1];
    
    var divHeadRow = tableHeader(divTable);
    addHeaderCell(divHeadRow," Penalty");            
    addHeaderCell(divHeadRow,"ANC");
    addHeaderCell(divHeadRow,"CTR");
    addHeaderCell(divHeadRow,"AMP");
    addHeaderCell(divHeadRow,"UMB");                    
    addHeaderCell(divHeadRow,"SW");
    addHeaderCell(divHeadRow,"Flows");    
    addHeaderCell(divHeadRow," Device");
    addHeaderCell(divHeadRow," MAC");
//    addHeaderCell(divHeadRow," User");    
//    addHeaderCell(divHeadRow," IP");
//    addHeaderCell(divHeadRow," Profile");

    
    for (var i=0;i<hosts.length;i++) {
	var host = hosts[i];

	var selectedRow = false;
	if (host["mac"] == gl_current_host["mac"]) {
	    selectedRow = true;
	}
	var divRow = document.createElement("div");
	
        divRow.setAttribute("class","divRow3");
	if (selectedRow) {
	    divRow.style.backgroundColor = "blueviolet";
//	    divHeader.style.backgroundColor = color;	    
	}
	var icon = "fa fa-question-circle"
	try {
	    profile = host["ise"]["endpointProfile"]
	}
	catch (error) {
	    profile = "-"
	}

	try {
	    var ipAddress = host["ise"]["ipAddresses"][0];
	}
	catch (err) {
	    var ipAddress = "";
	}

	if (profile.startsWith("Win")) {
	    icon = "fab fa-windows"
	}
	if (profile.startsWith("Mac")) {
	    icon = "fab fa-apple"
	}
	penalty = host["penalty"];

	color = getColor(penalty);
	addCell(divRow,penalty,color);
	
	if (host["ancpolicy"] == "Quarantine") {
	    addCellwCallback(divRow,"fa fa-lock",host["mac"],cbUnquarantine,"Unquarantine");
	}
	else {
	    addCellwCallback(divRow,"fa fa-unlock",host["mac"],cbQuarantine,"Quarantine");	    
	}
	addCellwCallback(divRow,"fa fa-binoculars",host["mac"],cbCTRhost,"Launch CTR");		
	addCellwCallback(divRow,"fa fa-infinity",host["mac"],cbAMPhostDetails,"AMP Events");
	addCellwCallback(divRow,"fa fa-umbrella",host["mac"],cbUMBhostDetails,"UMB Events");
	addCellwCallback(divRow,"fas fa-arrow-alt-circle-up",host["mac"],cbSWhostDetails,"SW Events")
	addCellwCallback(divRow,"fas fa-arrows-alt",ipAddress,cbFlowInfo,"SW Flows");	
	addCellwCallback(divRow,icon,host["mac"],cbHostDetails,"Endpoint Details");		

	addCellwCallback2(divRow,host["mac"],cbHostDetails);
//	addCell(divRow,host["userName"]);
//	addCell(divRow,host["ipAddresses"][0]);
//	addCell(divRow,host["profile"]);
	divTable.appendChild(divRow);	
    }
    

}
function showUserDetails(user) {

    var divChild = document.getElementById("divChild");
    var divOld = document.getElementById("divDetails");
    var divDetails = document.createElement("div");
    divDetails.setAttribute("class","divDetails");
    divDetails.setAttribute("id","divDetails");

    
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");

    try {
	var username = host["ise"]["userName"];
    }
    catch (err) {
	var username = "";
    }

    addCellStatic(divRow,"User",true);
    addCellStaticRight(divRow,user["user"]);
    divDetails.appendChild(divRow);

    divChild.replaceChild(divDetails,divOld);
    updateRetCode("OK","Retrieved User Details")

}

function showUsers(users) {

    var divs  = buildTable2();
    var divTable = divs[0];
    var divDetails = divs[1];
    
    var divHeadRow = tableHeader(divTable);
    addHeaderCell(divHeadRow," Penalty");
    addHeaderCell(divHeadRow," CTR");                
    addHeaderCell(divHeadRow,"AMP");
    addHeaderCell(divHeadRow,"UMB");                    
    addHeaderCell(divHeadRow,"SW");
    addHeaderCell(divHeadRow,"Details");
    addHeaderCell(divHeadRow,"Username");


    
    for (var i=0;i<users.length;i++) {
	var user = users[i];

	var selectedRow = false;
	if (user["user"] == gl_current_user["user"]) {
	    selectedRow = true;
	}
	
	var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");

	if (selectedRow) {
	    divRow.style.backgroundColor = "blueviolet";
//	    divHeader.style.backgroundColor = color;	    
	}

	penalty = user["penalty"];

	color = getColor(penalty);

	addCell(divRow,penalty,color);
	addCellwCallback(divRow,"fas fa-binoculars",user["user"],cbCTRuser,"Launch CTR")	
	addCellwCallback(divRow,"fa fa-infinity",user["user"],cbAMPuserDetails,"AMP Events");
	addCellwCallback(divRow,"fa fa-umbrella",user["user"],cbUMBuserDetails,"UMB Events");
	addCellwCallback(divRow,"fas fa-arrow-alt-circle-up",user["user"],cbSWuserDetails,"SW Events")

	addCellwCallback(divRow,"fas fa-user",user["user"],cbUserDetails,"User Details");		
	addCellwCallback2(divRow,user["user"],cbUserDetails);
	divTable.appendChild(divRow);	
    }
    
    user = users[0];
    if (user) {
	showUserDetails(user)
    }

}

function showFlows(rsp) {

//    alert(JSON.stringify(rsp));
    gl_details = "FLOWS";
    var flows = [];
    flows = rsp.flows;

    var divDetails = buildDivDetails();
    var divHeadRow = tableHeader(divDetails);
    addHeaderCell(divHeadRow,"Start");


    addHeaderCell(divHeadRow,"Client IP");
    addHeaderCell(divHeadRow,"Client Country");
    addHeaderCell(divHeadRow,"Server IP");
    addHeaderCell(divHeadRow,"Server Country");    
    addHeaderCell(divHeadRow,"Protocol");    
    addHeaderCell(divHeadRow,"Dest Port");
    addHeaderCell(divHeadRow,"Bytes Client/Server");    

// f
    for (var i=0;i<flows.length;i++) {
	var flow = [];
	var flow = flows[i];

	var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");

	addCell(divRow,flow["start-time"]);

	addCell(divRow,flow["client"]["ip"]);
	addCell(divRow,flow["client"]["country"]);	
        addCell(divRow,flow["server"]["ip"]);
	addCell(divRow,flow["server"]["country"]);		
        addCell(divRow,flow["protocol"]);	
        addCell(divRow,flow["server"]["port"]);
        addCell(divRow,flow["client"]["bytes"]+ "/" + ["server"]["bytes"]);

	divDetails.appendChild(divRow);
    }

}
function showAMPdetails(events) {

    gl_details = "AMP";
    

    
    var divDetails = buildDivDetails();
    
    var divHeadRow = tableHeader(divDetails);
    addHeaderCell(divHeadRow,"Details");    
    addHeaderCell(divHeadRow,"Event Time");
    addHeaderCell(divHeadRow,"Penalty");        
    addHeaderCell(divHeadRow,"Event Type");
    addHeaderCell(divHeadRow,"Hash");

// f
    for (var i=0;i<events.length;i++) {
	var event = [];
	var event = events[i];
	var penalty = event["penalty"]
	var AMP = event["eventstring"];
	var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");
	addCellwCallback(divRow,"fa fa-binoculars",event["eventid"],cbAMPeventDetails,"View AMP Event Details");
	addCell(divRow,AMP["AMP_date"]);
	addCell(divRow,penalty);	
	addCell(divRow,AMP["AMP_event_type"]);
	addCell(divRow,shortString(AMP["AMP_hash"]));

	divDetails.appendChild(divRow);
    }

}

function showSWdetails(events) {

    gl_details = "SW";

    var divDetails = buildDivDetails();
    var divHeadRow = tableHeader(divDetails);
    addHeaderCell(divHeadRow,"Details");        
    addHeaderCell(divHeadRow,"Event Time");
    addHeaderCell(divHeadRow,"Penalty");
    addHeaderCell(divHeadRow,"Event Type");    
    addHeaderCell(divHeadRow,"Source IP");
    addHeaderCell(divHeadRow,"Destination IP");
    addHeaderCell(divHeadRow,"Protocol");    
    addHeaderCell(divHeadRow,"Destination Port");
// f
    for (var i=0;i<events.length;i++) {
	var event = [];
	var penalty = events[i]["penalty"];
	var eventid = events[i]["eventid"];
	var event = events[i]["eventstring"];

	var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");
	var event_id = event["SW_security_event_ID"];
	var event_type = "Unknown event type";
	for (var j=0;j< gl_sw_events.length;j++) {
	    if (event_id == gl_sw_events[j]["id"]) {
		event_type = gl_sw_events[j]["name"];
		break;
	    }
	}
	addCellwCallback(divRow,"fa fa-binoculars",eventid,cbSWeventDetails,"View SW Event Details");
	addCell(divRow,event["SW_first_active"]);

	addCell(divRow,penalty);
	addCell(divRow,event_type);	
	addCell(divRow,event["SW_source_IP"]);
	addCell(divRow,event["SW_destination_IP"]);
	addCell(divRow,event["SW_destination_protocol"]);		
	addCell(divRow,event["SW_destination_port"]);		
	divDetails.appendChild(divRow);
    }


}


function showUMBdetails(events) {

    gl_details = "UMB";
    
    var divDetails = buildDivDetails();
    var divHeadRow = tableHeader(divDetails);
    addHeaderCell(divHeadRow,"Details");    
    addHeaderCell(divHeadRow,"Event Time");
    addHeaderCell(divHeadRow,"Penalty");    
    addHeaderCell(divHeadRow,"Internal IP");
    addHeaderCell(divHeadRow,"Domain");
    addHeaderCell(divHeadRow,"Category");

    

// f
    for (var i=0;i<events.length;i++) {
	var event = [];
	var event = events[i];
	var penalty = event["penalty"]	
	var UMB = event["eventstring"];
	var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");
	addCellwCallback(divRow,"fa fa-binoculars",event["eventid"],cbUMBeventDetails,"View Umbrella Event Details");	
	addCell(divRow,UMB["UMB_datetime"]);
	var penalty = event["penalty"]
	addCell(divRow,penalty);
	addCell(divRow,UMB["UMB_internalIp"]);
	addCell(divRow,shortString(UMB["UMB_destination"]));
	addCell(divRow,UMB["UMB_category"]);
	divDetails.appendChild(divRow);
    }

}

//
//  Form Builders
//

function stealthwatchEventsResponse(xhr) {
    gl_view = "SWEVENTS";
    stopTimeGlass();
    var rsp = JSON.parse(xhr.responseText);

    if (rsp.rtcResult != "OK") {
	alert("Error :" + rsp.rtcresult);
	return
    }
    var swEvents = []
    swEvents = rsp.data.results

    divTable = buildTable()

    var divHeadRow = document.createElement("div");
    divHeadRow.setAttribute("class","divHeadRow");
    divTable.appendChild(divHeadRow);

    addHeaderCell(divHeadRow,"Event ID");
    addHeaderCell(divHeadRow,"Event Type");
    addHeaderCell(divHeadRow,"First Active");
    addHeaderCell(divHeadRow,"Last Active");
    addHeaderCell(divHeadRow,"Source IP");
    addHeaderCell(divHeadRow,"Source Port");
    addHeaderCell(divHeadRow,"Source Protocol");
    addHeaderCell(divHeadRow,"Source Tag Type");
    addHeaderCell(divHeadRow,"Target IP");
    addHeaderCell(divHeadRow,"Target Port");
    addHeaderCell(divHeadRow,"Target Protocol");
    addHeaderCell(divHeadRow,"Target Tag Type");
    addHeaderCell(divHeadRow,"Hit Count");

    for (var i=0;i<swEvents.length;i++) {
	var swEvent = [];
	swEvent = swEvents[i];
        var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");

        addCell(divRow,swEvent["id"]);
        addCell(divRow,swEvent["securityEventType"]);
        addCell(divRow,swEvent["firstActiveTime"]);
        addCell(divRow,swEvent["lastActiveTime"]);

        addCell(divRow,swEvent["source"]["ipAddress"]);
        addCell(divRow,swEvent["source"]["port"]);
        addCell(divRow,swEvent["source"]["protocol"]);
	addCell(divRow,JSON.stringify(swEvent["source"]["tags"]));


        addCell(divRow,swEvent["target"]["ipAddress"]);
        addCell(divRow,swEvent["target"]["port"]);
        addCell(divRow,swEvent["target"]["protocol"]);
	addCell(divRow,JSON.stringify(swEvent["target"]["tags"]));
	
	addCell(divRow,swEvent["hitCount"]);
	divTable.appendChild(divRow);

    }

    updateRetCode("OK","Retrieved Stealthwatch Security Events")
    
}

function UmbrellaEventsResponse(xhr) {
    stopTimeGlass();
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult != "OK") {
	alert("Error :" + rsp.rtcResult);
	return
    }

    var Events = []
    Events = rsp.requests;
    var divTable = buildTable()

    var divHeadRow = document.createElement("div");
    divHeadRow.setAttribute("class","divHeadRow");
    divTable.appendChild(divHeadRow);

    addHeaderCell(divHeadRow,"Internal IP");
    addHeaderCell(divHeadRow,"External IP");
    addHeaderCell(divHeadRow,"Categories");
    addHeaderCell(divHeadRow,"Destination");
    addHeaderCell(divHeadRow,"Action Taken");
    addHeaderCell(divHeadRow,"Date");

    for (var i=0;i<Events.length;i++) {
	var Event = [];
	Event = Events[i];
        var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");

        addCell(divRow,Event["internalIp"]);
        addCell(divRow,Event["externalIp"]);
        addCell(divRow,JSON.stringify(Event["categories"]));
        addCell(divRow,Event["destination"]);
        addCell(divRow,Event["actionTaken"]);
	addCell(divRow,Event["datetime"]);
	divTable.appendChild(divRow);

    }

    updateRetCode("OK","Retrieved Umbrella Security Report")
    
}
function ISEsessionsResponse(xhr) {
    stopTimeGlass();
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult != "OK") {
	alert("Error :" + rsp.rtcResult);
	return
    }
    var sessions = []
    sessions = rsp.sessions;

    divTable = buildTable()
    divHeadrow = tableHeader(divTable)
    
    var divHeadRow = document.createElement("div");
    divHeadRow.setAttribute("class","divHeadRow");
    divTable.appendChild(divHeadRow);

    addHeaderCell(divHeadRow,"User Name");
    addHeaderCell(divHeadRow,"MAC");
    addHeaderCell(divHeadRow,"IP");
    addHeaderCell(divHeadRow,"SGT");
    addHeaderCell(divHeadRow,"OS");
    addHeaderCell(divHeadRow,"Profile");
    addHeaderCell(divHeadRow,"NAS");
    addHeaderCell(divHeadRow,"Port");
    addHeaderCell(divHeadRow,"State");            
    for (var i=0;i<sessions.length;i++) {
	var Event = [];
	session = sessions[i];
	if (session["state"] != "STARTED" && session["state"] != "POSTURED") {
	    continue;
	}
        var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");

        addCell(divRow,session["userName"]);	
        addCell(divRow,session["macAddress"]);
	var firstIP = session["ipAddresses"][0]
        addCell(divRow,firstIP);
        addCell(divRow,session["ctsSecurityGroup"]);
        addCell(divRow,session["endpointOperatingSystem"]);
        addCell(divRow,session["endpointProfile"]);
	addCell(divRow,session["nasIpAddress"]);	
	addCell(divRow,session["nasPortId"]);
	addCell(divRow,session["state"]);	
	divTable.appendChild(divRow);

    }

    updateRetCode("OK","Retrieved ISE sessions")
    
}

function AMPeventsResponse(xhr) {
    stopTimeGlass()
    var rsp = JSON.parse(xhr.responseText);

    if (rsp.rtcResult != "OK") {
	alert("Error :" + rsp.rtcResult);
	return
    }
    var Events = []
    Events = rsp.data
    var divTable = buildTable()
    var divHeadRow = tableHeader(divTable);

    addHeaderCell(divHeadRow,"Date");
    addHeaderCell(divHeadRow,"Event Type");
    addHeaderCell(divHeadRow,"Hostname");
    addHeaderCell(divHeadRow,"Network addresses");
    addHeaderCell(divHeadRow,"Last Active");

    for (var i=0;i<Events.length;i++) {
	var Event = [];
	Event = Events[i];
        var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");

        addCell(divRow,Event["date"]);
        addCell(divRow,Event["event_type"]);
	if (Event["computer"]) {
            addCell(divRow,Event["computer"]["hostname"]);
            addCell(divRow,JSON.stringify(Event["computer"]["network_addresses"]));
	}
	else {
            addCell(divRow,"No computer info");
            addCell(divRow,"No computer info");

	}
        addCell(divRow,Event["lastActive"]);
	divTable.appendChild(divRow);

    }

    updateRetCode("OK","Retrieved AMP Events")
    
}

function editSWconfig() {
    var divChild = startEdit();
    var divRow = addCellRow(divChild);
    for (var i=0;i<gl_sw_config.length;i++) {
	divRow = addCellRow(divChild);		
	addCellStatic(divRow,gl_sw_config[i].label);
	addCellInput(divRow,"text",gl_sw_config[i].id,gl_sw_config[i].id,gl_sw_config[i].value);
    }

    divRow = addCellRow(divChild);
    addCellButton(divRow,"Submit","Submit","submit",cbUpdateSWconfig);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);
    updateRetCode("OK","Updated Stealthwatch Configuration")
}
function editISEconfig() {
    var divChild = startEdit();
    var divRow = addCellRow(divChild);
    for (var i=0;i<gl_ise_config.length;i++) {
	divRow = addCellRow(divChild);	
	addCellStatic(divRow,gl_ise_config[i].label);
	addCellInput(divRow,"text",gl_ise_config[i].id,gl_ise_config[i].id,gl_ise_config[i].value);
    }

    divRow = addCellRow(divChild);
    addCellButton(divRow,"Submit","Submit","submit",cbUpdateISEconfig);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);
    updateRetCode("OK","Updated ISE Configuration")
}
function editAMPconfig() {
    var divChild = startEdit();
    
    var divRow = addCellRow(divChild);
    for (var i=0;i<gl_amp_config.length;i++) {
	divRow = addCellRow(divChild);		
	addCellStatic(divRow,gl_amp_config[i].label);
	addCellInput(divRow,"text",gl_amp_config[i].id,gl_amp_config[i].id,gl_amp_config[i].value);
    }

    divRow = addCellRow(divChild);
    addCellButton(divRow,"Submit","Submit","submit",cbUpdateAMPconfig);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);

    updateRetCode("OK","AMP Configuration")
}

function editUMBRELLAconfig() {
    var divChild = startEdit();
    
    var divRow = addCellRow(divChild);
    for (var i=0;i<gl_umbrella_config.length;i++) {
	divRow = addCellRow(divChild);		
	addCellStatic(divRow,gl_umbrella_config[i].label);
	addCellInput(divRow,"text",gl_umbrella_config[i].id,gl_umbrella_config[i].id,gl_umbrella_config[i].value);
    }

    divRow = addCellRow(divChild);
    addCellButton(divRow,"Submit","Submit","submit",cbUpdateUMBRELLAconfig);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);

    updateRetCode("OK","Updated Umbrella Configuration")
}

function addRTCelementSection(rsp,divChild,arr,rspname,divid) {

    var divSectionHolder = document.createElement("div");
    divSectionHolder.setAttribute("id",divid+"Section");
    divSectionHolder.setAttribute("class","divSectionHead");
    
    //    divSectionHolder.setAttribute("class","divSection");
    divChild.appendChild(divSectionHolder);
    for (var i=0;i<arr.length;i++) {
	event = arr[i];
	var divRow = addCellRow(divSectionHolder);
	divRow.setAttribute("class","row")
	description = event["description"];
	id          = event["id"];	
	name = rspname + String(id)
// really stuffy logic because we dont want to store names of events in DB for AMP and SW, since retrievable via API
	if (divid == "umb") {
	    addCellStatic(divRow,event["uname"]+ " /" + id);
	}
	else {
	    addCellStatic(divRow,event["name"]+ " /" + id);
	}
	var eventsConfig = [];
	var penalty = "0";

	try {
	    eventsConfig = rsp[rspname];

	    for (var j=0; j < eventsConfig.length; j++) {
		event = eventsConfig[j];
		if (event["eventid"] == id) {
		    penalty = event["penalty"];
		    break;
		}
	    }
	}
	catch (err) {
	}
	addCellNumber(divRow,name,name,penalty,1,100);	    
    }

    divSectionHolder.style.display = "none";
}
function editRTCconfig(rsp) {
    var divChild = startEdit();

    var divRow = addCellRow(divChild);
//    divRow.setAttribute("class","row")        
    addCellSectionHead(divRow,"Global RTC Options","");
    
    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")        
    addCellStatic(divRow,"RTC Quarantine Threshold");
    rtcThreshold = rsp["rtcThreshold"];
    if (typeof rtcThreshold == 'undefined') {
	rtcThreshold = 100;
    }
    addCellNumber(divRow,"rtcThreshold","rtcThreshold",rtcThreshold,1,100);

    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")    
    addCellStatic(divRow,"RTC ANC Policy Name");
    rtcPolicyName = rsp["rtcPolicyName"];
    if (typeof rtcPolicyName == 'undefined') {
	rtcPolicyName = "Quarantine";
    }
    addCellInput(divRow,"text","rtcPolicyName","rtcPolicyName",rtcPolicyName);    

    
    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")    
    addCellStatic(divRow,"RTC RED Threshold");
    rtcREDThreshold = rsp["rtcREDThreshold"];
    if (typeof rtcREDThreshold == 'undefined') {
	rtcREDThreshold = 100;
    }
    addCellNumber(divRow,"rtcREDThreshold","rtcREDThreshold",rtcREDThreshold,1,100);

    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")        
    addCellStatic(divRow,"RTC ORANGE Threshold");
    rtcORANGEThreshold = rsp["rtcORANGEThreshold"];
    if (typeof rtcORANGEThreshold == 'undefined') {
	rtcORANGEThreshold = 100;
    }
    addCellNumber(divRow,"rtcORANGEThreshold","rtcORANGEThreshold",rtcORANGEThreshold,1,100);

    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")        
    addCellStatic(divRow,"RTC YELLOW Threshold");
    rtcYELLOWThreshold = rsp["rtcYELLOWThreshold"];
    if (typeof rtcYELLOWThreshold == 'undefined') {
	rtcYELLOWThreshold = 100;
    }
    addCellNumber(divRow,"rtcYELLOWThreshold","rtcYELLOWThreshold",rtcYELLOWThreshold,1,100);

    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")        
    addCellStatic(divRow,"RTC WHITE Threshold");
    rtcWHITEThreshold = rsp["rtcWHITEThreshold"];
    if (typeof rtcWHITEThreshold == 'undefined') {
	rtcWHITEThreshold = 100;
    }
    addCellNumber(divRow,"rtcWHITEThreshold","rtcWHITEThreshold",rtcWHITEThreshold,1,100);
    

    

    divRow = addCellRow(divChild);
    addCellSectionHead(divRow,"Umbrella Event Configuration","umb");

    addRTCelementSection(rsp,divChild,gl_umbrella_events,"umbrellaEventsConfig","umb")

    divRow = addCellRow(divChild);
    addCellSectionHead(divRow,"StealthWatch Event Configuration","sw");

    addRTCelementSection(rsp,divChild,gl_sw_events,"swEventsConfig","sw")        

    divRow = addCellRow(divChild);
    addCellSectionHead(divRow,"AMP Event Configuration","amp");

    addRTCelementSection(rsp,divChild,gl_amp_events,"ampEventsConfig","amp")            

    divRow = addCellRow(divChild);
    addCellButton(divRow,"Submit","Submit","submit",cbUpdateRTCconfig);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);

    updateRetCode("OK","RTC Options")
}


function cbUnquarantine(ev1) {
    var name = this.id;
    alert("unquarantine " + name);
    post["MAC"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcUQ.py",post,uqResponse);
    updateRetCode("Wait","Unquarantining")
    
}
function cbQuarantine(ev1) {
    var name = this.id;
    alert("unquarantine " + name);
    post["MAC"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcQ.py",post,qResponse);
    updateRetCode("Wait","Quarantining")
    
}
function cbAMPeventDetails(ev1) {
    var name = this.id;
    post["eventid"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcAMPeventDetails.py",post,openJSONresponse);
    updateRetCode("Wait","Retrieving AMP Event Details")
}
function cbSWeventDetails(ev1) {
    var name = this.id;
    post["eventid"] = name;
    sendXpost(gl_xhr,"/cgi-bin/rtcSWeventDetails.py",post,openJSONresponse);
    updateRetCode("Wait","Retrieving SW Event Details")
}
function cbUMBeventDetails(ev1) {
    var name = this.id;
    post["eventid"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcUMBeventDetails.py",post,openJSONresponse);
    updateRetCode("Wait","Retrieving UMB Event Details")
}

function getHost(mac) {
    for (var i=0;i<gl_hosts.length;i++) {
	host = gl_hosts[i];
	if (mac == host["mac"]) {
	    return host;
	}
    }
    alert("Could not find MAC in host table- should not happen");
    
}
function getUser(username) {
    for (var i=0;i<gl_users.length;i++) {
	user = gl_users[i];
	if (username == user["user"]) {
	    return user;
	}
    }
    alert("Could not find User in user table- should not happen");
    
}

function cbHostDetails(ev1) {
    var name = this.id;
    gl_details = "";
    gl_current_host = getHost(name);
    updateRetCode("Wait","getting host details")
    showHosts(gl_hosts);    
    showHostDetails(host);
    
}
function cbUserDetails(ev1) {
    var name = this.id;
    gl_current_user = getUser(name);
    showUsers(gl_users);
    updateRetCode("Wait","getting user details")
    showUserDetails(user);
    
}

function cbAMPhostDetails(ev1) {
    var name = this.id;
    
    gl_current_host = getHost(name);
    showHosts(gl_hosts);
    AMPhostDetails(gl_current_host);
}
function AMPhostDetails(host) {
    var events = [];    
    try {
	events = host["ampevents"]["events"];
    }
    catch (error) {
	alert("No AMP Events for host " + name);
    }
    if (!events) {
	events = [];
    }
    showAMPdetails(events);
}

function cbAMPuserDetails(ev1) {
    var name = this.id;
    user = getUser(name);
    gl_current_user = user;
    showUsers(gl_users);
    AMPuserDetails(gl_current_user);
    
}
function AMPuserDetails(user) {
    var events = [];
    try {
	events = user["ampevents"]["events"];
	
    }
    catch (error) {
	alert("No AMP Events for user " + name);
    }
    if (!events) {
	events = [];
    }
    showAMPdetails(events);    
}


function cbUMBhostDetails(ev1) {

    var name = this.id;
    gl_current_host = getHost(name);
    showHosts(gl_hosts);    
    UMBhostDetails(gl_current_host);
}

function UMBhostDetails(host) {
    
    var events = [];
    try {
	events = host["umbevents"]["events"];
    }
    catch (error) {
	alert("No AMP Events for host " + name);
    }
    if (!events) {
	events = [];
    }
    showUMBdetails(events);    
}

function cbUMBuserDetails(ev1) {

    var name = this.id;

    gl_current_user = getUser(name);
    showUsers(gl_users);
    UMBuserDetails(user);
    
}
function UMBuserDetails(user) {
    
    var events = [];
    try {
	events = user["umbevents"]["events"];
    }
    catch (error) {
	alert("No UMB Events for user " + name);
    }
    if (!events) {
	events = [];
    }

    
    showUMBdetails(events);    
}

function cbSWhostDetails(ev1) {

    var name = this.id;

    gl_current_host = getHost(name);
    showHosts(gl_hosts);    
    SWhostDetails(gl_current_host);
    
}
function SWhostDetails(host) {
    
    var events = [];
    try {
	events = host["swevents"]["events"];
    }
    catch (error) {
	alert("No SW Events for host " + name);
    }
    if (!events) {
	events = [];
    }
    showSWdetails(events);    
}

function cbSWuserDetails(events) {

    var name = this.id;
    
    gl_current_user = getUser(name);
    showUsers(gl_users);
    SWuserDetails(gl_current_user);
}
function SWuserDetails(user) {
    var events = [];    
    try {
	events = user["swevents"]["events"];
    }
    catch (error) {
	alert("No SW Events for user " + name);
    }
    if (!events) {
	events = [];
    }
    
    showSWdetails(events);    
}


function addCTRarray(arr,events,what) {

    for (var i=0;i<events.length;i++) {
	var event = [];
	var event = events[i];
	var EVENT = event["eventstring"];
	if (arr.includes(EVENT[what])) {
	    
	}
	else {
	    arr.push(EVENT[what]);
	}
    }

}
function buildCTRq(arr,q) {
    for (var i=0;i<arr.length;i++) {
	if (q) {
	    q = q + "%0A" + arr[i];	    
	}
	else {
	    q = arr[i];
	}
    }
    return q

}
function cbCTRhost(ev1) {
    var name = this.id;
    gl_current_host = getHost(name);
    showHosts(gl_hosts);    
    launchCTR(gl_current_host);
}
function cbCTRuser(ev1) {
    var name = this.id;
    gl_current_user = getUser(name);
    showUsers(gl_users);    
    launchCTR(gl_current_user);
}

function launchCTR(host) {
    var CTR_AMP = [];
    var CTR_UMB = [];
    var CTR_SW  = [];
    
    try {
	var events = host["ampevents"]["events"];
    }
    catch (error) {
	var events = [];
    }
    addCTRarray(CTR_AMP,events,"AMP_hash");
    
    try {
	var events = host["umbevents"]["events"];
    }
    catch (error) {
	var events = [];

    }
    addCTRarray(CTR_UMB,events,"UMB_destination");    

    q = "";
    q = buildCTRq(CTR_AMP,q);
    q = buildCTRq(CTR_UMB,q);

    if (q) {
	var CTRlink = "https://visibility.amp.cisco.com/#/investigate?q=" 
	CTRlink = CTRlink + q;
	window.open(CTRlink, '_blank');
    }
    else {
	alert("No CTR observables found for hos " + name);
    }
    
}


function cbDestInfo(ev1) {
    var name = this.id;        
//    alert("AMP hash " + name);
    post["UMB_destination"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcDomain.py",post,domainResponse);
//    sendXpost(gl_xhr,"/cgi-bin/rtcDomain.py",post,openJSONresponse);    
    updateRetCode("Wait","Checking for domain info")

}
function cbFlowInfo(ev1) {

    var name = this.id;
    if (name) {
	post["IP"] = name
	sendXpost(gl_xhr,"/cgi-bin/rtcFLOWs.py",post,FLOWresponse);
        gl_retcode = "Checking for flows for IP " + name
	updateRetCode("Wait",gl_retcode);
	timeGlass();
	
    }
    else {
	alert("IP not found for flow search");
    }
}



function cbUpdateAPI() {
    var post = {};

    for (var i=0;i<gl_config.length;i++) {
	post[(gl_config[i].id)] = document.getElementById(gl_config[i].id).value;
    }
    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateAPI.py",post,updateAPIresponse);
}
function cbUpdateSWconfig() {
    var post = {};

    for (var i=0;i<gl_sw_config.length;i++) {
	post[(gl_sw_config[i].id)] = document.getElementById(gl_sw_config[i].id).value;
    }
    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateSWconfig.py",post,updateSWconfigResponse);
}
function cbUpdateISEconfig() {
    var post = {};

    for (var i=0;i<gl_ise_config.length;i++) {
	post[(gl_ise_config[i].id)] = document.getElementById(gl_ise_config[i].id).value;
    }
    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateISEconfig.py",post,updateISEconfigResponse);
}
function cbUpdateAMPconfig() {
    var post = {};

    for (var i=0;i<gl_amp_config.length;i++) {
	post[(gl_amp_config[i].id)] = document.getElementById(gl_amp_config[i].id).value;
    }
    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateAMPconfig.py",post,updateAMPconfigResponse);
}
function cbUpdateUMBRELLAconfig() {
    var post = {};

    for (var i=0;i<gl_umbrella_config.length;i++) {
	post[(gl_umbrella_config[i].id)] = document.getElementById(gl_umbrella_config[i].id).value;
    }
    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateUMBRELLAconfig.py",post,updateUMBRELLAconfigResponse);
}

function updateRTCelementsArray(arr,prefix) {
    var events = [];
    for (var i=0;i<arr.length;i++) {
	event = {};
	var thisid = String(arr[i].id);
	event["eventid"] = thisid
	try {
	    event["event_name"] = arr[i].uname;
	}
	catch (err) {
	}
	thisid2 = prefix + thisid
	var t  = document.getElementById(thisid2);
	try {
	    event["penalty"] = String(t.value);
	}
	catch (err) {
	    event["penalty"]  = "0"
	    alert("catch" + thisid);
	}
	events.push(event)
    }
    return events;

    
}
function cbUpdateRTCconfig() {
    var post = {};


    post["rtcThreshold"] = document.getElementById("rtcThreshold").value;
    post["rtcREDThreshold"] = document.getElementById("rtcREDThreshold").value;
    post["rtcORANGEThreshold"] = document.getElementById("rtcORANGEThreshold").value;
    post["rtcYELLOWThreshold"] = document.getElementById("rtcYELLOWThreshold").value;
    post["rtcWHITEThreshold"] = document.getElementById("rtcWHITEThreshold").value;            
    post["swEventsConfig"]       = updateRTCelementsArray(gl_sw_events,"swEventsConfig");
    post["umbrellaEventsConfig"] = updateRTCelementsArray(gl_umbrella_events,"umbrellaEventsConfig");    
    post["ampEventsConfig"]      = updateRTCelementsArray(gl_amp_events,"ampEventsConfig");    


    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateConfig.py",post,updateRTCconfigResponse);
}



function sendXpost(xhr,posturl,post,callback) {

/*    var pjson = encodeURIComponent(JSON.stringify(post)); */

    pjson = JSON.stringify(post)
    xhr.open("POST",posturl,true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
	    callback(xhr);
        }
    }
    /*    xhr.send("x=" + pjson); */
   xhr.send( pjson); 

}


