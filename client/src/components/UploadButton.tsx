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
        <div className="flex items-center space-x-2 text-sm text-secondary animate-slideInDown bg-accent/5 px-3 py-1.5 rounded-lg">
          <FileText className="h-4 w-4 text-accent animate-pulse" />
          <span className="truncate max-w-48 font-medium">{currentFileName}</span>
        </div>
      )}
      
      <button
        onClick={openFileDialog}
        disabled={isLoading}
        className="btn flex items-center space-x-2 relative overflow-hidden group"
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
        
        <div className="relative z-10 flex items-center space-x-2 transition-transform duration-300 group-hover:scale-105">
          {isLoading ? (
            <div className="spinner" style={{ width: '1rem', height: '1rem' }} />
          ) : (
            <Upload className="h-4 w-4 transition-transform duration-300 group-hover:rotate-12" />
          )}
          
          <span className="text-sm font-medium">
            {isLoading ? 'Processing...' : 'New CSV'}
          </span>
        </div>
        
        <div className="absolute inset-0 bg-gradient-to-r from-accent/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      </button>
    </div>
  );
};

export default UploadButton; 