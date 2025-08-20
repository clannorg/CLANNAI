const AWS = require('aws-sdk');

// Configure MediaConvert
const mediaconvert = new AWS.MediaConvert({
  region: process.env.AWS_REGION || 'eu-west-1',
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});

// Get MediaConvert endpoint (required for first setup)
const getMediaConvertEndpoint = async () => {
  try {
    const data = await mediaconvert.describeEndpoints().promise();
    return data.Endpoints[0].Url;
  } catch (error) {
    console.error('Error getting MediaConvert endpoint:', error);
    throw error;
  }
};

// Create HLS conversion job
const createHLSJob = async (inputS3Url, outputS3Path, gameId) => {
  try {
    // Get the MediaConvert endpoint
    const endpoint = await getMediaConvertEndpoint();
    
    // Create MediaConvert client with endpoint
    const mc = new AWS.MediaConvert({
      endpoint,
      region: process.env.AWS_REGION || 'eu-west-1',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    });

    const jobParams = {
      Role: process.env.MEDIACONVERT_ROLE_ARN, // We'll need to create this
      Settings: {
        TimecodeConfig: {
          Source: 'ZEROBASED'
        },
        OutputGroups: [
          {
            Name: 'HLS',
            OutputGroupSettings: {
              Type: 'HLS_GROUP_SETTINGS',
              HlsGroupSettings: {
                Destination: `s3://${process.env.AWS_BUCKET_NAME}/${outputS3Path}/`,
                SegmentLength: 6, // 6-second segments for fast seeking
                MinSegmentLength: 0,
                DirectoryStructure: 'SINGLE_DIRECTORY',
                ManifestDurationFormat: 'INTEGER',
                StreamInfResolution: 'INCLUDE',
                ClientCache: 'ENABLED',
                CaptionLanguageSetting: 'OMIT',
                ManifestCompression: 'NONE',
                CodecSpecification: 'RFC_4281',
                OutputSelection: 'MANIFESTS_AND_SEGMENTS',
                ProgramDateTime: 'EXCLUDE',
                SegmentControl: 'SEGMENTED_FILES',
                TimedMetadataId3Frame: 'NONE',
                TimedMetadataId3Period: -1
              }
            },
            Outputs: [
              // 360p output
              {
                NameModifier: '_360p',
                VideoDescription: {
                  Width: 640,
                  Height: 360,
                  CodecSettings: {
                    Codec: 'H_264',
                    H264Settings: {
                      RateControlMode: 'CBR',
                      Bitrate: 800000, // 800 Kbps
                      FramerateControl: 'SPECIFIED',
                      FramerateNumerator: 25,
                      FramerateDenominator: 1,
                      GopSize: 50,
                      GopSizeUnits: 'FRAMES'
                    }
                  }
                },
                AudioDescriptions: [
                  {
                    CodecSettings: {
                      Codec: 'AAC',
                      AacSettings: {
                        Bitrate: 96000,
                        CodingMode: 'CODING_MODE_2_0',
                        SampleRate: 48000
                      }
                    }
                  }
                ],
                ContainerSettings: {
                  Container: 'M3U8'
                }
              },
              // 720p output
              {
                NameModifier: '_720p',
                VideoDescription: {
                  Width: 1280,
                  Height: 720,
                  CodecSettings: {
                    Codec: 'H_264',
                    H264Settings: {
                      RateControlMode: 'CBR',
                      Bitrate: 2500000, // 2.5 Mbps
                      FramerateControl: 'SPECIFIED',
                      FramerateNumerator: 25,
                      FramerateDenominator: 1,
                      GopSize: 50,
                      GopSizeUnits: 'FRAMES'
                    }
                  }
                },
                AudioDescriptions: [
                  {
                    CodecSettings: {
                      Codec: 'AAC',
                      AacSettings: {
                        Bitrate: 128000,
                        CodingMode: 'CODING_MODE_2_0',
                        SampleRate: 48000
                      }
                    }
                  }
                ],
                ContainerSettings: {
                  Container: 'M3U8'
                }
              },
              // 1080p output
              {
                NameModifier: '_1080p',
                VideoDescription: {
                  Width: 1920,
                  Height: 1080,
                  CodecSettings: {
                    Codec: 'H_264',
                    H264Settings: {
                      RateControlMode: 'CBR',
                      Bitrate: 5000000, // 5 Mbps
                      FramerateControl: 'SPECIFIED',
                      FramerateNumerator: 25,
                      FramerateDenominator: 1,
                      GopSize: 50,
                      GopSizeUnits: 'FRAMES'
                    }
                  }
                },
                AudioDescriptions: [
                  {
                    CodecSettings: {
                      Codec: 'AAC',
                      AacSettings: {
                        Bitrate: 128000,
                        CodingMode: 'CODING_MODE_2_0',
                        SampleRate: 48000
                      }
                    }
                  }
                ],
                ContainerSettings: {
                  Container: 'M3U8'
                }
              }
            ]
          }
        ],
        Inputs: [
          {
            FileInput: inputS3Url,
            AudioSelectors: {
              'Audio Selector 1': {
                DefaultSelection: 'DEFAULT'
              }
            },
            VideoSelector: {}
          }
        ]
      },
      UserMetadata: {
        GameId: gameId,
        ConversionType: 'HLS'
      }
    };

    const job = await mc.createJob(jobParams).promise();
    console.log('✅ MediaConvert job created:', job.Job.Id);
    
    return {
      jobId: job.Job.Id,
      status: job.Job.Status,
      outputPath: `s3://${process.env.AWS_BUCKET_NAME}/${outputS3Path}/`
    };

  } catch (error) {
    console.error('❌ Error creating MediaConvert job:', error);
    throw error;
  }
};

// Check job status
const getJobStatus = async (jobId) => {
  try {
    const endpoint = await getMediaConvertEndpoint();
    const mc = new AWS.MediaConvert({
      endpoint,
      region: process.env.AWS_REGION || 'eu-west-1',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    });

    const job = await mc.getJob({ Id: jobId }).promise();
    return {
      status: job.Job.Status,
      progress: job.Job.JobPercentComplete || 0,
      createdAt: job.Job.CreatedAt,
      finishedAt: job.Job.FinishedAt
    };
  } catch (error) {
    console.error('Error getting job status:', error);
    throw error;
  }
};

module.exports = {
  createHLSJob,
  getJobStatus,
  getMediaConvertEndpoint
};