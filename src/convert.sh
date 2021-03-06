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



ARGS_NO=$#

SHOW_HELP=""
INPUT_FILE=""
ONLINE_CONVERT=""
LOCAL_TEMP=""
SKIP_CONVERT=""
REDUCE_QUALITY=""
SKIP_SHORTEN=""
SKIP_JOIN=""
DISABLE_JAVASCRIPT=""

for i in "$@"; do
case $i in
    -h|--help)              SHOW_HELP=1
                            shift                   # past argument with no value
                            ;;
    -i=*|--input=*)         INPUT_FILE="${i#*=}"
                            shift                   # past argument=value
                            ;;
    -oc|--onlineconvert)    ONLINE_CONVERT=1
                            shift                   # past argument with no value
                            ;;
    -lt|--localtemp)        LOCAL_TEMP=1
                            shift                   # past argument with no value
                            ;;
    -sc|--skipconvert)      SKIP_CONVERT=1
                            shift                   # past argument with no value
                            ;;
    -rq|--reduceuality)     REDUCE_QUALITY=1
                            shift                   # past argument with no value
                            ;;
    -ss|--skipshorten)      SKIP_SHORTEN=1
                            shift                   # past argument with no value
                            ;;
    -sj|--skipjoin)         SKIP_JOIN=1
                            shift                   # past argument with no value
                            ;;
    -nojs|--nojs)           DISABLE_JAVASCRIPT=1
                            shift                   # past argument with no value
                            ;;
    *)                      ;;                      # unknown option    
esac
done


function info {
    echo "Convert web page to PDF"
    echo "params: -h|-i|-oc|-sc|-ss|-sj"
}


if [ $ARGS_NO -eq 0 ]; then
    info
    echo "No params given"
    exit 0
fi
if [ -n "$SHOW_HELP" ]; then
    info
    exit 0
fi
if [ -z "$INPUT_FILE" ]; then
    info
    echo "Missing input file"
    exit 1
fi


input_filename=$(basename $INPUT_FILE)
OUTPUT_FILE="${input_filename%.*}"".pdf"


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


function check_command {
    if [ $# -lt 1 ]; then
      echo "missing parameter - command name"
      exit 1;
    fi
    suggest_pkg=""
    if [ $# -gt 1 ]; then
       suggest_pkg="$2"
    fi
  
    pckg_name="$1"
    if ! type "$pckg_name" &> /dev/null; then
      echo "Missing command: $pckg_name"
      if [ ! -z $suggest_pkg ]; then
          echo "Suggested package $suggest_pkg"
          exit 1;
      fi
      exit 1
    fi
}

check_command pdfinfo poppler-utils



TMP_ROOT=$SCRIPT_DIR

if [ -z "$LOCAL_TEMP" ]; then
    TMP_ROOT=$(mktemp -d -t "web2pdf-XXXXXXX")
    
    ## check if tmp dir was created
    if [[ ! "$TMP_ROOT" || ! -d "$TMP_ROOT" ]]; then
        echo "Could not create temp dir"
        exit 1
    fi
    
    ## deletes the temp directory
    function cleanup {      
        rm -rf "$TMP_ROOT"
        echo "Deleted temp working directory $TMP_ROOT"
    }
    
    ## register the cleanup function to be called on the EXIT signal
    trap cleanup EXIT
    
    echo "Created temporary directory: $TMP_ROOT"
fi


CONVERT_DIR="$TMP_ROOT/convert-pdf"
REDUCED_DIR="$TMP_ROOT/reduced-pdf"
CROP_DIR="$TMP_ROOT/crop-pdf"


function convert_webpage {
    if [ $# -lt 1 ]; then
        echo "missing parameter - input file"
        exit 1;
    fi

    local input_file="$1"

    COUNTER=0
    while read line; do           
        COUNTER=$((COUNTER+1))
        ##echo "$COUNTER url: $line"
        local output_file="$CONVERT_DIR/$(printf "%04d" $COUNTER).pdf"
        ##echo "$output_file url: $line"
      
        echo "Converting $line to $output_file"
        if [ -n "$ONLINE_CONVERT" ]; then
            ## online converter
            $SCRIPT_DIR/onlineconverter.py --link=$line --output=$output_file
            if [ $? -gt 0 ]; then
                echo "Unable to use online converter"
                exit 1
            fi
        else
            ## local converter
            if [ -n "$DISABLE_JAVASCRIPT" ]; then
                ##echo "JS disabled"
                wkhtmltopdf --disable-javascript $line $output_file
            else
                wkhtmltopdf --javascript-delay 5000 --no-stop-slow-scripts --enable-javascript $line $output_file
            fi
        fi
    done < "$input_file"
}


##
## reduce quality
##

function reduce_quality {
    if [ $# -lt 1 ]; then
        echo "missing parameter - output directory"
        exit 1;
    fi
    
    local input_dir=$1
    for pdf_file in $input_dir/*; do  
        out_file="$REDUCED_DIR/$(basename $pdf_file)"
        echo -e "\nReducing: $pdf_file -> $out_file"
        convert -monitor -density 120x120 -quality 60 $pdf_file $out_file
        ## gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=$out_file $pdf_file
    done
}



##
## Cropping pages from unnecessary white space
##

function crop_last_page {
    if [ $# -lt 2 ]; then
        echo "missing parameter - PDF file"
        exit 1;
    fi
    local IN_PDF="$1"
    local OUT_PDF="$2"
    
    PAGES_NUM=$( pdfinfo "$IN_PDF" | grep 'Pages' - | awk '{print $2}' )
    echo "Pages num: $PAGES_NUM"
    
    
    ## bounding box
    BBSize=`gs -sDEVICE=bbox -dBATCH -dNOPAUSE -dQUIET -dFirstPage=$PAGES_NUM -dLastPage=$PAGES_NUM "$IN_PDF" -c quit 2>&1`

    # assign height and width to new vars
    BBoxLowLeftX=$(echo $BBSize | awk '/%%BoundingBox:/ { print $2 }')
    BBoxLowLeftY=$(echo $BBSize | awk '/%%BoundingBox:/ { print $3 }')

    BBoxTopRightX=$(echo $BBSize | awk '/%%BoundingBox:/ { print $4 }')
    BBoxTopRightY=$(echo $BBSize | awk '/%%BoundingBox:/ { print $5 }')
    echo "box: $BBoxLowLeftX $BBoxLowLeftY $BBoxTopRightX $BBoxTopRightY"


    PDF_WIDTH=$( pdfinfo "$IN_PDF" | grep 'Page size' | awk '{print $3}' )
    PDF_HEIGHT=$( pdfinfo "$IN_PDF" | grep 'Page size' | awk '{print $5}' )
    echo "PDF page size: $PDF_WIDTH $PDF_HEIGHT"


    BBOX_WIDTH=$( echo "scale=2; $BBoxTopRightX - $BBoxLowLeftX" | bc )
    BBOX_HEIGHT=$( echo "scale=2; $BBoxTopRightY - $BBoxLowLeftY" | bc )
    echo "BBox size: $BBOX_WIDTH $BBOX_HEIGHT"


    BOTTOM_MARGIN=$BBoxLowLeftY
    TOP_MARGIN=$( echo "scale=2; $PDF_HEIGHT - $BBoxTopRightY" | bc )
    echo "Margins: $TOP_MARGIN $BOTTOM_MARGIN"


    TARGET_HEIGHT=$( echo "scale=2; $BBOX_HEIGHT + 2 * $TOP_MARGIN" | bc )
    TARGET_OFFSET=$( echo "scale=2; $BOTTOM_MARGIN - $TOP_MARGIN" | bc )
    echo "Target values: $TARGET_HEIGHT $TARGET_OFFSET"
    
    
    if [ $TARGET_HEIGHT -ge $PDF_HEIGHT ]; then
      ## target height exceeds current - do not need to crop - just copy file
      echo "Nothing to crop"
      return 1
    fi
    
    
    ## cutting
    gs                           \
      -o "$OUT_PDF"              \
      -dQUIET            \
      -sDEVICE=pdfwrite          \
      -dDEVICEWIDTHPOINTS=$PDF_WIDTH    \
      -dDEVICEHEIGHTPOINTS=$TARGET_HEIGHT   \
      -dPDFSETTINGS=/prepress       \
      -dFIXEDMEDIA                      \
      -dFirstPage=$PAGES_NUM -dLastPage=$PAGES_NUM  \
      -c "<</PageOffset [0 -$TARGET_OFFSET]>> setpagedevice"    \
      -f "$IN_PDF"
      
    return 0
}

function change_last_page {
    if [ $# -lt 2 ]; then
      echo "missing parameter - PDF file"
      exit 1;
    fi
    IN_PDF="$1"
    OUT_PDF="$2"
    echo "Files: $IN_PDF -> $OUT_PDF"

    SHORTENED_PDF=$(mktemp -t "shorten-XXXXXXX.pdf")
    CROPPED_PDF=$(mktemp -t "crop-XXXXXXX.pdf")
    echo "Tmp files: $SHORTENED_PDF $CROPPED_PDF"
    
    crop_last_page "$IN_PDF" "$CROPPED_PDF"
    CROP_RET=$?
    if [ $CROP_RET -ne 0 ]; then
      ## not cropped
      cp "$IN_PDF" "$OUT_PDF"
      
      rm $SHORTENED_PDF
      rm $CROPPED_PDF
      return 1
    fi
    
    PAGES_NUM=$( pdfinfo "$IN_PDF" | grep 'Pages' - | awk '{print $2}' )
    if [ $PAGES_NUM -lt 2 ]; then
      ## only one page - just copy last page
      cp "$CROPPED_PDF" "$OUT_PDF"
      
      rm $SHORTENED_PDF
      rm $CROPPED_PDF
      return 
    fi
    
    LAST_PAGE=$( echo "scale=2; $PAGES_NUM - 1" | bc )
    echo "Pages num: $PAGES_NUM $LAST_PAGE"
    
    ## cutting
    gs                           \
      -o "$SHORTENED_PDF"        \
      -dQUIET            \
      -sDEVICE=pdfwrite          \
      -dFirstPage=1 -dLastPage=$LAST_PAGE    \
      -f "$IN_PDF"
      
    ## merge PDFs
    ##gs -dBATCH -dNOPAUSE -dQUIET -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile="$OUT_PDF" "$SHORTENED_PDF" "$CROPPED_PDF"
    pdftk "$SHORTENED_PDF" "$CROPPED_PDF" cat output "$OUT_PDF"
    
    rm $SHORTENED_PDF
    rm $CROPPED_PDF
}
 
function shorten_all {
    if [ $# -lt 1 ]; then
        echo "missing parameter - output directory"
        exit 1;
    fi
    
    local input_dir=$1
    for pdf_file in $input_dir/*; do  
        out_file="$CROP_DIR/$(basename $pdf_file)"
        echo -e "\nCropping: $pdf_file -> $out_file"
        change_last_page "$pdf_file" "$out_file"
    done
}


##
## Join files to one PDF
##

## convert -density 160x160 -quality 100 $CONVERT_DIR/0001.pdf $CONVERT_DIR/0002.pdf test.pdf
## gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile=test.pdf $CONVERT_DIR/0001.pdf $CONVERT_DIR/0002.pdf

function join_loop {
    TMP_OUT_PDF1="book.tmp1.pdf"
    TMP_OUT_PDF2="book.tmp2.pdf"

    OUT_PDF="book.pdf"

    FIRST_FILE="1"

    for pdf_file in $CONVERT_DIR/*; do
      if [ ! -z $FIRST_FILE ]; then
          FIRST_FILE=""
          ##echo "first"
          cp "$pdf_file" "$TMP_OUT_PDF1"
          continue
      fi
      
      echo "Merging: $pdf_file"
      
      ##gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile="$OUT_PDF" "$OUT_PDF" "$pdf_file"
      
      gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile="$TMP_OUT_PDF2" "$TMP_OUT_PDF1" "$pdf_file"
      
      TMP=$TMP_OUT_PDF2
      TMP_OUT_PDF2=$TMP_OUT_PDF1
      TMP_OUT_PDF1=$TMP
    done

    cp $TMP_OUT_PDF1 $OUT_PDF

    rm $TMP_OUT_PDF1
    rm $TMP_OUT_PDF2
}

function join_gs {
    IN_PDF=$CONVERT_DIR/*
    OUT_PDF="gs-book.pdf"

    echo "Merging: $IN_PDF to $OUT_PDF"

    gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile="$OUT_PDF" $IN_PDF

    echo -e "\nDone. Output stored in $OUT_PDF"
}

function join_pdftk {
    if [ $# -lt 1 ]; then
        echo "missing parameter - PDF files"
        exit 1;
    fi
    
    local IN_PDF=$1
    local OUT_PDF="$SCRIPT_DIR/$OUTPUT_FILE"

    echo "Merging: $IN_PDF to $OUT_PDF"

    pdftk $IN_PDF cat output $OUT_PDF

    echo -e "\nDone. Output stored in $OUT_PDF"
}


###
### =========================================================================
###



if [ -z "$SKIP_CONVERT" ]; then
    mkdir -p "$CONVERT_DIR"
    echo "Converting links to PDFs"
    convert_webpage "$INPUT_FILE"
fi
INPUT_DIR="$CONVERT_DIR"


if [ -n "$REDUCE_QUALITY" ]; then
    mkdir -p "$REDUCED_DIR"
    echo "Reducing quality"
    reduce_quality "$INPUT_DIR"
    INPUT_DIR="$REDUCED_DIR"
fi


if [ -z "$SKIP_SHORTEN" ]; then
    mkdir -p "$CROP_DIR"
    echo "Cropping PDFs"
    shorten_all "$INPUT_DIR"
    INPUT_DIR="$CROP_DIR"
fi


if [ -z "$SKIP_JOIN" ]; then
    echo "Joining PDFs"
    join_pdftk "$INPUT_DIR/*"
fi


echo -e "\nConvertion done."

