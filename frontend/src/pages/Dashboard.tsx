import React, { useEffect, useState } from 'react';

interface Profile {
    email: string;
    first_name: string | null;
    last_name: string | null;
}

interface Task {
    id: number;
    title: string;
    status: string;
}

interface Meeting {
    id: number;
    title: string;
    scheduled_time: string; // Depending on how you manage dates, you might want to convert this into a Date object
}

interface DashboardData {
    profile: Profile;
    tasks: Task[];
    meetings: Meeting[];
}

interface DashboardProps {
    token: string;
}

const Dashboard: React.FC<DashboardProps> = ({ token }) => {
    const [data, setData] = useState<DashboardData | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const response = await fetch('http://localhost:8000/users/dashboard/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });
            if (response.ok) {
                const json: DashboardData = await response.json();
                setData(json);
            } else {
                console.error('Failed to fetch data');
            }
        };

        fetchData();
    }, [token]);

    if (!data) {
        return <p>Loading...</p>;
    }

    return (
        <div>
            <h1>Dashboard</h1>
            <h2>Profile</h2>
            <p>Email: {data.profile.email}</p>
            <p>First Name: {data.profile.first_name || 'Not provided'}</p>
            <p>Last Name: {data.profile.last_name || 'Not provided'}</p>
            <h2>Tasks</h2>
            <ul>
                {data.tasks.map(task => (
                    <li key={task.id}>{task.title} - {task.status}</li>
                ))}
            </ul>
            <h2>Meetings</h2>
            <ul>
                {data.meetings.map(meeting => (
                    <li key={meeting.id}>{meeting.title} at {new Date(meeting.scheduled_time).toLocaleString()}</li>
                ))}
            </ul>
        </div>
    );
};

export default Dashboard;
