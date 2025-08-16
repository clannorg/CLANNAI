'use client'

import { useState, useCallback, useRef } from 'react'

interface VideoUploadProps {
  onUploadSuccess: (gameData: any) => void
  onClose: () => void
  teams: any[]
}

const VideoUpload: React.FC<VideoUploadProps> = ({ onUploadSuccess, onClose, teams }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadSpeed, setUploadSpeed] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [selectedTeam, setSelectedTeam] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  if (!API_BASE_URL) {
    throw new Error('NEXT_PUBLIC_API_URL environment variable is not set')
  }

  // File validation
  const validateFile = (file: File) => {
    const allowedTypes = ['video/mp4', 'video/mov', 'video/quicktime', 'video/avi']
    const maxSize = 5 * 1024 * 1024 * 1024 // 5GB

    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type. Only MP4, MOV, and AVI files are allowed.')
    }

    if (file.size > maxSize) {
      throw new Error('File size too large. Maximum size is 5GB.')
    }

    return true
  }

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    try {
      validateFile(file)
      setSelectedFile(file)
      setError('')
      
      // Auto-generate title from filename
      if (!title) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
        setTitle(nameWithoutExt)
      }
    } catch (err: any) {
      setError(err.message)
      setSelectedFile(null)
    }
  }, [title])

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  // File input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  // Upload file
  const handleUpload = async () => {
    if (!selectedFile || !title.trim() || !selectedTeam) {
      setError('Please fill in all required fields and select a file')
      return
    }

    try {
      setUploading(true)
      setError('')
      setUploadProgress(0)
      setUploadSpeed(0)
      setTimeRemaining(0)

      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('Authentication required')
      }

      // Step 1: Get presigned URL
      const presignedResponse = await fetch(`${API_BASE_URL}/api/games/upload/presigned-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          fileName: selectedFile.name,
          fileType: selectedFile.type,
          fileSize: selectedFile.size,
          teamId: selectedTeam
        })
      })

      if (!presignedResponse.ok) {
        const errorData = await presignedResponse.json()
        throw new Error(errorData.error || 'Failed to get upload URL')
      }

      const { uploadUrl, s3Key, publicUrl } = await presignedResponse.json()

      // Step 2: Upload file directly to S3 with progress tracking
      setUploadProgress(25)
      
      const uploadResponse = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        const startTime = Date.now()
        let lastLoaded = 0
        let lastTime = startTime
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const currentTime = Date.now()
            const timeElapsed = (currentTime - lastTime) / 1000 // seconds
            
            if (timeElapsed > 0.5) { // Update every 500ms to avoid too frequent updates
              // Calculate speed
              const bytesUploaded = event.loaded - lastLoaded
              const speedBps = bytesUploaded / timeElapsed // bytes per second
              const speedMbps = (speedBps / (1024 * 1024)).toFixed(1) // MB/s
              
              // Calculate time remaining
              const remainingBytes = event.total - event.loaded
              const estimatedSeconds = remainingBytes / speedBps
              
              setUploadSpeed(parseFloat(speedMbps))
              setTimeRemaining(Math.ceil(estimatedSeconds))
              
              lastLoaded = event.loaded
              lastTime = currentTime
            }
            
            // Progress from 25% to 75% based on upload completion
            const uploadProgress = (event.loaded / event.total) * 50 // 50% of total progress
            setUploadProgress(25 + uploadProgress)
          }
        })
        
        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(xhr)
          } else {
            reject(new Error(`S3 upload failed with status ${xhr.status}`))
          }
        })
        
        xhr.addEventListener('error', () => {
          reject(new Error('Failed to upload file to S3'))
        })
        
        xhr.open('PUT', uploadUrl)
        xhr.setRequestHeader('Content-Type', selectedFile.type)
        xhr.send(selectedFile)
      })

      setUploadProgress(75)

      // Step 3: Confirm upload and create game record
      const confirmResponse = await fetch(`${API_BASE_URL}/api/games/upload/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          teamId: selectedTeam,
          s3Key: s3Key,
          originalFilename: selectedFile.name,
          fileSize: selectedFile.size,
          fileType: selectedFile.type
        })
      })

      if (!confirmResponse.ok) {
        const errorData = await confirmResponse.json()
        throw new Error(errorData.error || 'Failed to confirm upload')
      }

      const result = await confirmResponse.json()
      setUploadProgress(100)

      // Success!
      setTimeout(() => {
        onUploadSuccess(result.game)
        onClose()
      }, 500)

    } catch (err: any) {
      console.error('Upload error:', err)
      setError(err.message || 'Upload failed')
      setUploadProgress(0)
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatTimeRemaining = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    if (minutes < 60) return `${minutes}m ${remainingSeconds}s`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}h ${remainingMinutes}m`
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Upload Video</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              disabled={uploading}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* File Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver 
                ? 'border-[#016F32] bg-green-50' 
                : selectedFile 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {selectedFile ? (
              <div className="space-y-3">
                <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-sm text-red-600 hover:text-red-700"
                  disabled={uploading}
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-lg font-medium text-gray-900">Drop your video file here</p>
                  <p className="text-sm text-gray-500">or click to browse (MP4, MOV, AVI - max 5GB)</p>
                </div>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                  disabled={uploading}
                >
                  Browse Files
                </button>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/mov,video/quicktime,video/avi"
              onChange={handleFileInputChange}
              className="hidden"
              disabled={uploading}
            />
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#016F32] focus:border-transparent"
                placeholder="Enter video title"
                disabled={uploading}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#016F32] focus:border-transparent"
                placeholder="Enter video description (optional)"
                disabled={uploading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Team *
              </label>
              <select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#016F32] focus:border-transparent"
                disabled={uploading}
                required
              >
                <option value="">Select a team</option>
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Upload Progress */}
          {uploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <div className="flex flex-col">
                  <span className="text-gray-600">Uploading...</span>
                  {uploadSpeed > 0 && (
                    <span className="text-xs text-gray-500 mt-1">
                      {uploadSpeed} MB/s
                      {timeRemaining > 0 && (
                        <> • {formatTimeRemaining(timeRemaining)} remaining</>
                      )}
                    </span>
                  )}
                </div>
                <span className="text-gray-600">{Math.round(uploadProgress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-[#016F32] h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || !title.trim() || !selectedTeam || uploading}
            className="px-6 py-2 bg-[#016F32] text-white rounded-lg hover:bg-[#016F32]/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Upload Video'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default VideoUpload