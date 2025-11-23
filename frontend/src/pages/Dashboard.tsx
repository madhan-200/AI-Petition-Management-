import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import PetitionStatusTimeline from '../components/PetitionStatusTimeline';
import { Plus } from 'lucide-react';

interface Petition {
    id: number;
    title: string;
    description: string;
    status: string;
    urgency: string;
    department_name: string;
    created_at: string;
    updated_at: string;
}

const Dashboard: React.FC = () => {
    const [petitions, setPetitions] = useState<Petition[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
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

        fetchPetitions();
    }, []);

    if (loading) {
        return <div className="text-center py-10">Loading...</div>;
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">My Petitions</h1>
                <Link
                    to="/submit-petition"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                >
                    <Plus className="w-5 h-5 mr-2" />
                    New Petition
                </Link>
            </div>

            {petitions.length === 0 ? (
                <div className="text-center py-10 bg-white rounded-lg shadow">
                    <p className="text-gray-500">No petitions found. Submit one to get started!</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {petitions.map((petition) => (
                        <div key={petition.id} className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-lg leading-6 font-medium text-gray-900">{petition.title}</h3>
                                    <p className="mt-1 max-w-2xl text-sm text-gray-500">{petition.description}</p>
                                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${petition.urgency === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                                                petition.urgency === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                                                    petition.urgency === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-green-100 text-green-800'
                                            }`}>
                                            {petition.urgency} Urgency
                                        </span>
                                        <span>Dept: {petition.department_name || 'Pending Classification'}</span>
                                        <span>ID: #{petition.id}</span>
                                    </div>
                                </div>
                                <div className="text-sm text-gray-500">
                                    {new Date(petition.created_at).toLocaleDateString()}
                                </div>
                            </div>
                            <div className="mt-6">
                                <PetitionStatusTimeline
                                    status={petition.status}
                                    created_at={petition.created_at}
                                    updated_at={petition.updated_at}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
