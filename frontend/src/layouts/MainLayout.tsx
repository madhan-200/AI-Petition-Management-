import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store/store';
import { logout } from '../store/authSlice';
import { LogOut } from 'lucide-react';
import Chatbot from '../components/Chatbot';

const MainLayout: React.FC = () => {
    const { user } = useSelector((state: RootState) => state.auth);
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleLogout = () => {
        dispatch(logout());
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <Link to="/" className="flex-shrink-0 flex items-center text-xl font-bold text-indigo-600">
                                AI Petition
                            </Link>
                        </div>
                        <div className="flex items-center space-x-4">
                            {user ? (
                                <>
                                    <span className="text-gray-700">Welcome, {user.username}</span>
                                    <button
                                        onClick={handleLogout}
                                        className="p-2 rounded-md text-gray-400 hover:text-gray-500 focus:outline-none"
                                    >
                                        <LogOut className="h-6 w-6" />
                                    </button>
                                </>
                            ) : (
                                <div className="space-x-4">
                                    <Link to="/login" className="text-gray-700 hover:text-indigo-600">Login</Link>
                                    <Link to="/signup" className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Sign Up</Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </nav>
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <Outlet />
            </main>
            <Chatbot />
        </div>
    );
};

export default MainLayout;
