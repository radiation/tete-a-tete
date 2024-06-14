import React, { useEffect, useState } from 'react';

interface ProfileProps {
  token: string;
}

const Profile: React.FC<ProfileProps> = ({ token }) => {
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    const fetchProfile = async () => {
        try {
          const response = await fetch('http://localhost:8000/users/user', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
          }
          const data = await response.json();
          console.log("Profile Data:", data);  // Check what is being received exactly
          setProfile(data);
        } catch (error) {
          console.error('Failed to fetch profile:', error);
        }
      };

    fetchProfile();
  }, [token]);

  return (
    <div>
      <h1>Profile</h1>
      {profile ? (
        <div>
          <p>Email: {profile.email}</p>
          <p>First Name: {profile.first_name || 'Not provided'}</p>
          <p>Last Name: {profile.last_name || 'Not provided'}</p>
        </div>
      ) : (
        <p>Loading profile...</p>
      )}
    </div>
  );
};

export default Profile;
