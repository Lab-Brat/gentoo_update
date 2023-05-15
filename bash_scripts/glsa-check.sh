#!/bin/bash

# Check for GLSAs and install updates if necessary
glsa=$(glsa-check -l affected)

if [ -z "$glsa" ]
then
	echo "No affected GLSAs found."
else
	echo "Affected GLSAs found. Applying updates..."
	glsa-check -f affected
	echo "Updates applied."
fi

