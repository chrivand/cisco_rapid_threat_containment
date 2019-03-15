# Cisco Rapid Threat Containment Penalty System

 This is the result of a hackathon with the following concept: correlate security events from Cisco Umbrella, Advanced Malware Protection for Endpoints (AMP4E), Stealthwatch and the Identity Services Engine (ISE). If there was a correlation to be found, our system automatically placed the endpoints in quarantine with ISE (Rapid Threat Containment, or RTC). Next, a report was created with all the details, and the option to query more details regarding the endpoints that were quarantined. Finally, there was an option to cross-launch into Cisco Threat Response (CTR) to do more research on a quarantined endpoint. If an endpoint was cleaned, it could be directly unquarantined from the GUI. During our pitch we stressed on our extensive "roadmap" to add more granular features (currently under development).

 The created system contained 3 major components. The first component is responsible for retrieving and correlating the security events, and quarantining the endpoints. The second component takes care of controlling the database that contained the contextual information about the quarantined endpoints. The last component is in charge of the created GUI, which also has some functionality to query additional information, cross-launch into CTR, and to unquarantine the endpoints.

 ## Solution Components

 The system in more detail with an example workflow:

 1. The Umbrella Reporting API reports Command and Control traffic from a particular endpoint. The internal IP address, the time stamp and the domain are stored.

 2. The AMP4E and Stealthwatch API are also queried for this same IP address, and it is checked whether they have also seen a security event for that endpoint.

 3. If a correlation is found, the endpoint is placed in quarantine by the ISE API (ANC) and all of the contextual information is then send towards the database.

 4. The GUI periodically queries the database, checking the sequence number if an update has been made. If so, the domain, file hash and destination IP that triggered the security events can be seen per quarantined endpoint. These observables have been retrieved from Umbrella, AMP4E and Stealthwatch respectively.

 5. From the GUI it is possible to query Umbrella Investigate and Threat Grid for more in depth information about these observables. Furthermore, Stealthwatch can be queried to retrieve information regarding the hosts that the internal IP address was communicating with around the security event. All of these options can help an incident responder in making the right follow up actions.

 6. If the incident responder has all the needed information and cleaned the system accordingly, the endpoint can be unquarantined directly from the GUI using the ISE API.

 This system has further been optimized by adding a penalty point system with thresholds and by using MAC-address and User information instead of internal IP. Because of the penalty system, this now works more modular, multi-threaded and in a continuous loop. 

 ### Cisco Products / Services

 * Cisco Identity Services Engine
* Cisco Stealthwatch
* Cisco Umbrella
* Cisco Advanced Malware Protection for Endpoints

 ## Installation

 This will be published at a later point in time. Please contact us for further explanantion.

 ## Authors

 * Hakan Nohre
* Andre Lambertsen
* Ed McNicholas
* Christopher van der Made
