#!/bin/bash

# Lambda deployment script for ClannAI clip processor
set -e

echo "🚀 Deploying ClannAI Clip Processor Lambda..."

# Configuration
FUNCTION_NAME="clann-clip-processor"
REGION="eu-west-1"
RUNTIME="nodejs20.x"
HANDLER="index.handler"
ROLE_ARN="arn:aws:iam::905418018179:role/lambda-execution-role"
FFMPEG_LAYER_ARN="arn:aws:lambda:eu-west-1:533267207187:layer:ffmpeg628-x86_64:2"

# Create dependencies layer (only if node_modules exists and is not empty)
if [ -d "node_modules" ] && [ "$(ls -A node_modules)" ]; then
    echo "📦 Creating dependencies layer..."
    mkdir -p layer/nodejs
    cp -r node_modules layer/nodejs/
    cd layer
    zip -r ../dependencies-layer.zip .
    cd ..
    rm -rf layer
    
    # Upload layer
    echo "📤 Uploading dependencies layer..."
    LAYER_VERSION=$(aws lambda publish-layer-version \
        --layer-name clann-clip-processor-deps \
        --zip-file fileb://dependencies-layer.zip \
        --compatible-runtimes nodejs20.x \
        --region $REGION \
        --query 'Version' --output text)
    
    DEPS_LAYER_ARN="arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):layer:clann-clip-processor-deps:$LAYER_VERSION"
    echo "✅ Dependencies layer created: $DEPS_LAYER_ARN"
    
    rm -f dependencies-layer.zip
else
    echo "📦 Installing dependencies..."
    npm install --production
    
    echo "📦 Creating dependencies layer..."
    mkdir -p layer/nodejs
    cp -r node_modules layer/nodejs/
    cd layer
    zip -r ../dependencies-layer.zip .
    cd ..
    rm -rf layer
    
    # Upload layer
    echo "📤 Uploading dependencies layer..."
    LAYER_VERSION=$(aws lambda publish-layer-version \
        --layer-name clann-clip-processor-deps \
        --zip-file fileb://dependencies-layer.zip \
        --compatible-runtimes nodejs20.x \
        --region $REGION \
        --query 'Version' --output text)
    
    DEPS_LAYER_ARN="arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):layer:clann-clip-processor-deps:$LAYER_VERSION"
    echo "✅ Dependencies layer created: $DEPS_LAYER_ARN"
    
    rm -f dependencies-layer.zip
fi

# Create deployment package (exclude large files - dependencies now in layer)
echo "📁 Creating deployment package..."
zip -r function.zip . -x "*.git*" "deploy.sh" "README.md" "node_modules/*" "function.zip" "package-lock.json" "dependencies-layer.zip"

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "🔄 Updating existing function..."
    
    # Update function code
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $REGION
    
    # Update function configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --timeout 300 \
        --memory-size 1024 \
        --environment Variables="{AWS_BUCKET_NAME=end-nov-webapp-clann}" \
        --region $REGION
        
else
    echo "🆕 Creating new function..."
    
    # Create function
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://function.zip \
        --timeout 300 \
        --memory-size 1024 \
        --environment Variables="{AWS_BUCKET_NAME=end-nov-webapp-clann}" \
        --region $REGION
fi

# Add both FFmpeg and dependencies layers
echo "🎬 Adding layers (FFmpeg + Dependencies)..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --layers $FFMPEG_LAYER_ARN $DEPS_LAYER_ARN \
    --region $REGION

# Create function URL for easy access
echo "🔗 Creating function URL..."
aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --cors AllowCredentials=false,AllowHeaders="*",AllowMethods="*",AllowOrigins="*" \
    --region $REGION 2>/dev/null || echo "Function URL already exists"

# Get function URL
FUNCTION_URL=$(aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION --query 'FunctionUrl' --output text 2>/dev/null || echo "")

# Cleanup
rm -f function.zip

echo "✅ Deployment completed!"
echo ""
echo "📋 Function Details:"
echo "   Name: $FUNCTION_NAME"
echo "   Region: $REGION"
echo "   Runtime: $RUNTIME"
echo "   Memory: 1024 MB"
echo "   Timeout: 300 seconds"
if [ ! -z "$FUNCTION_URL" ]; then
    echo "   URL: $FUNCTION_URL"
fi
echo ""
echo "🧪 Test with:"
echo "curl -X POST $FUNCTION_URL \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"gameId\":\"test\",\"events\":[{\"timestamp\":60,\"beforePadding\":5,\"afterPadding\":3}],\"s3VideoUrl\":\"s3://your-bucket/video.mp4\"}'"