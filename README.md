This swift middleware should enable the integration of Persistent Identifiers 
(PID) to the swift pipeline.

[![Build Status](https://travis-ci.org/BeneDicere/swift-persistent-identifier.svg?branch=master)](https://travis-ci.org/BeneDicere/swift-persistent-identifier)

1. If a object is given and its not requested to create a PID, nothing special 
happens.

2. If a object is given and its requested to create a PID (through X-Pid-Create
header), a PID is created and stored with the swift object (X-Object-Meta-Pid).
The response to the PUT request then contains a X-Pid-Url header.

2.1 If the swift proxy is configured to store the checksum within a PID 
(add_checksum = True in proxy config), the Etag (that is representing the 
md5sum of objects smaller then 5GB) is stored within the PID.

3. If a objekt is given to the object-server with an existing PID (we call this
parent, given by "X-Pid-Parent" header), the PID is registered as the "parent".
A new PID is assigned to the objekt pointing to its current swift location and
the value "EUDAT/PPID" is referring to the parent PID.
