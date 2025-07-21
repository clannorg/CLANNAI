require('dotenv').config();
const { S3Client, ListBucketsCommand, HeadBucketCommand, PutObjectCommand } = require('@aws-sdk/client-s3');

// Configure AWS SDK v3
const s3Client = new S3Client({
    region: process.env.AWS_REGION,
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    }
});

async function testS3Connection() {
    console.log('\n=== Testing S3 Connection ===\n');
    
    try {
        // Test 1: List buckets
        console.log('Test 1: Listing buckets...');
        const listBucketsResponse = await s3Client.send(new ListBucketsCommand({}));
        console.log('✅ Successfully connected to S3');
        console.log('Available buckets:', listBucketsResponse.Buckets.map(b => b.Name));

        // Test 2: Check specific bucket
        console.log('\nTest 2: Checking target bucket...');
        const bucketName = 'end-nov-webapp-clann';
        if (!bucketName) {
            throw new Error('AWS_BUCKET_NAME not set in environment variables');
        }
        
        await s3Client.send(new HeadBucketCommand({ Bucket: bucketName }));
        console.log(`✅ Successfully verified bucket: ${bucketName}`);

        // Test 3: Upload test object
        console.log('\nTest 3: Uploading test object...');
        const testData = {
            message: "Hello from S3 test!",
            timestamp: new Date().toISOString()
        };

        const uploadParams = {
            Bucket: bucketName,
            Key: `test-uploads/test-${Date.now()}.json`,
            Body: JSON.stringify(testData),
            ContentType: 'application/json'
        };

        const uploadResult = await s3Client.send(new PutObjectCommand(uploadParams));
        console.log('✅ Successfully uploaded test object');
        console.log('Upload details:', {
            bucket: bucketName,
            key: uploadParams.Key,
            etag: uploadResult.ETag
        });

    } catch (error) {
        console.error('❌ S3 Test Failed:', error.message);
        if (error.code) {
            console.error('Error Code:', error.code);
        }
    }
}

// Run the test
testS3Connection();
