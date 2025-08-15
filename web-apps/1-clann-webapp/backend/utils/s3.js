const { S3Client, PutObjectCommand, GetObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');

const s3Client = new S3Client({
    region: process.env.AWS_REGION || 'eu-west-1',
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    }
});

const BUCKET_NAME = process.env.AWS_BUCKET_NAME || 'clannai-uploads';

// Generate pre-signed URL for direct browser upload
const generatePresignedUploadUrl = async (fileName, fileType, fileSize) => {
    try {
        // Validate file type
        const allowedTypes = ['video/mp4', 'video/mov', 'video/quicktime', 'video/avi'];
        if (!allowedTypes.includes(fileType)) {
            throw new Error('Invalid file type. Only MP4, MOV, and AVI files are allowed.');
        }

        // Validate file size (max 5GB)
        const maxSize = 5 * 1024 * 1024 * 1024; // 5GB
        if (fileSize > maxSize) {
            throw new Error('File size too large. Maximum size is 5GB.');
        }

        // Generate unique key
        const timestamp = Date.now();
        const cleanFileName = fileName.replace(/[^a-zA-Z0-9.-]/g, '_');
        const key = `videos/${timestamp}-${cleanFileName}`;

        const command = new PutObjectCommand({
            Bucket: BUCKET_NAME,
            Key: key,
            ContentType: fileType,
            ContentLength: fileSize,
            Metadata: {
                'original-filename': fileName,
                'upload-timestamp': timestamp.toString()
            }
        });

        // Generate presigned URL valid for 10 minutes
        const presignedUrl = await getSignedUrl(s3Client, command, { expiresIn: 600 });

        return {
            uploadUrl: presignedUrl,
            s3Key: key,
            publicUrl: `https://${BUCKET_NAME}.s3.${process.env.AWS_REGION || 'eu-west-1'}.amazonaws.com/${key}`
        };
    } catch (error) {
        console.error('Error generating presigned URL:', error);
        throw error;
    }
};

// Upload file directly to S3 (for server-side uploads)
const uploadToS3 = async (fileBuffer, fileName, fileType) => {
    try {
        const timestamp = Date.now();
        const cleanFileName = fileName.replace(/[^a-zA-Z0-9.-]/g, '_');
        const key = `videos/${timestamp}-${cleanFileName}`;

        const command = new PutObjectCommand({
            Bucket: BUCKET_NAME,
            Key: key,
            Body: fileBuffer,
            ContentType: fileType,
            Metadata: {
                'original-filename': fileName,
                'upload-timestamp': timestamp.toString()
            }
        });

        const result = await s3Client.send(command);
        const publicUrl = `https://${BUCKET_NAME}.s3.${process.env.AWS_REGION || 'eu-west-1'}.amazonaws.com/${key}`;

        return {
            s3Key: key,
            publicUrl: publicUrl,
            result: result
        };
    } catch (error) {
        console.error('Error uploading to S3:', error);
        throw error;
    }
};

// Get file info from S3
const getFileInfo = async (s3Key) => {
    try {
        const command = new GetObjectCommand({
            Bucket: BUCKET_NAME,
            Key: s3Key
        });

        const response = await s3Client.send(command);
        return {
            contentType: response.ContentType,
            contentLength: response.ContentLength,
            lastModified: response.LastModified,
            metadata: response.Metadata
        };
    } catch (error) {
        console.error('Error getting file info:', error);
        throw error;
    }
};

module.exports = {
    generatePresignedUploadUrl,
    uploadToS3,
    getFileInfo,
    BUCKET_NAME
};