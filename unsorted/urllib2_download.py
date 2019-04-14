#!/usr/bin/env python3
'''Written as an example for others'''
import urllib.request


def main():
    # File size:     4.29 MB
    small_file_url = 'http://biomirror.aarnet.edu.au/biomirror/blast/16SMicrobial.tar.gz'
    # File size:  1434.49 MB
    large_file_url = 'http://biomirror.aarnet.edu.au/biomirror/blast/cdd_delta.tar.gz'
    # Download files
    download_small_file(small_file_url, '16SMicrobial.tar.gz')
    download_large_file(large_file_url, 'cdd_delta.tar.gz')


def download_small_file(url, output_fp):
    # Use a context manager to retrieve a Response object
    # Context managers useful as they automatically operation open and close operations
    with urllib.request.urlopen(url) as response:
        with open(output_fp, 'wb') as output_fh:
            # First we download the data and store it in memory as a variable
            file_data = response.read()
            # Next, the file data in memory is written to a file
            output_fh.write(file_data)
    # Downloading and storing file data in memory is problematic for large files. A better approach
    # is to stream the file and write out small parts of the file.


def download_large_file(url, output_fp):
    # Set the part size (chunk size) to 10 KB
    chunk_size = 1024 * 10
    # Open URL and output file
    with urllib.request.urlopen(url) as response:
        with open(output_fp, 'wb') as output_fh:
            # Download the first chunk
            chunk = response.read(chunk_size)
            # Loop until no more chunks are downloaded
            while chunk:
                # Write data chunk to file
                output_fh.write(chunk)
                # Get the next chunk
                chunk = response.read(chunk_size)


if __name__ == '__main__':
    main()
