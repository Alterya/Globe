import React, { useRef } from 'react';
import { Upload, FileText } from 'lucide-react';

interface UploadButtonProps {
  onFileUpload: (file: File) => Promise<void>;
  isLoading?: boolean;
  currentFileName?: string;
}

const UploadButton: React.FC<UploadButtonProps> = ({ 
  onFileUpload, 
  isLoading = false,
  currentFileName 
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
      }

      // Validate file size (max 50MB)
      if (file.size > 50 * 1024 * 1024) {
        alert('File size must be less than 50MB');
        return;
      }

      try {
        await onFileUpload(file);
      } catch (error) {
        alert(error instanceof Error ? error.message : 'Upload failed');
      }
    }
    
    // Reset input
    e.target.value = '';
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="flex items-center space-x-3">
      {currentFileName && (
        <div className="flex items-center space-x-2 text-sm text-secondary">
          <FileText className="h-4 w-4" />
          <span className="truncate max-w-48">{currentFileName}</span>
        </div>
      )}
      
      <button
        onClick={openFileDialog}
        disabled={isLoading}
        className="btn flex items-center space-x-2 hover:scale-105 transition-transform"
        title="Upload new CSV file"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
          disabled={isLoading}
        />
        
        {isLoading ? (
          <div className="spinner" style={{ width: '1rem', height: '1rem' }} />
        ) : (
          <Upload className="h-4 w-4" />
        )}
        
        <span className="text-sm font-medium">
          {isLoading ? 'Uploading...' : 'New CSV'}
        </span>
      </button>
    </div>
  );
};

export default UploadButton; 