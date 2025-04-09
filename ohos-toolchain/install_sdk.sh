#!/usr/bin/env bash
ARCHIVE_NAME="ohos-sdk-windows_linux-public.tar.gz"
ZIP_PATTERN="native-linux-x64-*-Release.zip"

if [ ! -f "$ARCHIVE_NAME" ]; then
    echo "Error: Archive $ARCHIVE_NAME not found" >&2
    exit 1
fi
tar xzf "$ARCHIVE_NAME" >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Error: Failed to extract the archive" >&2
    exit 1
fi

rm -rf windows/ && \
    mv linux/native-linux-x64-*.zip . && \
    rm -rf linux/ && \ 
    rm -f manifest_tag.xml && \
    rm -rf $ARCHIVE_NAME


files=( $ZIP_PATTERN )

if [ ${#files[@]} -eq 0 ]; then
    echo "Error: No files matching pattern '$ZIP_PATTERN' found" >&2
    exit 1
elif [ ${#files[@]} -gt 1 ]; then
    echo "Error: Multiple files matching pattern '$ZIP_PATTERN' found" >&2
    exit 1
fi

ZIP_FILE="${files[0]}"

unzip -q "$ZIP_FILE" >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Error: Failed to extract $ZIP_FILE" >&2
    exit 1
fi

rm -rf $ZIP_FILE
echo "ohos-sdk successfully installed"

exit 0
