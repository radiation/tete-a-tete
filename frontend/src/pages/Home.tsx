import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
    return (
        <div>
            <h1>Welcome to Our Application</h1>
            <p>This is the best place to manage your tasks and meetings efficiently.</p>
            <div>
                <Link to="/login">Login</Link> | <Link to="/register">Sign Up</Link>
            </div>
            <section>
                <h2>Features</h2>
                <ul>
                    <li>Manage your tasks</li>
                    <li>Schedule meetings</li>
                    <li>Collaborate with your team</li>
                </ul>
            </section>
            <section>
                <h2>Contact Us</h2>
                <p>If you have any questions, please feel free to <Link to="/contact">contact us</Link>.</p>
            </section>
        </div>
    );
};

export default Home;
