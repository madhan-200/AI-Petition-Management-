import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { AlertCircle } from 'lucide-react';

interface Petition {
    id: number;
    title: string;
    description: string;
    status: string;
    urgency: string;
    department_name: string;
    citizen_username: string;
    created_at: string;
    updated_at: string;
}

const OfficerDashboard: React.FC = () => {
    const [petitions, setPetitions] = useState<Petition[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedPetition, setSelectedPetition] = useState<Petition | null>(null);
    const [newStatus, setNewStatus] = useState('');
    const [remarks, setRemarks] = useState('');

    useEffect(() => {
        fetchPetitions();
    }, []);

    const fetchPetitions = async () => {
        try {
            const response = await api.get('petitions/');
            setPetitions(response.data);
        } catch (error) {
            console.error('Failed to fetch petitions', error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateStatus = async () => {
        if (!selectedPetition || !newStatus) return;

        try {
            await api.patch(`petitions/${selectedPetition.id}/`, {
                status: newStatus,
                remarks: remarks,
            });
            fetchPetitions();
            setSelectedPetition(null);
            setNewStatus('');
            setRemarks('');
        } catch (error) {
            console.error('Failed to update petition', error);
        }
    };

    if (loading) {
        return <div className="text-center py-10">Loading...</div>;
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Officer Dashboard</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                    {petitions.map((petition) => (
                        <div
                            key={petition.id}
                            className={`bg-white shadow rounded-lg p-6 cursor-pointer hover:shadow-md transition-shadow ${selectedPetition?.id === petition.id ? 'ring-2 ring-indigo-500' : ''
                                }`}
                            onClick={() => setSelectedPetition(petition)}
                        >
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <h3 className="text-lg font-medium text-gray-900">{petition.title}</h3>
                                    <p className="mt-1 text-sm text-gray-500">{petition.description}</p>
                                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${petition.urgency === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                                            petition.urgency === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                                                petition.urgency === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-green-100 text-green-800'
                                            }`}>
                                            {petition.urgency}
                                        </span>
                                        <span>Citizen: {petition.citizen_username}</span>
                                        <span>Dept: {petition.department_name}</span>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${petition.status === 'RESOLVED' ? 'bg-green-100 text-green-800' :
                                        petition.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                        {petition.status.replace('_', ' ')}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="lg:col-span-1">
                    {selectedPetition ? (
                        <div className="bg-white shadow rounded-lg p-6 sticky top-6">
                            <h2 className="text-lg font-medium text-gray-900 mb-4">Update Status</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Petition ID</label>
                                    <p className="mt-1 text-sm text-gray-900">#{selectedPetition.id}</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">New Status</label>
                                    <select
                                        value={newStatus}
                                        onChange={(e) => setNewStatus(e.target.value)}
                                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                    >
                                        <option value="">Select Status</option>
                                        <option value="UNDER_REVIEW">Under Review</option>
                                        <option value="ASSIGNED">Assigned</option>
                                        <option value="IN_PROGRESS">In Progress</option>
                                        <option value="RESOLVED">Resolved</option>
                                        <option value="REJECTED">Rejected</option>
                                        <option value="CLOSED">Closed</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Remarks</label>
                                    <textarea
                                        value={remarks}
                                        onChange={(e) => setRemarks(e.target.value)}
                                        rows={3}
                                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                        placeholder="Add remarks..."
                                    />
                                </div>
                                <button
                                    onClick={handleUpdateStatus}
                                    disabled={!newStatus}
                                    className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Update Status
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-white shadow rounded-lg p-6 text-center text-gray-500">
                            <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                            <p>Select a petition to update its status</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OfficerDashboard;
