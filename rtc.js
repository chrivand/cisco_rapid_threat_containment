/// ======================================
///  Config Classes
/// =====================================
function Config(config,table,header) {
    this.config  = config;
    this.table = table;
    this.header = header;
    this.getConfigURL = "/cgi-bin/rtcGetXconfig.py";
    this.updateConfigURL = "/cgi-bin/rtcUpdateXconfig.py";
    this.xhr = new XMLHttpRequest();    
}

Config.prototype.getConfig = function() {
    post = {}
    post["table"] = this.table
    post["post"] = {};    
    sendXpost2(this.xhr,this,this.getConfigURL,post,this.getConfigResponse);
}

Config.prototype.editConfig = function() {

    var divChild = startEdit();
    addRow(divChild,this.header,"","divHeaderRow");    
    var divRow = addCellRow(divChild);
    for (var i=0;i<this.config.length;i++) {
	divRow = addCellRow(divChild);		
	addCellStatic(divRow,this.config[i].label);
	if (this.config[i].type == "select") {
	    if (config[i].multiple) {
		addCellMultipleSelection(divRow,this.config[i].id,this.config[i].options,this.config[i].value);		
	    }
	    else {
		addCellSelection(divRow,this.config[i].id,this.config[i].options,this.config[i].value);
	    }
	}
	if (this.config[i].type == "text") {
	    var value = this.config[i].value;
	    if (value == undefined) {
		value = "";
	    }
	    addCellInput(divRow,"text",this.config[i].id,this.config[i].id,value);
	}
	if (this.config[i].type == "label") {
	    var value = this.config[i].value;
	    if (value == undefined) {
		value = "";
	    }
	    addCellStaticRight(divRow,value);
	}
    }
    divRow = addCellRow(divChild);
    addCellButton2(divRow,"Submit","Submit","submit",this.updateConfig,this);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);
    updateRetCode("OK","Updated Configuration")
}

Config.prototype.getConfigResponse = function(xhr,th) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var config = JSON.parse(rsp.configstring);
	for (var i=0;i<th.config.length;i++) {
	    var id = th.config[i].id;
	    th.config[i].value = config[id];
	}
	refreshDynamicOptions(th.table);
    }
    else {
	alert("Error in updating config  parameters " + rsp.rtcResult + rsp.info);
    }
    th.editConfig()
    
}
Config.prototype.updateConfig = function(th) {
    var post = {};
    for (var i=0;i<th.config.length;i++) {
	if (th.config[i].type != "label") {
	    post[(th.config[i].id)] = document.getElementById(th.config[i].id).value;
	}
    }
    var ppost = {}
    ppost["table"] = th.table;
    ppost["post"] = post;
    sendXpost2(th.xhr,th,th.updateConfigURL,ppost,th.getConfigResponse);
}


SWconfig.prototype = Object.create(Config.prototype);
SWconfig.prototype.constructor = SWconfig;

function SWconfig(hostgroups){
    config = [     
	{ "type": "text", "id" :"sw_server","value":"", "label": "SW SERVER" },
	{ "type": "text", "id" :"sw_username","value":"", "label": "SW USERNAME" },	
	{ "type": "text", "id" :"sw_password","value":"", "label": "SW PASSWORD" },
	{  "type": "select", "multiple":10,"id" :"hostgroups","value":[], "label": "SELECT HOST GROUPS","type":"select","options":hostgroups },	
    ];
    
    Config.call(this,config,"swconfig","Stealthwatch Configuration");
}

ISEconfig.prototype = Object.create(Config.prototype);
ISEconfig.prototype.constructor = ISEconfig;

function ISEconfig(){
    config = [     
	{ "type": "text", "id" :"ise_server","value":"", "label": "ISE SERVER" },
	{ "type": "text", "id" :"ise_username","value":"", "label": "ISE USERNAME" },	
	{ "type": "text", "id" :"ise_password","value":"", "label": "ISE PASSWORD" },
	{ "type": "text", "id" :"pxgrid_nodename","value":"", "label": "PXGRID NODE NAME" },
	{ "type": "label","id" :"pxgrid_password","value":"", "label": "PXGRID PASSWORD (SET DYNAMICALLY)" },		
	{ "type": "text", "id" :"pxgrid_client_cert","value":"", "label": "PXGRID CLIENT CERT" },
	{ "type": "text", "id" :"pxgrid_client_key","value":"", "label": "PXGRID CLIENT KEY" },
	{ "type": "text", "id" :"pxgrid_client_key_pw","value":"", "label": "PXGRID CLIENT KEY PASSWORD" },
	{ "type": "text", "id" :"pxgrid_server_cert","value":"", "label": "PXGRID SERVER CERT" }
    ];
    
    Config.call(this,config,"iseconfig","ISE Configuration");
}

AMPconfig.prototype = Object.create(Config.prototype);
AMPconfig.prototype.constructor = AMPconfig;
function AMPconfig(){
    config = [

	{ "type": "text","id" :"amp_api_client_id","value":"", "label": "AMP CLIENT ID" },
	{ "type": "text","id" :"amp_api_key","value":"", "label": "AMP CLIENT KEY" },
	{ "type": "text","id" :"tg_api_key","value":"", "label": "ThreatGrid KEY" }	
    ];
    Config.call(this,config,"ampconfig","AMP Configuration");
}

UMBconfig.prototype = Object.create(Config.prototype);
UMBconfig.prototype.constructor = UMBconfig;
function UMBconfig(){
    config = [
	{ "type": "text","id" :"u_orgid","value":"", "label": "UMBRELLA ORG ID" },
	{ "type": "text","id" :"u_investigate_token","value":"", "label": "UMBRELLA INVESTIGATE" },
	{ "type": "text","id" :"u_enforce_token","value":"", "label": "UMBRELLA ENFORCEMENT" },
	{ "type": "text","id" :"u_secret","value":"", "label": "UMBRELLA SECRET" },
	{ "type": "text","id" :"u_key","value":"", "label": "UMBRELLA KEY" },
    ];
    Config.call(this,config,"umbrellaconfig","Umbrella Configuration");
}

CTRconfig.prototype = Object.create(Config.prototype);
CTRconfig.prototype.constructor = CTRconfig;
function CTRconfig(){
    config = [
	{ "type": "text", "id" :"ctr_api_client_id","value":"", "label": "CTR CLIENT ID" },
	{ "type": "text", "id" :"ctr_api_password","value":"", "label": "CTR PASSWORD" }	
    ];
    Config.call(this,config,"ctrconfig","CTR Configuration");
}
ADconfig.prototype = Object.create(Config.prototype);
ADconfig.prototype.constructor = ADconfig;
function ADconfig(adgroups){
    config = [
	{ "type": "text","id" :"ad_server","value":"", "label": "AD SERVER" },
	{ "type": "text","id" :"ad_base_dn","value":"", "label": "AD BASE DN" },	
	{ "type": "text","id" :"ad_username","value":"", "label": "AD USERNAME" },			
	{ "type": "text", "id" :"ad_password","value":"", "label": "AD PASSWORD" },
	{  "type": "select", "multiple":10,"id" :"ad_groups","value":[], "label": "SELECT AD GROUPS","type":"select","options":adgroups },	

    ];
    Config.call(this,config,"adconfig","Active Directory Configuration");
}


/// ================================
///  Events Classes for AMP, UMB, SW
///=================================
function Events(id,header,key,headings,events) {
    this.id = id;
    this.header = header;
    this.key = key;
    this.headings = headings;
    try {
	this.events = events;
    }
    catch (error) {
	alert("No events for " + this.key);
	this.events = [];
    }
    
}

Events.prototype.showEvents = function() {
    var flowWindow = window.open("rtcreport.html","");

    flowWindow.document.title = "Events";
    gl_bajs_th = this;
    // temp: needing global var gl_bajs_th because inside function below this will refer to window object
    // need to use onload because otherwise window not loaded before reading attributes etc, causing exceptions
    flowWindow.onload = function() {

	var divDetails = buildDivNewWindow(flowWindow,gl_bajs_th.header,gl_bajs_th.id);    
	var divHeadRow = tableHeader(divDetails);
	for (i=0;i< gl_bajs_th.headings.length;i++) {
	    addHeaderCell(divHeadRow,gl_bajs_th.headings[i]);
	}
	var events = gl_bajs_th.events;
	for (var i=0;i<events.length;i++) {
	    var divRow = document.createElement("div");
            divRow.setAttribute("class","divRow3");
	    var event = events[i];
	    gl_bajs_th.eventDetails(divRow,event)
	    divDetails.appendChild(divRow);
	}
    }

}
function AMPevents(id,events){
    Events.call(this,id,"AMP Events","amp",["Details", "Event Time", "Penalty","Event Type","Hash"],events);
}
    
AMPevents.prototype = Object.create(Events.prototype);
AMPevents.prototype.constructor = AMPevents;

AMPevents.prototype.eventDetails = function(divRow,event) {
    var penalty = event["penalty"]
    var AMP = event["eventstring"];
    addCellwCallback3(divRow,"fa fa-binoculars",event["eventid"],cbAMPeventDetails,"View AMP Event Details",this);
    addCell(divRow,AMP["AMP_date"]);
    addCell(divRow,penalty);	
    addCell(divRow,AMP["AMP_event_type"]);
    addCell(divRow,shortString(AMP["observable"]));
}

UMBevents.prototype = Object.create(Events.prototype);
UMBevents.prototype.constructor = UMBevents;

function UMBevents(id,events){
    Events.call(this,id,"Umbrella Events","umb",["Details", "Event Time", "Penalty","Inernal IP","Domain","Category"],events);
}
UMBevents.prototype.eventDetails = function(divRow,event) {
    var penalty = event["penalty"]
    var UMB = event["eventstring"];
    addCellwCallback3(divRow,"fa fa-binoculars",event["eventid"],cbUMBeventDetails,"View Umbrella Event Details",this);
    addCell(divRow,UMB["UMB_datetime"]);
    addCell(divRow,penalty);
    addCell(divRow,UMB["ip"]);
    addCell(divRow,shortString(UMB["UMB_destination"]));
    addCell(divRow,UMB["UMB_category"]);
}

SWevents.prototype = Object.create(Events.prototype);
SWevents.prototype.constructor = SWevents;

function SWevents(id,events){
    Events.call(this,id,"Stealthwatch Events","sw",["Details", "Event Time", "Penalty","Event Type","Source IP","Destination IP","Protocol","Destination Port"],events);
}
SWevents.prototype.eventDetails = function(divRow,event) {

    var penalty = event["penalty"];
    var eventid = event["eventid"];
    var event = event["eventstring"];
    var event_id = event["SW_security_event_ID"];
    var event_type = SW_get_event_name(event_id);

    addCellwCallback3(divRow,"fa fa-binoculars",eventid,cbSWeventDetails,"View SW Event Details",this);
    addCell(divRow,event["SW_first_active"]);
    addCell(divRow,penalty);
    addCell(divRow,event_type);
    addCell(divRow,event["SW_source_IP"]);
    addCell(divRow,event["SW_destination_IP"]);
    addCell(divRow,event["SW_destination_protocol"]);
    addCell(divRow,event["SW_destination_port"]);		
}


/// ===============================
///  Stored Events Classes
///================================
function StoredEvents(icon,key,getEventsURL,headings,header) {
    this.icon = icon
    this.key = key;
    this.getEventsURL  = getEventsURL;
    this.headings = headings;
    this.header = header;
    this.xhr = new XMLHttpRequest();    
    this.events = [];
    this.updatetime = ""
    this.loadedEvents = false;
}


StoredEvents.prototype.getEvents = function(recurring) {
    post = {}
    post["recurring"] = recurring;    
    sendXpost2(this.xhr,this,this.getEventsURL,post,this.getEventsResponse);
}

StoredEvents.prototype.edit = function() {
    gl_view = this.key;    
    if (this.updatetime) {
	gl_retcode = "Last updated : "  + this.updatetime;
	updateRetCode("OK",gl_retcode)    
	if (isEmpty(this.current_item)) {
	    this.current_item = this.items[0];
	}
	this.showItems()
	/*
	if (this.current_item) {
	    this.showItemDetails(this.current_item)
	}
	*/
    }
    else {
	alert("Events not retrieved yet, application still initializing")
    }
}
StoredEvents.prototype.getEventsResponse = function(xhr,th) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	th.items = rsp.items;
	if (th.items.length > 0) {
	    if (isEmpty(th.current_item)) {
		th.current_item = th.items[0];
	    }
	}
	if ( (rsp["recurring"]) || (th.updatetime == "")) {
	    // do not update screen when not initiated by menu click, recurring updates and first time
	    var d = new Date();
	    th.updatetime = d.toString();
	    th.timer(th);
	    if (gl_view == th.key) {
		th.edit();
		/*
		if (th.detailsView == "amp") {
		    th.ampEvents.showEvents();
		}
		if (th.detailsView == "umb") {
		    th.umbEvents.showEvents();
		}
		if (th.detailsView == "sw") {
		    th.swEvents.showEvents();
		}
		*/
	    }
	}
	else {
	    // we come here through click
	    gl_view = th.key;
	    th.edit();
	}
    }

    else {
	alert("Error in getting Items" + rsp.rtcResult + rsp.info);
    }
}
StoredEvents.prototype.showItems = function() {

    var divTable  = buildTable2();

    addRow(divTable,this.header,"","divHeaderRow");        
    var divHeadRow = tableHeader(divTable);

    for (var i=0;i<this.headings.length;i++) {
	addHeaderCell(divHeadRow,this.headings[i]);            
    }
    for (var i=0;i<this.items.length;i++) {
	var divRow = this.showItem(this.items[i]);
	divTable.appendChild(divRow);		
    }

}
StoredEvents.prototype.getItem = function(id) {
   for (var i=0;i<this.items.length;i++) {
	var item = this.items[i];
        if (id == item[this.key]) {
	    this.current_item = item;
	    this.showItems();
	    return item
	}
   }
    return null;
   
}
StoredEvents.prototype.showItemDetails = function(item) {
    
}

StoredEvents.prototype.cbDetails = function(th,id) {
    var item = th.getItem(id);
    if (item) {
	th.showItemDetails(item);
    }
    else {
	alert("Could not find item in items table- should not happen");
    }
}

StoredEvents.prototype.cbFlowInfo = function(th,id) {

    alert("Getting flow currently only supported for stored IPs");
    var name = this.id;    
    return;
}

StoredEvents.prototype.cbPurge = function(th,id) {
    alert("Purging " + th.key  + " " + id);
    post["type"] = th.key
    post["name"] = id  
    sendXpost2(th.xhr,th,"/cgi-bin/rtcPurgeItem.py",post,th.purgeResponse);
}
StoredEvents.prototype.purgeResponse = function(xhr,th) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Purge Successful");		
    }
    else {
	alert("Error in Purge" + rsp.rtcResult + rsp.info);
    }
}


StoredEvents.prototype.uqResponse = function(xhr,th) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Unquarantine/Quarantine Successful");		
    }
    else {
	alert("Error in Quarantine/Unqurantining" + rsp.rtcResult + rsp.info);
    }
}

StoredEvents.prototype.cbCTR = function(th,id) {
    var item = th.getItem(id);
    if (item) {
	launchCTR(item);
    }
    else {
	alert("Could not find item in items table- should not happen");
    }
}
StoredEvents.prototype.cbAMPdetails = function(th,id) {
    var item = th.getItem(id);
    if (item) {
	th.ampEvents = new AMPevents(id,item["ampevents"]["events"])
	th.ampEvents.showEvents();
	th.detailsView = "amp";	
    }
    else {
	alert("Could not find item in items table- should not happen");
    }
}
StoredEvents.prototype.cbUMBdetails = function(th,id) {
    var item = th.getItem(id);
    if (item) {
	th.umbEvents = new UMBevents(id,item["umbevents"]["events"])
	th.umbEvents.showEvents();
	th.detailsView = "umb";		
    }
    else {
	alert("Could not find item in items table- should not happen");
    }
}

StoredEvents.prototype.cbSWdetails = function(th,id) {
    var item = th.getItem(id);
    if (item) {
	th.swEvents = new SWevents(id,item["swevents"]["events"])
	th.swEvents.showEvents();
	th.detailsView = "sw";			
    }
    else {
	alert("Could not find item in items table- should not happen");
    }
}

StoredEvents.prototype.timer = function(th) {
     th.timeglass = window.setTimeout(function(){ th.cbTimer(th)},10000);
}
StoredEvents.prototype.cbTimer = function(th) {
    // todo tocheck with the below enabled rtcFLOWs.py response does not get processed????
    th.getEvents(true);
    
}
StoredEvents.prototype.stopTimer = function(th) {
    window.clearTimeout(th.timeglass)
    gl_timeglass = null;
}
StoredEvents.prototype.cbQuarantineNotSupported = function(th,id) {
    alert("Quarantine/Unquarantine for " + th.key + " is currently not supported");
}

StoredEvents.prototype.addQuarantineCell = function(divRow,item) {
	    addCellwCallback3(divRow,"fa fa-times","",this.cbQuarantineNotSupported,"Not Supported",this);
}
StoredEvents.prototype.getIcon = function(item) {
    return this.icon;
}


StoredEvents.prototype.showItem = function(item) {

    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow3");
    if (item[this.key] == this.current_item[this.key]) {
	divRow.style.backgroundColor = "blueviolet";
    }
    penalty = item["penalty"];
    color = getColor(penalty);
    addCell(divRow,penalty,color);
    this.addQuarantineCell(divRow,item);
    addCellwCallback3(divRow,"fas fa-binoculars",item[this.key],this.cbCTR,"Launch CTR",this)

    // insert AMP events
    if (item["ampevents"]["rtcResult"] == "OK") {    
	var ampevents = item["ampevents"]["events"];
	if (ampevents.length > 0) {
	    addCellwCallback3(divRow,"fa fa-infinity",item[this.key],this.cbAMPdetails,"AMP Events",this);
	}
	else {
	    addCell(divRow,"","")
	}
    }
    else {
	addCellwCallback3(divRow,"fa fa-times",item[this.key],this.cbUMBdetails,"AMP DB Error",this);
    }

    // insert UMB events
    if (item["umbevents"]["rtcResult"] == "OK") {
	var umbevents = item["umbevents"]["events"];
	if (umbevents.length > 0) {
	    addCellwCallback3(divRow,"fa fa-umbrella",item[this.key],this.cbUMBdetails,"UMB Events",this);
	}
	else {
	    addCell(divRow,"","")
	}
    }
    else {
	addCellwCallback3(divRow,"fa fa-times",item[this.key],this.cbUMBdetails,"UMB DB Error",this);
    }


    // SW events
    if (item["swevents"]["rtcResult"] == "OK") {    
	var swevents = item["swevents"]["events"];
	if (swevents.length > 0) {
	    addCellwCallback3(divRow,"fas fa-arrow-alt-circle-up",item[this.key],this.cbSWdetails,"SW Events",this)
	}
	else {
	    addCell(divRow,"","")
	}
    }
    else {
	addCellwCallback3(divRow,"fa fa-times",item[this.key],this.cbUMBdetails,"SW DB Error",this);
    }
    
    addCellwCallback3(divRow,"fas fa-arrows-alt",item[this.key],this.cbFlowInfo,"Flow Info",this);			    
    addCellwCallback3(divRow,this.getIcon(item),item[this.key],this.cbDetails,"Details",this);    
    addCellwCallback2(divRow,item[this.key],this.cbDetails,this);
    addCellwCallback3(divRow,"fas fa-trash-alt",item[this.key],this.cbPurge,"Purge",this);			

    return(divRow);	
}

function MACsStoredEvents(){
    
    StoredEvents.call(this,"fas fa-desktop","mac","/cgi-bin/rtcGetMACs.py",[" Penalty","ANC","CTR","AMP","UMB","SW","Flows","Device","MAC","Purge"],"Hosts/MAC addresses");
}
    
MACsStoredEvents.prototype = Object.create(StoredEvents.prototype);
MACsStoredEvents.prototype.constructor = MACsStoredEvents;


MACsStoredEvents.prototype.getIcon = function(item) {
    var icon = "fa fa-question-circle"
    try {
	profile = item["ise"]["endpointProfile"]
    }
    catch (error) {
        profile = "-"
    }
    if (profile.startsWith("Win")) {
	icon = "fab fa-windows"
    }
    if (profile.startsWith("Mac")) {
        icon = "fab fa-apple"
    }
    return icon;
}

MACsStoredEvents.prototype.addQuarantineCell = function(divRow,item) {
	if (item["ancpolicy"] == gl_rtc_config["rtcPolicyName"]) {
	    addCellwCallback3(divRow,"fa fa-lock",item["mac"],this.cbUnquarantine,"Unquarantine",this);
	}
	else {
	    addCellwCallback3(divRow,"fa fa-unlock",item["mac"],this.cbQuarantine,"Quarantine",this);	    
	}
}
MACsStoredEvents.prototype.cbQuarantine = function(th,id) {
    alert("unquarantine " + id);
    post["MAC"] = name
    sendXpost2(th.xhr,"/cgi-bin/rtcQ.py",post,this.uqResponse);
    updateRetCode("Wait","Quarantining")
}
MACsStoredEvents.prototype.cbUnquarantine = function(th,id) {

    alert("unquarantine " + name);
    post["MAC"] = name
    sendXpost2(gl_xhr,"/cgi-bin/rtcUQ.py",post,this.uqResponse);
    updateRetCode("Wait","UnQuarantining")
}


MACsStoredEvents.prototype.showItemDetails = function(host) {
    if (host === undefined) {
	return;
    }
    var flowWindow = window.open("rtcreport.html","");
    flowWindow.onload = function() {

	flowWindow.document.title = "User details for " + host["mac"];
	var divDetails = buildDivNewWindow(flowWindow,"MAC ",host["mac"]);    
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

	addRow(divDetails,"User",username);        
	try {
	    var ipAddress = host["ise"]["ipAddresses"][0];
	}
	catch (err) {
	    var ipAddress = "";
	}
    
	addRow(divDetails,"IP",ipAddress);        
	try {
	    var endpointProfile = host["ise"]["endpointProfile"];
	}
	catch (err) {
	    var endpointProfile = "";
	}
	addRow(divDetails,"Profile",endpointProfile);            

	try {
	    var sgt = host["ise"]["ctsSecurityGroup"];
	}
	catch
	    (err) {
		var sgt = "";
	    }
	addRow(divDetails,"SGT",sgt);            

	try {
	    var hostname = host["amp"]["data"][0]["hostname"];
	}
	catch (err) {
	    var hostname = "";
	}
	addRow(divDetails,"Hostname",hostname);            
	try {
	    var os = host["amp"]["data"][0]["operating_system"];
	}
	catch (err) {
	    var os = "";
	}
	addRow(divDetails,"OS",os);                
	try {
	    var nas = host["ise"]["nasIpAddress"];
	}
	catch (err) {
	    var nas = "";
	}
	addRow(divDetails,"Device",nas);                
	try {
	    var nasport = host["ise"]["nasPortId"];
	}
	catch (err) {
	    var nasport = "";
	}
	addRow(divDetails,"Interface",nasport);

    }

}

function UsersStoredEvents(){
    StoredEvents.call(this,"fas fa-user","user","/cgi-bin/rtcGetUsers.py",[" Penalty","Quarantine"," CTR","AMP","UMB","SW","Flows","Details","Username","Purge"],"Users");
}
    
UsersStoredEvents.prototype = Object.create(StoredEvents.prototype);
UsersStoredEvents.prototype.constructor = UsersStoredEvents;

UsersStoredEvents.prototype.showDetails = function() {

    divDetails = buildDivNewWindow(newwin,"","") 
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
}
UsersStoredEvents.prototype.showItemDetails = function(user) {
    if (user === undefined) {
	return;
    }
    var flowWindow = window.open("rtcreport.html","");
    flowWindow.onload = function() {

	flowWindow.document.title = "User details for " + user["user"];
	var divDetails = buildDivNewWindow(flowWindow,"User ",user["user"]);    
    
	addRow(divDetails,"Username" ,user["user"]);
	addRow(divDetails,"Mail" ,user["ad_info"]["mail"]);
	var memberofs = user["ad_info"]["memberOf"];
	for (var i=0;i<memberofs.length;i++) {
	    addRow(divDetails,"MemberOf" ,memberofs[i]);	
	}
	addRow(divDetails,"Last Bad Password",user["ad_info"]["badPasswordTime"]);
	addRow(divDetails,"Bad Password Count",user["ad_info"]["badPwdCount"]);        
	addRow(divDetails,"Last Logon",user["ad_info"]["lastLogon"]);    
    }
}

function HostnamesStoredEvents(){
    StoredEvents.call(this,"fas fa-desktop","hostname","/cgi-bin/rtcGetHostnames.py",[" Penalty","Isolated"," CTR","AMP","UMB","SW","Flows","Details","Hostnames","Purge"],"Hostnames");
}
    
HostnamesStoredEvents.prototype = Object.create(StoredEvents.prototype);
HostnamesStoredEvents.prototype.constructor = HostnamesStoredEvents;


HostnamesStoredEvents.prototype.addQuarantineCell = function(divRow,item) {

    if (item["isolationavailable"]) {
	if (item["isolation"] == "isolated") {
	    addCellwCallback3(divRow,"fa fa-lock",item["guid"],cbStopIsolation,"Stop Isolation",this);
	}
        else {
    	    if (item["isolation"] == "not_isolated") {
		addCellwCallback3(divRow,"fa fa-unlock",item["guid"],cbStartIsolation,"Start Isolation",this);
	    }
	    else {
    		if (item["isolation"] == "pending_start") {		    
		    addCellwCallback3(divRow,"fa fa-question-circle",item["guid"],cbInProgress,"Endpoint isolation starting",this);
		}
		else {
		    if (item["isolation"] == "pending_stop") {		    
			addCellwCallback3(divRow,"fa fa-question-circle",item["guid"],cbInProgress,"Endpoint isolation stopping",this);
		    }
		    else {
			addCellwCallback3(divRow,"fa fa-question-circle",item["guid"],cbInProgress,"Endpoint isolation unknown",this);
		    }
		}
	    }
        }
    }
    else {
	addCellwCallback3(divRow,"fa fa-remove",item["guid"],cbNotCapable,"Client not capable of isolation",this);
    }
    return (divRow);
}


HostnamesStoredEvents.prototype.showDetails = function() {
    var divChild = document.getElementById("divChild");
    var divOld = document.getElementById("divDetails");
    var divDetails = document.createElement("div");
    divDetails.setAttribute("class","divDetails");
    divDetails.setAttribute("id","divDetails");

    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");

    var hostname = hostname["hostname"]

    addCellStatic(divRow,"Hostname",true);
    addCellStaticRight(divRow,hostname);
    divDetails.appendChild(divRow);

    divChild.replaceChild(divDetails,divOld);
}

function IPsStoredEvents(){
    StoredEvents.call(this,"fas fa-desktop","ip","/cgi-bin/rtcGetIPs.py",[" Penalty","ANC"," CTR","AMP","UMB","SW","Flows","Details","IP","Purge"],"IP Addresses");
}
IPsStoredEvents.prototype = Object.create(StoredEvents.prototype);
IPsStoredEvents.prototype.constructor = IPsStoredEvents;


IPsStoredEvents.prototype.cbFlowInfo = function(th,id) {

    if (id) {
	th.xhr_flows = new XMLHttpRequest();    	
	post["IP"] = id
	sendXpost2(th.xhr_flows,th,"/cgi-bin/rtcFLOWs.py",post,th.FLOWresponse);
        gl_retcode = "Checking for flows for IP " + id
	updateRetCode("Wait",gl_retcode);
	timeGlass();
    }
    else {
	alert("IP not found for flow search");
    }
}
IPsStoredEvents.prototype.FLOWresponse = function(xhr,th) {
    stopTimeGlass();
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
        showFlows(rsp);
        updateRetCode("OK","Retrieved flows");
    }
    else {
        alert("Error in receiving flows" + rsp.rtcResult + rsp.info);
    }
}


/// =====================================================
///    API Search Objects
/// ====================================================
function SearchAPI(getEventsURL,headings,header) {
    this.getEventsURL  = getEventsURL;
    this.header = header
    this.headings = headings;
    this.xhr = new XMLHttpRequest();
    this.days = 0;
    this.hours = 1;
    this.minutes = 1;
}

SearchAPI.prototype.searchOptions = function() {
    
    var divChild = startEdit();
    addRow(divChild,this.header,"","divHeaderRow");
    
    var divRow = addCellRow(divChild);
    addCellStatic(divRow,"Search Constraints");    
    divRow = addCellRow(divChild);
    addCellStatic(divRow,"DAYS");
    addCellNumber(divRow,"days","days",this.days,0,3);

    divRow = addCellRow(divChild);
    addCellStatic(divRow,"HOURS");
    addCellNumber(divRow,"hours","hours",this.hours,0,23);

    divRow = addCellRow(divChild);
    addCellStatic(divRow,"MINUTES");
    addCellNumber(divRow,"minutes","minutes",this.minutes,0,59);	    

    divRow = addCellRow(divChild);
    addCellButton2(divRow,"Submit","Search API","submit",this.cbSearchAPI,this);
    addCellButton(divRow,"Cancel","Cancel","submit",mAbout);
}

SearchAPI.prototype.cbSearchAPI = function(th) {

    var post = {};
    th.days = document.getElementById("days").value;
    post["days"] = th.days;
    th.hours = document.getElementById("hours").value;
    post["hours"] = th.hours;
    th.minutes = document.getElementById("minutes").value;            
    post["minutes"] = th.minutes;
    sendXpost2(th.xhr,th,th.getEventsURL,post,th.getEventsResponse);
    gl_retcode = "Retrieving events,please wait...";
    updateRetCode("Wait",gl_retcode);
    timeGlass();
    
}

SearchAPI.prototype.getEventsResponse = function(xhr,th) {

    stopTimeGlass();
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult != "OK") {
	alert("Error :" + rsp.rtcResult);
	return
    }
    th.items = rsp.events;
    var divTable = buildTable()
    var divHeadRow = document.createElement("div");
    divHeadRow.setAttribute("class","divHeadRow");
    divTable.appendChild(divHeadRow);

    for (var i=0;i<th.headings.length;i++) {
	addHeaderCell(divHeadRow,th.headings[i]);            
    }
    for (var i=0;i<th.items.length;i++) {
	var divRow = th.showItem(th.items[i]);
	divTable.appendChild(divRow);
    }
    updateRetCode("OK","Retrieved Events")
    
}
function AMPsearchAPI(){
    SearchAPI.call(this,"/cgi-bin/rtcAMPevents.py",["Date","Event Type","Hostname","Username","Network Addresses","Last Active"],"AMP Events");
}
AMPsearchAPI.prototype = Object.create(SearchAPI.prototype);
AMPsearchAPI.prototype.constructor = AMPsearchAPI;

AMPsearchAPI.prototype.showItem = function(item) {
    Event = item;
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow3");

    addCell(divRow,Event["date"]);
    addCell(divRow,Event["event_type"]);
    if (Event["computer"]) {
	addCell(divRow,Event["computer"]["hostname"]);
        addCell(divRow,Event["computer"]["user"]);
        addCell(divRow,JSON.stringify(Event["computer"]["network_addresses"]));
    }
    else {
        addCell(divRow,"No info");
        addCell(divRow,"No info");
        addCell(divRow,"No info");	    
    }
    addCell(divRow,Event["lastActive"]);
    return(divRow);
}

function SWsearchAPI(){
    SearchAPI.call(this,"/cgi-bin/rtcSWevents.py",["Event ID","Event Type","First Active","Last Active","Source IP","Source Port","Source Protocol","Source Tag Type","Target IP","Target Port","Target Protocol","Target Tag Type","Hit Count"],"Stealthwatch Events");
}

SWsearchAPI.prototype = Object.create(SearchAPI.prototype);
SWsearchAPI.prototype.constructor = SWsearchAPI;

SWsearchAPI.prototype.showItem = function(item) {
	var swEvent = item
        var divRow = document.createElement("div");
        divRow.setAttribute("class","divRow3");
        addCell(divRow,swEvent["id"]);
        var event_id = swEvent["securityEventType"];
	var event_type = SW_get_event_name(event_id);
        addCell(divRow,event_type);	
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
	return(divRow);
}

function UMBsearchAPI(){
    SearchAPI.call(this,"/cgi-bin/rtcUMBRELLAevents.py",["Internal IP","External IP","Categories","Destination","Action Taken","Date"],"Umbrella Events");
}

UMBsearchAPI.prototype = Object.create(SearchAPI.prototype);
UMBsearchAPI.prototype.constructor = UMBsearchAPI;

UMBsearchAPI.prototype.showItem = function(item) {
    Event = item
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow3");

    addCell(divRow,Event["internalIp"]);
    addCell(divRow,Event["externalIp"]);
    addCell(divRow,JSON.stringify(Event["categories"]));
    addCell(divRow,Event["destination"]);
    addCell(divRow,Event["actionTaken"]);
    addCell(divRow,Event["datetime"]);
    return(divRow);
}
///
///    Functions using objects above
///

function getStarted() {

    // global xhr requests

    gl_timeelapsed = 0;
    gl_rtcconfig_xhr = new XMLHttpRequest();
    gl_rtcprocess_xhr = new XMLHttpRequest();
    gl_rtcstart_xhr = new XMLHttpRequest();
    gl_xhr = new XMLHttpRequest();                

    
    gl_sw_config = new SWconfig([]);
    gl_ise_config = new ISEconfig();
    gl_amp_config = new AMPconfig();
    gl_umb_config = new UMBconfig();
    gl_ctr_config = new CTRconfig();
    gl_ad_config = new ADconfig([]);

    gl_mac_stored_events = new MACsStoredEvents();
    gl_mac_stored_events.getEvents(false);
    gl_users_stored_events = new UsersStoredEvents(false);
    gl_users_stored_events.getEvents(false);
    gl_hostnames_stored_events = new HostnamesStoredEvents(false);
    gl_hostnames_stored_events.getEvents(false);
    gl_IPs_stored_events = new IPsStoredEvents();
    gl_IPs_stored_events.getEvents(false);

    gl_AMP_search_api = new AMPsearchAPI();
    gl_SW_search_api = new SWsearchAPI();
    gl_UMB_search_api = new UMBsearchAPI();        

    var rtcconfig_xhr =  new XMLHttpRequest();
    var post = {"table":"rtcconfig"}
    sendXpost(rtcconfig_xhr,"/cgi-bin/rtcGetXconfig.py",post,updateRTCconfigResponse);
    gl_reading_rtcconfig = true;
    
    // global views

    gl_ise_anc_policies = [];
    gl_sw_events = [];
    gl_sw_hostgroups = [];
    gl_amp_events = [];
    gl_adgroups = [];
    gl_umbrella_events = [
	{ "id" : 0, "uname" : "Command and Control", "description" : "Client communicated to Command and Control Domain" },
	{ "id" : 1, "uname" : "Cryptomining", "description" : "Client communicated to Crypto miningDomain" },	
    ];

    gl_retcode = "";
    gl_rtc_config = {};

    mAbout();    
    refreshDynamicOptions("all")

    gl_retcode = "";
    updateRetCode("OK",gl_retcode)    

    gl_view = "";
    

}
function refreshDynamicOptions(item) {
    var event_types_xhr = new XMLHttpRequest();    
    post = {}
    post = {"item":item}        
    sendXpost(event_types_xhr,"/cgi-bin/rtcGetDynamicOptions.py",post,dynamicOptionsResponse);
}

function dynamicOptionsResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var item = rsp.item;
	// item check

	if ( (item == "adconfig") || (item == "all")) {
	    var adgroups = rsp["ADgroups"];
	    gl_ad_config = new ADconfig(adgroups);
	}

	if ( (item == "swconfig") || (item == "all")) {
	    try {
		var events = rsp["swEvents"]["data"];
		var hostGroups = rsp["swHostGroups"]["data"];
	    }
	    catch (err) {
		events = {};
	    }
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
	    if (hostGroups) {
		var gl_sw_hostgroup_names = [];
		for (var i=0;i<hostGroups.length;i++) {
		    hostGroup = hostGroups[i];
		    var t_hostGroup = {};
		    t_hostGroup["name"] = hostGroup["name"];
		    t_hostGroup["id"] = hostGroup["id"];
		    if (t_hostGroup["id"] < 60000) {
			gl_sw_hostgroups.push(t_hostGroup);
			gl_sw_hostgroup_names.push(t_hostGroup["name"]);
		    }

		}
		new SWconfig(gl_sw_hostgroup_names);
	    }
	}

	if ( (item == "ampconfig") || (item == "all")) {	
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
	if ( (item == "iseconfig") || (item == "all")) {
	    try {
		var ancpolicies = rsp["isePolicies"]["SearchResult"]["resources"];
		gl_ise_anc_policies = [];
		for (var i=0;i<ancpolicies.length;i++) {
		    gl_ise_anc_policies.push(ancpolicies[i].name);
		}
	    }
	    catch (err) {}
	}
    }	
    else {
	    alert("Error Dynamic Options " + item + " " +  rsp.rtcResult + rsp.info);
    }

}

//
//  Helper Functions
//
function isEmpty(obj) {
    if (obj)
	return Object.keys(obj).length === 0;
    else
	return true
    
}

function shortString(s) {
    shorter = s
    if (s) {
	if (s.length > 20) {
	    shorter = s.substring(0,15) + "...";
//	endstr  = s.substring((s.length-5),4);
//	alert(s.length-5);
//	alert(endstr);
	    shorter = shorter;
	}
	return shorter
    }
    else {
	return ""
    }
    
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
function catchEvent2(eventObj, event, eventHandler,th,id) {
    if (eventObj.addEventListener) {
        eventObj.addEventListener(event, function eh() {eventHandler(th,id)}, false);
    }
    else if (eventObj.attachEvent) {
        event = "on" + event;
        eventObj.attachEvent(event, function eh() {eventHandler(th,id)});
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

    divChild.appendChild(divTable);
    
    return divTable;

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
function buildDivNewWindow(newwin,t1,t2) {
/// wait for window to load

    var divChild = newwin.document.getElementById("divChild");	
    var newDiv = newwin.document.createElement("div");
    newDiv.setAttribute("class","divDetails");
    newDiv.setAttribute("id","divDetails");
    addRow(divChild,t1,t2,"divHeaderRow");
    divChild.appendChild(newDiv);
    return newDiv;
}

function addRow(divDetails,left,right,cssclass="divRow3") {
    var divRow = document.createElement("div");
    divRow.setAttribute("class",cssclass);
    addCellStatic(divRow,left,true);
    addCellStaticRight(divRow,right);
    divDetails.appendChild(divRow);    

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

    if (typeof(text) == "undefined") {
	text = "";
    }
    var divHeader = document.createElement("div");
    if (color) {
	divHeader.style.backgroundColor = color;
    }
    divHeader.setAttribute("class","divCell");
    var txt = document.createTextNode(text);
    divHeader.appendChild(txt);
    divRow.appendChild(divHeader);

}
function addCellwCallback2(divRow,text,callback,th) {

    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divCell");
    divHeader.setAttribute("id",text);    
    var txt = document.createTextNode(text);
    catchEvent2(divHeader,"click",callback,th,text);
    divHeader.appendChild(txt);
    divRow.appendChild(divHeader);

}
function addCellwCallback3(divRow,iconClass,id,callback,tooltiptext,th) {


    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divCell");
    divHeader.setAttribute("id",id);
    catchEvent2(divHeader, "click", callback,th,id);    
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
function addCellSelection(divRow,id,options,selectedname) {
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
    if (selectedname) {
	select.value = selectedname;
    }
    divSel.appendChild(select);
    divRow.appendChild(divSel);
}

function addCellMultipleSelection(divRow,id,options,selection) {
    var divSel = document.createElement("div");
    divSel.setAttribute("class","col-75");
    var select = document.createElement("select");
    select.setAttribute("id",id);    
    select.setAttribute("multiple","multiple");
    select.setAttribute("size",10);
    for (i=0;i<options.length;i++) {
        option =  document.createElement("option");
        option.value = options[i];
        option.textContent = options[i];
	if (selection.includes(options[i])) {
	    option.setAttribute("selected",true);
	}
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
    //    divRow.setAttribute("class","divrow");
    divRow.setAttribute("class","row");    
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

function addFileInput(divRow,id,accept) {
    var input = document.createElement("input");
    input.setAttribute("type","FILE");
    input.setAttribute("id",id);
    input.setAttribute("accept",accept);    
    divRow.appendChild(input);
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
function addCellButton2(divRow,id,label,type,callback,th) {


    var btnAdd = document.createElement("input");
    btnAdd.setAttribute("type", type);
    btnAdd.setAttribute("value", label);
    btnAdd.setAttribute("id", id);
    catchEvent2(btnAdd, "click", callback,th);

    var divHeader = document.createElement("div");
    divHeader.setAttribute("class","divButton");
    divHeader.appendChild(btnAdd);
    divRow.appendChild(divHeader);

}

//
//  Menu Callbacks
//
function mAbout() {

    gl_view = "";
    var t = "Mice Control - A revolutionary system for Rapid Threat Containment of Evil Rats. Powered by cats.py<br><br>";
    t = t+ '<img src="about.jpg"></img><br><br>';
    t = t+ "Copyright &copy 1997-2018";
    displayText(t);
    updateRetCode("OK","About RTC");
}
function cbResetRTCevents() {

    post = {"fullreset":false};
    sendXpost(gl_xhr,"/cgi-bin/rtcResetDB.py",post,resetDBresponse);
    updateRetCode("Wait","Resetting Events");
}
function cbCreateDatabase() {

    post = {"fullreset":true};
    sendXpost(gl_xhr,"/cgi-bin/rtcResetDB.py",post,resetDBresponse);
    updateRetCode("Wait","Recreating Database");
}

function mRTCdatabase() {

    var divTable = buildTable2();
    addRow(divTable,"Reset Database","","divHeaderRow");                
/*    var divHeadRow = tableHeader(divTable);	
    divTable.appendChild(divHeadRow); */
    var divRow = document.createElement("div");
    divRow = addCellRow(divChild);    
    addCellButton(divRow,"Reset Events","Reset Events","submit",cbResetRTCevents);
    addCellButton(divRow,"(Re)Create Database","(Re)Create Database","submit",cbCreateDatabase);        
    divTable.appendChild(divRow);    
}

function cbBackupConfig() {
    gl_view = "";
    var post = {};
    post = {"table":""}    
    sendXpost(gl_rtcprocess_xhr,"/cgi-bin/rtcGetXconfig.py",post,rtcBackupResponse);
    updateRetCode("Wait","Getting RTC Config Backup");
}

function mRTCbackup() {

    var divTable = buildTable2();
    addRow(divTable,"RTC Backup","","divHeaderRow");                    
    var divHeadRow = tableHeader(divTable);
    addHeaderCell(divHeadRow,"Enter Backup JSON file");
    divTable.appendChild(divHeadRow);
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow3");
	
//    addFileInput(divRow,"restorefile","text/plain");
    addFileInput(divRow,"restorefile","text/json");    
    divTable.appendChild(divRow);	    
    divRow = addCellRow(divChild);    
    addCellButton(divRow,"Backup Config","Backup Config","submit",cbBackupConfig);
    addCellButton(divRow,"Restore Config","Restore Config","submit",cbRestoreConfig);        
    divTable.appendChild(divRow);    
}

function rtcRestoreResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Restored Config");	
    }
    else {
	alert(rsp.rtcResult);
	updateRetCode("Error","Could not Restore Config");		
    }
}

function cbRestoreConfig() {
    var input = document.getElementById("restorefile");
    const file = input.files.item(0);
    if (file == null) {
	alert("No file selected!");
	return;
    }
    const reader = new FileReader();
    reader.onload = function(event) {
	try {
	    var contents = event.target.result;
	    var config = JSON.parse(contents);
	    var post = {};
	    post["config"] = config;
	    sendXpost(gl_rtcprocess_xhr,"/cgi-bin/rtcRestoreConfig.py",post,rtcRestoreResponse);
	    updateRetCode("Wait","Restoring config");
	    
	}
	catch (err) {
	    alert("Unable to parse file");
	}
    }
    reader.onerror = function(event) {
	alert("File could not be read! Code " + event.target.error.code);
    }
    reader.readAsText(file);
}
function mRTCprocess() {
    gl_view = "";
    post = {};
    sendXpost(gl_rtcprocess_xhr,"/cgi-bin/rtcGetProcess.py",post,rtcGetProcessResponse);
    updateRetCode("Wait","Getting RTC Process status");
}

function cbStartRTC() {

    var post = {};
    var amploglevel= document.getElementById("amploglevel").value;
    post["amploglevel"] = amploglevel;
    var umbloglevel= document.getElementById("umbloglevel").value;
    post["umbloglevel"] = umbloglevel;
    var swloglevel= document.getElementById("swloglevel").value;
    post["swloglevel"] = swloglevel;

    sendXpost(gl_rtcstart_xhr,"/cgi-bin/rtcStart.py",post,rtcStartResponse);
    updateRetCode("Wait","Starting RTC: Wait...");
    window.setTimeout(mRTCprocess,2000);
}
function cbViewLogs() {

    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcViewLogs.py",post,rtcViewLogsResponse);
    updateRetCode("Wait","Fetching RTC Logs");
}
function cbDeleteLogs() {

    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcDeleteLogs.py",post,rtcDeleteLogsResponse);
    updateRetCode("Wait","Fetching RTC Logs");
}

function cbStopRTC() {

    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcStop.py",post,rtcStopResponse);
    updateRetCode("Wait","Stopping RTC");
}

function viewRTClogs(rsp) {

    var logs = []
    var processes = []    
    logs = rsp.logs;
    processes = rsp.processes
    var divTable = buildTable();


    if (logs.length >= 0) {
	var divHeadRow = tableHeader(divTable);	
	addHeaderCell(divHeadRow,"Time");
	addHeaderCell(divHeadRow,"Function");
	addHeaderCell(divHeadRow,"Level");
	addHeaderCell(divHeadRow,"Message");	
	divTable.appendChild(divHeadRow);
	for (var i=0;i<logs.length;i++) {
	    var log = [];
	    log = logs[i];
            var divRow = document.createElement("div");
            divRow.setAttribute("class","divRow3");
	
            addCell(divRow,log["time"]);
            addCell(divRow,log["function"]);
            addCell(divRow,log["level"]);
            addCell(divRow,log["message"]);	    	    	    
	    divTable.appendChild(divRow);	    
	}

    }
    divRow = addCellRow(divChild);    
    addCellButton(divRow,"View Processes","View Processes","submit",mRTCprocess);    
    divTable.appendChild(divRow);    
    updateRetCode("OK","Retrieved Logs")
    
}
function editRTCprocesses(rsp) {

    var processes = []
    processes = rsp.rtcprocesses;
    var divTable = buildTable2();
    addRow(divTable,"RTC Process","","divHeaderRow");        

    if (processes.length > 0) {
	var divHeadRow = tableHeader(divTable);	
	addHeaderCell(divHeadRow,"PID");
	addHeaderCell(divHeadRow,"Process Name");
	addHeaderCell(divHeadRow,"Command Line");
	divTable.appendChild(divHeadRow);
	for (var i=0;i<processes.length;i++) {
	    var process = [];
	    process = processes[i];
            var divRow = document.createElement("div");
            divRow.setAttribute("class","divRow3");

            addCell(divRow,process["pid"]);
	    addCell(divRow,"rtcMain.py");	
            addCell(divRow,process["cmdline"]);
	    divTable.appendChild(divRow);	    
	}

    }
    divRow = addCellRow(divChild);    
    if (processes.length > 0) {
	addCellButton(divRow,"Stop","Stop Process","submit",cbStopRTC);
    }
    else {
	divRow = addCellRow(divChild);
	addCellStatic(divRow,"AMP log level");
	addCellNumber(divRow,"amploglevel","amploglevel",2,0,7);
	divTable.appendChild(divRow);

	divRow = addCellRow(divChild);
	addCellStatic(divRow,"Umbrella log level");
	addCellNumber(divRow,"umbloglevel","umbloglevel",2,0,7);
	divTable.appendChild(divRow);

	divRow = addCellRow(divChild);
	addCellStatic(divRow,"Stealthwatch log level");
	addCellNumber(divRow,"swloglevel","swloglevel",2,0,7);
	divTable.appendChild(divRow);
	
	divRow = addCellRow(divChild);       	
	addCellButton(divRow,"Start","Start Process","submit",cbStartRTC);

	divRow = addCellRow(divChild);       	
	addCellButton(divRow,"Delete","Delete Logs","submit",cbDeleteLogs);
	
    }
    addCellButton(divRow,"View","View Logs","submit",cbViewLogs);    
    divTable.appendChild(divRow);    
    updateRetCode("OK","Retrieved Processes")
    
}

function resetDBresponse(xhr) {
    updateRetCode("OK","Reset Events");
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	if (rsp.fullreset) {
	    updateRetCode("OK","Reset DB - full reset");
	}
	else {
	    updateRetCode("OK","Reset DB - reset events only");
	}
    }
    else {
	alert(rsp.rtcResult);
	updateRetCode("Error","Could not Reset Events - Process running");		
    }
}
function rtcStartResponse(xhr) {

    // do nothing... this may come back late because of apache handling of the CGI which forks a subprocess
}
function rtcDeleteLogsResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Deleted RTC Logs");
    }
    else {
	updateRetCode("Error","Could not delete RTC Logs: "+rsp.rtcResult);	
    }
}
function rtcStopResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Stopped RTC");
	editRTCprocesses(rsp)
    }
    else {
	updateRetCode("Error","Could not stop RTC: "+rsp.rtcResult);	
    }
}
function rtcViewLogsResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Fetched RTC Logs");
	viewRTClogs(rsp)
    }
    else {
	updateRetCode("Error","Could not stop RTC: "+rsp.rtcResult);	
    }
}


function rtcGetProcessResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	editRTCprocesses(rsp);
    }
    else {
	alert("Error" + JSON.stringify(rsp.rtcresult))	
    }
}
function rtcBackupResponse(xhr) {

    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	var configstring = JSON.stringify(rsp.configstring);
	var blob = new Blob([configstring], { type: "text/plain;charset=utf-8" });
        saveAs(blob, "backup.json");
    }
    else {
	alert("Error" + JSON.stringify(rsp.rtcresult))	
    }
}
///
/// Menu Functions - callbacks from HTML defined menues
///
function mHostView() {
    gl_mac_stored_events.edit();
}
function mUserView() {
    gl_users_stored_events.edit();    
}

function mIPview() {
    gl_IPs_stored_events.edit()
}

function mHostnameView() {
    gl_hostnames_stored_events.edit();
}


function mStealthwatchEvents() {
    gl_view = "";    
    gl_SW_search_api.searchOptions();
}
function mAMPevents() {
    gl_view = "";    
    gl_AMP_search_api.searchOptions();
}

function mUmbrellaEvents() {
    gl_view = "";    
    gl_UMB_search_api.searchOptions();    
}
function mISEsessions() {
    gl_view = "";    
    post = {};
    sendXpost(gl_xhr,"/cgi-bin/rtcISEsessions.py",post,ISEsessionsResponse);
    gl_retcode = "Retrieving ISE sessions,please wait...";
    updateRetCode("Wait",gl_retcode);
    timeGlass();

}

function mEditRTC() {
    gl_view = "";    
    editRTCconfig(gl_rtc_config);
}
function mEditSW() {
    gl_view = "";        
    gl_sw_config.getConfig();
}
function mEditISE() {
    gl_view = "";        
    gl_ise_config.getConfig();
}

function mEditAMP() {
    gl_view = "";        
    gl_amp_config.getConfig();
}
function mEditCTR() {
    gl_view = "";        
    gl_ctr_config.getConfig();

}
function mEditAD() {
    gl_view = "";
    gl_ad_config.getConfig();
}
function mEditUmbrella() {
    gl_view = "";        
    gl_umb_config.getConfig();

}
//
//  Responses XMLHTTP request
//

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


function startIsolateResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Started Isolation ");		
    }
    else {
	alert("Error in Isolation" + rsp.rtcResult + rsp.info);
    }
}
function stopIsolateResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	updateRetCode("OK","Stopped Isolation");		
    }
    else {
	alert("Error in Stopping Isolation" + rsp.rtcResult + rsp.info);
    }
}


function updateRTCconfigResponse(xhr) {
    var rsp = JSON.parse(xhr.responseText);
    if (rsp.rtcResult == "OK") {
	gl_rtc_config = JSON.parse(rsp.configstring)
	gl_reading_rtcconfig = false;
    }
    else {
	alert("Error in updating RTC config  parameters" + rsp.rtcResult + rsp.info);
    }


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

function showIPdetails(ip) {

    var divChild = document.getElementById("divChild");
    var divOld = document.getElementById("divDetails");
    var divDetails = document.createElement("div");
    divDetails.setAttribute("class","divDetails");
    divDetails.setAttribute("id","divDetails");
    var divRow = document.createElement("div");
    divRow.setAttribute("class","divRow2");

    var ip = ip["ip"]

    addCellStatic(divRow,"IP",true);
    addCellStaticRight(divRow,ip);
    divDetails.appendChild(divRow);

    divChild.replaceChild(divDetails,divOld);


}

function showFlows(rsp) {

//    alert(JSON.stringify(rsp));

    var flows = [];
    flows = rsp.data.flows;

    var flowWindow = window.open("rtcreport.html","");
    flowWindow.onload = function() {

	flowWindow.document.title = "Flows for IP";
	var divDetails = buildDivNewWindow(flowWindow,"Flows for IP","");    
	var divHeadRow = tableHeader(divDetails);
	addHeaderCell(divHeadRow,"Start");
	addHeaderCell(divHeadRow,"Subject IP");
	addHeaderCell(divHeadRow,"Subject SGT");	
	addHeaderCell(divHeadRow,"Subject Country");
	addHeaderCell(divHeadRow,"Subject Process");
	addHeaderCell(divHeadRow,"Subject Process User");		
	addHeaderCell(divHeadRow,"Peer IP");
	addHeaderCell(divHeadRow,"Peer Country");
	addHeaderCell(divHeadRow,"Peer Host Groups");    	
	addHeaderCell(divHeadRow,"Protocol");    
	addHeaderCell(divHeadRow,"Dest Port");
	addHeaderCell(divHeadRow,"Bytes Client/Server");    

// f
	for (var i=0;i<flows.length;i++) {
	    var flow = [];
	    var flow = flows[i];

	    var divRow = document.createElement("div");
            divRow.setAttribute("class","divRow3");

	    addCell(divRow,flow["statistics"]["firstActiveTime"]);
	    addCell(divRow,flow["subject"]["ipAddress"]);
	    addCell(divRow,flow["subject"]["trustSecName"]);	    
	    addCell(divRow,flow["subject"]["countryCode"]);
	    addCell(divRow,flow["subject"]["processName"]);
	    addCell(divRow,flow["subject"]["processUsername"]);	    
	    
            addCell(divRow,flow["peer"]["ipAddress"]);
	    addCell(divRow,flow["peer"]["countryCode"]);
            addCell(divRow,flow["peer"]["hostGroupIds"]);		    
            addCell(divRow,flow["protocol"]);	
            addCell(divRow,flow["peer"]["portProtocol"]["port"]);
	    var sbytes = flow["subject"]["bytes"];
	    var pbytes = flow["peer"]["bytes"];
	    
            addCell(divRow,sbytes + "/" + pbytes);

	    divDetails.appendChild(divRow);
	}
    }

}

function SW_get_event_name(event_id) {
    for (var j=0;j< gl_sw_events.length;j++) {
	if (event_id == gl_sw_events[j]["id"]) {
	    event_type = gl_sw_events[j]["name"];
	    return event_type;
	}
    }
    return "Unknown Event";

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

    var flowWindow = window.open("rtcreport.html","");
    flowWindow.onload = function() {

	flowWindow.document.title = "ISE sessions";
	var divDetails = buildDivNewWindow(flowWindow,"ISE Sessions","");    
	var divHeadRow = tableHeader(divDetails);

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
	    divDetails.appendChild(divRow);
	}
    }
    updateRetCode("OK","Retrieved ISE sessions")
    
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
    if (gl_reading_rtcconfig) {
	alert("Fetching RTC config - Please try again soon")
	return;
    }
    var divChild = startEdit();
    addRow(divChild,"Configure RTC","","divHeaderRow");            
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
    addCellStatic(divRow,"RTC AMP Host Isolation");
    rtcAMPhostisolation = rsp["rtcAMPhostisolation"];
    if (typeof rtcAMPhostisolation == 'undefined') {
	rtcAMPhostisolation = "Disabled";
    }
//    addCellInput(divRow,"text","rtcPolicyName","rtcPolicyName",rtcPolicyName);    
    addCellSelection(divRow,"rtcAMPhostisolation",["Enabled","Disabled"],rtcAMPhostisolation);

    divRow = addCellRow(divChild);
    divRow.setAttribute("class","row")    
    addCellStatic(divRow,"RTC ANC Policy Name");
    rtcPolicyName = rsp["rtcPolicyName"];
    if (typeof rtcPolicyName == 'undefined') {
	rtcPolicyName = "";
    }
//    addCellInput(divRow,"text","rtcPolicyName","rtcPolicyName",rtcPolicyName);    
    addCellSelection(divRow,"rtcPolicyName",gl_ise_anc_policies,rtcPolicyName);
    
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


function cbStartIsolation(ev1) {
    var name = this.id;
    alert("start isolation " + name);
    post["guid"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcStartIsolate.py",post,startIsolateResponse);
    updateRetCode("Wait","Starting Isolating Host")
}
function cbStopIsolation(ev1) {
    var name = this.id;
    alert("stop isolatiopn " + name);
    post["guid"] = name
    sendXpost(gl_xhr,"/cgi-bin/rtcStopIsolate.py",post,stopIsolateResponse);
    updateRetCode("Wait","Stopping Isolating Host")
}
function cbNotCapable(ev1) {
    var name = this.id;
    alert("Endpoint does not support host isolation " + name);
}
function cbInProgress(ev1) {
    var name = this.id;
    alert("Endpoint currently being isolated" + name);
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

function launchCTR(item) {
    var CTR_AMP = [];
    var CTR_UMB = [];
    var CTR_SW  = [];
    
    try {
	var events = item["ampevents"]["events"];
    }
    catch (error) {
	var events = [];
    }
    addCTRarray(CTR_AMP,events,"observable");
    
    try {
	var events = item["umbevents"]["events"];
    }
    catch (error) {
	var events = [];

    }
    addCTRarray(CTR_UMB,events,"observable");    

    q = "";
    q = buildCTRq(CTR_AMP,q);
    q = buildCTRq(CTR_UMB,q);

    if (q) {
	var CTRlink = "https://visibility.amp.cisco.com/#/investigate?q=" 
	CTRlink = CTRlink + q;
	window.open(CTRlink, '_blank');
    }
    else {
	alert("No CTR observables found for host " + name);
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
	    event["penalty"] = String(t.value)
	}
	catch (err) {
	    event["penalty"]  = "0"
//	    alert("catch" + thisid);
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
    post["rtcAMPhostisolation"] = document.getElementById("rtcAMPhostisolation").value;
    post["rtcPolicyName"] = document.getElementById("rtcPolicyName").value;
    ppost = {};
    ppost["post"] = post;
    ppost["table"] = "rtcconfig";
    sendXpost(gl_xhr,"/cgi-bin/rtcUpdateXconfig.py",ppost,updateRTCconfigResponse);
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
function sendXpost2(xhr,th,posturl,post,callback) {

/*    var pjson = encodeURIComponent(JSON.stringify(post)); */

    pjson = JSON.stringify(post)
    xhr.open("POST",posturl,true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
	    callback(xhr,th);
        }
    }
    /*    xhr.send("x=" + pjson); */
   xhr.send( pjson); 

}


