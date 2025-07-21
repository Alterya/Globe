import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>;
  isLoading?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, isLoading = false }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setErrorMessage('Please select a CSV file');
      setUploadStatus('error');
      setTimeout(() => setUploadStatus('idle'), 3000);
      return;
    }

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      setErrorMessage('File size must be less than 50MB');
      setUploadStatus('error');
      setTimeout(() => setUploadStatus('idle'), 3000);
      return;
    }

    try {
      setUploadStatus('idle'); // Keep uploading state
      await onFileUpload(file);
      // Don't set success status - let the parent component handle navigation
      setErrorMessage('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Upload failed');
      setUploadStatus('error');
      setTimeout(() => {
        setUploadStatus('idle');
        setErrorMessage('');
      }, 3000);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const getStatusIcon = () => {
    if (isLoading) {
      return <div className="spinner" style={{ width: '2rem', height: '2rem' }} />;
    }
    
    switch (uploadStatus) {
      case 'success':
        return <CheckCircle className="h-12 w-12 text-success" />;
      case 'error':
        return <AlertCircle className="h-12 w-12 text-error" />;
      default:
        return <Upload className="h-12 w-12 text-muted" />;
    }
  };

  const getStatusMessage = () => {
    if (isLoading) {
      return 'Processing your CSV file...';
    }
    
    switch (uploadStatus) {
      case 'success':
        return 'CSV uploaded successfully!';
      case 'error':
        return errorMessage;
      default:
        return 'Drop your VASP CSV file here, or click to browse';
    }
  };

  const getStatusColor = () => {
    switch (uploadStatus) {
      case 'success':
        return 'text-success';
      case 'error':
        return 'text-error';
      default:
        return 'text-secondary';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-4">
            Welcome to Globe
          </h1>
          <p className="text-lg text-secondary">
            Upload your VASP threat intelligence CSV file to begin analysis
          </p>
        </div>

        <div
          className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center
            transition-all duration-300 cursor-pointer
            ${isDragActive 
              ? 'border-accent bg-accent-light scale-105' 
              : uploadStatus === 'error'
                ? 'border-error bg-error/5'
                : uploadStatus === 'success'
                  ? 'border-success bg-success/5'
                  : 'border-border-color bg-glass-bg hover:border-accent hover:bg-accent-light'
            }
          `}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={openFileDialog}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            className="hidden"
            disabled={isLoading}
          />

          <div className="flex flex-col items-center space-y-4">
            {getStatusIcon()}
            
            <div className="space-y-2">
              <p className={`text-lg font-medium ${getStatusColor()}`}>
                {getStatusMessage()}
              </p>
              
              {uploadStatus === 'idle' && (
                <div className="space-y-2">
                  <p className="text-sm text-muted">
                    Supports: CSV files up to 50MB
                  </p>
                  <div className="flex items-center justify-center space-x-2 text-xs text-muted">
                    <FileText className="h-4 w-4" />
                    <span>Drag & Drop or Click to Upload</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {isDragActive && (
            <div className="absolute inset-0 bg-accent/10 border-2 border-accent border-dashed rounded-2xl flex items-center justify-center">
              <p className="text-accent font-medium">Drop CSV file here</p>
            </div>
          )}
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-muted">
            Your data is processed locally and securely. No files are uploaded to external servers.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FileUpload; 