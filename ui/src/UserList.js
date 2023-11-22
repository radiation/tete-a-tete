import React, { useEffect, useState } from 'react';
import axios from 'axios';

const UserList = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:8000/api/user?format=json')
            .then(response => {
                setUsers(response.data);
            })
            .catch(error => {
                console.error('There was an error!', error);
            });
    }, []);

    return (
        <div>
            {users.map(user => (
                <div key={user.id}>
                    <h2>{user.first_name} {user.last_name}</h2>
                    <p>{user.email_address}</p>
                </div>
            ))}
        </div>
    );
};

export default UserList;
