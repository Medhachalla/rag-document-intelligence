import { NavLink } from "react-router-dom";


function Navbar() {
    return (
        <nav>
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
    );
}


export default Navbar;
