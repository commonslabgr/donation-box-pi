#!/bin/bash
mysql -uroot -pc0mm0ns "donationbox" < "truncate_coins.sql"
mysql -uroot -pc0mm0ns "donationbox" < "truncate_donations.sql"
