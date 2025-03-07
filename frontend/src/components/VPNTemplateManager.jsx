import React, { useState, useEffect } from "react";
import { Shield, Upload } from "lucide-react";
import config from '../config';

const API_URL = config.API_URL;

const VPNTemplateManager = () => {
    const [file, setFile] = useState(null);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            setError("Veuillez sélectionner un fichier");
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData();
        formData.append("template", file);

        try {
            const response = await fetch(`${API_URL}/api/vpn/template`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess("Template VPN mis à jour avec succès");
                setFile(null);
                // Reset file input
                e.target.reset();
            } else {
                throw new Error(data.error || "Erreur lors de l'upload du template");
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
                <Shield className="w-6 h-6 text-blue-500" />
                <h2 className="text-xl font-bold">Template VPN</h2>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded">
                    {error}
                </div>
            )}

            {success && (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded">
                    {success}
                </div>
            )}

            <form onSubmit={handleUpload} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fichier template OpenVPN (.ovpn)
                    </label>
                    <input
                        type="file"
                        accept=".ovpn"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-gray-500
                            file:mr-4 file:py-2 file:px-4
                            file:rounded file:border-0
                            file:text-sm file:font-semibold
                            file:bg-blue-50 file:text-blue-700
                            hover:file:bg-blue-100"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className={`flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${
                        loading ? "opacity-50 cursor-not-allowed" : ""
                    }`}
                >
                    <Upload className="w-4 h-4" />
                    {loading ? "Upload en cours..." : "Upload Template"}
                </button>
            </form>
        </div>
    );
};

export default VPNTemplateManager;