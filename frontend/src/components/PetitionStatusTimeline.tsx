import React from 'react';
import { CheckCircle, Clock, XCircle } from 'lucide-react';

interface Props {
    status: string;
    created_at: string;
    updated_at: string;
}

const steps = [
    { id: 'SUBMITTED', label: 'Submitted' },
    { id: 'UNDER_REVIEW', label: 'Under Review' },
    { id: 'ASSIGNED', label: 'Assigned' },
    { id: 'IN_PROGRESS', label: 'In Progress' },
    { id: 'RESOLVED', label: 'Resolved' },
];

const PetitionStatusTimeline: React.FC<Props> = ({ status, updated_at }) => {
    const currentStepIndex = steps.findIndex((s) => s.id === status);
    const isRejected = status === 'REJECTED';
    const isClosed = status === 'CLOSED';

    if (isRejected) {
        return (
            <div className="flex items-center text-red-600">
                <XCircle className="w-5 h-5 mr-2" />
                <span className="font-medium">Petition Rejected</span>
            </div>
        );
    }

    if (isClosed) {
        return (
            <div className="flex items-center text-gray-600">
                <XCircle className="w-5 h-5 mr-2" />
                <span className="font-medium">Petition Closed</span>
            </div>
        );
    }

    return (
        <div className="w-full py-4">
            <div className="flex items-center justify-between relative">
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-gray-200 -z-10"></div>
                {steps.map((step, index) => {
                    const isCompleted = index <= currentStepIndex;
                    const isCurrent = index === currentStepIndex;

                    return (
                        <div key={step.id} className="flex flex-col items-center bg-white px-2">
                            <div
                                className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${isCompleted
                                    ? 'bg-indigo-600 border-indigo-600 text-white'
                                    : 'bg-white border-gray-300 text-gray-300'
                                    }`}
                            >
                                {isCompleted ? <CheckCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                            </div>
                            <span
                                className={`text-xs mt-1 font-medium ${isCurrent ? 'text-indigo-600' : 'text-gray-500'
                                    }`}
                            >
                                {step.label}
                            </span>
                        </div>
                    );
                })}
            </div>
            <div className="mt-2 text-xs text-gray-500 text-right">
                Last updated: {new Date(updated_at).toLocaleString()}
            </div>
        </div>
    );
};

export default PetitionStatusTimeline;
