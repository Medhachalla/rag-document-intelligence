import { NavLink } from "react-router-dom";


function Navbar() {
    return (
        <header className="navbar">
            <NavLink className="brand" to="/" end>
                <span className="brand-mark">
                    DS
                </span>

                <span>
                    DocSense AI
                </span>
            </NavLink>

            <nav className="nav-links">
                <NavLink to="/" end>
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
