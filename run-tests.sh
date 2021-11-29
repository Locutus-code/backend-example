#!/bin/sh

pytest  --base-url `chalice url --stage test` --alluredir test-results/ $1 $2 $3 $4 $5 $6
