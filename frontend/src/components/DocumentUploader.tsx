import React, { useState, useRef } from 'react';
import { Upload, FileText, RefreshCw, Cpu } from 'lucide-react';

interface DocumentUploaderProps {
  onUpload: (file: File, engine: string, extractOnly: boolean) => void;
  isLoading: boolean;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onUpload, isLoading }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [engine, setEngine] = useState('auto');
  const [extractOnly, setExtractOnly] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File) => {
    setSelectedFile(file);
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile) {
      onUpload(selectedFile, engine, extractOnly);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Upload className="w-5 h-5 text-indigo-600" />
            Upload Document for Verification
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Accepts utility bills, rent agreements, bank statements & identity cards (PNG, JPEG, WebP, PDF &le; 15MB)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-600 font-medium flex items-center gap-1">
            <Cpu className="w-3.5 h-3.5 text-slate-500" /> Engine:
          </label>
          <select
            value={engine}
            onChange={(e) => setEngine(e.target.value)}
            className="text-xs border border-slate-300 rounded-md px-2 py-1 bg-slate-50 text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="auto">Auto (Tesseract / Fallback)</option>
            <option value="tesseract">Tesseract OCR</option>
            <option value="mock">Deterministic Mock (Benchmark)</option>
          </select>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-indigo-500 bg-indigo-50/50'
              : selectedFile
              ? 'border-emerald-400 bg-emerald-50/20'
              : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".png,.jpg,.jpeg,.webp,.pdf,image/png,image/jpeg,image/webp,application/pdf"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
          />

          {selectedFile ? (
            <div className="flex flex-col items-center">
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="max-h-36 rounded-lg shadow-sm mb-3 object-contain border border-slate-200" />
              ) : (
                <FileText className="w-12 h-12 text-emerald-600 mb-2" />
              )}
              <div className="text-sm font-semibold text-slate-800">{selectedFile.name}</div>
              <div className="text-xs text-slate-500 mt-0.5">
                {(selectedFile.size / 1024).toFixed(1)} KB &bull; {selectedFile.type || 'Document'}
              </div>
              <span className="mt-3 text-xs text-indigo-600 hover:underline">Click or drop to replace file</span>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 mb-3">
                <Upload className="w-6 h-6" />
              </div>
              <div className="text-sm font-semibold text-slate-800">
                Drag & drop your document here, or <span className="text-indigo-600">browse</span>
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Supports English, Hindi, and Marathi Devanagari text
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between mt-4">
          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700">
            <input
              type="checkbox"
              checked={extractOnly}
              onChange={(e) => setExtractOnly(e.target.checked)}
              className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span>Extract address fields only (skip geographic verification)</span>
          </label>

          <button
            type="submit"
            disabled={!selectedFile || isLoading}
            className={`px-5 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all ${
              !selectedFile || isLoading
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow'
            }`}
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Processing Document...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" />
                {extractOnly ? 'Extract Address' : 'Verify Document Address'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
