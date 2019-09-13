#!/usr/bin/python3

# run script like this: >>> python3.6 email_config_health_checker.py esa_config.xml

import xml.etree.ElementTree as ET
import sys
import json
import re
import checkdmarc


def debug(message):
    if False:
        print(message)

# class for email health check 
class EHC:
    def __init__(self,configstring,ourdomain=""):
        self.remarks = []        
        self.ourdomain = ourdomain
        self.XML_File = configstring
        if self.XML_File:
            self.root = ET.fromstring(configstring)
            debug("Root is {}".format(self.root))
            debug("printing children")
            for child in self.root:
                debug("child tag {} child atrib {}".format(child.tag,child.attrib))


        else:
            debug("bajs")


    def dmarc_check(self,domainname,approved_nameservers,approved_mx_hostnames):
        domainlist = []
        domainlist.append(domainname)
        rsp = checkdmarc.check_domains(domainlist,approved_nameservers=approved_nameservers,approved_mx_hostnames=approved_mx_hostnames) 
        
        ns = rsp["ns"]
        if ns["warnings"]:
            ns_warnings = ns["warnings"]
            for warning in ns_warnings:
                self.add_remark_warning(warning,"DNS CHECKS")
                

        mx = rsp["mx"]
        hosts = mx["hosts"]
        for host in hosts:
            if host["tls"] == False:
                tls_compliance = [
                    { 'host_name':host["hostname"], 'tls_status':'non_compliant', 'error':None }
                ]
                self.add_remark_warning("TLS is not compliant","TLS COMPLIANCE")
                
        
        if mx["warnings"]:
            mx_warnings = mx["warnings"]
            for warning in mx_warnings:
                self.add_remark_warning(warning,"DNS CHECK")
                

        dmarc = rsp["dmarc"]
        if "error" in dmarc:
            error = dmarc["error"]
            dmarc_compliance = [
                { 'domain':domainname, 'dmarc_status':'non_compliant', 'error':error }
            ]
            self.add_remark_warning("Dmarc is not compliant:"+dmarc["error"],"DNS CHECKS")
        else:
            dmarc_compliance = [
                { 'domain':domainname, 'dmarc_status':'compliant', 'error':None }
            ]
            self.add_remark_ok("DMARC DNS record has been published (Compliant)","DNS CHECKS")
            
    def get_licenses(self):
        self.licenses_dict = {
            'ETF': 0,
            'AMP': 0,
            'TG': 0,
            'CASE': 0,
            'OF': 0,
            'CSP': 0,
            'BV': 0,
            'IMH': 0,
            'IMS': 0,
            'IEE': 0,
            'DLP': 0,
            'SOP': 0,
            'MCA': 0
        }

        for line in self.XML_File:
            if "Feature" in line:
                if "External Threat Feeds" in line:
                    self.licenses_dict['ETF'] = 1
                elif "File Reputation" in line:
                    self.licenses_dict['AMP'] = 1
                elif "File Analysis" in line:
                    self.licenses_dict['TG'] = 1
                elif "IronPort Anti-Spam" in line:
                    self.licenses_dict['CASE'] = 1
                elif "Outbreak Filters" in line:
                    self.licenses_dict['OF'] = 1
                elif "Cloudmark SP" in line:
                    self.licenses_dict['CSP'] = 1
                elif "Bounce Verification" in line:
                    self.licenses_dict['BV'] = 1
                elif "Incoming Mail Handling" in line:
                    self.licenses_dict['IMH'] = 1
                elif "Intelligent Multi-Scan" in line:
                    self.licenses_dict['IMS'] = 1
                elif "IronPort Email Encryption" in line:
                    self.licenses_dict['IEE'] = 1
                elif "Data Loss Prevention" in line:
                    self.licenses_dict['DLP'] = 1
                elif "Sophos" in line:
                    self.licenses_dict['SOP'] = 1
                elif "McAfee" in line:
                    self.licenses_dict['MCA'] = 1
        debug(json.dumps(self.licenses_dict,indent=4,sort_keys=True))

        
    def xml_get_text_in_tag(self,xml_tag):

        found_items = 0
        for item in self.root.iter(xml_tag):
             found_items = found_items +1
             text = item.text
        if found_items == 1:
            return text
        else:
            debug("did not find exactly one of tag {}, found {}".format(xml_tag,str(found_items)))
             
    def add_remark_warning(self,txt,category):
        remark = {"level":"warning","text":txt,"category":category}
        self.remarks.append(remark)

    def add_remark_ok(self,txt,category):
        remark = {"level":"ok","text":txt,"category":category}
        self.remarks.append(remark)

    def add_remark_debug(self,txt,category):
        if True:
            return
        remark = {"level":"debug","text":txt,"category":category}
        self.remarks.append(remark)

    def print_remarks(self):
        for r in self.remarks:
            print(r["level"] + r["text"])
            
    def check_rules(self):

        rules_enabled = [
            { 'name':'Checking if CASE Anti-SPAM Enabled', 'text': 'case_enabled', 'value':'1','license':None },
            { 'name':'Checking if Intelligent Multi-Scan Enabled', 'text': 'ims_enabled', 'value':'1','license':None },
            { 'name':'Checking if File Reputation Enabled', 'text': 'rep_enabled', 'value':'1','license':None },
            { 'name':'Checking if URL Scanning Enabled', 'text': 'urlscanning_enabled', 'value':'1','license':None },
            { 'name':'Checking if Graymail Detection Enabled', 'text': 'graymail_detection_enabled', 'value':'1','license':None },
            { 'name':'Checking if Domain Reputation Enabled', 'text': 'domain_rep_enabled', 'value':'1','license':None },                        
            
        ]
        rules_values = [
            { 'name':'Checking SPAM threshold for always scan', 'text': 'case_advisory_scan_size', 'minvalue':'1048176','maxvalue':'1048176','license':None },
            { 'name':'Checking SPAM threshold for never scan', 'text': 'case_max_message_size', 'minvalue':'2097152','maxvalue':'2097152','license':None },
        ]
        for r in rules_enabled:
            if self.xml_get_text_in_tag(r["text"]) == r["value"]:
                self.add_remark_ok(r["name"],"FEATURE ENABLED")
            else:
                self.add_remark_warning(r["name"],"FEATURE ENABLED")

        for r in rules_values:
            config_value = int(self.xml_get_text_in_tag(r["text"]))
            if config_value >= int(r["minvalue"]) and config_value <= int(r["maxvalue"]):
                self.add_remark_ok(r["name"],"FEATURE LIMIT")
            else:
                self.add_remark_warning(r["name"] + " " + str(config_value),"FEATURE LIMIT")                
                                                         

    def xml_get_hat_incoming(self):
## ugly assumes first hat is hat for incoming
        found_items = 0
        for item in self.root.iter("hat"):
             found_items = found_items +1
             found_hat = item.text
             return found_hat

    def get_result(self):
        return self.remarks

    def print_result(self):
        return json.dumps(self.remarks)
    
    def print_result2(self):
        result = ""
        for remark in self.remarks:
            if remark["level"] == "ok":
                result = result + "CHECK PASSED:"+ remark["text"] + "<br>"
            else:
                result = result + "ERROR:"+ remark["text"] + "<br>"
                
        return result
    
        
    def check_hat(self):
        hat = self.xml_get_hat_incoming()
        debug("start hat")
        debug(hat)
        debug("end hat")


        x = None

        lines = hat.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            ### Check WHITELIST, that not too many IPs are defined
            x = re.search("^WHITELIST:",line)
            if x:
                debug("match WHITELIST")
                debug(x.string)
                num_of_IPs_in_whitelist = 0
                grabbed_whitelist = False
                while grabbed_whitelist == False:
                    i = i + 1
                    line1 = lines[i]
                    y = re.search("\$",line1)
                    if y:
# end of whitelist
                        break
                    else:
                        newip = line1
                        num_of_IPs_in_whitelist = num_of_IPs_in_whitelist + 1
                        debug("New IP found in whitelist {}".format(newip))
                if num_of_IPs_in_whitelist > 10:
                    self.add_remark_warning("Lots of IPs in WHITELIST {}".format(str(num_of_IPs_in_whitelist)),"HAT")
                else:
                    self.add_remark_ok("Reasonable number of IPs in  WHITELIST {}".format(str(num_of_IPs_in_whitelist)),"HAT")

            #
            #  Check that BLACKLIST SRBRS score has not been changed and that policy is BLOCKED!
            #
            x = re.search("^BLACKLIST:",line)
            if x:
                debug("match BLACKLIST")
                debug(x.string)
                i = i+1
                line1 = lines[i]
                debug("blacklist is " + line1)
                line1 = line1.replace("sbrs[","")
                line1 = line1.replace("]","")
                (low,high) = line1.split(':')
                low = low.strip()
                high = high.strip()
                debug(low)
                debug(high)
                blacklist_ok = True
                if (float(low) > -10):
                    self.add_remark_warning("Too lenient blacklist! Lower end is {}".format(low),"HAT")
                    blacklist_ok = False
                if (float(high) > -3):
                    self.add_remark_warning("Too lenient blacklist! Higher End  is {}".format(high),"HAT")
                    blacklist_ok = False                        
                if (float(high) < -3):
                    self.add_remark_warning("Too harsh blacklist! Higher End  is {}".format(high),"HAT")
                    blacklist_ok = False
                i = i+1
                line1 = lines[i]
                y = re.search("\$BLOCKED",line1)
                if not y:
                    self.add_remark_warning("Blacklist is not Blocking!! {}".format(line1),"HAT")
                    blacklist_ok = False
                if blacklist_ok:
                    self.add_remark_ok("Blacklist is ok, low {} high {}, and blocking".format(low,high),"HAT")
            #
            #  Check that SUSPECTLIST SRBRS score has not been changed and that policy is THROTTLED!
            #  check that SBRS score none -> throttled...
            x = re.search("^SUSPECTLIST:",line)
            if x:
                debug("match SUSPECTLIST")
                debug(x.string)
                i = i+1
                line1 = lines[i]
                debug("suspectlist is " + line1)
                line1 = line1.replace("sbrs[","")
                line1 = line1.replace("]","")
                (low,high) = line1.split(':')
                low = low.strip()
                high = high.strip()
                debug(low)
                debug(high)
                suspectlist_ok = True
                if (float(low) != -3.0):
                    self.add_remark_warning("Changed defaults for Suspect List! Lower end is {}".format(low),"HAT")
                    suspectlist_ok = False
                if (float(high) != -1.0):
                    self.add_remark_warning("Changed defaults for Suspect List! Higher End  is {}".format(high),"HAT")
                    suspectlist_ok = False                        
                i = i+1
                line1 = lines[i]
                if "sbrs[none]" in line1:
                    self.add_remark_ok("Suspectlist contains domains with no reputation sbrs[none] {}".format(line1),"HAT")
                    i = i+1
                    line1 = lines[i]
                else:
                    suspectlist_ok = False
                    self.add_remark_warning("Suspectlist should contain domains with no reputation sbrs[none] {}".format(line1),"HAT")
                y = re.search("\$THROTTLED",line1)
                if not y:
                    self.add_remark_warning("Suspectlist should be throttled {}".format(line1),"HAT")
                    suspectlist_ok = False
                if suspectlist_ok:
                    self.add_remark_ok("Suspectlist is ok, low {} high {}, including none-reputation and throttling".format(low,high),"HAT")
            #
            x = re.search("^\$ACCEPTED",line)
            if x:
                self.add_remark_debug("found accepted","Debug")                
                grabbed_accept_policy = False
                grabbing = False
                spf_enabled = False
                dkim_enabled = False
                dmarc_enabled = False                
                while grabbed_accept_policy == False:
                    i = i + 1
                    line1 = lines[i]
                    y = re.search("ACCEPT {}",line1)
                    if y:
                        self.add_remark_debug("Accept one line","Debug")                                            
                        break
                    y = re.search("ACCEPT {",line1)
                    if y:
                        grabbing = True
                        self.add_remark_debug("Grabbing","Debug")                                                                    
                    else:
                        y = re.search("}",line1)
                        if y and grabbing:
                            self.add_remark_debug("Grabbed","Debug")
                            break
                    self.add_remark_debug("Grabbing",line1)                                                                                            
                    y = re.search("dkim_verification_profile",line1)
                    if y:
                        dkim_enabled = True
                    y = re.search("dmarc_verification_profile",line1)
                    if y:
                        dmarc_enabled = True
                    y = re.search("spf_profile",line1)
                    if y:
                        spf_enabled = True

                if dkim_enabled:
                    self.add_remark_ok("Check DKIM Enabled","HAT Mail Flow Policy")
                else:
                    self.add_remark_warning("Check DKIM Enabled","HAT Mail Flow Policy")                    
                if dmarc_enabled:
                    self.add_remark_ok("Check DMARC Enabled","HAT Mail Flow Policy")
                else:
                    self.add_remark_warning("Check DMARC Enabled","HAT Mail Flow Policy")                    
                if spf_enabled:
                    self.add_remark_ok("Check SPF Enabled","HAT Mail Flow Policy")
                else:
                    self.add_remark_warning("Check SPF Enabled","HAT Mail Flow Policy")                    


                
                    
            i = i + 1

            
    
