# Amatica-ePADD
Scripts for translating ePADD packages to Archivematica and back. Intended to be used in the Archivematica automation-tools framework.

## Scripts
_amatica-epadd-restructure.py_
Takes the bagged output from ePADD appraisal and restructures it to meet Archivematica transfer requirements.
* moves indexes, lexicons, and sessions to metadata folder
* moves blobs to objects folder
* extracts blob checksums to checksum.hash to be used during ingest
* stores all other files in metadata folder

_epadd-amatica-restructure.py_
Takes the bagged output from Archivematica AIPstore and restructures it to meet ePADD requirements.
* moves indexes, lexicons, session, and blobs to the user folder
* deletes thumbnails folder
* updates bag manifest with path changes

_epaddProcessingMCP.xml_
Processing MCP that must be included in Archivematica ingest.
* automates all approvals
* does not unpack zip files
* normalizes files for preservation
* does not create DIP

## Issues
* Amatica automatically removes files that start with '.', that might be a problem
* This workflow only repackages pres. normalized AIPs. I haven't looked into access normalized files in AIPs or DIPs.
