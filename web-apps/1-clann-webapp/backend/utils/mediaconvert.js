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

// Create clips job with individual padding - SIMPLIFIED VERSION
const createClipsJob = async (inputS3Url, events, gameId) => {
  try {
    console.log('🎬 Creating MediaConvert clips job...');
    console.log('📹 Input:', inputS3Url);
    console.log('📝 Events:', events);

    // Get the MediaConvert endpoint
    const endpoint = await getMediaConvertEndpoint();
    
    // Create MediaConvert client with endpoint
    const mc = new AWS.MediaConvert({
      endpoint,
      region: process.env.AWS_REGION || 'eu-west-1',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    });

    const timestamp = Date.now();
    const outputPath = `clips/${gameId}/${timestamp}`;

    // Simple job: create one concatenated clip with all events
    const totalDuration = events.reduce((total, event) => {
      const beforePadding = event.beforePadding || 5;
      const afterPadding = event.afterPadding || 5;
      return total + beforePadding + afterPadding;
    }, 0);

    // Create input clippings for each event
    const inputClippings = events.map((event) => {
      const beforePadding = event.beforePadding || 5;
      const afterPadding = event.afterPadding || 5;
      const startTime = Math.max(0, event.timestamp - beforePadding);
      const duration = beforePadding + afterPadding;

      return {
        StartTimecode: formatTimecode(startTime),
        EndTimecode: formatTimecode(startTime + duration)
      };
    });

    const jobParams = {
      Role: process.env.MEDIACONVERT_ROLE_ARN,
      Settings: {
        TimecodeConfig: {
          Source: 'ZEROBASED'
        },
        Inputs: [
          {
            AudioSelectors: {
              'Audio Selector 1': {
                Offset: 0,
                DefaultSelection: 'DEFAULT',
                ProgramSelection: 1
              }
            },
            VideoSelector: {
              ColorSpace: 'FOLLOW'
            },
            FilterEnable: 'AUTO',
            PsiControl: 'USE_PSI',
            FilterStrength: 0,
            DeblockFilter: 'DISABLED',
            DenoiseFilter: 'DISABLED',
            TimecodeSource: 'EMBEDDED',
            FileInput: inputS3Url,
            InputClippings: inputClippings
          }
        ],
        OutputGroups: [
          {
            Name: 'File Group',
            OutputGroupSettings: {
              Type: 'FILE_GROUP_SETTINGS',
              FileGroupSettings: {
                Destination: `s3://${process.env.AWS_BUCKET_NAME}/${outputPath}/`
              }
            },
            Outputs: [
              {
                NameModifier: '_highlight_reel',
                VideoDescription: {
                  Width: 1920,
                  Height: 1080,
                  CodecSettings: {
                    Codec: 'H_264',
                    H264Settings: {
                      RateControlMode: 'QVBR',
                      MaxBitrate: 8000000, // 8 Mbps max
                      QvbrSettings: {
                        QvbrQualityLevel: 7
                      }
                    }
                  }
                },
                AudioDescriptions: [
                  {
                    AudioTypeControl: 'FOLLOW_INPUT',
                    CodecSettings: {
                      Codec: 'AAC',
                      AacSettings: {
                        AudioDescriptionBroadcasterMix: 'NORMAL',
                        Bitrate: 96000,
                        RateControlMode: 'CBR',
                        CodecProfile: 'LC',
                        CodingMode: 'CODING_MODE_2_0',
                        RawFormat: 'NONE',
                        SampleRate: 48000
                      }
                    }
                  }
                ],
                ContainerSettings: {
                  Container: 'MP4',
                  Mp4Settings: {
                    CslgAtom: 'INCLUDE',
                    FreeSpaceBox: 'EXCLUDE',
                    MoovPlacement: 'PROGRESSIVE_DOWNLOAD'
                  }
                }
              }
            ]
          }
        ]
      }
    };

    console.log('🚀 Submitting MediaConvert job...');
    console.log('📋 Job params:', JSON.stringify(jobParams, null, 2));
    
    const job = await mc.createJob(jobParams).promise();
    
    console.log('✅ MediaConvert job created:', job.Job.Id);
    return {
      jobId: job.Job.Id,
      outputPath: outputPath,
      status: job.Job.Status
    };

  } catch (error) {
    console.error('❌ Error creating MediaConvert clips job:', error);
    console.error('❌ Error details:', error.message);
    if (error.stack) {
      console.error('❌ Stack trace:', error.stack);
    }
    throw error;
  }
};

// Helper function to format seconds to timecode (HH:MM:SS:FF)
const formatTimecode = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const frames = Math.floor((seconds % 1) * 30); // Assuming 30fps
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}:${frames.toString().padStart(2, '0')}`;
};

module.exports = {
  createHLSJob,
  createClipsJob,
  getJobStatus,
  getMediaConvertEndpoint
};