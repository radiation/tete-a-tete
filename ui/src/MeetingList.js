import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MeetingList = () => {
    const [meetings, setMeetings] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:8000/api/meeting?format=json') // replace with your Django API endpoint
            .then(response => {
                setMeetings(response.data);
            })
            .catch(error => {
                console.error('There was an error!', error);
            });
    }, []);

    return (
        <div>
            {meetings.map(meeting => (
                <div key={meeting.id}>
                    <h2>{meeting.title}</h2>
                    <p>{meeting.start_date}</p>
                </div>
            ))}
        </div>
    );
};

export default MeetingList;