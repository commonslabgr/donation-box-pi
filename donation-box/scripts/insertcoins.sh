#!/bin/bash
mysql -uwpuser -pdbc0mm0ns "donationbox" < "insert_05EUR.sql"
sleep 1
mysql -uwpuser -pdbc0mm0ns "donationbox" < "insert_1EUR.sql"
sleep 1
mysql -uwpuser -pdbc0mm0ns "donationbox" < "insert_2EUR.sql"
