#!/bin/bash
dd if=/dev/zero of=test bs=1024 count=1000
#cat test > /dev/null
rm test