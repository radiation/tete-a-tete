import React from 'react';
import UserList from './UserList';
import MeetingForm from './MeetingForm';
import MeetingList from './MeetingList';

function App() {
  console.log('App.js');
  return (
    <div className="App">
      <UserList />
      <MeetingForm />
      <MeetingList />
    </div>
  );
}

export default App;