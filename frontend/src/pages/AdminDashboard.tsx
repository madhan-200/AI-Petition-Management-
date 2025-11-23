import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { BarChart, FileText, Clock, TrendingUp } from 'lucide-react';

interface Stats {
    totalPetitions: number;
    pendingPetitions: number;
    resolvedPetitions: number;
    criticalPetitions: number;
}

const AdminDashboard: React.FC = () => {
    const [stats, setStats] = useState<Stats>({
        totalPetitions: 0,
        pendingPetitions: 0,
        resolvedPetitions: 0,
        criticalPetitions: 0,
    });
    const [petitions, setPetitions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await api.get('petitions/');
            const data = response.data;
            setPetitions(data);

            setStats({
                totalPetitions: data.length,
                pendingPetitions: data.filter((p: any) =>
                    ['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED', 'IN_PROGRESS'].includes(p.status)
                ).length,
                resolvedPetitions: data.filter((p: any) => p.status === 'RESOLVED').length,
                criticalPetitions: data.filter((p: any) => p.urgency === 'CRITICAL').length,
            });
        } catch (error) {
            console.error('Failed to fetch data', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="text-center py-10">Loading...</div>;
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-white shadow rounded-lg p-6">
                    <div className="flex items-center">
                        <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                            <FileText className="h-6 w-6 text-white" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                            <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Total Petitions</dt>
                                <dd className="text-2xl font-semibold text-gray-900">{stats.totalPetitions}</dd>
                            </dl>
                        </div>
                    </div>
                </div>

                <div className="bg-white shadow rounded-lg p-6">
                    <div className="flex items-center">
                        <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                            <Clock className="h-6 w-6 text-white" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                            <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                                <dd className="text-2xl font-semibold text-gray-900">{stats.pendingPetitions}</dd>
                            </dl>
                        </div>
                    </div>
                </div>

                <div className="bg-white shadow rounded-lg p-6">
                    <div className="flex items-center">
                        <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                            <TrendingUp className="h-6 w-6 text-white" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                            <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Resolved</dt>
                                <dd className="text-2xl font-semibold text-gray-900">{stats.resolvedPetitions}</dd>
                            </dl>
                        </div>
                    </div>
                </div>

                <div className="bg-white shadow rounded-lg p-6">
                    <div className="flex items-center">
                        <div className="flex-shrink-0 bg-red-500 rounded-md p-3">
                            <BarChart className="h-6 w-6 text-white" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                            <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Critical</dt>
                                <dd className="text-2xl font-semibold text-gray-900">{stats.criticalPetitions}</dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Petitions</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Citizen</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Urgency</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {petitions.slice(0, 10).map((petition) => (
                                <tr key={petition.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#{petition.id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{petition.title}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{petition.citizen_username}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{petition.department_name}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${petition.urgency === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                                            petition.urgency === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                                                petition.urgency === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-green-100 text-green-800'
                                            }`}>
                                            {petition.urgency}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{petition.status.replace('_', ' ')}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
