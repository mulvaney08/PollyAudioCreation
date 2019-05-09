''' A script that reads text from a file and uploads to Amazon Polly
    Amazon Polly allows text to be turned into audio, an mp3 file
    is created and uploaded to an s3 buckets

    Usage: polly.py <Text file containing text to be converted to audio>
                    <S3 bucket name>
                    <Folder inside S3 bucket>
'''

import sys
import datetime
from contextlib import closing
import boto3

POLLY_CLIENT = boto3.client('polly')
S3_CLIENT = boto3.client('s3')
CURRENT_DATETIME = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')


def call_polly(file, s3_bucket, s3_folder):
    '''
    Function that calls Polly api and sends the contents of the chosen text file
    '''
    if file.mode == 'r':
        contents = file.read()
        try:
            response = POLLY_CLIENT.synthesize_speech(OutputFormat='mp3',
                                                      Text=contents,
                                                      TextType='text',
                                                      VoiceId='Salli')
        except POLLY_CLIENT.exceptions.EndpointConnectionError as exception:
            print(exception)
        upload_to_s3(response, s3_bucket, s3_folder)

def upload_to_s3(response, s3_bucket, s3_folder):
    '''
    Function that creates an mp3 file and uploads it to S3
    '''
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = "polly-boto.mp3"
            s3_file_name = "PollyAudio_" + str(CURRENT_DATETIME)
            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file_out:
                    file_out.write(stream.read())
                    S3_CLIENT.upload_file(output, s3_bucket, s3_folder.format(s3_file_name))
            except IOError as ioe:
                # Could not write to file, exit gracefully
                print(ioe)
                sys.exit(-1)

def main():
    '''
    Main function, checks incomming args and calls necessary functions
    '''
    if len(sys.argv) < 2:
        print("No text file specified")
        sys.exit(1)
    else:
        text_file = sys.argv[1]
        file = open(text_file, "r")

    if len(sys.argv) < 3:
        print("No S3 bucket specified")
        sys.exit(1)
    else:
        s3_bucket = sys.argv[2]

    if len(sys.argv) < 4:
        print("No folder on S3 specified")
        sys.exit(1)
    else:
        s3_folder = sys.argv[3] + "/{}"

    call_polly(file, s3_bucket, s3_folder)

if __name__ == "__main__":
    main()
