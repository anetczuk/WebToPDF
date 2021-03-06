#!/bin/bash
# MIT License
# 
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


repeats=1
untilfailure=0

for i in "$@"; do
case $i in
    -r=*|--repeat=*)        repeats="${i#*=}"
                            shift                   # past argument=value
                            ;;
    -uf|--untilfailure)     untilfailure=1
                            shift                   # past argument with no value
                            ;;
    *)                      ;;                      # unknown option
esac
done



cd $SCRIPT_DIR


if [ $repeats -eq 1 ] && [ $untilfailure -eq 0 ]; then
    ## no repeating -- just single call
    python -m unittest discover $@
    exit $?
fi


## repeating mode
counter=0
while [ $repeats -gt 0 ] || [ $untilfailure -ne 0 ]; do
    let counter=counter+1
    
    echo -e "\n\nTests iteration: $counter" 
    python -m unittest discover $@
    err_code=$?
    if [ $err_code -ne 0 ]; then
        echo "Tests failed: $err_code"
        exit $err_code
    fi
    let repeats=repeats-1 
done
