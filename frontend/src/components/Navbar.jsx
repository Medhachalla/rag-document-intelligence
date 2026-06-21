import { NavLink } from "react-router-dom";


function Navbar() {
    return (
        <header className="navbar">
            <NavLink className="brand" to="/">
                DocSense AI
            </NavLink>

            <nav className="nav-links">
                <NavLink to="/">
                    Dashboard
                </NavLink>

                <NavLink to="/upload">
                    Upload
                </NavLink>

                <NavLink to="/chat">
                    Chat
                </NavLink>
            </nav>
        </header>
    );
}


export default Navbar;
