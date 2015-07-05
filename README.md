This swift middleware should enaple the integration of Persistent Identifiers 
(PID) to the swift pipeline.

[![Build Status](https://travis-ci.org/BeneDicere/swift-persistent-identifier.svg?branch=master)](https://travis-ci.org/BeneDicere/swift-persistent-identifier)

1. If a objekt is given and its not requested to create a PID, nothing happens.

2. If a objekt is given and its requested to create a PID (through header), a 
PID is created and stored with the objekt (X-Object-Meta-Pid).

3. If a objekt is given to the object-server with an existing PID, the PID is
registered as the "parent". A new PID is assigned to the objekt pointing to
its current swift location.
