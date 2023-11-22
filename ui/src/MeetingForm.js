import React, { useState } from 'react';
import axios from 'axios';

const MeetingForm = () => {
    const [title, setTitle] = useState('');
    const [scheduler, setScheduler] = useState('');
    const [attendee, setAttendee] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    const handleSubmit = event => {
        event.preventDefault();

        const meeting = {
            title: title,
            scheduler: scheduler,
            attendee: attendee,
            start_date: startDate,
            end_date: endDate
        };

        axios.post('http://localhost:8000/api/meeting', meeting)
            .then(res => console.log(res.data));
    };

    return (
        <form onSubmit={handleSubmit}>
            <label>
                Title:
                <input type="text" name="title" onChange={e => setTitle(e.target.value)} />
            </label>
            <label>
                Scheduler:
                <input type="text" name="scheduler" onChange={e => setScheduler(e.target.value)} />
            </label>
            <label>
                Attendee:
                <input type="text" name="attendee" onChange={e => setAttendee(e.target.value)} />
            </label>
            <label>
                Start Date:
                <input type="date" name="startDate" onChange={e => setStartDate(e.target.value)} />
            </label>
            <label>
                End Date:
                <input type="date" name="startDate" onChange={e => setEndDate(e.target.value)} />
            </label>
            <input type="submit" value="Submit" />
        </form>
    );
};

export default MeetingForm;