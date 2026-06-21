import { BrowserRouter, Routes, Route } from "react-router-dom";

import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";


function App(){

return (
<BrowserRouter>

<Routes>

<Route path="/" element={<Upload/>}/>

<Route path="/dashboard" element={<Dashboard/>}/>

<Route path="/chat" element={<Chat/>}/>

</Routes>

</BrowserRouter>
)

}


export default App;