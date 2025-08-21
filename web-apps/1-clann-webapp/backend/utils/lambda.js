const AWS = require('aws-sdk');

// Initialize Lambda client
const lambda = new AWS.Lambda({
    region: process.env.AWS_REGION || 'eu-west-1'
});

const LAMBDA_FUNCTION_NAME = 'clann-clip-processor';

/**
 * Invoke Lambda function for clip processing
 */
const invokeClipProcessor = async (gameId, events, s3VideoUrl) => {
    console.log('🚀 Invoking Lambda clip processor...');
    console.log(`📊 Processing ${events.length} events for game ${gameId}`);
    
    const payload = {
        gameId,
        events,
        s3VideoUrl
    };
    
    const params = {
        FunctionName: LAMBDA_FUNCTION_NAME,
        InvocationType: 'RequestResponse', // Synchronous invocation
        Payload: JSON.stringify(payload)
    };
    
    try {
        console.log('📤 Sending payload to Lambda:', JSON.stringify(payload, null, 2));
        
        const result = await lambda.invoke(params).promise();
        
        if (result.FunctionError) {
            console.error('❌ Lambda function error:', result.FunctionError);
            console.error('📄 Error payload:', result.Payload);
            throw new Error(`Lambda function failed: ${result.FunctionError}`);
        }
        
        const response = JSON.parse(result.Payload);
        console.log('✅ Lambda response:', response);
        
        if (response.statusCode !== 200) {
            const errorBody = JSON.parse(response.body);
            throw new Error(`Lambda returned error: ${errorBody.error || errorBody.message}`);
        }
        
        const responseBody = JSON.parse(response.body);
        console.log('🎉 Clip processing completed successfully');
        
        return {
            success: true,
            downloadUrl: responseBody.downloadUrl,
            fileName: responseBody.fileName,
            duration: responseBody.duration,
            eventCount: responseBody.eventCount,
            outputKey: responseBody.outputKey,
            message: responseBody.message
        };
        
    } catch (error) {
        console.error('❌ Lambda invocation failed:', error);
        throw new Error(`Failed to invoke Lambda function: ${error.message}`);
    }
};

module.exports = {
    invokeClipProcessor
};