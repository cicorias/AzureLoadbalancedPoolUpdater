#!/bin/bash
azure config mode arm

kv=$(cat ./rawcert.pem)

azure ad app create -n "lbupdater" --home-page "https://lbupdater/" -i "https://lbupdater/" --key-usage "Verify" --key-value $kv -vv
