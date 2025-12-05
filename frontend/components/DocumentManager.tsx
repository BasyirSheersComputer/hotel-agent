"use client";

/**
 * Copyright (c) 2025 Sheers Software Sdn. Bhd.
 * All Rights Reserved.
 * 
 * Document Manager Component
 * Handles document upload, listing, and deletion for KB management.
 */

import { useState, useEffect, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Document {
    doc_id: string;
    filename: string;
    status: string;
    uploaded_at: string;
    uploaded_by?: string;
}

interface DocumentManagerProps {
    isDemo?: boolean;
}

export default function DocumentManager({ isDemo = false }: DocumentManagerProps) {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [reindexing, setReindexing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

    // Fetch documents
    const fetchDocuments = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE}/api/admin/documents`, {
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                throw new Error("Failed to fetch documents");
            }

            const data = await res.json();
            setDocuments(data.documents || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load documents");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    // Handle file upload
    const handleUpload = async (files: FileList | null) => {
        if (!files || files.length === 0) return;

        setUploading(true);
        setError(null);
        setSuccess(null);

        const file = files[0];
        const formData = new FormData();
        formData.append("file", file);

        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE}/api/admin/upload`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
                body: formData,
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Upload failed");
            }

            const data = await res.json();
            setSuccess(`Successfully uploaded: ${data.filename}`);
            fetchDocuments();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
            setUploading(false);
        }
    };

    // Handle drag events
    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (isDemo) {
            setError("Upload is disabled in demo mode");
            return;
        }

        handleUpload(e.dataTransfer.files);
    };

    // Handle delete
    const handleDelete = async (docId: string) => {
        setError(null);
        setSuccess(null);

        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE}/api/admin/document/${docId}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                throw new Error("Failed to delete document");
            }

            setSuccess("Document deleted successfully");
            setDeleteConfirm(null);
            fetchDocuments();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Delete failed");
        }
    };

    // Handle reindex
    const handleReindex = async () => {
        setReindexing(true);
        setError(null);
        setSuccess(null);

        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE}/api/admin/reindex`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                throw new Error("Reindex failed");
            }

            const data = await res.json();
            setSuccess(`Reindex complete: ${data.success}/${data.total} documents processed`);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Reindex failed");
        } finally {
            setReindexing(false);
        }
    };

    // Format date
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    // Get status badge style
    const getStatusStyle = (status: string) => {
        switch (status) {
            case "active":
                return "bg-green-100 text-green-800";
            case "processing":
                return "bg-blue-100 text-blue-800";
            case "failed":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    return (
        <div className="space-y-6">
            {/* Alerts */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex justify-between items-center">
                    <p className="text-red-700">{error}</p>
                    <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">✕</button>
                </div>
            )}

            {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex justify-between items-center">
                    <p className="text-green-700">{success}</p>
                    <button onClick={() => setSuccess(null)} className="text-green-500 hover:text-green-700">✕</button>
                </div>
            )}

            {/* Upload Section */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Upload Document</h2>

                <div
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive
                            ? "border-blue-500 bg-blue-50"
                            : "border-slate-300 hover:border-slate-400"
                        } ${isDemo ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}`}
                >
                    <div className="text-4xl mb-3">📄</div>
                    <p className="text-slate-600 mb-2">
                        {uploading ? "Uploading..." : "Drag and drop your file here"}
                    </p>
                    <p className="text-sm text-slate-400 mb-4">
                        Supports PDF, TXT, and MD files (max 50MB)
                    </p>

                    <label className={`inline-flex items-center px-4 py-2 bg-slate-900 text-white rounded-lg font-medium ${isDemo || uploading ? "opacity-50 cursor-not-allowed" : "hover:bg-slate-800 cursor-pointer"
                        }`}>
                        <input
                            type="file"
                            className="hidden"
                            accept=".pdf,.txt,.md"
                            onChange={(e) => !isDemo && handleUpload(e.target.files)}
                            disabled={isDemo || uploading}
                        />
                        {uploading ? "Uploading..." : "Choose File"}
                    </label>

                    {isDemo && (
                        <p className="mt-4 text-sm text-yellow-600 bg-yellow-50 rounded-lg px-3 py-2 inline-block">
                            Upload is disabled in demo mode
                        </p>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-slate-900">
                    Documents ({documents.length})
                </h2>
                <button
                    onClick={handleReindex}
                    disabled={reindexing || isDemo}
                    className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${reindexing || isDemo
                            ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                            : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                        }`}
                >
                    <span className={reindexing ? "animate-spin" : ""}>🔄</span>
                    {reindexing ? "Reindexing..." : "Rebuild Index"}
                </button>
            </div>

            {/* Document List */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center text-slate-500">Loading documents...</div>
                ) : documents.length === 0 ? (
                    <div className="p-8 text-center text-slate-500">
                        <div className="text-4xl mb-3">📂</div>
                        <p>No documents uploaded yet</p>
                        <p className="text-sm text-slate-400 mt-1">Upload a PDF or TXT file to get started</p>
                    </div>
                ) : (
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                            <tr>
                                <th className="px-6 py-4 font-medium">Filename</th>
                                <th className="px-6 py-4 font-medium">Status</th>
                                <th className="px-6 py-4 font-medium">Uploaded</th>
                                <th className="px-6 py-4 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {documents.map((doc) => (
                                <tr key={doc.doc_id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 font-medium text-slate-900">
                                        <div className="flex items-center gap-2">
                                            <span>📄</span>
                                            {doc.filename}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusStyle(doc.status)}`}>
                                            {doc.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-600">
                                        {formatDate(doc.uploaded_at)}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        {deleteConfirm === doc.doc_id ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span className="text-slate-500 text-xs">Delete?</span>
                                                <button
                                                    onClick={() => handleDelete(doc.doc_id)}
                                                    className="px-3 py-1 bg-red-600 text-white rounded text-xs font-medium hover:bg-red-700"
                                                >
                                                    Yes
                                                </button>
                                                <button
                                                    onClick={() => setDeleteConfirm(null)}
                                                    className="px-3 py-1 bg-slate-200 text-slate-700 rounded text-xs font-medium hover:bg-slate-300"
                                                >
                                                    No
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => !isDemo && setDeleteConfirm(doc.doc_id)}
                                                disabled={isDemo}
                                                className={`text-red-600 hover:text-red-800 font-medium ${isDemo ? "opacity-50 cursor-not-allowed" : ""
                                                    }`}
                                            >
                                                Delete
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
