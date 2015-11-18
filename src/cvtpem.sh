#!/bin/bash

echo $(openssl x509 -in ./cert.pem -fingerprint -noout) | sed 's/SHA1 Fingerprint=//g' | sed 's/://g' | xxd -r -ps | base64

echo ''
echo ''

linecount=`expr $(wc -l < cert.pem) - 2`
echo $linecount
tail -n+2 cert.pem | head -n $linecount > rawcert.pem