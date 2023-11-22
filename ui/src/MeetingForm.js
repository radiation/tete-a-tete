import React, { useState } from 'react';
import axios from 'axios';

const MeetingForm = () => {
    const [title, setTitle] = useState('');
    const [startDate, setStartDate] = useState('');

    const handleSubmit = event => {
        event.preventDefault();

        const meeting = {
            title: title,
            start_date: startDate
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
                Start Date:
                <input type="date" name="startDate" onChange={e => setStartDate(e.target.value)} />
            </label>
            <input type="submit" value="Submit" />
        </form>
    );
};

export default MeetingForm;